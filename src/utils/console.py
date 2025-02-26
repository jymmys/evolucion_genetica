from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich.layout import Layout
from rich import print as rprint
from datetime import datetime

console = Console()

def print_generation_stats(gen: int, best_agent, avg_fitness: float):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", justify="right", style="green")
    
    table.add_row("Generación", str(gen))
    table.add_row("Fitness", f"{best_agent.fitness:.4f}")
    table.add_row("Profit Factor", f"{best_agent.profit_factor:.4f}")
    table.add_row("Sharpe Ratio", f"{best_agent.sharpe_ratio:.4f}")
    table.add_row("Max Drawdown", f"{best_agent.drawdown:.4f}")
    table.add_row("Trades", str(best_agent.trades))
    table.add_row("Promedio Población", f"{avg_fitness:.4f}")
    
    panel = Panel(
        table,
        title=f"[bold blue]Estadísticas de Generación {gen}",
        border_style="blue"
    )
    console.print(panel)
    
    # Mostrar indicadores en uso
    indicators_panel = Panel(
        ", ".join(best_agent.indicators),
        title="[bold yellow]Indicadores Activos",
        border_style="yellow"
    )
    console.print(indicators_panel)

def create_progress():
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="green"),
        TextColumn("[bold]{task.percentage:>3.0f}%"),
        console=console
    )

def print_header():
    console.clear()
    title = "[bold cyan]Sistema de Trading Genético[/bold cyan]"
    subtitle = f"[yellow]Sesión iniciada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/yellow]"
    
    console.print(Panel(f"{title}\n{subtitle}", border_style="cyan"))

def print_menu():
    try:
        menu = Table(show_header=False, box=None)
        menu.add_column("Opción", style="cyan")
        menu.add_column("Descripción", style="white")
        
        menu.add_row("1.", "[green]Entrenar nuevas estrategias")
        menu.add_row("2.", "[yellow]Evaluar estrategias existentes")
        menu.add_row("3.", "[blue]Optimizar parámetros")
        menu.add_row("4.", "[red]Salir")
        
        console.print(Panel(menu, title="[bold]Menú Principal", border_style="cyan"))
        return console.input("[bold cyan]Seleccione una opción[/bold cyan] :arrow_right: ")
    except KeyboardInterrupt:
        console.print("\n[bold red]Programa interrumpido por el usuario[/bold red]")
        return "4"  # Retorna opción de salir

def print_training_summary(best_fitness: float):
    """Muestra el resumen final del entrenamiento"""
    console.print(Panel(
        f"[green]Entrenamiento completado![/green]\n"
        f"Mejor fitness alcanzado: [bold]{best_fitness:.4f}[/bold]",
        title="[bold]Resumen de Entrenamiento",
        border_style="green"
    ))
