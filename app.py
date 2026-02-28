# app.py
import streamlit as st
#Configurar Pagina
st.set_page_config(
    page_title="COCO&FONO", 
    layout="wide", 
    page_icon="🔥"
)

from styles import load_styles

#
from dashboards.admin_verification import render_admin_verification
#from dashboards.admin_dashboard import render_admin_dashboard
from dashboards.admin_users import render_admin_users
from dashboards.admin_reports import render_admin_reports
from components.formulario import render_formulario
from services.analytics import render_real_pending_panel
from dashboards.admin_delete_emitters import render_admin_delete_emitters
from dashboards.admin_commissions import render_admin_commissions
from services.commission_initializer import initialize_commission_system
import streamlit.components.v1 as components



#from dashboards.user_dashboard import render_user_dashboard
#from dashboards.admin_emitters import render_create_emitter
#

from core.db import Base, engine, SessionLocal
from models.schema import User
from services.auth import login_user
from dashboards.admin import render_admin
from dashboards.user import render_user
from dashboards.user import render_ranking

if "user" not in st.session_state:
    st.session_state.user = None

if "reclutador_id" not in st.session_state:
    st.session_state.reclutador_id = None

if "reclutador_mico_id" not in st.session_state:
    st.session_state.reclutador_mico_id = None

db = SessionLocal()

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

initialize_commission_system()

#----------------------------------------------------
# Estado de sesión
#----------------------------------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if "reclutador_id" not in st.session_state:
    st.session_state.reclutador_id = None
    
if "reclutador_mico_id" not in st.session_state:
    st.session_state.reclutador_mico_id = None

#----------------------------------------------------
# Emcabezado
#----------------------------------------------------

col1, col2 = st.columns([0.7,0.3])

#col1.title(f":blue[COCO&FONO]") #muy pequeño
col1.markdown(
    "<h1 style='font-size:110px;color:blue;'>COCO&FONO</h1>",
    unsafe_allow_html=True
)

col1.markdown(
    "<h1 style='font-size:70px;'>Panel de Administración</h1>",
    unsafe_allow_html=True
)
#col1.title(f"Panel de Administración", width=730)

#---------------------------------
# SPOTIFY
#---------------------------------
import streamlit.components.v1 as components

st.markdown("---")
st.subheader("🎵 Música")

# Playlists base (puedes agregar más)
playlists = {
    "Baila Reggaeton 🔥": "37i9dQZF1DWY7IeIP1cdjF",
    "Reggaeton Classics 👑": "37i9dQZF1DX8SfyqmSFDwe",
    "Reggaeton Mix 💃": "37i9dQZF1EIhSxvE5Wz9xS",
    "Reggaeton Viejo 🕶️": "37i9dQZF1DX4qKWGR9z0LI",
    "Perreo Intenso 🥵": "37i9dQZF1DX0BcQWzuB7ZO",
    "Flow Callejero 🚘": "37i9dQZF1DX2apWzyECwyZ",
    "Reggaeton 2010s 📀": "37i9dQZF1DX8CwbNGNKurt",
    "Reggaeton 2020 🔊": "37i9dQZF1DX7fvUMiyfOF3",
    "Perreo 2000s 📟": "37i9dQZF1DX8tZsk68tuDw",
    "Latin Hits 🔥": "37i9dQZF1DX10zKzsJ2jva",
}

search = st.text_input("Buscar playlist por palabra clave")

filtered = {
    name: pid for name, pid in playlists.items()
    if search.lower() in name.lower()
} if search else playlists

selected_playlist = st.selectbox(
    "Seleccionar playlist",
    list(filtered.keys())
)

if selected_playlist:
    playlist_id = filtered[selected_playlist]

    components.iframe(
        f"https://open.spotify.com/embed/playlist/{playlist_id}",
        height=380
    )
#----------------------------------------------------
# Inicializar sesión
#----------------------------------------------------

