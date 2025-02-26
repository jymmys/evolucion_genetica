from src.genetic.agent import TradingAgent
from rich.console import Console
from rich.table import Table

console = Console()

def test_agent_creation():
    # Crear un agente gen
    agent = TradingAgent()
    
    # Mostrar información del agente
    table = Table(title="Información del Agente")
    table.add_column("Atributo", style="cyan")
    table.add_column("Valor", style="green")
    
    table.add_row("Número de Indicadores", str(len(agent.indicators)))
    table.add_row("Indicadores", ", ".join(agent.indicators))
    table.add_row("Pesos", str([f"{w:.4f}" for w in agent.weights]))
    
    console.print(table)

if __name__ == "__main__":
    console.print("[bold blue]Probando creación de agente...[/bold blue]")
    test_agent_creation()
