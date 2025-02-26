import pandas as pd
import numpy as np
from src.evaluation.backtest import BacktestEngine
from src.genetic.agent import TradingAgent
from src.indicators.ninjatrader import NinjaIndicators
from rich.console import Console

console = Console()

def run_backtest_example():
    # Cargar datos históricos desde CSV
    data = pd.read_csv('/workspaces/codespaces-blank/data/historical_data.csv')
    
    # Convertir Date y Time a índice datetime
    data['datetime'] = pd.to_datetime(data['Date'].astype(str) + ' ' + data['Time'])
    data.set_index('datetime', inplace=True)
    
    # Eliminar columnas Date y Time ya que ahora están en el índice
    data = data.drop(['Date', 'Time'], axis=1)

    # 2. Crear un agente de trading
    agent = TradingAgent(NinjaIndicators.AVAILABLE_INDICATORS)

    # 3. Configurar el motor de backtesting
    backtest = BacktestEngine(
        initial_capital=100000,
        risk_per_trade=0.02,      # 2% riesgo por operación
        max_position_size=0.1,     # Máximo 10% del capital por posición
        stop_loss_pct=0.02,        # Stop loss del 2%
        take_profit_pct=0.04       # Take profit del 4%
    )

    # 4. Ejecutar el backtest
    console.print("[bold blue]Iniciando backtesting...")
    results = backtest.run_backtest(agent, data)

    # 5. Mostrar resultados
    console.print("\n[bold green]Resultados del Backtest:[/bold green]")
    for metric, value in results.items():
        if isinstance(value, float):
            console.print(f"{metric}: {value:.2%}")
        else:
            console.print(f"{metric}: {value}")

    # 6. Mostrar detalles de las operaciones
    if backtest.trades:
        console.print("\n[bold yellow]Últimas 5 operaciones:[/bold yellow]")
        for trade in backtest.trades[-5:]:
            console.print(f"""
            Entrada: {trade.entry_time} a {trade.entry_price:.2f}
            Salida: {trade.exit_time} a {trade.exit_price:.2f}
            P&L: {trade.pnl:.2f} ({trade.return_pct:.2%})
            Razón: {trade.exit_reason}
            MAE: {trade.max_adverse_excursion:.2f}
            MFE: {trade.max_favorable_excursion:.2f}
            """)

if __name__ == "__main__":
    run_backtest_example()
