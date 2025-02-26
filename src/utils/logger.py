import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler

class SystemLogger:
    def __init__(self, name: str = "TradingSystem"):
        self.console = Console()
        
        # Crear directorio de logs relativo al directorio actual del proyecto
        self.log_dir = Path(os.getcwd()) / "data" / "logs"
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self.console.print(f"[green]Directorio de logs creado en: {self.log_dir}[/green]")
        except Exception as e:
            self.console.print(f"[yellow]No se pudo crear el directorio de logs: {e}[/yellow]")
            # Usar directorio temporal como fallback
            import tempfile
            self.log_dir = Path(tempfile.gettempdir()) / "trading_logs"
            self.log_dir.mkdir(exist_ok=True)
            self.console.print(f"[yellow]Usando directorio alternativo: {self.log_dir}[/yellow]")
        
        # Crear logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Configurar formato
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        try:
            # Handler para archivo
            log_file = self.log_dir / f"trading_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(fmt))
            self.logger.addHandler(file_handler)
            self.console.print(f"[green]Archivo de log creado: {log_file}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error al crear archivo de log: {e}[/red]")
            self.console.print("[yellow]Continuando solo con logs en consola[/yellow]")
        
        # Handler para consola con Rich (siempre disponible)
        console_handler = RichHandler(rich_tracebacks=True)
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str, exc_info=None):
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info=True):
        self.logger.critical(message, exc_info=exc_info)
    
    def validate_logs(self):
        """Valida el sistema de logs y retorna un reporte de estado"""
        status = {
            "log_dir_exists": False,
            "log_dir_writable": False,
            "current_log_file": None,
            "last_messages": [],
            "errors_found": []
        }
        
        try:
            # Verificar directorio de logs
            status["log_dir_exists"] = self.log_dir.exists()
            
            # Verificar permisos de escritura
            try:
                test_file = self.log_dir / "test_write.tmp"
                test_file.write_text("test")
                test_file.unlink()
                status["log_dir_writable"] = True
            except Exception as e:
                status["errors_found"].append(f"Error de escritura: {str(e)}")
            
            # Obtener archivo de log actual
            current_logs = list(self.log_dir.glob("trading_system_*.log"))
            if current_logs:
                latest_log = max(current_logs, key=lambda x: x.stat().st_mtime)
                status["current_log_file"] = str(latest_log)
                
                # Leer últimos mensajes
                with open(latest_log, 'r') as f:
                    status["last_messages"] = f.readlines()[-10:]  # Últimas 10 líneas
                    
            return status
            
        except Exception as e:
            self.error(f"Error validando logs: {str(e)}")
            return status
    
    def print_validation_report(self):
        """Imprime un reporte de validación del sistema de logs"""
        status = self.validate_logs()
        
        self.console.print("\n[bold blue]Reporte de Validación de Logs[/bold blue]")
        self.console.print(f"Directorio de logs: {self.log_dir}")
        self.console.print(f"Directorio existe: [{'green' if status['log_dir_exists'] else 'red'}]✓[/]")
        self.console.print(f"Permisos de escritura: [{'green' if status['log_dir_writable'] else 'red'}]✓[/]")
        
        if status["current_log_file"]:
            self.console.print(f"\nArchivo de log actual: {status['current_log_file']}")
            self.console.print("\n[yellow]Últimos mensajes:[/yellow]")
            for msg in status["last_messages"]:
                self.console.print(f"  {msg.strip()}")
        
        if status["errors_found"]:
            self.console.print("\n[red]Errores encontrados:[/red]")
            for error in status["errors_found"]:
                self.console.print(f"  - {error}")

# Crear instancia global
logger = SystemLogger()
