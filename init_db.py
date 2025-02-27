import os
import enum
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from logger_config import setup_logger
from datetime import datetime, timedelta

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

# 🔹 Enum para periodicidad
class PeriodicidadEnum(enum.Enum):
    UN_MES = "1"
    TRES_MESES = "3"
    SEIS_MESES = "6"
    UN_ANIO = "12"

# 🔹 Enum para la intensidad del escaneo
class IntensidadEscaneoEnum(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    DEFAULT = "DEFAULT"
    HIGH = "HIGH"
    INSANE = "INSANE"

# 🔹 Clase `Activo`
class Activo(Base):
    __tablename__ = "activos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_url = Column(Text, unique=True, nullable=False)
    responsable = Column(String(255), nullable=False)
    email_responsable = Column(Text, nullable=False)  # ✅ Guardamos emails separados por comas en un campo de texto
    tipo = Column(String(100), nullable=False)
    intensidad = Column(Enum(IntensidadEscaneoEnum), nullable=False, default=IntensidadEscaneoEnum.MEDIUM)
    ultima_auditoria = Column(TIMESTAMP, nullable=True)
    periodicidad = Column(Enum(PeriodicidadEnum), nullable=True)
    proxima_auditoria = Column(TIMESTAMP, nullable=True)

    def calcular_proxima_auditoria(self):
        """ Calcula la próxima auditoría en base a la última auditoría y la periodicidad """
        if not self.ultima_auditoria or not self.periodicidad:
            return None

        dias = {
            PeriodicidadEnum.UN_MES: 30,
            PeriodicidadEnum.TRES_MESES: 90,
            PeriodicidadEnum.SEIS_MESES: 180,
            PeriodicidadEnum.UN_ANIO: 365
        }.get(self.periodicidad, None)

        return self.ultima_auditoria + timedelta(days=dias) if dias else None

# 🔹 Clase `EscaneoProgramado`
class EscaneoProgramado(Base):
    __tablename__ = "escaneos_programados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activo_id = Column(Integer, ForeignKey("activos.id", ondelete="CASCADE"), nullable=False)
    fecha_programada = Column(TIMESTAMP, nullable=False, default=datetime.now)  
    estado = Column(String(50), nullable=False, default="Pendiente")
    ultima_ejecucion = Column(TIMESTAMP, nullable=True)
    siguiente_ejecucion = Column(TIMESTAMP, nullable=True)
    intensidad = Column(Enum(IntensidadEscaneoEnum), nullable=False) 

# 🔹 Clase `EscaneoCompletado`
class EscaneoCompletado(Base):
    __tablename__ = "escaneos_completados"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activo_id = Column(Integer, ForeignKey("activos.id", ondelete="CASCADE"), nullable=False)
    estado = Column(String(50), nullable=False, default="Completado")
    fecha_inicio = Column(TIMESTAMP, nullable=True)
    fecha_fin = Column(TIMESTAMP, nullable=True)
    intensidad = Column(Enum(IntensidadEscaneoEnum), nullable=False, default=IntensidadEscaneoEnum.DEFAULT)  
    report_file = Column(JSONB, nullable=True)  
    total_vuln_altas = Column(Integer, default=0)
    total_vuln_medias = Column(Integer, default=0)
    total_vuln_bajas = Column(Integer, default=0)
    total_vuln_info = Column(Integer, default=0)

# 🔹 Clase `DefinicionesReporte`
class DefinicionesReporte(Base):
    __tablename__ = "definiciones_reporte"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(250), nullable=False)
    criticidad = Column(String(25), nullable=False)
    categoria = Column(String(250), nullable=False)
    cwe = Column(Integer, nullable=False)
    detalles = Column(Text, nullable=False)
    riesgo = Column(Text, nullable=False)
    solucion = Column(Text, nullable=False)
    referencias = Column(JSONB, nullable=True)

# 🔹 Función para crear las tablas
def crear_tablas():
    logger.info(f"Conectando a la base de datos en: {DATABASE_URL}")
    try:
        logger.info("Creando tablas en la base de datos...")
        Base.metadata.create_all(engine)
        logger.info("Tablas creadas correctamente.")
    except Exception as e:
        logger.error(f"Error creando las tablas en la base de datos: {e}")