import os
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from logger_config import setup_logger

load_dotenv()
logger = setup_logger()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
Base = declarative_base()

class Activo(Base):
    __tablename__ = "activos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_url = Column(Text, unique=True, nullable=False)
    responsable = Column(String(255), nullable=False)
    email_responsable = Column(ARRAY(Text), nullable=False)  # Manejo de array de emails
    tipo = Column(String(100), nullable=False)
    ultima_auditoria = Column(TIMESTAMP)
    proxima_auditoria = Column(TIMESTAMP)

# 🔹 Tabla de Escaneos Programados
class EscaneoProgramado(Base):
    __tablename__ = "escaneos_programados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activo_id = Column(Integer, ForeignKey("activos.id", ondelete="CASCADE"), nullable=False)
    fecha_programada = Column(TIMESTAMP, nullable=False)
    frecuencia = Column(String(50), nullable=False)
    estado = Column(String(50), nullable=False, default="Pendiente")
    ultima_ejecucion = Column(TIMESTAMP)
    siguiente_ejecucion = Column(TIMESTAMP)
    configuracion_json = Column(JSON)  # JSONB en PostgreSQL

# 🔹 Tabla de Escaneos Completados
class EscaneoCompletado(Base):
    __tablename__ = "escaneos_completados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activo_id = Column(Integer, ForeignKey("activos.id", ondelete="CASCADE"), nullable=False)
    estado = Column(String(50), nullable=False, default="Completado")
    fecha_inicio = Column(TIMESTAMP)
    fecha_fin = Column(TIMESTAMP)
    intensidad = Column(String(50), nullable=False, default="DEFAULT")
    report_file = Column(JSON)  # JSONB en PostgreSQL
    total_vuln_altas = Column(Integer, default=0)
    total_vuln_medias = Column(Integer, default=0)
    total_vuln_bajas = Column(Integer, default=0)
    total_vuln_info = Column(Integer, default=0)

def crear_tablas():
    try:
        logger.info(f"Conectando a la base de datos en: {DATABASE_URL}")
    except Exception as e:
        logger.error(f"ERROR conectando a la base de datos en: {e}")
    try:
        logger.info("Creando tablas en la base de datos...")
        Base.metadata.create_all(engine)
        logger.info("Tablas creadas correctamente.")
    except Exception as e:
        logger.error(f"ERROR creando las tablas dentor de la bbdd {e}")