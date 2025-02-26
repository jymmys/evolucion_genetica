from pathlib import Path
from rich.console import Console
from rich.table import Table
from datetime import datetime
import re

console = Console()

def analyze_logs():
    """Analiza los archivos de log y busca errores o problemas"""
    console.print("[bold blue]Analizador de Logs del Sistema de Trading[/bold blue]\n")
    
    # 1. Buscar directorio de logs
    log_paths = [
        Path("logs"),
        Path("data/logs"),
        Path.cwd() / "data" / "logs",
        Path.home() / "trading_logs"
    ]
    
    log_dir = None
    for path in log_paths:
        if path.exists():
            log_dir = path
            break
    
    if not log_dir:
        console.print("[red]No se encontró el directorio de logs en ninguna ubicación conocida[/red]")
        return
    
    console.print(f"[green]Directorio de logs encontrado en: {log_dir}[/green]")
    
    # 2. Analizar archivos de log
    log_files = list(log_dir.glob("trading_system_*.log"))
    if not log_files:
        console.print("[yellow]No se encontraron archivos de log[/yellow]")
        return
    
    # 3. Crear tabla de resultados
    table = Table(title="Análisis de Logs")
    table.add_column("Archivo", style="cyan")
    table.add_column("Errores", justify="right", style="red")
    table.add_column("Warnings", justify="right", style="yellow")
    table.add_column("Info", justify="right", style="green")
    table.add_column("Último Error", style="red")
    
    total_errors = 0
    error_patterns = []
    
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                content = f.read()
                
            # Contar eventos
            errors = len(re.findall(r'ERROR', content))
            warnings = len(re.findall(r'WARNING', content))
            infos = len(re.findall(r'INFO', content))
            
            # Buscar último error
            last_error = "Ninguno"
            error_matches = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - .* - ERROR - (.*)', content)
            if error_matches:
                last_error = error_matches[-1][:50] + "..." if len(error_matches[-1]) > 50 else error_matches[-1]
                error_patterns.append(last_error)
            
            total_errors += errors
            
            table.add_row(
                log_file.name,
                str(errors),
                str(warnings),
                str(infos),
                last_error
            )
            
        except Exception as e:
            console.print(f"[red]Error analizando {log_file}: {e}[/red]")
    
    console.print(table)
    
    # 4. Análisis de patrones de error
    if error_patterns:
        console.print("\n[bold red]Patrones de Error Encontrados:[/bold red]")
        for pattern in set(error_patterns):
            console.print(f"• {pattern}")
            
        # 5. Sugerir soluciones
        console.print("\n[bold yellow]Sugerencias de Solución:[/bold yellow]")
        for pattern in set(error_patterns):
            if "permission denied" in pattern.lower():
                console.print("• Verificar permisos de escritura en el directorio de logs")
            elif "no such file" in pattern.lower():
                console.print("• Asegurarse de que todos los directorios necesarios existan")
            elif "dashboard" in pattern.lower():
                console.print("• Revisar la configuración del dashboard y sus dependencias")
    
    # 6. Resumen
    console.print(f"\n[bold]Resumen del Análisis:[/bold]")
    console.print(f"Total de archivos de log: {len(log_files)}")
    console.print(f"Total de errores encontrados: {total_errors}")

if __name__ == "__main__":
    analyze_logs()
