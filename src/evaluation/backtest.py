import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.progress import track
from src.genetic.agent import TradingAgent

console = Console()

@dataclass
class TradeResult:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float
    exit_price: float
    position_size: float
    pnl: float
    return_pct: float
    drawdown: float
    trade_duration: int
    max_adverse_excursion: float  # Máxima excursión adversa
    max_favorable_excursion: float  # Máxima excursión favorable
    entry_reason: str
    exit_reason: str

class BacktestEngine:
    def __init__(self, 
                 initial_capital: float = 100000.0, 
                 risk_per_trade: float = 0.02,
                 max_position_size: float = 0.1,
                 stop_loss_pct: float = 0.02,
                 take_profit_pct: float = 0.04):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.trades: List[TradeResult] = []
        self.equity_curve = []
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0
        
    def run_backtest(self, agent: TradingAgent, market_data: pd.DataFrame) -> Dict:
        """
        Ejecuta el backtesting con gestión de riesgo y métricas detalladas
        """
        self.equity_curve = [self.initial_capital]
        open_position = False
        position_size = 0
        entry_price = 0
        entry_time = None
        stop_loss = 0
        take_profit = 0
        max_adverse_excursion = 0
        max_favorable_excursion = 0
        
        for i in range(len(market_data)):
            current_bar = market_data.iloc[i]
            historical_data = market_data.iloc[:i+1].values
            
            # Obtener señal del agente
            signal = agent.get_signal(historical_data)
            
            if not open_position and abs(signal) > 0.5:
                # Entrada
                entry_price = current_bar['Close']
                entry_time = current_bar.name
                
                # Calcular tamaño de posición basado en riesgo
                risk_amount = self.current_capital * self.risk_per_trade
                max_size = self.current_capital * self.max_position_size
                position_size = min(risk_amount / self.stop_loss_pct, max_size)
                
                # Establecer stop loss y take profit
                stop_loss = entry_price * (1 - self.stop_loss_pct * np.sign(signal))
                take_profit = entry_price * (1 + self.take_profit_pct * np.sign(signal))
                
                open_position = True
                max_adverse_excursion = 0
                max_favorable_excursion = 0
                
            elif open_position:
                # Actualizar MAE y MFE
                price_movement = (current_bar['Close'] - entry_price) * np.sign(position_size)
                max_adverse_excursion = min(max_adverse_excursion, price_movement)
                max_favorable_excursion = max(max_favorable_excursion, price_movement)
                
                # Verificar condiciones de salida
                exit_price = None
                exit_reason = ""
                
                if (position_size > 0 and current_bar['Low'] <= stop_loss) or \
                   (position_size < 0 and current_bar['High'] >= stop_loss):
                    exit_price = stop_loss
                    exit_reason = "Stop Loss"
                elif (position_size > 0 and current_bar['High'] >= take_profit) or \
                     (position_size < 0 and current_bar['Low'] <= take_profit):
                    exit_price = take_profit
                    exit_reason = "Take Profit"
                elif abs(signal) < 0.2:
                    exit_price = current_bar['Close']
                    exit_reason = "Signal Exit"
                
                if exit_price is not None:
                    # Cerrar posición
                    pnl = (exit_price - entry_price) * position_size
                    return_pct = pnl / self.current_capital
                    
                    # Actualizar capital
                    self.current_capital += pnl
                    self.equity_curve.append(self.current_capital)
                    
                    # Actualizar drawdown
                    self._update_drawdown()
                    
                    # Registrar trade
                    self.trades.append(
                        TradeResult(
                            entry_time=entry_time,
                            exit_time=current_bar.name,
                            entry_price=entry_price,
                            exit_price=exit_price,
                            position_size=position_size,
                            pnl=pnl,
                            return_pct=return_pct,
                            drawdown=self.current_drawdown,
                            trade_duration=(current_bar.name - entry_time).days,
                            max_adverse_excursion=max_adverse_excursion,
                            max_favorable_excursion=max_favorable_excursion,
                            entry_reason="Signal Entry",
                            exit_reason=exit_reason
                        )
                    )
                    
                    open_position = False
        
        return self._calculate_metrics()
    
    def _update_drawdown(self):
        """Actualiza el drawdown actual y máximo"""
        peak = max(self.equity_curve)
        self.current_drawdown = (peak - self.current_capital) / peak
        self.max_drawdown = max(self.max_drawdown, self.current_drawdown)
    
    def _calculate_metrics(self) -> Dict:
        """Calcula métricas detalladas del backtest"""
        if not self.trades:
            return self._empty_metrics()
        
        returns = pd.Series([trade.return_pct for trade in self.trades])
        winning_trades = [trade for trade in self.trades if trade.pnl > 0]
        losing_trades = [trade for trade in self.trades if trade.pnl < 0]
        
        total_profit = sum(trade.pnl for trade in winning_trades)
        total_loss = abs(sum(trade.pnl for trade in losing_trades))
        
        metrics = {
            "total_return": (self.current_capital - self.initial_capital) / self.initial_capital,
            "sharpe_ratio": self._calculate_sharpe_ratio(returns),
            "sortino_ratio": self._calculate_sortino_ratio(returns),
            "max_drawdown": self.max_drawdown,
            "win_rate": len(winning_trades) / len(self.trades),
            "profit_factor": total_profit / (total_loss + 1e-10),
            "total_trades": len(self.trades),
            "avg_trade_duration": np.mean([trade.trade_duration for trade in self.trades]),
            "avg_mae": np.mean([trade.max_adverse_excursion for trade in self.trades]),
            "avg_mfe": np.mean([trade.max_favorable_excursion for trade in self.trades]),
            "expectancy": (total_profit / len(winning_trades) * len(winning_trades) / len(self.trades)) - \
                        (total_loss / len(losing_trades) * len(losing_trades) / len(self.trades))
        }
        
        return metrics
    
    def _empty_metrics(self) -> Dict:
        """Retorna métricas vacías cuando no hay trades"""
        return {
            "total_return": 0,
            "sharpe_ratio": 0,
            "sortino_ratio": 0,
            "max_drawdown": 0,
            "win_rate": 0,
            "profit_factor": 0,
            "total_trades": 0,
            "avg_trade_duration": 0,
            "avg_mae": 0,
            "avg_mfe": 0,
            "expectancy": 0
        }
    
    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calcula el Sharpe Ratio anualizado"""
        if len(returns) < 2:
            return 0.0
        return np.sqrt(252) * returns.mean() / (returns.std() + 1e-10)
    
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calcula el Sortino Ratio anualizado"""
        if len(returns) < 2:
            return 0.0
        downside_returns = returns[returns < 0]
        return np.sqrt(252) * returns.mean() / (downside_returns.std() + 1e-10)
