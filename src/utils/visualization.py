import matplotlib.pyplot as plt
import numpy as np
from rich.console import Console
from rich.table import Table
from pathlib import Path

console = Console()

def plot_training_history(fitness_history: list, output_path: str):
    plt.figure(figsize=(12, 6))
    plt.plot(fitness_history, label='Mejor Fitness')
    plt.title('Evolución del Fitness Durante el Entrenamiento')
    plt.xlabel('Generación')
    plt.ylabel('Fitness')
    plt.grid(True)
    plt.legend()
    
    # Guardar gráfico
    plot_path = Path(output_path) / 'training_history.png'
    plt.savefig(plot_path)
    plt.close()
    
    console.print(f"[green]Gráfico guardado en: {plot_path}[/green]")

def create_performance_report(agent, output_path: str):
    # Crear tabla de métricas
    table = Table(title="Reporte de Rendimiento")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", justify="right", style="green")
    
    table.add_row("Sharpe Ratio", f"{agent.sharpe_ratio:.4f}")
    table.add_row("Profit Factor", f"{agent.profit_factor:.4f}")
    table.add_row("Max Drawdown", f"{agent.drawdown:.2%}")
    table.add_row("Número de Trades", str(agent.trades))
    
    console.print(table)
    
    # Guardar reporte
    report_path = Path(output_path) / 'performance_report.txt'
    with open(report_path, 'w') as f:
        f.write(f"Performance Report\n")
        f.write(f"=================\n")
        f.write(f"Sharpe Ratio: {agent.sharpe_ratio:.4f}\n")
        f.write(f"Profit Factor: {agent.profit_factor:.4f}\n")
        f.write(f"Max Drawdown: {agent.drawdown:.2%}\n")
        f.write(f"Trades: {agent.trades}\n")
        f.write(f"\nIndicadores utilizados:\n")
        f.write(", ".join(agent.indicators))
