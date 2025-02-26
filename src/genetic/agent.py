import numpy as np
from typing import List
import random
import pickle
import sys
from pathlib import Path

# Agregar el directorio raíz al path de Python
current_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(current_dir))

from src.config.config import GeneticConfig
from src.indicators.technical import AVAILABLE_INDICATORS  # Agregar esta importación
from src.indicators.available_indicators import get_random_indicators, NINJATRADER_INDICATORS

class TradingAgent:
    def __init__(self, indicators: List[str] = None):
        # Si no se proporcionan indicadores, generar aleatorios
        self.indicators = (indicators if indicators is not None 
                         else get_random_indicators())
        self.weights = np.random.normal(0, 0.1, len(self.indicators))
        self.fitness = 0.0
        self.sharpe_ratio = 0.0
        self.drawdown = 0.0
        self.profit_factor = 0.0
        self.trades = 0
    
    def mutate(self, prob: float):
        """Mutación mejorada que puede cambiar indicadores"""
        # Mutar pesos
        for i in range(len(self.weights)):
            if random.random() < prob:
                mutation_type = random.random()
                if mutation_type < 0.7:
                    self.weights[i] += np.random.normal(0, 0.05)
                elif mutation_type < 0.9:
                    self.weights[i] += np.random.normal(0, 0.1)
                else:
                    self.weights[i] = np.random.normal(0, 0.1)
        
        # Ocasionalmente cambiar completamente los indicadores
        if random.random() < prob * 0.1:  # 10% de probabilidad de cambio total
            self.indicators = get_random_indicators()
            self.weights = np.random.normal(0, 0.1, len(self.indicators))
        # Ocasionalmente reemplazar un indicador
        elif random.random() < prob * 0.2:  # 20% de probabilidad de reemplazo
            idx = random.randint(0, len(self.indicators) - 1)
            new_indicator = random.choice(NINJATRADER_INDICATORS)
            if new_indicator not in self.indicators:
                self.indicators[idx] = new_indicator
        
        # Normalizar pesos
        norm = np.linalg.norm(self.weights)
        if norm > 0:
            self.weights = self.weights / norm
    
    def crossover(self, other: 'TradingAgent', prob: float) -> tuple['TradingAgent', 'TradingAgent']:
        """Crossover mejorado con manejo seguro de indicadores"""
        if random.random() < prob:
            # Crear nuevos agentes con los indicadores originales
            child1 = TradingAgent(AVAILABLE_INDICATORS)
            child2 = TradingAgent(AVAILABLE_INDICATORS)
            
            # Mezclar indicadores de manera segura
            all_indicators = list(set(self.indicators) | set(other.indicators))
            num_indicators = random.randint(
                min(4, len(all_indicators)),
                min(8, len(all_indicators))
            )
            
            # Asignar indicadores a los hijos
            if len(all_indicators) >= num_indicators:
                child1.indicators = random.sample(all_indicators, num_indicators)
                child2.indicators = random.sample(all_indicators, num_indicators)
                
                # Ajustar tamaño de pesos
                child1.weights = np.random.normal(0, 1, len(child1.indicators))
                child2.weights = np.random.normal(0, 1, len(child2.indicators))
                
                # Heredar pesos cuando sea posible
                for i, ind in enumerate(child1.indicators):
                    if ind in self.indicators:
                        idx = self.indicators.index(ind)
                        child1.weights[i] = self.weights[idx]
                    elif ind in other.indicators:
                        idx = other.indicators.index(ind)
                        child1.weights[i] = other.weights[idx]
                
                for i, ind in enumerate(child2.indicators):
                    if ind in other.indicators:
                        idx = other.indicators.index(ind)
                        child2.weights[i] = other.weights[idx]
                    elif ind in self.indicators:
                        idx = self.indicators.index(ind)
                        child2.weights[i] = self.weights[idx]
                
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
        return sum(w * self._calculate_indicator(ind, market_data) 
                  for w, ind in zip(self.weights, self.indicators))

    def _calculate_indicator(self, indicator: str, data: np.ndarray) -> float:
        """Implementación básica del cálculo de indicadores"""
        try:
            # Asegurarse de que estamos trabajando con el precio de cierre
            prices = data[:, 3] if data.ndim > 1 else data
            
            if len(prices) < 2:
                return 0.0
                
            if indicator == "RSI":
                # Calcular RSI usando los últimos 14 períodos
                period = 14
                if len(prices) < period:
                    return 50.0
                    
                deltas = np.diff(prices[-period-1:])
                gain = np.mean(deltas[deltas > 0]) if any(deltas > 0) else 0
                loss = abs(np.mean(deltas[deltas < 0])) if any(deltas < 0) else 0
                
                if loss == 0:
                    return 100.0
                rs = gain / loss
                return 100.0 - (100.0 / (1.0 + rs))
                
            elif indicator == "SMA":
                # Media móvil simple de 20 períodos
                return np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)
                
            elif indicator == "EMA":
                # Media móvil exponencial de 12 períodos
                period = min(12, len(prices))
                weights = np.exp(np.linspace(-1., 0., period))
                weights /= weights.sum()
                return np.sum(prices[-period:] * weights)
                
            else:
                # Valor por defecto: retorna el último precio normalizado
                return (prices[-1] - np.mean(prices)) / np.std(prices) if len(prices) > 1 else 0.0
                
        except Exception as e:
            print(f"Error calculando indicador {indicator}: {e}")
            return 0.0
