import os
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
import traceback

# Configurar path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

console = Console()

def validate_logging_system():
    """Validación completa del sistema de logging"""
    errors = []
    warnings = []
    
    console.print("[bold blue]Iniciando validación del sistema de logging...[/bold blue]\n")
    
    # 1. Verificar estructura de directorios
    directories = {
        "root": root_dir,
        "data": root_dir / "data",
        "logs": root_dir / "data" / "logs",
        "src": root_dir / "src",
        "utils": root_dir / "src" / "utils"
    }
    
    console.print("[yellow]Verificando estructura de directorios...[/yellow]")
    for name, path in directories.items():
        try:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                warnings.append(f"Directorio {name} creado: {path}")
            
            # Verificar permisos
            if not os.access(path, os.W_OK):
                errors.append(f"Sin permisos de escritura en {path}")
        except Exception as e:
            errors.append(f"Error con directorio {name}: {str(e)}")
    
    # 2. Verificar imports
    console.print("\n[yellow]Verificando imports necesarios...[/yellow]")
    try:
        from src.utils.unified_logger import unified_logger
        console.print("[green]✓ Logger importado correctamente[/green]")
    except ImportError as e:
        errors.append(f"Error importando unified_logger: {str(e)}")
        console.print(f"[red]Error en imports: {str(e)}[/red]")
        return
    
    # 3. Probar escritura de logs
    console.print("\n[yellow]Probando escritura de logs...[/yellow]")
    try:
        test_log_file = directories["logs"] / "test_log.txt"
        with open(test_log_file, "w") as f:
            f.write("Test de escritura")
        test_log_file.unlink()  # Eliminar archivo de prueba
        console.print("[green]✓ Prueba de escritura exitosa[/green]")
    except Exception as e:
        errors.append(f"Error en prueba de escritura: {str(e)}")
    
    # 4. Probar unified_logger
    console.print("\n[yellow]Probando unified_logger...[/yellow]")
    try:
        unified_logger.log('test', 'INFO', 'Mensaje de prueba de logging')
        console.print("[green]✓ Logger funcionando correctamente[/green]")
    except Exception as e:
        errors.append(f"Error usando unified_logger: {str(e)}")
        console.print(traceback.format_exc())
    
    # 5. Mostrar resultados
    table = Table(title="Resultados de la Validación")
    table.add_column("Tipo", style="cyan")
    table.add_column("Mensaje", style="white")
    
    if not errors and not warnings:
        console.print("\n[bold green]✓ Sistema de logging validado correctamente[/bold green]")
    else:
        if errors:
            console.print("\n[bold red]Errores encontrados:[/bold red]")
            for error in errors:
                table.add_row("ERROR", error, style="red")
        
        if warnings:
            console.print("\n[bold yellow]Advertencias:[/bold yellow]")
            for warning in warnings:
                table.add_row("WARNING", warning, style="yellow")
    
    console.print(table)
    
    # 6. Sugerir soluciones
    if errors:
        console.print("\n[bold yellow]Sugerencias de solución:[/bold yellow]")
        console.print("1. Ejecutar los siguientes comandos:")
        console.print("   mkdir -p /workspaces/codespaces-blank/data/logs")
        console.print("   chmod -R 755 /workspaces/codespaces-blank/data")
        console.print("2. Verificar que PYTHONPATH incluye el directorio raíz:")
        console.print(f"   export PYTHONPATH={root_dir}")
        console.print("3. Reinstalar dependencias:")
        console.print("   pip install -r requirements.txt")

if __name__ == "__main__":
    try:
        validate_logging_system()
    except Exception as e:
        console.print(f"[bold red]Error crítico: {str(e)}[/bold red]")
        console.print(traceback.format_exc())
