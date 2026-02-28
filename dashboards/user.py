import streamlit as st
from components.formulario import render_formulario
from core.db import SessionLocal
from services.analytics import get_user_metrics
from services.emitter import get_emitters_by_recruiter
from services.analytics import get_recruiter_ranking
from models.schema import Emitter

#------------

from core.db import SessionLocal
#------------

#user_info = st.session_state.user
#recruiter_id = st.session_state.reclutador_id


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
        col4.metric("Calificación 1 a 10", f"{r['score']}")

        st.divider()

def render_user(user, recruiter_id):
    user_info = st.session_state.get("user")

    if not user_info:
        st.warning("Sesión no iniciada")
        st.stop()
    
    st.title(f"Dashboard Usuario: {user}")
    st.subheader("Bienvenido, aquí puedes registrar tus emisores y ver tus métricas.")
    st.divider()
    db = SessionLocal()  # creamos la sesión de base de datos
    
    metrics = get_user_metrics(recruiter_id)
    def tarjeta_dato(titulo, valor, color="#4CAF50", txt_color="#4CAF50", bg_color="#4CAF50"):
        st.markdown(
            f"""
            <div style="
                background-color:{bg_color};
                padding:10px;
                border-radius:20px;
                text-align:center;
                box-shadow:0px 4px 10px rgba(0,0,0,0.3);
            ">
                <h4 style="color:{txt_color}; margin-bottom:10px;">{titulo}</h4>
                <h2 style="color:{color}; margin:10;">{valor}</h2>
            </div>
            """,
            unsafe_allow_html=True
    )
    
    col1, col2, col3, col4 = st.columns(4)
    st.subheader(f"**Resumen de métricas para ID {recruiter_id}**", text_alignment="center")
    with col1:
            tarjeta_dato("Cuentas registradas",metrics['total_registradas'], "#1436CA", "#13A4CD", "#DAE6EA")
    #st.write(f"Cuentas registradas: {metrics['total_registradas']}")
    with col2:
            tarjeta_dato("Cuentas verificadas",metrics['verificadas'], "#4CAF50", "#6BE832", "#E8EA63")
    #st.write(f"Cuentas verificadas: {metrics['verificadas']}")
    with col3:
            tarjeta_dato("Cuentas pendientes",metrics['pendientes'], "#C59226", "#A37B0B", "#3FCBCB")
    #st.write(f"Cuentas pendientes: {metrics['pendientes']}")
    with col4:
            tarjeta_dato("Comisiones pendientes",metrics['comisiones_pendientes'], "#FFFFFF", "#FFFFFF", "#D9B91B")
    #st.write(f"Comisiones pendientes: {metrics['comisiones_pendientes']}")
    with col1:
            tarjeta_dato("Comisiones pagadas",metrics['comisiones_pagadas'], "#D8E42E", "#13A4CD", "#0C1214")
    #st.write(f"Comisiones pagadas: {metrics['comisiones_pagadas']}")
    with col2:
            tarjeta_dato("Total pagado", f"$ {metrics['total_pagado']}", "#4CAF50", "#13A4CD", "#DAE6EA")
    #st.write(f"Total pagado: ${metrics['total_pagado']}")
    with col3:
            tarjeta_dato("Total pendiente",f"$ {metrics['total_pendiente']}", "#4CAF50", "#13A4CD", "#E6BD29")
    #st.write(f"Total pendiente: ${metrics['total_pendiente']}")
    with col4:
            tarjeta_dato("Cuentas Reales",metrics['cuentas_reales'], "#FFFFFF", "#FFFFFF", "#2400F0")

    st.markdown(
    """
    <hr style="border: 2px solid #4CAF50; border-radius:5px;">
    """,
    unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)
#-----------------------------------
# DATA FRAME
#-----------------------------------
    with col1:

        st.subheader("Lista completa de emisores")

        # -------------------------
        # FILTROS
        # -------------------------
        st.divider()
        st.markdown("### 🔎 Filtros")
        colf1, colf2, colf3 = st.columns(3)

        with colf1:
            filtro_estado = st.selectbox(
                "Estado de Cuenta",
                ["Todos", "Verificada", "Pendiente"]
            )

        with colf2:
            filtro_comision = st.selectbox(
                "Estado Comisión",
                ["Todos", "Pagada", "Pendiente"]
            )

        with colf3:
            filtro_real = st.selectbox(
                "Check Real",
                ["Todos", "Solo Reales", "No Reales"]
            )

        if st.button("🔃 Refrescar"):
            st.rerun()

        # -------------------------
        # QUERY BASE
        # -------------------------
        query = db.query(Emitter).filter(
            Emitter.reclutador_id == recruiter_id
        )

        # -------------------------
        # APLICAR FILTROS
        # -------------------------
        if filtro_estado != "Todos":
            query = query.filter(Emitter.estado_cuenta == filtro_estado)

        if filtro_comision != "Todos":
            query = query.filter(Emitter.estado_comision == filtro_comision)

        if filtro_real == "Solo Reales":
            query = query.filter(Emitter.check_real == True)

        elif filtro_real == "No Reales":
            query = query.filter(Emitter.check_real == False)

        emitters = query.all()

        # -------------------------
        # DATAFRAME
        # -------------------------
        st.dataframe(
            [{
                "Nombre": e.nombre,
                "ID Mico": e.mico_id,
                "Estado": e.estado_cuenta,
                "Comisión": e.estado_comision,
                "Check Real": e.check_real
            } for e in emitters],
            use_container_width=True,
            height=400
        )    

    with col2:
        render_ranking()
    
    nuevo_registro = st.toggle(label="Ingresar nuevo emisor")
    if nuevo_registro:
        render_formulario(
            username=user_info["username"],
            recruiter_id=st.session_state.reclutador_id,
            role=user_info["role"]
        )
    # Aquí luego podemos agregar métricas específicas del usuario