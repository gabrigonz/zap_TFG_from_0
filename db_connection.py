import psycopg2
import os
from dotenv import load_dotenv
from logger_config import setup_logger

load_dotenv()
logger = setup_logger()

def get_db_connection():
    """Conectar con PostgreSQL"""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception as e:
        logger.info(f"Error al conectarse con PostgreSQL; {e}")
        return None