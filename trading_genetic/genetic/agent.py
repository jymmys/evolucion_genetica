import numpy as np
from typing import List
import random
import pickle
from trading_genetic.config.config import GeneticConfig  # Importación absoluta

class TradingAgent:
    def __init__(self, indicators: List[str]):
        self.indicators = random.sample(indicators, random.randint(4, 8))
        self.weights = np.random.normal(0, 1, len(self.indicators))
        self.fitness = 0.0
        self.sharpe_ratio = 0.0
        self.drawdown = 0.0
        self.profit_factor = 0.0
        self.trades = 0

    def mutate(self, prob: float):
        if random.random() < prob:
            idx = random.randint(0, len(self.weights) - 1)
            self.weights[idx] += np.random.normal(0, 0.1)

    def crossover(self, other: 'TradingAgent', prob: float) -> tuple['TradingAgent', 'TradingAgent']:
        if random.random() < prob:
            point = random.randint(1, len(self.weights) - 1)
            weights1 = np.concatenate([self.weights[:point], other.weights[point:]])
            weights2 = np.concatenate([other.weights[:point], self.weights[point:]])
            child1, child2 = TradingAgent(self.indicators), TradingAgent(self.indicators)
            child1.weights, child2.weights = weights1, weights2
            return child1, child2
        return self, other

    def save(self, filepath: str):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, filepath: str):
        with open(filepath, 'rb') as f:
            return pickle.load(f)

    def get_ensemble_weight(self, all_agents: List['TradingAgent']) -> float:
        total_sharpe = sum(agent.sharpe_ratio for agent in all_agents)
        return self.sharpe_ratio / total_sharpe if total_sharpe > 0 else 0

    def get_signal(self, market_data) -> float:
        return sum(w * self._calculate_indicator(ind, market_data) for w, ind in zip(self.weights, self.indicators))

    def _calculate_indicator(self, indicator: str, data) -> float:
        pass