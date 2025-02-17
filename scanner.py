from zapv2 import ZAPv2
import time, json, logging, os
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler


load_dotenv()

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

log_handler = RotatingFileHandler(
    "scanner_logs.log", maxBytes=5*1024*1024, backupCount=3 
)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

logger = logging.getLogger()

if not logger.hasHandlers():
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)

logger.info("Sistema de logging inicializado.")

def connect_to_zap():
    zap_url = os.getenv("ZAP_URL")
    api_key = os.getenv("ZAP_API_KEY")
    if not zap_url or not api_key:
        logger.error("Falta configurar ZAP_URL o ZAP_API_KEY en el archivo .env")
        return None
    try:
        zap = ZAPv2(apikey=api_key, proxies={'http': zap_url})
        logger.info(f"Conectado a ZAP, versión: {zap.core.version}")
        return zap
    except Exception as e:
        logger.error(f"Error al conectar con ZAP: {e}")
        return None

zap=connect_to_zap()

def is_in_sites(url):
    try:
        sites = zap.core.sites
        if url not in sites:
            zap.core.access_url(url)
            time.sleep(1)
            logger.info(f"URL: {url} añadida a sitios")
            return True
        else:
            zap.core.new_session(name='nueva_sesion', overwrite=True)
            logger.info("Nueva sesion...")
            time.sleep(2)
            zap.core.access_url(url)
            return True
    except Exception as e:
        logger.error(f"Error al tratar de meter la URL en sitios {e}")
        return False


def scan_strength(strength):
    count = 0
    try:
        for policy_id in range(5):
            zap.ascan.set_policy_attack_strength(policy_id, strength.upper())
            zap.ascan.set_policy_alert_threshold(policy_id, 'DEFAULT')

        scan_info_strength = zap.ascan.policies()
        time.sleep(2)
        for policy in scan_info_strength:
            if policy['attackStrength'] == strength.upper():
                count += 1

        if count == 5:  
            logger.info("Attack Strength Configured Correctly")
            return True
        else:
            logger.error("Attack Strength NOT Configured for all policies")
            raise RuntimeError("Attack Strength setting failed.")
    
    except Exception as error:
        logger.error(f"Error setting scan strength: {error}")
        return False  

def active_scan(url,strength):
    try:
        if not scan_strength(strength):
            logger.error("No se pudo configurar el Attack Strength, abortando escaneo.")
            return False

        # Iniciar el Spider
        spider_id = zap.spider.scan(url)
        if not spider_id:
            logger.error(f"No se pudo iniciar el Spider para {url}")
            return False
        
        logger.info(f"Spider iniciado con ID: {spider_id}")

        while int(zap.spider.status(spider_id)) < 100:
            logger.info(f" Spider status: {zap.spider.status(spider_id)}%")
            time.sleep(2)

        logger.info(f"Spider completado en {url}")

        ajax_spider_id = zap.ajaxSpider.scan(url)
        if not ajax_spider_id:
            logger.error(f"No se pudo iniciar el Spider AJAX para {url}")
            return False

        logger.info(f"🔎 Spider AJAX iniciado para {url}")

        while zap.ajaxSpider.status < 'running':
            logger.info(f"Spider AJAX ejecutándose...")
            time.sleep(2)

        logger.info(f"Spider AJAX completado en {url}")

        scan_id = zap.ascan.scan(url)
        if not scan_id:
            logger.error(f"No se pudo iniciar el Active Scan para {url}")
            return False

        logger.info(f"Active Scan iniciado con ID: {scan_id}")

        while int(zap.ascan.status(scan_id)) < 100:
            logger.info(f"Active Scan status: {zap.ascan.status(scan_id)}%")
            time.sleep(2)

        logger.info(f"Active Scan completado en {url}")
        return True

    except Exception as e:
        logger.error(f"Error en active_scan: {e}")
        return False

if __name__ == '__main__':
    url = 'http://example.com'
    strength = 'low'
    is_in_sites(url)
    active_scan(url,strength)