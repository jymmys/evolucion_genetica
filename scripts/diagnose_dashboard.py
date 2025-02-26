from pathlib import Path
import sys
import os
from rich.console import Console
from rich.table import Table
import traceback
import time

# Configurar path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

console = Console()

def diagnose_dashboard():
    """Diagnóstico completo del sistema de dashboard y logging"""
    status = {
        'directory_checks': [],
        'import_checks': [],
        'permission_checks': [],
        'log_checks': []
    }
    
    console.print("[bold blue]Diagnóstico del Sistema Dashboard[/bold blue]\n")
    
    # 1. Verificar estructura de directorios necesaria
    required_dirs = {
        'data': root_dir / 'data',
        'logs': root_dir / 'data' / 'logs',
        'src': root_dir / 'src',
        'src/utils': root_dir / 'src' / 'utils',
        'src/visualization': root_dir / 'src' / 'visualization',
    }

    console.print("[yellow]Verificando directorios...[/yellow]")
    for name, path in required_dirs.items():
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                status['directory_checks'].append(('created', name, str(path)))
                console.print(f"[green]✓ Creado directorio: {path}[/green]")
            except Exception as e:
                status['directory_checks'].append(('error', name, str(e)))
                console.print(f"[red]✗ Error creando {path}: {e}[/red]")
        else:
            status['directory_checks'].append(('exists', name, str(path)))
            console.print(f"[green]✓ Directorio existente: {path}[/green]")

    # 2. Verificar permisos
    console.print("\n[yellow]Verificando permisos...[/yellow]")
    for name, path in required_dirs.items():
        try:
            test_file = path / '.test_write'
            test_file.write_text('test')
            test_file.unlink()
            status['permission_checks'].append(('success', name))
            console.print(f"[green]✓ Permisos correctos en: {path}[/green]")
        except Exception as e:
            status['permission_checks'].append(('error', name, str(e)))
            console.print(f"[red]✗ Error de permisos en {path}: {e}[/red]")

    # 3. Verificar imports
    console.print("\n[yellow]Verificando imports...[/yellow]")
    imports_to_check = [
        ('rich', 'Rich library'),
        ('pandas', 'Pandas library'),
        ('numpy', 'Numpy library')
    ]
    
    for module, name in imports_to_check:
        try:
            __import__(module)
            status['import_checks'].append(('success', name))
            console.print(f"[green]✓ {name} importado correctamente[/green]")
        except ImportError as e:
            status['import_checks'].append(('error', name, str(e)))
            console.print(f"[red]✗ Error importando {name}: {e}[/red]")

    # 4. Probar sistema de logging
    console.print("\n[yellow]Probando sistema de logging...[/yellow]")
    try:
        from src.utils.unified_logger import unified_logger
        
        # Crear log de prueba
        test_log = unified_logger.log('test', 'INFO', 'Test de diagnóstico dashboard')
        status['log_checks'].append(('success', 'logger_import'))
        console.print("[green]✓ Sistema de logging funcionando[/green]")
        
        # Verificar archivos de log
        log_files = list(Path(required_dirs['logs']).glob('*.log'))
        if log_files:
            status['log_checks'].append(('success', 'log_files', str(len(log_files))))
            console.print(f"[green]✓ {len(log_files)} archivos de log encontrados[/green]")
        else:
            status['log_checks'].append(('warning', 'no_logs'))
            console.print("[yellow]! No se encontraron archivos de log[/yellow]")
            
    except Exception as e:
        status['log_checks'].append(('error', 'logger_test', str(e)))
        console.print(f"[red]✗ Error en sistema de logging: {e}[/red]")

    # 5. Generar reporte
    console.print("\n[bold cyan]Reporte de Diagnóstico:[/bold cyan]")
    
    issues = []
    for category, checks in status.items():
        for check in checks:
            if check[0] == 'error':
                issues.append(f"[red]• {category}: {check[1]} - {check[2]}[/red]")
            elif check[0] == 'warning':
                issues.append(f"[yellow]• {category}: {check[1]}[/yellow]")

    if issues:
        console.print("\n[bold red]Problemas Encontrados:[/bold red]")
        for issue in issues:
            console.print(issue)
            
        console.print("\n[bold yellow]Soluciones Sugeridas:[/bold yellow]")
        console.print("1. Ejecutar los siguientes comandos:")
        console.print("   mkdir -p /workspaces/codespaces-blank/data/logs")
        console.print("   chmod -R 755 /workspaces/codespaces-blank/data")
        console.print(f"2. Verificar PYTHONPATH:\n   export PYTHONPATH={root_dir}")
        console.print("3. Reinstalar dependencias:\n   pip install -r requirements.txt")
    else:
        console.print("[bold green]✓ No se encontraron problemas[/bold green]")

if __name__ == "__main__":
    try:
        diagnose_dashboard()
    except Exception as e:
        console.print(f"[bold red]Error crítico durante el diagnóstico: {str(e)}[/bold red]")
        console.print(traceback.format_exc())
