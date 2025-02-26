import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
import atexit
import json
import threading
from queue import Queue
import traceback

class UnifiedLogger:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.console = Console()
            self.log_queue = Queue()
            self.setup_logging()
            self.initialized = True
            
            # Registrar función de limpieza al salir
            atexit.register(self.cleanup)
    
    def setup_logging(self):
        """Configura el sistema de logging"""
        # Crear estructura de directorios
        self.base_dir = Path(os.getcwd())
        self.log_dir = self.base_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Archivo de log principal
        self.main_log = self.log_dir / f"trading_system_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configurar logger principal
        self.logger = logging.getLogger('TradingSystem')
        self.logger.setLevel(logging.DEBUG)
        
        # Formato detallado para archivo
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        
        # Handler para archivo
        file_handler = logging.FileHandler(self.main_log)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Handler para consola con Rich
        console_handler = RichHandler(
            rich_tracebacks=True,
            show_time=True,
            show_path=True
        )
        console_handler.setLevel(logging.INFO)
        
        # Limpiar handlers existentes
        self.logger.handlers.clear()
        
        # Agregar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Crear archivos de log específicos
        self.create_specialized_logs()
        
        self.console.print(f"[green]Sistema de logging inicializado en: {self.log_dir}[/green]")
    
    def create_specialized_logs(self):
        """Crea loggers especializados para diferentes componentes"""
        self.specialized_loggers = {
            'trading': self._create_specialized_logger('trading'),
            'genetic': self._create_specialized_logger('genetic'),
            'backtest': self._create_specialized_logger('backtest'),
            'dashboard': self._create_specialized_logger('dashboard'),
            'performance': self._create_specialized_logger('performance')
        }
    
    def _create_specialized_logger(self, name: str):
        """Crea un logger especializado"""
        logger = logging.getLogger(f'TradingSystem.{name}')
        logger.setLevel(logging.DEBUG)
        
        # Archivo específico
        log_file = self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        logger.handlers.clear()
        logger.addHandler(handler)
        return logger
    
    def log(self, component: str, level: str, message: str, **kwargs):
        """Log unificado con soporte para metadatos"""
        logger = self.specialized_loggers.get(component, self.logger)
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'component': component,
            'message': message,
            'metadata': kwargs
        }
        
        # Agregar a la cola para procesamiento asíncrono
        self.log_queue.put(log_entry)
        
        # Log inmediato
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(message)
    
    def process_log_queue(self):
        """Procesa la cola de logs"""
        while not self.log_queue.empty():
            entry = self.log_queue.get()
            self._save_structured_log(entry)
    
    def _save_structured_log(self, entry: dict):
        """Guarda log estructurado en formato JSON"""
        structured_log_file = self.log_dir / 'structured_logs.jsonl'
        with structured_log_file.open('a') as f:
            json.dump(entry, f)
            f.write('\n')
    
    def get_component_stats(self, component: str = None):
        """Obtiene estadísticas de los logs"""
        stats = {
            'total_entries': 0,
            'errors': 0,
            'warnings': 0,
            'components': {}
        }
        
        try:
            structured_log_file = self.log_dir / 'structured_logs.jsonl'
            if structured_log_file.exists():
                with structured_log_file.open('r') as f:
                    for line in f:
                        entry = json.loads(line)
                        comp = entry['component']
                        
                        if component and comp != component:
                            continue
                            
                        if comp not in stats['components']:
                            stats['components'][comp] = {'total': 0, 'errors': 0, 'warnings': 0}
                            
                        stats['total_entries'] += 1
                        stats['components'][comp]['total'] += 1
                        
                        level = entry.get('metadata', {}).get('level', 'INFO')
                        if 'ERROR' in level:
                            stats['errors'] += 1
                            stats['components'][comp]['errors'] += 1
                        elif 'WARNING' in level:
                            stats['warnings'] += 1
                            stats['components'][comp]['warnings'] += 1
        
        except Exception as e:
            self.logger.error(f"Error al obtener estadísticas: {e}")
        
        return stats
    
    def cleanup(self):
        """Limpieza al cerrar el sistema"""
        self.process_log_queue()
        self.console.print("[yellow]Sistema de logging finalizado[/yellow]")

# Instancia global
unified_logger = UnifiedLogger()

# Decorador para logging automático
def log_this(component='general'):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                unified_logger.log(component, 'INFO', f"Iniciando {func.__name__}")
                result = func(*args, **kwargs)
                unified_logger.log(component, 'INFO', f"Completado {func.__name__}")
                return result
            except Exception as e:
                unified_logger.log(
                    component, 
                    'ERROR',
                    f"Error en {func.__name__}: {str(e)}",
                    traceback=traceback.format_exc()
                )
                raise
        return wrapper
    return decorator
