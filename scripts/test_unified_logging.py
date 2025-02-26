import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.utils.unified_logger import unified_logger
import time
import random

def simulate_trading_activity():
    """Simula actividad de trading para probar el logging"""
    components = ['trading', 'genetic', 'backtest', 'dashboard', 'performance']
    
    try:
        # 1. Verificar directorios
        log_dir = root_dir / "data" / "logs"
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
            unified_logger.log('test', 'INFO', f'Creado directorio de logs: {log_dir}')
        
        # 2. Generar logs de prueba
        for i in range(10):
            component = random.choice(components)
            
            # Simular diferentes tipos de eventos
            if random.random() < 0.7:  # 70% INFO
                unified_logger.log(component, 'INFO', 
                    f'Operación normal #{i} en {component}',
                    operation_id=i,
                    timestamp=time.time()
                )
            elif random.random() < 0.9:  # 20% WARNING
                unified_logger.log(component, 'WARNING',
                    f'Advertencia en operación #{i}',
                    operation_id=i,
                    issue='performance_warning'
                )
            else:  # 10% ERROR
                try:
                    raise ValueError(f'Error simulado en {component}')
                except Exception as e:
                    unified_logger.log(component, 'ERROR',
                        str(e),
                        operation_id=i,
                        traceback=True
                    )
            
            time.sleep(0.5)  # Simular actividad real
            
        # 3. Verificar logs generados
        stats = unified_logger.get_component_stats()
        print("\nEstadísticas de logging:")
        print(f"Total de entradas: {stats['total_entries']}")
        print(f"Errores: {stats['errors']}")
        print(f"Advertencias: {stats['warnings']}")
        
        # 4. Mostrar logs por componente
        print("\nRegistros por componente:")
        for comp, data in stats['components'].items():
            print(f"{comp}: {data['total']} registros "
                  f"({data['errors']} errores, {data['warnings']} advertencias)")
        
    except Exception as e:
        unified_logger.log('test', 'CRITICAL', 
            f'Error en prueba de logging: {str(e)}',
            traceback=True
        )
        raise

if __name__ == '__main__':
    print("Iniciando pruebas del sistema de logging...")
    try:
        simulate_trading_activity()
        print("\nPruebas completadas exitosamente")
    except KeyboardInterrupt:
        print("\nPruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\nError en las pruebas: {e}")
    finally:
        # Asegurar que los logs se guarden
        unified_logger.cleanup()
