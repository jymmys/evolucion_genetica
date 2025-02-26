import sys
from pathlib import Path
import numpy as np
from typing import List
import random
import argparse
import json
import multiprocessing
from rich.panel import Panel
from rich.table import Table

# Agregar el directorio raíz al path de Python
current_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(current_dir))

from src.genetic.agent import TradingAgent
from src.config.config import GeneticConfig
from src.indicators.technical import AVAILABLE_INDICATORS
from src.utils.console import (
    console,
    print_generation_stats,
    create_progress,
    print_header,
    print_menu,
    print_training_summary
)
from src.utils.visualization import plot_training_history, create_performance_report
from src.utils.agent_bank import AgentBank
from src.indicators.ninjatrader import NinjaIndicators
from src.optimization.optimizer import ParameterOptimizer

def show_menu():
    return print_menu()

def train_agents(config: GeneticConfig, output_path: str):
    print_header()
    n_cpus = max(1, multiprocessing.cpu_count() - 2)
    console.print(f"[bold green]Iniciando entrenamiento con {n_cpus} procesos paralelos[/bold green]")
    
    # Inicializar banco de agentes
    bank = AgentBank(output_path)
    
    # Inicializar población
    with create_progress() as progress:
        task = progress.add_task("Inicializando población...", total=config.population_size)
        agents = []
        for _ in range(config.population_size):
            agents.append(TradingAgent(AVAILABLE_INDICATORS))
            progress.advance(task)
    
    best_fitness_history = []
    best_agent = None
    
    # Barra de progreso para generaciones
    with create_progress() as progress:
        gen_task = progress.add_task("Evolucionando...", total=config.generations)
        
        for gen in range(config.generations):
            # Evaluar población
            with multiprocessing.Pool(n_cpus) as pool:
                fitness_values = pool.map(evaluate_agent, agents)
            
            # Actualizar fitness y encontrar el mejor
            for agent, fitness in zip(agents, fitness_values):
                agent.fitness = fitness
            
            # Ordenar agentes por fitness
            agents.sort(key=lambda x: x.fitness, reverse=True)
            current_best = agents[0]
            
            # Guardar el mejor agente
            if best_agent is None or current_best.fitness > best_agent.fitness:
                best_agent = current_best
                best_agent_path = f"{output_path}/best_agent_gen_{gen}.pkl"
                best_agent.save(best_agent_path)
                console.print(f"[bold green]Nuevo mejor agente guardado: {best_agent_path}[/bold green]")
            
            # Selección y reproducción
            next_generation = []
            elite_count = max(1, int(0.1 * len(agents)))
            next_generation.extend(agents[:elite_count])
            
            while len(next_generation) < config.population_size:
                parent1 = tournament_select(agents, k=3)
                parent2 = tournament_select(agents, k=3)
                
                if random.random() < config.crossover_prob:
                    child1, child2 = parent1.crossover(parent2, 1.0)
                    child1.mutate(config.mutation_prob)
                    child2.mutate(config.mutation_prob)
                    next_generation.extend([child1, child2])
            
            agents = next_generation[:config.population_size]
            
            # Guardar mejores agentes en el banco
            for agent in agents[:config.elite_size]:
                metrics = {
                    "sharpe_ratio": agent.sharpe_ratio,
                    "profit_factor": agent.profit_factor,
                    "drawdown": agent.drawdown,
                    "trades": agent.trades,
                    "fitness": agent.fitness
                }
                agent_id = bank.save_agent(agent, gen, metrics)
                console.print(f"[cyan]Agente {agent_id} guardado en el banco[/cyan]")
            
            # Mostrar mejores agentes periódicamente
            if gen % 5 == 0:
                console.print("\n[bold yellow]Top 5 Mejores Agentes hasta ahora:[/bold yellow]")
                best_agents = bank.get_best_agents(n=5)
                for agent_id, data in best_agents:
                    bank.display_agent_stats(agent_id)
            
            # Estadísticas
            best_fitness = max(fitness_values)
            avg_fitness = np.mean(fitness_values)
            best_fitness_history.append(best_fitness)
            
            print_generation_stats(gen, best_agent, avg_fitness)
            progress.advance(gen_task)
    
    print_training_summary(max(best_fitness_history))
    
    # Agregar visualización al final del entrenamiento
    plot_training_history(best_fitness_history, output_path)
    create_performance_report(best_agent, output_path)
    
    # Al finalizar el entrenamiento, mostrar resumen
    console.print("\n[bold green]Resumen Final del Banco de Agentes[/bold green]")
    best_agents = bank.get_best_agents(n=10)
    for agent_id, data in best_agents:
        bank.display_agent_stats(agent_id)
    
    return best_agent, best_fitness_history

def tournament_select(population: List[TradingAgent], k: int) -> TradingAgent:
    """Selección por torneo"""
    tournament = random.sample(population, k)
    return max(tournament, key=lambda agent: agent.fitness)

