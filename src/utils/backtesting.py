import numpy as np
from typing import Dict, List
from src.genetic.agent import TradingAgent

class Backtester:
    def __init__(self, data: np.ndarray, split_date: str = "2020-01-01"):
        self.data = data
        self.split_date = split_date
        self.train_data, self.test_data = self._split_data()
        
    def _split_data(self) -> tuple[np.ndarray, np.ndarray]:
        # Implementar división de datos
        split_idx = int(len(self.data) * 0.8)  # 80% training, 20% testing
        return self.data[:split_idx], self.data[split_idx:]
        
    def evaluate_agent(self, agent: TradingAgent, data: np.ndarray) -> Dict[str, float]:
        signals = agent.get_signal(data)
        returns = np.diff(data) * signals[:-1]
        
        # Calcular métricas
        profit_factor = np.sum(returns > 0) / abs(np.sum(returns < 0)) if np.sum(returns < 0) != 0 else np.inf
        sharpe = np.mean(returns) / np.std(returns) if np.std(returns) != 0 else 0
        max_dd = self._calculate_max_drawdown(np.cumsum(returns))
        
        return {
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "trades": len(returns)
        }
        
    def _calculate_max_drawdown(self, equity_curve: np.ndarray) -> float:
        rolling_max = np.maximum.accumulate(equity_curve)
        drawdowns = (rolling_max - equity_curve) / rolling_max
        return np.max(drawdowns)
