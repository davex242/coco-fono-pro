# dashboards/admin_users.py

import streamlit as st
from models.schema import User
from datetime import datetime


def render_admin_users(db):

    st.title("👥 Gestión de Usuarios")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📋 Lista de Usuarios", "➕ Crear Usuario"])

    # =====================================================
    # 📋 TAB 1 - LISTA + EDITAR + ELIMINAR
    # =====================================================
    with tab1:

        users = db.query(User).all()

        if not users:
            st.warning("No hay usuarios registrados.")
            return

        for user in users:

            with st.expander(f"👤 {user.username} (ID: {user.id})"):

                col1, col2 = st.columns(2)

                with col1:
                    new_username = st.text_input(
                        "Username",
                        value=user.username,
                        key=f"username_{user.id}"
                    )

                    new_password = st.text_input(
                        "Password",
                        value=user.password,
                        key=f"password_{user.id}"
                    )

                with col2:
                    new_role = st.selectbox(
                        "Rol",
                        ["admin", "user"],
                        index=0 if user.role == "admin" else 1,
                        key=f"role_{user.id}"
                    )
                    
                    new_mico_id = st.text_input("ID de MICO",
                        value=user.mico_id,
                        key=f"mico_{user.mico_id}"
                    )

                    new_active = st.checkbox(
                        "Activo",
                        value=user.is_active,
                        key=f"active_{user.id}"
                    )

                col_save, col_delete = st.columns(2)

                # 🔄 ACTUALIZAR
                if col_save.button("💾 Guardar Cambios", key=f"save_{user.id}"):

                    user.username = new_username
                    user.password = new_password
                    user.mico_id = new_mico_id
                    user.role = new_role
                    user.is_active = new_active

                    db.commit()

                    st.success("Usuario actualizado correctamente.")
                    st.rerun()

                # 🗑 ELIMINAR
                if col_delete.button("🗑 Eliminar Usuario", key=f"delete_{user.id}"):

                    db.delete(user)
                    db.commit()

                    st.success("Usuario eliminado.")
                    st.rerun()

    # =====================================================
    # ➕ TAB 2 - CREAR USUARIO
    # =====================================================
    with tab2:

        st.subheader("Crear Nuevo Usuario")

        username = st.text_input("Nuevo Username")
        password = st.text_input("Nuevo Password")
        mico_id = st.text_input("ID de MICO")
        role = st.selectbox("Rol", ["admin", "user"])
        is_active = st.checkbox("Activo", value=True)

        if st.button("➕ Crear Usuario"):

            if username == "" or password == "":
                st.error("Username y Password son obligatorios.")
                return

            # Verificar si ya existe
            existing_user = db.query(User).filter(User.username == username, User.mico_id == mico_id).first()

            if existing_user:
                st.error("Ese username ya existe.")
                return

            new_user = User(
                username=username,
                password=password,
                mico_id=mico_id,
                role=role,
                is_active=is_active,
                created_at=datetime.now()
            )

            db.add(new_user)
            db.commit()

            st.success("Usuario creado correctamente.")
            st.rerun()
