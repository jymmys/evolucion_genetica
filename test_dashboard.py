import sys
from pathlib import Path
import pandas as pd
import time
from rich.console import Console
from rich.prompt import Confirm
from src.utils.logger import logger

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.visualization.dashboard import TradingDashboard
from src.genetic.agent import TradingAgent
from src.evaluation.backtest import BacktestEngine
from src.genetic.evolution import EvolutionEngine
from src.evaluation.evaluator import StrategyEvaluator
from src.config.config import GeneticConfig

console = Console()

class TrainingConfig:
    def __init__(self):
        self.generations = 100          # Aumentado de 20 a 100
        self.population_size = 50       # Aumentado el tamaño de población
        self.training_iterations = 5    # Número de ciclos completos de entrenamiento
        self.evaluation_period = 10     # Cada cuántas generaciones evaluar
        self.min_fitness_target = 0.8   # Objetivo de fitness mínimo

def run_dashboard():
    logger.info("Iniciando sistema de trading")
    try:
        # Configuración inicial
        console.print("[bold blue]Sistema de Trading - Dashboard Interactivo[/bold blue]")
        
        # Cargar datos históricos
        console.print("\n[yellow]Cargando datos históricos...[/yellow]")
        data = pd.read_csv('data/historical_data.csv')
        train_size = int(len(data) * 0.8)
        train_data = data[:train_size]
        test_data = data[train_size:]
        
        # Inicializar componentes
        dashboard = TradingDashboard()
        dashboard.create_layout()
        config = GeneticConfig()
        backtest_engine = BacktestEngine()
        
        # Mostrar instrucciones
        console.print("\n[bold cyan]Controles disponibles:[/bold cyan]")
        console.print("p - Pausar/Reanudar el Dashboard")
        console.print("s - Guardar estado actual")
        console.print("q - Cerrar Dashboard (continúa el programa)")
        time.sleep(3)
        
        # Mostrar opciones
        console.print("\n[green]Seleccione una operación:[/green]")
        console.print("1. Entrenar nuevos agentes")
        console.print("2. Ejecutar backtesting de agente existente")
        choice = input("\nOpción (1/2): ")
        
        logger.info(f"Modo seleccionado: {choice}")
        
        dash_generator = dashboard.show()
        next(dash_generator)
        
        if choice == "1":
            try:
                # Modo entrenamiento con configuración mejorada
                logger.info("Iniciando modo entrenamiento")
                training_config = TrainingConfig()
                evaluator = StrategyEvaluator(train_data, test_data)
                evolution = EvolutionEngine(config, evaluator)
                
                best_overall_agent = None
                best_overall_fitness = 0
                
                while dashboard.is_running:
                    if not dashboard.paused:
                        for training_cycle in range(training_config.training_iterations):
                            logger.info(f"Iniciando ciclo de entrenamiento {training_cycle + 1}")
                            
                            for gen in range(training_config.generations):
                                try:
                                    # Evolucionar población
                                    best_agent, population_metrics = evolution.evolve_one_generation()
                                    
                                    # Ejecutar backtest del mejor agente
                                    backtest_results = backtest_engine.run_backtest(best_agent, test_data)
                                    
                                    # Actualizar mejor agente global
                                    if best_agent.fitness > best_overall_fitness:
                                        logger.info(f"Nuevo mejor agente encontrado: Fitness = {best_agent.fitness:.4f}")
                                        best_overall_fitness = best_agent.fitness
                                        best_overall_agent = best_agent
                                        # Guardar mejor agente
                                        best_agent.save(f"results/best_agent_gen_{gen}_cycle_{training_cycle}.pkl")
                                    
                                    # Actualizar dashboard con métricas reales
                                    dashboard.update_metrics(
                                        generation=gen+1,
                                        best_fitness=best_overall_fitness,  # Mostrar el mejor global
                                        avg_fitness=population_metrics['avg_fitness'],
                                        best_agent_metrics={
                                            **backtest_results,
                                            'agent_id': best_agent.id,
                                            'num_indicators': len(best_agent.indicators),
                                            'training_cycle': training_cycle + 1,
                                            'total_generations': training_cycle * training_config.generations + gen + 1
                                        }
                                    )
                                    
                                    # Actualizar gráficos y estado
                                    dashboard.update_charts(
                                        fitness_history=evolution.best_fitness_history,
                                        trade_history=backtest_results['trades']
                                    )
                                    
                                    status_message = (
                                        f"Ciclo {training_cycle + 1}/{training_config.training_iterations} - "
                                        f"Generación {gen + 1}/{training_config.generations}\n"
                                        f"Mejor Fitness Global: {best_overall_fitness:.4f}"
                                    )
                                    
                                    dashboard.update_status(status_message, style="green")
                                    
                                    # Verificar si alcanzamos el objetivo de fitness
                                    if best_overall_fitness >= training_config.min_fitness_target:
                                        dashboard.update_status(
                                            f"¡Objetivo de fitness alcanzado! ({best_overall_fitness:.4f})",
                                            style="bold green"
                                        )
                                        time.sleep(2)
                                        break
                                    
                                    time.sleep(0.3)  # Reducido para más velocidad
                                    
                                except Exception as e:
                                    logger.error(f"Error en generación {gen}: {str(e)}", exc_info=True)
                                    dashboard.update_status(f"Error en generación: {str(e)}", style="red")
                                    time.sleep(2)
                                    continue
                                    
                    time.sleep(0.1)

            except Exception as e:
                logger.error("Error en modo entrenamiento", exc_info=True)
                raise
                
            # Continuar con el programa después de cerrar el dashboard
            console.print("\n[green]Dashboard cerrado. ¿Desea continuar con el entrenamiento? (s/n)[/green]")
            if input().lower() == 's':
                # Continuar entrenamiento sin dashboard
                pass
                
        elif choice == "2":
            # Modo backtesting
            logger.info("Iniciando modo backtesting")
            try:
                agent_path = input("\nRuta del agente a evaluar (results/best_agent_*.pkl): ")
                agent = TradingAgent.load(agent_path)
                
                console.print(f"\n[yellow]Ejecutando backtest para {agent_path}...[/yellow]")
                results = backtest_engine.run_backtest(agent, test_data)
                
                # Mostrar resultados en el dashboard
                dashboard.update_metrics(
                    generation=1,
                    best_fitness=agent.fitness,
                    avg_fitness=agent.fitness,
                    best_agent_metrics=results
                )
                
                dashboard.update_charts(
                    fitness_history=[agent.fitness],
                    trade_history=results['trades']
                )
                
                dashboard.update_status(
                    f"Backtest completado - Profit Factor: {results['profit_factor']:.2f}",
                    style="green"
                )
                
                time.sleep(5)  # Mantener resultados visibles
                
            except Exception as e:
                logger.error("Error en modo backtesting", exc_info=True)
                raise
                
    except KeyboardInterrupt:
        logger.info("Operación interrumpida por el usuario")
        console.print("\n[yellow]Operación interrumpida por el usuario[/yellow]")
        
    except Exception as e:
        logger.critical(f"Error crítico en el sistema: {str(e)}", exc_info=True)
        console.print(f"\n[red]Error crítico: {str(e)}[/red]")
        
    finally:
        logger.info("Finalizando sistema de trading")
        time.sleep(1)

if __name__ == "__main__":
    run_dashboard()
