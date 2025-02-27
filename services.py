from datetime import datetime, timedelta
from init_db import session, Activo, EscaneoProgramado, EscaneoCompletado, IntensidadEscaneoEnum, PeriodicidadEnum
from scanner import *
def programar_escaneo_manual(target_url, responsable, emails, tipo, fecha_programada, intensidad, periodicidad, nuevo_activo):
    
    if isinstance(emails, str):
        emails = [email.strip() for email in emails.split(",")]

    activo = session.query(Activo).filter_by(target_url=target_url).first()

    if not activo and nuevo_activo:
        activo = Activo(
            target_url=target_url,
            responsable=responsable,
            email_responsable=",".join(emails),
            tipo=tipo,
            ultima_auditoria=None,
            periodicidad=PeriodicidadEnum(periodicidad),
            intensidad=IntensidadEscaneoEnum(intensidad),
            proxima_auditoria=None
        )
        session.add(activo)
        session.commit()

        activo.proxima_auditoria = activo.calcular_proxima_auditoria()
        session.commit()
        
    es_inmediato = fecha_programada == "now"
    if es_inmediato:

        fecha_inicio = datetime.now()
        zap = connect_to_zap()
        is_in_sites(target_url,zap)
        scan_id = active_scan(zap,target_url,intensidad)
        fecha_fin = datetime.now()
        time.sleep(2)
        report=get_report(zap, target_url)
        escaneo_completado = EscaneoCompletado(
            activo_id=activo.id,
            estado="Completado" if scan_id else "Error",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            intensidad=IntensidadEscaneoEnum(intensidad),
            report_file=report,
            total_vuln_altas=0,
            total_vuln_medias=0,
            total_vuln_bajas=0,
            total_vuln_info=0
        )
        session.add(escaneo_completado)
        get_total_vulnerabilities(zap,target_url)
        activo.ultima_auditoria = fecha_fin
        activo.proxima_auditoria = activo.calcular_proxima_auditoria()
        session.commit()

        return {
            "success": f"Escaneo INMEDIATO completado para {target_url}",
            "activo_id": activo.id,
            "ultima_auditoria": activo.ultima_auditoria,
            "proxima_auditoria": activo.proxima_auditoria
        }

    else:
        
        fecha_programada = datetime.strptime(fecha_programada, "%Y-%m-%dT%H:%M")  # Convertir string a datetime
        nuevo_escaneo = EscaneoProgramado(
            activo_id=activo.id,
            fecha_programada=fecha_programada,
            estado="Pendiente",
            intensidad=IntensidadEscaneoEnum(intensidad),
            siguiente_ejecucion=fecha_programada
        )
        session.add(nuevo_escaneo)

        
        activo.proxima_auditoria = fecha_programada
        session.commit()

        return {
            "success": f"Escaneo PROGRAMADO para {target_url} el {fecha_programada}",
            "activo_id": activo.id,
            "proxima_auditoria": activo.proxima_auditoria
        }