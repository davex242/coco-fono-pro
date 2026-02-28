import streamlit as st
import os
from datetime import datetime, date
from services.emitter import create_emitter
from core.db import SessionLocal
from models.schema import User


def save_file(uploaded_file, mico_id):
    """
    Guarda archivo en assets/uploads/{mico_id}/
    Devuelve SOLO el nombre del archivo
    """
    if not uploaded_file:
        return None

    base_path = "assets/uploads"
    emitter_folder = os.path.join(base_path, str(mico_id))

    os.makedirs(emitter_folder, exist_ok=True)

    # 🔥 Limpia el nombre por seguridad
    filename = os.path.basename(uploaded_file.name)

    file_path = os.path.join(emitter_folder, filename)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 👇 CAMBIO IMPORTANTE
    return filename

def render_formulario(username, recruiter_id, role):
    db = SessionLocal()

    selected_recruiter = None
    recruiter_mico_id = None  # Mico ID real
    reclutador_nombre = None


    st.divider()
    st.subheader("Registro de Emisor")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        nombre = st.text_input("Nombre del emisor")
        mico_id = st.text_input("ID de Mico")
        metodo_pago = st.selectbox("Método de pago", ["Payoneer", "Binance", "Nequi"])

    with col2:
        pago_id = st.text_input("ID de pago")
        fecha_registro = st.date_input("Fecha de Registro", format="DD/MM/YYYY")
        telefono = st.text_input("Teléfono")

    with col3:
        # -----------------------------
        # RECLUTADOR
        # -----------------------------
        if role == "admin":
            # Admin puede seleccionar reclutador
            #reclutadores = db.query(User).filter(User.role == "user").all()
            reclutadores = db.query(User).all()

            recruiter_options = {
                f"{r.username} (ID {r.mico_id})": {
                    "id": r.id,
                    "mico_id": r.mico_id,
                    "username": r.username
                }
                for r in reclutadores
            }

            selected = st.selectbox(
                "Seleccionar Reclutador",
                options=list(recruiter_options.keys())
            )

            selected_recruiter = recruiter_options[selected]
            recruiter_mico_id = selected_recruiter["mico_id"]  # Mico ID real
            reclutador_nombre = selected_recruiter["username"]

        else:
            user_obj = db.query(User).filter(User.id == recruiter_id).first()

            recruiter_mico_id = user_obj.mico_id
            reclutador_nombre = user_obj.username

            st.text_input(
                "ID del reclutador",
                value=recruiter_mico_id,
                disabled=True
            )
        #reclutador_id = st.text_input(
        #    "ID del reclutador",
        #    value=str(id),
        #    disabled=True
        #)
        estado_cuenta = st.selectbox(
            "Estado de la cuenta",
            ["Pendiente", "Verificada", "Cancelada", "Rechazada"]
        )
        fecha_verificacion = st.date_input("Fecha Verificación", value=None, disabled=True)

    with col4:
        estado_comision = st.selectbox(
            "Estado de comisión",
            ["Pendiente", "Pagada"],
            disabled=True
        )
        check_real = st.checkbox("Es Real", value=False, disabled=True)

    st.markdown(
        "<hr style='border:2px solid #4CAF50; border-radius:5px;'>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    captura_pago = col1.file_uploader("Captura de pago", type=["png", "jpg", "jpeg"])
    captura_transmision = col2.file_uploader("Captura de transmisión", type=["png", "jpg", "jpeg"])
    captura_form = col3.file_uploader("Captura de formulario", type=["png", "jpg", "jpeg"])
    captura_chat = col4.file_uploader("Captura de chat WhatsApp", type=["png", "jpg", "jpeg"])


    
    st.divider()

    col_btn1, col_btn2 = st.columns(2)

    if col_btn1.button("Registrar Emisor", icon="💾"):

        if not nombre or not mico_id:
            st.error("Nombre y Mico ID son obligatorios")
            return

        # 🔥 Guardar archivos físicamente
        path_pago = save_file(captura_pago, mico_id)
        path_transmision = save_file(captura_transmision, mico_id)
        path_form = save_file(captura_form, mico_id)
        path_chat = save_file(captura_chat, mico_id)

        '''# -----------------------------
        # FECHA VERIFICACIÓN CONTROLADA
        # -----------------------------
        fecha_verificacion_final = None

        if estado_cuenta == "Verificada":
            if fecha_verificacion:
                fecha_verificacion_final = fecha_verificacion
            else:
                fecha_verificacion_final = date.today()'''
        # -----------------------------
        # FECHA VERIFICACIÓN AUTOMÁTICA
        # -----------------------------
        fecha_verificacion_final = None

        if estado_cuenta == "Verificada":
            fecha_verificacion_final = date.today()
            fecha_verificacion = fecha_verificacion_final

        emitter_data = {
            "nombre": nombre,
            "mico_id": mico_id,
            "metodo_pago": metodo_pago,
            "pago_id": pago_id,
            "fecha_registro": fecha_registro,
            "telefono": telefono,
            "reclutador_nombre":reclutador_nombre,
            "reclutador_id": int(recruiter_mico_id),
            "estado_cuenta": estado_cuenta,
            "fecha_verificacion": fecha_verificacion,
            "estado_comision": estado_comision,
            "check_real": check_real,
            "captura_form": path_form,
            "captura_pago": path_pago,
            "captura_transmision": path_transmision,
            "captura_chat": path_chat,
        }

        #create_emitter(db, emitter_data)

        #st.success(f"Emisor {nombre} registrado exitosamente")

        try:
            create_emitter(db, emitter_data)
            st.success("Emisor registrado")
        except ValueError as e:
            st.error(str(e))
        
        st.write(reclutador_nombre)
        st.write(recruiter_mico_id)
            
        #st.rerun()
