
import logging
from logging.handlers import RotatingFileHandler
def setup_logger():
    """
    Configura un logger centralizado con rotación de archivos.
    """
    logger = logging.getLogger("zap_scanner")
    
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

    
        log_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        log_handler = RotatingFileHandler(
            "logs/zap_scanner.log", maxBytes=5*1024*1024, backupCount=3
        )
        log_handler.setFormatter(log_formatter)
        log_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)

        logger.addHandler(log_handler)
        logger.addHandler(console_handler)

    return logger