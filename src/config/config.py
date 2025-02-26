from dataclasses import dataclass
from typing import List

@dataclass
class GeneticConfig:
    generations: int = 10
    population_size: int = 5
    crossover_prob: float = 0.9
    mutation_prob: float = 0.25
    islands: int = 3
    migration_frequency: int = 60
    migration_rate: float = 0.15
    decimation_coef: int = 1
    fresh_blood_rate: float = 0.15
    fresh_blood_frequency: int = 3
    restart_threshold: int = 20
    min_indicators: int = 4
    max_indicators: int = 8
    bank_size: int = 1000
    evaluation_periods: int = 1000
    validation_size: float = 0.2
    indicator_mutation_rate: float = 0.2
    weight_mutation_std: float = 0.1
    tournament_size: int = 3
    elite_size: int = 2

@dataclass
class FitnessCriteria:
    min_profit_factor: float = 1.0
    min_trades: int = 100
    max_drawdown: float = 0.10
    min_sharpe: float = 0.98
