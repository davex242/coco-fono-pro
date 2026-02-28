import streamlit as st
from services.analytics import get_admin_metrics, get_recruiter_ranking
from services.emitter import get_all_emitters
from core.db import SessionLocal
import pandas as pd
from models.schema import Emitter

def render_ranking():
    session = SessionLocal()

    ranking = get_recruiter_ranking(session)

    st.header("🏆 Ranking de Reclutadores")

    if not ranking:
        st.info("No hay datos todavía.")
        return

    for idx, r in enumerate(ranking, start=1):
#        st.markdown(f"#### TOP {idx} {r['reclutador_id'].title()}")

        col1, col2, col3, col4 = st.columns(4)

        col1.markdown(f"#### TOP {idx} {r['reclutador_id'].title()}")
        col2.metric("Total Reclutados", r["total_reclutados"])
        col3.metric("Cuentas Reales", r["cuentas_reales"])
        col4.metric("Calificación 1-10", f"{r['score']}")

        st.divider()

def render_admin(user):
    db = SessionLocal()  # creamos la sesión de base de datos

    st.title(f"Dashboard Admin: {user}")
    
    metrics = get_admin_metrics()
    def tarjeta_dato(titulo, valor, color="#4CAF50", txt_color="#4CAF50", bg_color="#4CAF50"):
        st.markdown(
            f"""
            <div style="
                font-size:15px;
                background-color:{bg_color};
                padding:10px;
                height:100px;
                width:150px;
                border-radius:20px;
                text-align:center;
                box-shadow:0px 4px 10px rgba(0,0,0,0.3);
            ">
                <h6 style="color:{txt_color}; margin-bottom:10px;">{titulo}</h4>
                <h6 style="color:{color}; margin:10;">{valor}</h2>
            </div>
            """,
            unsafe_allow_html=True
    )
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    st.subheader(f"**Resumen de métricas**", text_alignment="center")
    with col1:
            tarjeta_dato("Registradas",metrics['total_registradas'], "#1436CA", "#13A4CD", "#DAE6EA")
    #st.write(f"Cuentas registradas: {metrics['total_registradas']}")
    with col2:
            tarjeta_dato("Verificadas",metrics['verificadas'], "#4CAF50", "#6BE832", "#E8EA63")
    #st.write(f"Cuentas verificadas: {metrics['verificadas']}")
    with col3:
            tarjeta_dato("Pendientes",metrics['pendientes'], "#C59226", "#A37B0B", "#3FCBCB")
    #st.write(f"Cuentas pendientes: {metrics['pendientes']}")
    with col4:
            tarjeta_dato("Sin Pagar",metrics['comisiones_pendientes'], "#FFFFFF", "#FFFFFF", "#D9B91B")
    #st.write(f"Comisiones pendientes: {metrics['comisiones_pendientes']}")
    with col5:
            tarjeta_dato("Pagada",metrics['comisiones_pagadas'], "#D8E42E", "#E7ECED", "#08AADF")
    #st.write(f"Comisiones pagadas: {metrics['comisiones_pagadas']}")
    with col6:
            tarjeta_dato("Total pagado", f"$ {metrics['total_pagado']}", "#4CAF50", "#13A4CD", "#DAE6EA")
    #st.write(f"Total pagado: ${metrics['total_pagado']}")
    with col1:
            tarjeta_dato("Total pendiente",f"$ {metrics['total_pendiente']}", "#4CAF50", "#13A4CD", "#E6BD29")
    #st.write(f"Total pendiente: ${metrics['total_pendiente']}")
    with col2:
            tarjeta_dato("Cuentas Reales",metrics['cuentas_reales'], "#FFFFFF", "#FFFFFF", "#2400F0")

    st.markdown(
    """
    <hr style="border: 2px solid #4CAF50; border-radius:5px;">
    """,
    unsafe_allow_html=True
    )

#    st.write("**Resumen de métricas**")
#    st.write(f"Cuentas registradas: {metrics['total_registradas']}")
#    st.write(f"Cuentas verificadas: {metrics['verificadas']}")
#    st.write(f"Cuentas pendientes: {metrics['pendientes']}")
#    st.write(f"Comisiones pendientes: {metrics['comisiones_pendientes']}")
#    st.write(f"Comisiones pagadas: {metrics['comisiones_pagadas']}")
#    st.write(f"Total pagado: ${metrics['total_pagado']}")
#    st.write(f"Total pendiente: ${metrics['total_pendiente']}")
    col1, col2 = st.columns(2)

    emitters = get_all_emitters(db)

    st.subheader("Lista completa de emisores")

    # 1️⃣ Convertimos a DataFrame
    df = pd.DataFrame([{
    "ID": e.id,  # IMPORTANTE para poder actualizar luego
    "Nombre": e.nombre,
    "ID Mico": e.mico_id,
    "Estado": e.estado_cuenta,
    "Comisión": e.estado_comision,
    "Check Real": e.check_real
    } for e in emitters])

    # 2️⃣ Editor
    edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Estado": st.column_config.SelectboxColumn(
        "Estado",
        options=["Pendiente", "Verificada", "Rechazada"]
        ),
        "Comisión": st.column_config.SelectboxColumn(
        "Comisión",
        options=["Pendiente", "Pagada"]
        ),
        "Check Real": st.column_config.CheckboxColumn(
        "Check Real"
        ),
    },
    disabled=["ID", "ID Mico"]  # no editar claves
    )

    # 3️⃣ Botón guardar
    if st.button("Guardar cambios emisores"):
        for _, row in edited_df.iterrows():
            emitter = db.query(Emitter).filter(Emitter.id == row["ID"]).first()
            if emitter:
                emitter.nombre = row["Nombre"]
                emitter.estado_cuenta = row["Estado"]
                emitter.estado_comision = row["Comisión"]
                emitter.check_real = row["Check Real"]

        db.commit()
        st.success("Cambios guardados correctamente")
        st.rerun()
        #    with col2:
        #        render_ranking()