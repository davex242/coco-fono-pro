from sqlalchemy import func
from models.schema import Emitter, CommissionHistory
from config import COMMISSION_RULES, BONUS_VOLUME
from datetime import datetime

def get_verified_emitters(db, recruiter_id=None):
    query = db.query(Emitter).filter(
        Emitter.estado_cuenta == "Verificada",
        Emitter.check_real == True
    )

    if recruiter_id:
        query = query.filter(Emitter.reclutador_id == recruiter_id)

    return query.all()


def calculate_commission_amount(emitters):

    total = 0

    for e in emitters:
        base = COMMISSION_RULES.get(e.metodo_pago, 0)
        total += base

    total_accounts = len(emitters)

    bonus = 0
    for meta, reward in BONUS_VOLUME.items():
        if total_accounts >= meta:
            bonus = reward

    return total + bonus


def get_commission_summary(db, recruiter_id=None):

    emitters = get_verified_emitters(db, recruiter_id)

    total_accounts = len(emitters)
    total_pending = len([e for e in emitters if e.estado_comision == "Pendiente"])
    total_paid = len([e for e in emitters if e.estado_comision == "Pagada"])

    total_money = calculate_commission_amount(
        [e for e in emitters if e.estado_comision == "Pendiente"]
    )

    return {
        "total_accounts": total_accounts,
        "total_pending": total_pending,
        "total_paid": total_paid,
        "total_money": total_money
    }


def mark_commissions_paid(db, recruiter_id):

    db.query(Emitter).filter(
        Emitter.reclutador_id == recruiter_id,
        Emitter.estado_cuenta == "Verificada",
        Emitter.check_real == True,
        Emitter.estado_comision == "Pendiente"
    ).update({"estado_comision": "Pagada"})

    db.commit()

def registrar_historial_comision(db, emitters, tipo):
    """
    Registra en commission_history el pago de las comisiones de los emisores.
    `emitters`: lista de objetos Emitter cuya comisión se pagó
    `tipo`: "manual" o "global"
    """
    if not emitters:
        return

    # Agrupar por reclutador
    reclutadores = {}
    for e in emitters:
        if e.reclutador_id not in reclutadores:
            reclutadores[e.reclutador_id] = []
        reclutadores[e.reclutador_id].append(e)

    for rec_id, emisores in reclutadores.items():
        total_cuentas = len(emisores)
        cuentas_reales = sum(1 for e in emisores if e.check_real)
        total_pagado = sum(e.monto_comision for e in emisores)
        fecha_pago = datetime.now()

        historial = CommissionHistory(
            recruiter_id=rec_id,
            total_cuentas=total_cuentas,
            cuentas_reales=cuentas_reales,
            total_pagado=total_pagado,
            pagado=True,
            fecha_pago=fecha_pago
        )

        db.add(historial)

    db.commit()