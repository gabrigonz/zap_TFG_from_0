from flask import Blueprint, jsonify, request
from init_db import Activo, session
from services import programar_escaneo_manual
from sqlalchemy.exc import SQLAlchemyError
from logger_config import setup_logger

logger = setup_logger()
bp = Blueprint("routes", __name__)

@bp.route("/buscar_activos", methods=["GET"])
def buscar_activos():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([]) 
    
    try:
        if "%" in query or "_" in query or "select" in query or "'" in query:
            return jsonify({"error": "Caracteres inválidos en la búsqueda"}), 400  

        activos = session.query(Activo).filter(Activo.target_url.ilike(f"%{query}%")).limit(10).all()
        if not activos:
            return jsonify([])
        resultados = [{"id": activo.id, "url": activo.target_url} for activo in activos]
        return jsonify(resultados)

    except SQLAlchemyError as e:
        session.rollback() 
        return jsonify({"error": "Error en la base de datos"}), 500  # Cambiar a 500 en vez de 400
 # Devuelve 500 en lugar de 400

@bp.route("/programar_escaneo", methods=["POST", "GET"])
def programar_escaneo():
    data = request.get_json()
    logger.info("Datos recibidos en Flask:", data)

    target_url = data.get("target_url")
    intensidad = data.get("strength", "DEFAULT")
    schedule = data.get("schedule", False) 
    nuevo_activo = data.get("nuevo_activo", False)

    if not target_url:
        return jsonify({"error": "El campo 'Target URL' es obligatorio"}), 400
    
    if schedule:
        fecha_programada = data.get("scanDateTime")
    else:
        fecha_programada = "now"

    if nuevo_activo:
        responsable = data.get("responsable")
        emails = data.get("emails")
        tipo = data.get("tipo")
        periodicidad = data.get("periodicidad", "3")

        if not responsable or not emails or not tipo or not periodicidad:
            return jsonify({"error": "Faltan datos obligatorios para crear un nuevo activo"}), 400
    else:
        responsable = None
        emails = None
        tipo = None
        periodicidad = None

    try:
        resultado = programar_escaneo_manual(
            target_url, responsable, emails, tipo, fecha_programada, intensidad, periodicidad, nuevo_activo
        )
    except Exception as e:
        print(f"Error en services.py: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify(resultado)
