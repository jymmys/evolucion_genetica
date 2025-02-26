from typing import Dict, Any
import numpy as np
from .technical_indicators import TechnicalIndicators

class NinjaIndicators:
    AVAILABLE_INDICATORS = [
        # Tendencia
        "ADX", "ADXR", "EMA", "MACD", "SMA", "TEMA", "WMA",
        # Momentum
        "RSI", "CCI", "Stochastic", "StochRSI", "WilliamsR",
        # Volatilidad
        "ATR", "BBANDS", "KeltnerChannel",
        # Volumen
        "OBV", "VWMA", "VolumeOscillator"
    ]
    
    @staticmethod
    def calculate_indicator(name: str, data: np.ndarray, params: Dict[str, Any] = None) -> np.ndarray:
        if params is None:
            params = {}
            
        close = data[:, 3] if data.ndim > 1 else data
        high = data[:, 1] if data.ndim > 1 else data
        low = data[:, 2] if data.ndim > 1 else data
        volume = data[:, 4] if data.ndim > 1 and data.shape[1] > 4 else None
        
        try:
            if name == "ADX":
                adx, _, _ = TechnicalIndicators.ADX(high, low, close, params.get('period', 14))
                return adx
            elif name == "BBANDS":
                _, middle, _ = TechnicalIndicators.BBANDS(close, params.get('period', 20))
                return middle
            elif name == "RSI":
                return TechnicalIndicators.RSI(close, params.get('period', 14))
            elif name == "MACD":
                macd, _, _ = TechnicalIndicators.MACD(close)
                return macd
            elif name == "EMA":
                return TechnicalIndicators.EMA(close, params.get('period', 14))
            elif name == "SMA":
                return TechnicalIndicators.SMA(close, params.get('period', 14))
            elif name == "ATR":
                return TechnicalIndicators.ATR(high, low, close, params.get('period', 14))
            elif name == "Stochastic":
                k, _ = TechnicalIndicators.Stochastic(high, low, close)
                return k
            # ... Agregar más indicadores según se necesite
                
            return np.zeros_like(close)
            
        except Exception as e:
            print(f"Error calculando {name}: {e}")
            return np.zeros_like(close)
