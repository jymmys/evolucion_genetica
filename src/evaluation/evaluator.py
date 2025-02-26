from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from rich.console import Console
from rich.table import Table
from ..genetic.agent import TradingAgent
from .backtest import BacktestEngine

console = Console()

class StrategyEvaluator:
    def __init__(self, data_train: pd.DataFrame, data_test: pd.DataFrame):
        self.data_train = data_train
        self.data_test = data_test
        self.backtest_engine = BacktestEngine()
        
    def evaluate_population(self, agents: List[TradingAgent]) -> List[float]:
        """Evalúa una población completa de agentes"""
        fitness_scores = []
        
        for agent in agents:
            # Evaluación en conjunto de entrenamiento
            train_results = self.backtest_engine.run_backtest(agent, self.data_train)
            
            # Evaluación en conjunto de prueba
            test_results = self.backtest_engine.run_backtest(agent, self.data_test)
            
            # Calcular fitness combinado
            fitness = self._calculate_combined_fitness(train_results, test_results)
            fitness_scores.append(fitness)
            
            # Actualizar métricas del agente
            self._update_agent_metrics(agent, train_results, test_results)
        
        return fitness_scores
    
    def _calculate_combined_fitness(self, train_results: Dict, test_results: Dict) -> float:
        """Calcula el fitness combinando resultados de train y test"""
        # Pesos para diferentes métricas
        weights = {
            'profit_factor': 0.3,
            'sharpe_ratio': 0.2,
            'win_rate': 0.15,
            'max_drawdown': 0.15,
            'expectancy': 0.2
        }
        
        # Calcular fitness para cada conjunto
        train_fitness = self._calculate_weighted_fitness(train_results, weights)
        test_fitness = self._calculate_weighted_fitness(test_results, weights)
        
        # Penalizar diferencias grandes entre train y test (evitar overfitting)
        consistency_penalty = abs(train_fitness - test_fitness) * 0.5
        
        return min(train_fitness, test_fitness) - consistency_penalty
    
    def _calculate_weighted_fitness(self, results: Dict, weights: Dict) -> float:
        """Calcula el fitness ponderado basado en múltiples métricas"""
        fitness_components = {
            'profit_factor': min(results['profit_factor'] / 3.0, 1.0),
            'sharpe_ratio': min(max(results['sharpe_ratio'] / 2.0, 0), 1.0),
            'win_rate': results['win_rate'],
            'max_drawdown': 1.0 - min(results['max_drawdown'] / 0.2, 1.0),
            'expectancy': min(results['expectancy'] / 0.02, 1.0)
        }
        
        return sum(weights[k] * v for k, v in fitness_components.items())
    
    def _update_agent_metrics(self, agent: TradingAgent, train_results: Dict, test_results: Dict):
        """Actualiza las métricas del agente"""
        agent.train_metrics = train_results
        agent.test_metrics = test_results
        agent.fitness = self._calculate_combined_fitness(train_results, test_results)
    
    def generate_report(self, agent: TradingAgent) -> str:
        """Genera un reporte detallado del rendimiento del agente"""
        table = Table(title=f"Reporte de Rendimiento - Agente {id(agent)}")
        
        table.add_column("Métrica", style="cyan")
        table.add_column("Entrenamiento", justify="right", style="green")
        table.add_column("Prueba", justify="right", style="yellow")
        
        metrics_to_show = [
            ('Retorno Total', 'total_return', '{:.2%}'),
            ('Profit Factor', 'profit_factor', '{:.2f}'),
            ('Ratio Sharpe', 'sharpe_ratio', '{:.2f}'),
            ('Drawdown Máx.', 'max_drawdown', '{:.2%}'),
            ('Win Rate', 'win_rate', '{:.2%}'),
            ('Expectancy', 'expectancy', '{:.4f}'),
            ('Trades Totales', 'total_trades', '{:.0f}')
        ]
        
        for label, metric, fmt in metrics_to_show:
            train_val = fmt.format(agent.train_metrics[metric])
            test_val = fmt.format(agent.test_metrics[metric])
            table.add_row(label, train_val, test_val)
        
        return table
