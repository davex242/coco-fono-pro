from core.db import SessionLocal
from models.schema import Emitter, User
from sqlalchemy import func, case, outerjoin, or_
import streamlit as st

def get_real_pending_summary(db):

    results = (
        db.query(
            User.username,
            func.count(Emitter.id).label("total")
        )
        .join(Emitter, Emitter.reclutador_id == User.mico_id)
        .filter(
            Emitter.estado_cuenta == "Verificada",
            Emitter.check_real == True,
            or_(
                Emitter.estado_comision != "Pagada",
                Emitter.estado_comision.is_(None)
            )
        )
        .group_by(User.username)
        .all()
    )

    total_general = sum(r.total for r in results)

    return total_general, results

def render_real_pending_panel(db):
    total_general, data = get_real_pending_summary(db)

    st.markdown(f"""
    <div style="
        font-size:15px;
        height:80px;
        background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.3);
        margin-bottom: 30px;
    ">
        <h5 style="
            font-size:15px;
            color: white;
            margin-bottom: 10px;
        ">
            💰 Total cuentas reales verificadas con comisión pendiente: {total_general}
        </h5>
    """, unsafe_allow_html=True)
    #st.markdown(
    #    f"<h1 style='color:#00E5FF; font-size:60px;'>{total_general}</h1>",
    #    unsafe_allow_html=True
    #)
    
    # Tarjetas pequeñas
    cols = st.columns(4)

    for i, recruiter in enumerate(data):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="
                background-color: #1F2933;
                width:110px;
                height:110px;
                padding: 15px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
                margin-bottom: 15px;
            ">
                <h6 style="color:#A0AEC0; margin-bottom:8px;">
                    {recruiter.username}
                </h6><h6 style="color:#38BDF8; margin:0;">{recruiter.total}</h6>
            </div>
            """, unsafe_allow_html=True)

def get_admin_metrics():
    session = SessionLocal()
    try:
        total_registradas = session.query(Emitter).count()
        verificadas = session.query(Emitter).filter(Emitter.estado_cuenta == "Verificada").count()
        pendientes = session.query(Emitter).filter(Emitter.estado_cuenta == "Pendiente").count()
        comisiones_pendientes = session.query(Emitter).filter(Emitter.estado_comision == "Pendiente", Emitter.check_real == True).count()
        comisiones_pagadas = session.query(Emitter).filter(Emitter.estado_comision == "Pagada").count()
        total_pagado = comisiones_pagadas * 25  # ejemplo: cada comisión $25
        total_pendiente = comisiones_pendientes * 25
        cuenta_real = session.query(Emitter).filter(Emitter.check_real == True).count()
        return {
            "total_registradas": total_registradas,
            "verificadas": verificadas,
            "pendientes": pendientes,
            "comisiones_pendientes": comisiones_pendientes,
            "comisiones_pagadas": comisiones_pagadas,
            "total_pagado": total_pagado,
            "total_pendiente": total_pendiente,
            "cuentas_reales": cuenta_real
        }
    finally:
        session.close()

def get_user_metrics(rec_id):
    session = SessionLocal()
    try:
        total_registradas = session.query(Emitter).filter(Emitter.reclutador_id == rec_id).count()
        verificadas = session.query(Emitter).filter(Emitter.estado_cuenta == "Verificada", Emitter.reclutador_id == rec_id).count()
        pendientes = session.query(Emitter).filter(Emitter.estado_cuenta == "Pendiente", Emitter.reclutador_id == rec_id).count()
        comisiones_pendientes = session.query(Emitter).filter(Emitter.estado_comision == "Pendiente", Emitter.reclutador_id == rec_id, Emitter.check_real == 1).count()
        comisiones_pagadas = session.query(Emitter).filter(Emitter.estado_comision == "Pagada", Emitter.reclutador_id == rec_id).count()
        total_pagado = comisiones_pagadas * 25  # ejemplo: cada comisión $25
        total_pendiente = comisiones_pendientes * 25
        cuenta_real = session.query(Emitter).filter(Emitter.check_real == 1, Emitter.reclutador_id == rec_id).count()
        return {
            "total_registradas": total_registradas,
            "verificadas": verificadas,
            "pendientes": pendientes,
            "comisiones_pendientes": comisiones_pendientes,
            "comisiones_pagadas": comisiones_pagadas,
            "total_pagado": total_pagado,
            "total_pendiente": total_pendiente,
           "cuentas_reales": cuenta_real
        }
    finally:
        session.close()
        
def get_recruiter_ranking(session):
    """
    Devuelve ranking de reclutadores basado en efectividad
    calculando un rate 1-10 ponderado según total de cuentas del sistema
    """

    # total de cuentas de todo el sistema
    total_sistema = session.query(func.count(Emitter.mico_id)).scalar() or 0
    if total_sistema == 0:
        return []

    # outer join para incluir reclutadores aunque no tengan Emitter
    data = (
        session.query(
            User.username.label("reclutador_nombre"),
            func.count(Emitter.mico_id).label("total_reclutador"),
            func.sum(case((Emitter.estado_cuenta == "Verificada", 1), else_=0)).label("cuentas_verificadas"),
            func.sum(case((Emitter.check_real == True, 1), else_=0)).label("cuentas_reales")
        )
        .outerjoin(Emitter, Emitter.reclutador_id == User.mico_id)
        .group_by(User.username)
        .all()
    )

    ranking = []

    for row in data:
        total_reclutador = row.total_reclutador or 0
        verificadas = row.cuentas_verificadas or 0
        reales = row.cuentas_reales or 0

        score = 1  # mínimo 1
        if total_reclutador > 0:
            weight = total_reclutador / total_sistema
            efectividad = (reales + verificadas * 0.5) / total_reclutador
            score = round(1 + efectividad * weight * 9, 2)
            score = min(max(score, 1), 10)

        ranking.append({
            "reclutador_id": row.reclutador_nombre,
            "total_reclutados": total_reclutador,
            "cuentas_verificadas": verificadas,
            "cuentas_reales": reales,
            "score": score
        })

    # ordenar por rate descendente
    ranking.sort(key=lambda x: x["score"], reverse=True)

    return ranking