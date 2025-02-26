from typing import Dict, Any, List, Tuple
import numpy as np
import random
from rich.console import Console
from rich.table import Table
from rich.progress import track
from ..config.config import GeneticConfig
from ..genetic.agent import TradingAgent
from ..indicators.ninjatrader import NinjaIndicators

console = Console()

class ParameterOptimizer:
    def __init__(self, base_config: GeneticConfig):
        self.base_config = base_config
        self.best_params = {}
        self.best_fitness = 0.0
        self.param_ranges = {}
        
    def optimize(self, param_ranges: Dict[str, List[float]], n_trials: int = 50) -> Dict[str, Any]:
        """Optimiza los parámetros usando búsqueda aleatoria"""
        self.param_ranges = param_ranges
        results = []
        
        for trial in track(range(n_trials), description="Optimizando parámetros..."):
            # Generar parámetros aleatorios
            params = self._generate_random_params(param_ranges)
            
            # Crear config con nuevos parámetros
            trial_config = self._create_trial_config(params)
            
            # Evaluar configuración
            fitness = self._evaluate_config(trial_config)
            
            results.append((params, fitness))
            console.print(f"[cyan]Trial {trial + 1}/{n_trials}:[/cyan] Fitness = [green]{fitness:.4f}[/green]")
        
        # Encontrar mejores parámetros
        best_result = max(results, key=lambda x: x[1])
        self.best_params = best_result[0]
        self.best_fitness = best_result[1]
        
        self._display_optimization_results(results)
        return self.best_params

    def _generate_random_params(self, param_ranges: Dict[str, List[float]]) -> Dict[str, Any]:
        params = {}
        for param_name, range_vals in param_ranges.items():
            min_val, max_val = range_vals
            if isinstance(min_val, int) and isinstance(max_val, int):
                params[param_name] = random.randint(min_val, max_val)
            else:
                params[param_name] = min_val + random.random() * (max_val - min_val)
        return params

    def _create_trial_config(self, params: Dict[str, Any]) -> GeneticConfig:
        config_dict = self.base_config.__dict__.copy()
        config_dict.update(params)
        return GeneticConfig(**config_dict)

    def _evaluate_config(self, config: GeneticConfig) -> float:
        try:
            # Generar datos de prueba
            n_periods = 100
            market_data = np.random.random((n_periods, 4))
            market_data = np.cumsum(market_data, axis=0) * 0.01

            # Crear y evaluar agente
            agent = TradingAgent(NinjaIndicators.AVAILABLE_INDICATORS)
            signals = np.array([agent.get_signal(market_data[:i+1]) 
                              for i in range(len(market_data)-1)])
            signals = np.clip(signals, -1, 1)
            
            # Calcular retornos
            price_changes = np.diff(market_data[:, 3])
            returns = price_changes * signals
            
            if len(returns) == 0:
                return 0.0
                
            # Calcular métricas
            sharpe = np.mean(returns) / (np.std(returns) + 1e-6)
            profit_factor = (np.sum(returns[returns > 0]) / 
                           abs(np.sum(returns[returns < 0]) + 1e-6))
            
            # Calcular fitness
            fitness = (
                min(profit_factor / 2.0, 1.0) * 0.4 +
                min(max(sharpe / 2.0, 0.0), 1.0) * 0.6
            )
            
            return max(0.0, min(1.0, fitness))
            
        except Exception as e:
            console.print(f"[red]Error en evaluación: {e}[/red]")
            return 0.0

    def _display_optimization_results(self, results: List[Tuple[Dict[str, Any], float]]):
        table = Table(title="[bold]Resultados de Optimización[/bold]")
        table.add_column("Parámetro", style="cyan")
        table.add_column("Mejor Valor", style="green", justify="right")
        table.add_column("Rango", style="yellow", justify="right")
        
        for param, value in self.best_params.items():
            min_val, max_val = self.param_ranges[param]
            table.add_row(
                param,
                f"{value:.4f}" if isinstance(value, float) else str(value),
                f"{min_val:.2f} - {max_val:.2f}"
            )
        
        table.add_row("Mejor Fitness", f"{self.best_fitness:.4f}", "")
        console.print(table)

def evaluate_agent(agent: TradingAgent, market_data: np.ndarray) -> float:
    """Evalúa un agente usando los datos de mercado proporcionados"""        
    try:
        signals = np.array([agent.get_signal(market_data[:i+1]) 
                          for i in range(len(market_data)-1)])
        signals = np.clip(signals, -1, 1)
        
        # Calcular retornos
        price_changes = np.diff(market_data[:, 3])
        returns = price_changes * signals
        
        if len(returns) == 0:
            return 0.0
            
        # Calcular métricas
        sharpe = np.mean(returns) / (np.std(returns) + 1e-6)
        profit_factor = (np.sum(returns[returns > 0]) / 
                       abs(np.sum(returns[returns < 0]) + 1e-6))
        
        # Calcular fitness
        fitness = (
            min(profit_factor / 2.0, 1.0) * 0.4 +
            min(max(sharpe / 2.0, 0.0), 1.0) * 0.6
        )
        
        return max(0.0, min(1.0, fitness))
        
    except Exception as e:
        console.print(f"[red]Error en evaluate_agent: {e}[/red]")
        return 0.0

