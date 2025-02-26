from typing import Dict, Any, List
import numpy as np

"""Indicadores técnicos disponibles para el sistema de trading"""

AVAILABLE_INDICATORS = [
    "RSI",
    "SMA",
    "EMA",
    "MACD",
    "BB",  # Bollinger Bands
    "ATR",
    "ADX",
    "CCI",
    "MOM",  # Momentum
    "ROC",  # Rate of Change
    "WMA",  # Weighted Moving Average
    "STOCH"  # Stochastic
]

# Constantes para parámetros de indicadores
INDICATOR_PARAMS = {
    "RSI": {"period": 14},
    "SMA": {"period": 20},
    "EMA": {"period": 12},
    "MACD": {"fast": 12, "slow": 26, "signal": 9},
    "BB": {"period": 20, "std": 2},
    "ATR": {"period": 14},
    "ADX": {"period": 14},
    "CCI": {"period": 20}
}

class TechnicalIndicators:
    @staticmethod
    def calculate_indicator(name: str, data: np.ndarray, params: Dict[str, Any] = None) -> np.ndarray:
        if params is None:
            params = {}
            
        if name == "RSI":
            return TechnicalIndicators._calculate_rsi(data, params.get('period', 14))
        # Implementar otros indicadores según necesidad
        return np.zeros_like(data)

    @staticmethod
    def _calculate_rsi(data: np.ndarray, period: int) -> np.ndarray:
        # Implementación básica de RSI
        delta = np.diff(data)
        gain = (delta > 0) * delta
        loss = (delta < 0) * -delta
        
        avg_gain = np.mean(gain[:period])
        avg_loss = np.mean(loss[:period])
        
        if avg_loss == 0:
            return 100 * np.ones_like(data)
            
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