def evaluate_agent(agent: TradingAgent) -> float:
    """Evalúa un agente y retorna su fitness normalizado"""
    try:
        # Generar datos de mercado simulados
        n_periods = 100
        market_data = np.random.random((n_periods, 4))
        market_data = np.cumsum(market_data, axis=0) * 0.01  # Reducir la escala
        
        # Obtener señales de mercado simulados
        signals = np.array([agent.get_signal(market_data[:i+1]) 
                          for i in range(len(market_data)-1)])
        signals = np.clip(signals, -1, 1)  # Limitar señales entre -1 y 1
        
        # Calcular retornos
        price_changes = np.diff(market_data[:, 3])
        returns = price_changes * signals
        if len(returns) == 0:
            return 0.0
        
        # Calcular métricas normalizadas
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        # Profit factor normalizado
        profit_factor = min(
            (np.sum(positive_returns) / abs(np.sum(negative_returns)) 
             if len(negative_returns) > 0 else 1.0),
            10.0  # Límite máximo
        )
        
        # Sharpe ratio normalizado
        sharpe = min(
            (np.mean(returns) / (np.std(returns) + 1e-6)),  # Evitar división por cero
            5.0  # Límite máximo
        )
        
        # Drawdown normalizado
        cumulative_returns = np.cumsum(returns)
        rolling_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = rolling_max - cumulative_returns
        max_drawdown = min(
            np.max(drawdowns) if len(drawdowns) > 0 else 0.0,
            1.0  # Límite máximo
        )
        
        # Actualizar métricas del agente
        agent.sharpe_ratio = sharpe
        agent.drawdown = max_drawdown
        agent.profit_factor = profit_factor
        agent.trades = len(returns[returns != 0])
        
        # Calcular fitness combinado y normalizado
        fitness = (
            (profit_factor / 10.0) * 0.4 +  # Normalizado a [0, 1]
            (1.0 - max_drawdown) * 0.3 +    # Ya está en [0, 1]
            (max(0, sharpe) / 5.0) * 0.3    # Normalizado a [0, 1]
        )
        
        return max(0, min(1, fitness))  # Asegurar que esté en [0, 1]
        
    except Exception as e:
        print(f"Error evaluando agente: {e}")
        return 0.0

def evaluate_existing_agent(agent_path: str):
    """Evaluar una estrategia existente"""
    try:
        if agent_path is None:
            console.print("[bold red]Error: Debe especificar la ruta del agente a evaluar[/bold red]")
            return False
            
        if not Path(agent_path).exists():
            console.print(f"[bold red]Error: No se encuentra el archivo {agent_path}[/bold red]")
            return False
            
        console.print(f"[yellow]Cargando agente desde: {agent_path}[/yellow]")
        agent = TradingAgent.load(agent_path)
        
        # Generar datos de prueba más extensos
        n_periods = 1000
        market_data = np.random.random((n_periods, 4))
        market_data = np.cumsum(market_data, axis=0) * 0.01
        
        # Evaluar agente
        fitness = evaluate_agent(agent)
        
        console.print(f"\n[bold green]Evaluación completada![/bold green]")
        create_performance_report(agent, 'results')
        
        return fitness
        
    except Exception as e:
        console.print(f"[bold red]Error evaluando agente: {e}[/bold red]")
        return False

def optimize_parameters(config: GeneticConfig, param_file: str = None):
    """Optimiza los parámetros del sistema"""
    console.print("[bold blue]Iniciando optimización de parámetros...[/bold blue]")
    
    # Cargar rangos de parámetros
    if param_file and Path(param_file).exists():
        with open(param_file) as f:
            param_ranges = json.load(f)
    else:
        # Rangos por defecto
        param_ranges = {
            "crossover_prob": (0.7, 1.0),
            "mutation_prob": (0.1, 0.4),
            "tournament_size": (2, 5),
            "elite_size": (1, 4),
            "indicator_mutation_rate": (0.1, 0.3),
            "weight_mutation_std": (0.05, 0.2)
        }
    
    # Crear y ejecutar optimizador
    optimizer = ParameterOptimizer(config)
    best_params = optimizer.optimize(param_ranges)
    
    # Guardar mejores parámetros
    output_file = "results/best_params.json"
    with open(output_file, "w") as f:
        json.dump(best_params, f, indent=4)
    
    console.print(f"[green]Parámetros optimizados guardados en: {output_file}[/green]")

def main():
    parser = argparse.ArgumentParser(description='Trading System RL-GA')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--mode', choices=['train', 'test', 'optimize', 'interactive'], default='interactive')
    parser.add_argument('--output', type=str, default='results/')
    parser.add_argument('--agent', type=str, help='Path to agent file for testing')
    parser.add_argument('--param', type=str, help='Parameters for optimization')
    
    args = parser.parse_args()
    config = load_config(args.config) if args.config else GeneticConfig()

    if args.mode == 'interactive':
        while True:
            choice = show_menu()
            if choice == '1':
                train_agents(config, args.output)
            elif choice == '2':
                # Mostrar lista de agentes disponibles
                agents_dir = Path('results')
                if not agents_dir.exists():
                    console.print("[bold red]No hay agentes guardados para evaluar[/bold red]")
                    continue
                    
                agents = list(agents_dir.glob('best_agent_*.pkl'))
                if not agents:
                    console.print("[bold red]No hay agentes guardados para evaluar[/bold red]")
                    continue
                
                table = Table(title="Agentes Disponibles")
                table.add_column("ID", style="cyan")
                table.add_column("Archivo", style="green")
                
                for i, agent_path in enumerate(agents, 1):
                    table.add_row(str(i), str(agent_path))
                
                console.print(table)
                
                agent_idx = console.input("\n[bold cyan]Seleccione el número del agente a evaluar (0 para cancelar): [/bold cyan]")
                if not agent_idx.isdigit() or int(agent_idx) == 0:
                    continue
                    
                agent_idx = int(agent_idx) - 1
                if 0 <= agent_idx < len(agents):
                    evaluate_existing_agent(str(agents[agent_idx]))
                else:
                    console.print("[bold red]Selección inválida[/bold red]")
            elif choice == '3':
                optimize_parameters(config, args.param)
            elif choice == '4':
                break
    else:
        if args.mode == 'train':
            train_agents(config, args.output)
        elif args.mode == 'test':
            test_agents(config, args.output)
        else:
            optimize_parameters(config, args.output)

def load_config(path: str) -> GeneticConfig:
    with open(path) as f:
        data = json.load(f)
    return GeneticConfig(**data['genetic_algorithm'])

if __name__ == '__main__':
    main()

