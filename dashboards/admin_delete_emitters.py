# dashboards/admin_delete_emitters.py
import os
import streamlit as st
from models.schema import Emitter

from services.emitter import (
    get_all_emitters,
    delete_emitters_by_mico_ids,
    delete_emitters_by_ids,
    get_emitters_by_mico_ids
)

def render_admin_delete_emitters(db):

    st.header("🗑 Eliminación de Emisores")

    tab1, tab2 = st.tabs([
        "📋 Selección Manual",
        "📥 Eliminación por Lista de Mico ID"
    ])

    # =====================================================
    # TAB 1 – TABLA CON CHECKBOX
    # =====================================================

    with tab1:

        emitters = get_all_emitters(db)

        if not emitters:
            st.info("No hay emisores registrados.")
            return

        st.subheader("Seleccionar cuentas a eliminar")

        selected_ids = []

        for emitter in emitters:

            col1, col2, col3, col4, col5, col6 = st.columns([1,2,1,1,1,1])

            with col1:
                check = st.checkbox(
                    "",
                    key=f"delete_{emitter.id}"
                )
                if check:
                    selected_ids.append(emitter.id)

            with col2:
                st.write(f"**{emitter.nombre}**")
                st.caption(f"Mico ID: {emitter.mico_id}")

            # Mostrar thumbnails si existen
            def show_thumb(filename, mico_id):

                filename = os.path.basename(filename)

                if not filename:
                    return

                # Normaliza separadores por si vienen mezclados
                filename = os.path.basename(filename)

                BASE_DIR = os.getcwd()

                full_path = os.path.join(
                    BASE_DIR,
                    "assets",
                    "uploads",
                    str(mico_id),
                    filename
                )

                if os.path.exists(full_path):
                    st.image(full_path, width=60)
                else:
                    st.caption("⚠️ Imagen no encontrada")
                    
            with col3:
                filename = os.path.basename(emitter.captura_form)
                show_thumb(emitter.captura_form, emitter.mico_id)

            with col4:
                show_thumb(emitter.captura_pago, emitter.mico_id)

            with col5:
                show_thumb(emitter.captura_transmision, emitter.mico_id)

            with col6:
                show_thumb(emitter.captura_chat, emitter.mico_id)

        st.divider()

        if selected_ids:
            if st.button("Eliminar seleccionados", type="primary", key="check_ids"):
                delete_emitters_by_ids(db, selected_ids)
                st.success("Cuentas eliminadas correctamente.")
                st.rerun()

    # =====================================================
    # TAB 2 – ELIMINACIÓN POR LISTA
    # =====================================================

    with tab2:

        st.subheader("Ingresar lista de Mico ID (uno por línea)")

        text_input = st.text_area("Lista de Mico ID")

        if "found_emitters" not in st.session_state:
            st.session_state.found_emitters = []

        if st.button("Buscar cuentas"):

            if not text_input.strip():
                st.warning("Debes ingresar al menos un Mico ID.")
                return

            mico_list = [
                x.strip() for x in text_input.splitlines() if x.strip()
            ]

            # 🔥 SOLO BUSCAR, NO ELIMINAR
            st.session_state.found_emitters = (
                db.query(Emitter)
                .filter(Emitter.mico_id.in_(mico_list))
                .all()
            )

            st.session_state.mico_list = mico_list

        found_emitters = st.session_state.found_emitters

        if found_emitters:

            found_micos = [e.mico_id for e in found_emitters]
            not_found = list(set(st.session_state.mico_list) - set(found_micos))

            st.subheader("Resumen")

            st.write(f"### ✅ Encontradas")
            st.write(found_micos if found_micos else "Ninguna")

            st.write(f"### ❌ No encontradas")
                       
            st.write(not_found if not_found else "Ninguna")
            
            if st.button("Confirmar eliminación", type="primary", key="list_btn"):

                ids_to_delete = [e.mico_id for e in found_emitters]
                Micos_del = delete_emitters_by_mico_ids(db, ids_to_delete)

                st.success("Cuentas eliminadas correctamente.")

                st.write(Micos_del)
                
                # 🔥 limpiar estado
                st.session_state.found_emitters = []

                if st.button("Aceptar"):
                    st.rerun()
