import numpy as np
import pandas as pd
from typing import List, Dict
from .backtest import TradeResult

class TradingMetrics:
    @staticmethod
    def calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.0) -> float:
        """Calcula el Sharpe Ratio anualizado"""
        excess_returns = returns - risk_free_rate
        if len(excess_returns) < 2:
            return 0.0
        return np.sqrt(252) * np.mean(excess_returns) / (np.std(excess_returns) + 1e-10)
    
    @staticmethod
    def calculate_sortino_ratio(returns: np.ndarray, risk_free_rate: float = 0.0) -> float:
        """Calcula el Sortino Ratio anualizado"""
        excess_returns = returns - risk_free_rate
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) < 1:
            return 0.0
        return np.sqrt(252) * np.mean(excess_returns) / (np.std(downside_returns) + 1e-10)
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: np.ndarray) -> float:
        """Calcula el máximo drawdown"""
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (peak - equity_curve) / peak
        return np.max(drawdown)
    
    @staticmethod
    def analyze_trades(trades: List[TradeResult]) -> Dict:
        """Análisis detallado de trades"""
        if not trades:
            return {}
        
        df = pd.DataFrame([vars(trade) for trade in trades])
        
        return {
            "total_trades": len(trades),
            "profitable_trades": len(df[df.pnl > 0]),
            "loss_trades": len(df[df.pnl < 0]),
            "win_rate": len(df[df.pnl > 0]) / len(trades),
            "avg_profit": df[df.pnl > 0].pnl.mean() if len(df[df.pnl > 0]) > 0 else 0,
            "avg_loss": df[df.pnl < 0].pnl.mean() if len(df[df.pnl < 0]) > 0 else 0,
            "largest_win": df.pnl.max(),
            "largest_loss": df.pnl.min(),
            "avg_trade_duration": df.trade_duration.mean(),
            "profit_factor": abs(df[df.pnl > 0].pnl.sum() / df[df.pnl < 0].pnl.sum()) if len(df[df.pnl < 0]) > 0 else float('inf')
        }
