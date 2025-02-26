from src.genetic.agent import TradingAgent
from rich.console import Console
from rich.table import Table
import numpy as np

console = Console()

def test_trading_system():
    console.print("\n[bold cyan]Test del Sistema de Trading[/bold cyan]")
    
    # 1. Crear varios agentes
    console.print("\n[yellow]1. Creando múltiples agentes...[/yellow]")
    agents = [TradingAgent() for _ in range(3)]
    
    for i, agent in enumerate(agents, 1):
        table = Table(title=f"Agente {i}")
        table.add_column("Atributo", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("Indicadores", ", ".join(agent.indicators))
        table.add_row("Número de Indicadores", str(len(agent.indicators)))
        table.add_row("Pesos", str([f"{w:.4f}" for w in agent.weights]))
        
        console.print(table)
    
    # 2. Probar mutación
    console.print("\n[yellow]2. Probando mutación...[/yellow]")
    agent = agents[0]
    console.print("Antes de mutación:", ", ".join(agent.indicators))
    agent.mutate(prob=0.5)
    console.print("Después de mutación:", ", ".join(agent.indicators))
    
    # 3. Probar crossover
    console.print("\n[yellow]3. Probando crossover...[/yellow]")
    parent1, parent2 = agents[0], agents[1]
    child1, child2 = parent1.crossover(parent2, prob=1.0)
    
    table = Table(title="Resultado del Crossover")
    table.add_column("Agente", style="cyan")
    table.add_column("Indicadores", style="green")
    
    table.add_row("Padre 1", ", ".join(parent1.indicators))
    table.add_row("Padre 2", ", ".join(parent2.indicators))
    table.add_row("Hijo 1", ", ".join(child1.indicators))
    table.add_row("Hijo 2", ", ".join(child2.indicators))
    
    console.print(table)

if __name__ == "__main__":
    test_trading_system()
