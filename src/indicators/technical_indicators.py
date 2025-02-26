import numpy as np
from typing import Tuple, Optional

class TechnicalIndicators:
    @staticmethod
    def EMA(data: np.ndarray, period: int = 14) -> np.ndarray:
        """Exponential Moving Average"""
        alpha = 2 / (period + 1)
        ema = np.zeros_like(data)
        ema[0] = data[0]
        for i in range(1, len(data)):
            ema[i] = alpha * data[i] + (1 - alpha) * ema[i-1]
        return ema

    @staticmethod
    def SMA(data: np.ndarray, period: int = 14) -> np.ndarray:
        """Simple Moving Average"""
        return np.convolve(data, np.ones(period)/period, mode='valid')

    @staticmethod
    def BBANDS(data: np.ndarray, period: int = 20, num_std: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Bollinger Bands"""
        sma = TechnicalIndicators.SMA(data, period)
        std = np.array([np.std(data[i-period:i]) for i in range(period, len(data))])
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)
        return upper, sma, lower

    @staticmethod
    def RSI(data: np.ndarray, period: int = 14) -> np.ndarray:
        """Relative Strength Index"""
        deltas = np.diff(data)
        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.convolve(gain, np.ones(period)/period, mode='valid')
        avg_loss = np.convolve(loss, np.ones(period)/period, mode='valid')
        
        rs = avg_gain / (avg_loss + 1e-10)  # Evitar división por cero
        rsi = 100 - (100 / (1 + rs))
        
        return np.pad(rsi, (period, 0), mode='edge')

    @staticmethod
    def MACD(data: np.ndarray, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Moving Average Convergence Divergence"""
        fast_ema = TechnicalIndicators.EMA(data, fast_period)
        slow_ema = TechnicalIndicators.EMA(data, slow_period)
        macd_line = fast_ema - slow_ema
        signal_line = TechnicalIndicators.EMA(macd_line, signal_period)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def ATR(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Average True Range"""
        tr = np.zeros_like(high)
        for i in range(1, len(tr)):
            h_l = high[i] - low[i]
            h_pc = abs(high[i] - close[i-1])
            l_pc = abs(low[i] - close[i-1])
            tr[i] = max(h_l, h_pc, l_pc)
        
        atr = np.zeros_like(tr)
        atr[period-1] = np.mean(tr[:period])
        for i in range(period, len(tr)):
            atr[i] = (atr[i-1] * (period-1) + tr[i]) / period
        return atr

    @staticmethod
    def ADX(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Average Directional Index"""
        # Calcular True Range
        tr = TechnicalIndicators.ATR(high, low, close, period)
        
        # Calcular +DM y -DM
        hdiff = np.diff(high)
        ldiff = np.diff(low)
        
        pdm = np.where((hdiff > 0) & (hdiff > -ldiff), hdiff, 0)
        ndm = np.where((ldiff < 0) & (-ldiff > hdiff), -ldiff, 0)
        
        # Calcular +DI y -DI
        pdi = 100 * TechnicalIndicators.EMA(pdm, period) / (tr[1:] + 1e-10)
        ndi = 100 * TechnicalIndicators.EMA(ndm, period) / (tr[1:] + 1e-10)
        
        # Calcular ADX
        dx = 100 * np.abs(pdi - ndi) / (pdi + ndi + 1e-10)
        adx = TechnicalIndicators.EMA(dx, period)
        
        return adx, pdi, ndi

    @staticmethod
    def Stochastic(high: np.ndarray, low: np.ndarray, close: np.ndarray, k_period: int = 14, d_period: int = 3) -> Tuple[np.ndarray, np.ndarray]:
        """Stochastic Oscillator"""
        n = len(close)
        k = np.zeros(n)
        
        for i in range(k_period-1, n):
            c = close[i]
            h = np.max(high[i-k_period+1:i+1])
            l = np.min(low[i-k_period+1:i+1])
            k[i] = 100 * (c - l) / (h - l + 1e-10)
        
        d = TechnicalIndicators.SMA(k, d_period)
        return k, d

    # Continuar con más implementaciones según necesidad...
