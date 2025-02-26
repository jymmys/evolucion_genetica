from src.utils.logger import logger
import time

def test_logging():
    """Realiza una serie de pruebas en el sistema de logging"""
    print("Iniciando pruebas de logging...")
    
    # 1. Validar sistema de logs
    logger.info("Iniciando validación de logs")
    logger.print_validation_report()
    
    # 2. Probar diferentes niveles de log
    logger.debug("Mensaje de prueba - DEBUG")
    logger.info("Mensaje de prueba - INFO")
    logger.warning("Mensaje de prueba - WARNING")
    logger.error("Mensaje de prueba - ERROR")
    
    # 3. Probar manejo de excepciones
    try:
        raise ValueError("Error de prueba")
    except Exception as e:
        logger.error("Error controlado de prueba", exc_info=True)
    
    # 4. Esperar un momento y mostrar últimos logs
    time.sleep(1)
    logger.print_validation_report()

if __name__ == "__main__":
    test_logging()
