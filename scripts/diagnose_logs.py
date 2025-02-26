from pathlib import Path
from rich.console import Console
from rich.table import Table
import os
import sys

console = Console()

def diagnose_system():
    """Diagnóstico completo del sistema de logs"""
    console.print("[bold blue]Diagnóstico del Sistema de Logs[/bold blue]\n")

    # 1. Verificar estructura de directorios
    required_dirs = [
        "data",
        "data/logs",
        "logs",
        "results"
    ]

    console.print("[yellow]Verificando directorios necesarios...[/yellow]")
    for dir_name in required_dirs:
        path = Path(dir_name)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                console.print(f"[green]✓ Creado directorio: {path}[/green]")
            except Exception as e:
                console.print(f"[red]✗ Error creando {path}: {e}[/red]")
        else:
            # Verificar permisos
            if os.access(path, os.W_OK):
                console.print(f"[green]✓ Directorio existe y tiene permisos: {path}[/green]")
            else:
                console.print(f"[red]✗ Directorio existe pero sin permisos: {path}[/red]")
                try:
                    os.chmod(path, 0o755)
                    console.print(f"[green]  → Permisos corregidos para: {path}[/green]")
                except Exception as e:
                    console.print(f"[red]  → No se pudieron corregir permisos: {e}[/red]")

    # 2. Verificar archivos de log existentes
    console.print("\n[yellow]Verificando archivos de log...[/yellow]")
    log_files = list(Path("data/logs").glob("*.log"))
    if not log_files:
        console.print("[red]No se encontraron archivos de log[/red]")
        console.print("Creando archivo de log inicial...")
        try:
            with open("data/logs/trading_system_init.log", "w") as f:
                f.write("Log iniciado: " + str(os.getcwd()) + "\n")
            console.print("[green]✓ Archivo de log inicial creado[/green]")
        except Exception as e:
            console.print(f"[red]✗ Error creando archivo de log: {e}[/red]")
    else:
        console.print(f"[green]✓ {len(log_files)} archivos de log encontrados[/green]")

    # 3. Verificar permisos del sistema
    console.print("\n[yellow]Verificando permisos del sistema...[/yellow]")
    current_dir = Path.cwd()
    try:
        test_file = current_dir / "test_write_permission.tmp"
        test_file.write_text("test")
        test_file.unlink()
        console.print("[green]✓ Permisos de escritura correctos[/green]")
    except Exception as e:
        console.print(f"[red]✗ Problema con permisos de escritura: {e}[/red]")

    # 4. Verificar variables de entorno
    console.print("\n[yellow]Verificando variables de entorno...[/yellow]")
    python_path = sys.path
    console.print(f"PYTHONPATH incluye:")
    for path in python_path:
        console.print(f"  - {path}")

    # 5. Resumen y recomendaciones
    console.print("\n[bold cyan]Resumen del Diagnóstico:[/bold cyan]")
    if any(not Path(d).exists() for d in required_dirs):
        console.print("[red]! Algunos directorios requeridos no existen[/red]")
        console.print("  → Ejecute: mkdir -p data/logs")
    
    if not log_files:
        console.print("[red]! No hay archivos de log[/red]")
        console.print("  → El sistema creará nuevos archivos de log automáticamente")
    
    # 6. Intentar solución automática
    console.print("\n[yellow]¿Desea intentar una solución automática? (s/n)[/yellow]")
    if input().lower() == 's':
        try:
            # Crear estructura completa
            for dir_name in required_dirs:
                Path(dir_name).mkdir(parents=True, exist_ok=True)
            
            # Establecer permisos correctos
            for dir_name in required_dirs:
                os.chmod(dir_name, 0o755)
            
            # Crear archivo de log inicial si no existe
            if not log_files:
                with open("data/logs/trading_system_init.log", "w") as f:
                    f.write("Log iniciado: " + str(os.getcwd()) + "\n")
            
            console.print("[green]✓ Solución automática completada[/green]")
        except Exception as e:
            console.print(f"[red]✗ Error en solución automática: {e}[/red]")
            console.print("  → Intente ejecutar el script con privilegios elevados")

if __name__ == "__main__":
    diagnose_system()
