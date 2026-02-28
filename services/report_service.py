# services/report_service.py
from sqlalchemy.orm import Session
from models.schema import Emitter, User
from datetime import datetime

# -----------------------------------------------------------
# Obtener todos los emisores, opcionalmente filtrando por reclutador_id
# -----------------------------------------------------------
def get_emitters(db: Session, reclutador_id: int = None):
    query = db.query(Emitter).join(User, Emitter.reclutador_id == User.id)

    if reclutador_id:
        query = query.filter(Emitter.reclutador_id == reclutador_id)

    emitters = query.all()

    results = []
    for e in emitters:
        results.append({
            "id": e.id,
            "nombre": e.nombre,
            "mico_id": e.mico_id,
            "metodo_pago": e.metodo_pago,
            "pago_id": e.pago_id,
            "fecha_registro": e.fecha_registro,
            "telefono": e.telefono,
            "reclutador_id": e.reclutador_id,
            "reclutador_nombre": e.reclutador.username if e.reclutador else "",
            "estado_cuenta": e.estado_cuenta,
            "fecha_verificacion": e.fecha_verificacion,
            "estado_comision": e.estado_comision,
            "check_real": e.check_real,
            "captura_form": e.captura_form,
            "captura_pago": e.captura_pago,
            "captura_transmision": e.captura_transmision,
            "captura_chat": e.captura_chat
        })
    return results

# -----------------------------------------------------------
# Obtener detalle de un emisor por ID
# -----------------------------------------------------------
def get_emitter_detail(db: Session, emitter_id: int):
    emitter = db.query(Emitter).join(User, Emitter.reclutador_id == User.id)\
        .filter(Emitter.id == emitter_id).first()

    if not emitter:
        return None

    return {
        "id": emitter.id,
        "nombre": emitter.nombre,
        "mico_id": emitter.mico_id,
        "metodo_pago": emitter.metodo_pago,
        "pago_id": emitter.pago_id,
        "fecha_registro": emitter.fecha_registro,
        "telefono": emitter.telefono,
        "reclutador_id": emitter.reclutador_id,
        "reclutador_nombre": emitter.reclutador.username if emitter.reclutador else "",
        "estado_cuenta": emitter.estado_cuenta,
        "fecha_verificacion": emitter.fecha_verificacion,
        "estado_comision": emitter.estado_comision,
        "check_real": emitter.check_real,
        "captura_form": emitter.captura_form,
        "captura_pago": emitter.captura_pago,
        "captura_transmision": emitter.captura_transmision,
        "captura_chat": emitter.captura_chat
    }

# -----------------------------------------------------------
# Crear un nuevo emisor
# -----------------------------------------------------------
def create_emitter(db: Session, data: dict):
    nuevo = Emitter(
        nombre=data.get("nombre"),
        mico_id=data.get("mico_id"),
        metodo_pago=data.get("metodo_pago"),
        pago_id=data.get("pago_id"),
        fecha_registro=data.get("fecha_registro", datetime.now()),
        telefono=data.get("telefono"),
        reclutador_id=data.get("reclutador_id"),
        estado_cuenta=data.get("estado_cuenta", "pendiente"),
        fecha_verificacion=data.get("fecha_verificacion"),
        estado_comision=data.get("estado_comision", "pendiente"),
        check_real=data.get("check_real", False),
        captura_form=data.get("captura_form"),
        captura_pago=data.get("captura_pago"),
        captura_transmision=data.get("captura_transmision"),
        captura_chat=data.get("captura_chat")
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# -----------------------------------------------------------
# Actualizar un emisor
# -----------------------------------------------------------
def update_emitter(db: Session, emitter_id: int, update_data: dict):
    emitter = db.query(Emitter).filter(Emitter.id == emitter_id).first()
    if not emitter:
        return None

    for key, value in update_data.items():
        setattr(emitter, key, value)

    db.commit()
    db.refresh(emitter)
    return emitter

# -----------------------------------------------------------
# Eliminar un emisor
# -----------------------------------------------------------
def delete_emitter(db: Session, emitter_id: int):
    emitter = db.query(Emitter).filter(Emitter.id == emitter_id).first()
    if not emitter:
        return False
    db.delete(emitter)
    db.commit()
    return True