if st.session_state.user is None:
    
    st.subheader("🔐 Login")
    
    username = st.text_input("Usuario")
    #rec_id = user.id  #st.text_input("Digita tu ID de mico:")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        user = login_user(username, password)
        
        st.write(user)
        
        if user:
            st.session_state.user = {
                "username": user.username, 
                "role": user.role,
                "user_id": user.id,          # 🔥 ID interno
                "mico_id": user.mico_id      # 🔥 Mico real
            }
            
            st.success(f"Bienvenido {user.username} ({user.role})")
            
            st.session_state.reclutador_id = user.id  # 🔥 guardamos ID
            st.session_state.reclutador_mico_id = user.mico_id
            st.experimental_rerun = None  # NO hacer nada, Streamlit recarga automáticamente
            #st.write("DEBUG:", user.mico_id)
        
        else:
            
            st.error("Usuario o contraseña incorrectos")
    #st.write("DEBUG:", user.mico_id)
    
#----------------------------------------------------
# Dashboard
#----------------------------------------------------

else:
    
    user_info = st.session_state.user
    
    col2.subheader(f":green[Sesión iniciada como:] {user_info['username']}")
    col2.subheader(f"Rol: {user_info['role']}", text_alignment="left")
    col2.image(r"assets\logo.jpeg", width=250)
    #col2.header(f"Mico ID - {user_info['mico_id']}")
    st.markdown("---")

#----------------------------------------------------
# Admin View
#----------------------------------------------------
    
    if user_info["role"] == "admin":

#----------------------------------------------------
# Side Bar Solo Admin
#----------------------------------------------------
                
        #st.header("Dashboard Admin")
        #st.write("Aquí irán los módulos de administración y métricas generales.")
        #st.write("Por ejemplo: lista de emisores, comisiones, reportes.")
        with st.sidebar:
            
            st.title("⚙️ Admin Panel")

            menu = st.radio(
                "Navegación",
                [
                    "Dashboard General",
                    "Usuarios",
                    "Reportes",
                    "Verificación de Cuentas",
                    "Panel de Comisiones",
                    "Nuevo Emisor",
                    "Eliminar Cuentas"
                ]
            )            

        #----------------------------------------------------
        # Tabs dentro de cada Modulo
        #----------------------------------------------------
        if menu == "Dashboard General":
            
            #---------------------------------------
            # Resumen Comisiones pendientes
            #---------------------------------------
            render_real_pending_panel(db)
            #---------------------------------------
            
            tab1, tab2, tab3 = st.tabs([
                
                "📊 Métricas", 
                "🏆 Ranking",
                "⚙️ Configuracioó"
            ])

            with tab1:
            
                render_admin(user_info['username'])
            
            with tab2:
            
                #render_admin_reports()
                render_ranking()
            
            with tab3:
                
                #Futuras opciones
                st.subheader("Configuraciones")
                st.write("Opciones futuras del sistema")

        elif menu == "Usuarios":
            render_admin_users(db)

        elif menu == "Reportes":
            render_admin_reports(db)
            
        elif menu == "Verificación de Cuentas":
            render_admin_verification(db)
        
        elif menu == "Nuevo Emisor":
            render_formulario(
                username=user_info["username"],
                recruiter_id=st.session_state.reclutador_id,
                role=user_info["role"]
            )
        elif menu == "Eliminar Cuentas":
            render_admin_delete_emitters(db)
        elif menu == "Panel de Comisiones":
            render_admin_commissions(db)
#        elif menu == "Nuevo Emisor":
#            render_formulario(user_info["username"],
#                st.session_state.reclutador_id
#            )
            
#----------------------------------------------------
# Users View
#----------------------------------------------------
       
        
        #render_admin(user_info['username'])

    else:
        #st.write("DEBUG:", user_info['mico_id'])
        if st.session_state.reclutador_mico_id:
            col2.header(f"Mico ID - {user_info['mico_id']}")        
        render_user(user_info['username'], user_info['mico_id'])
        
        #render_ranking()
        #st.write("Aquí irán los módulos visibles para un usuario normal.")
        #st.write("Por ejemplo: sus propios emisores y métricas personales.")

#----------------------------------------------------
# Cerrar Session
#----------------------------------------------------

    col1, col2 = st.columns([0.9,0.1])
    
    if col2.button("Cerrar sesión", key="btn_cerrar"):
        
        st.session_state.user = None
        st.session_state.reclutador_id = None
        
