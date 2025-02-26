import os
from pathlib import Path
from rich.console import Console

console = Console()

def init_project_structure():
    """Inicializa la estructura de directorios del proyecto"""
    base_dir = Path(os.getcwd())
    
    # Directorios necesarios
    directories = [
        "data/logs",
        "data/historical",
        "results/agents",
        "results/backtest",
        "src/genetic",
        "src/evaluation",
        "src/indicators",
        "src/utils",
        "src/visualization"
    ]
    
    for dir_path in directories:
        full_path = base_dir / dir_path
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]Creado directorio: {full_path}[/green]")
        except Exception as e:
            console.print(f"[red]Error al crear {full_path}: {e}[/red]")

if __name__ == "__main__":
    console.print("[bold blue]Inicializando estructura del proyecto...[/bold blue]")
    init_project_structure()
