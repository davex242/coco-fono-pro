# dashboards/admin_verification.py

import streamlit as st
import os
import csv
from datetime import datetime, date
from sqlalchemy.orm import joinedload
from models.schema import Emitter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
import streamlit.components.v1 as components



EXPORT_PATH = "exports/verificaciones"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "assets", "uploads")

def get_image_path(mico_id, filename):
    if not filename:
        return None

    # Si en BD viene solo nombre de archivo
    clean_name = os.path.basename(filename)

    full_path = os.path.join(UPLOAD_FOLDER, str(mico_id), clean_name)

    if os.path.exists(full_path):
        return full_path

    return None

def ensure_export_folder():
    os.makedirs(EXPORT_PATH, exist_ok=True)


def export_csv(summary):
    ensure_export_folder()
    filename = f"{EXPORT_PATH}/verificacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Tipo", "ID"])

        for i in summary["verificados"]:
            writer.writerow(["Verificados", i])

        for i in summary["ya_verificados"]:
            writer.writerow(["Ya Verificados", i])

        for i in summary["no_encontrados"]:
            writer.writerow(["No Encontrados", i])

    return filename


def export_pdf(summary):
    ensure_export_folder()
    filename = f"{EXPORT_PATH}/verificacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(filename)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Resumen de Verificación", styles["Heading1"]))
    elements.append(Spacer(1, 0.5 * inch))

    for title, key in [
        ("Cuentas Verificadas", "verificados"),
        ("Cuentas Ya Verificadas", "ya_verificados"),
        ("IDs No Encontrados", "no_encontrados"),
    ]:
        elements.append(Paragraph(title, styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))

        items = [ListItem(Paragraph(str(i), styles["Normal"])) for i in summary[key]]
        elements.append(ListFlowable(items, bulletType="bullet"))
        elements.append(Spacer(1, 0.5 * inch))

    doc.build(elements)

    return filename


def render_admin_verification(db):

    st.title("✅ Verificación de Cuentas")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["Verificación Manual", "Verificación Masiva", "Cuentas Reales", "Emitters No Verificados"])

    # =========================================================
    # TAB 1 - VERIFICACION MANUAL
    # =========================================================

    with tab1:

        st.subheader("Cuentas Pendientes")

        pendientes = (
            db.query(Emitter)
            .filter(Emitter.estado_cuenta == "Pendiente")
            .all()
        )

        if not pendientes:
            st.success("No hay cuentas pendientes.")
        else:
            for emitter in pendientes:

                with st.expander(f"MICO ID {emitter.mico_id} - {emitter.nombre}"):

                    col1, col2 = st.columns(2)

                    check_real = col1.checkbox(
                        "Cuenta Real",
                        value=emitter.check_real,
                        key=f"real_{emitter.id}"
                    )

                    estado = col2.selectbox(
                        "Estado Cuenta",
                        ["Pendiente", "Verificada", "Rechazada"],
                        index=["Pendiente", "Verificada", "Rechazada"].index(emitter.estado_cuenta),
                        key=f"estado_{emitter.id}"
                    )

                    if st.button("Guardar Cambios", key=f"save_{emitter.id}"):

                        #emitter.check_real = check_real
                        emitter.estado_cuenta = estado

                        if estado == "verificada":
                            emitter.fecha_verificacion = date.today()

                        db.commit()
                        st.success("Actualizado correctamente")
                        st.rerun()

    # =========================================================
    # TAB 2 - VERIFICACION MASIVA
    # =========================================================

    with tab2:

        st.subheader("Verificación Masiva por IDs")

        ids_input = st.text_area(
            "Pega aquí los IDs (separados por coma o salto de línea)"
        )

        if st.button("Verificar IDs"):

            raw_ids = ids_input.replace(",", "\n").split("\n")
            ids = [i.strip() for i in raw_ids if i.strip()]

            summary = {
                "verificados": [],
                "ya_verificados": [],
                "no_encontrados": []
            }

            for mico in ids:

                emitter = db.query(Emitter).filter(Emitter.mico_id == mico).first()

                if not emitter:
                    summary["no_encontrados"].append(mico)

                elif emitter.estado_cuenta == "Verificada":
                    summary["ya_verificados"].append(mico)

                else:
                    emitter.estado_cuenta = "Verificada"
                    #emitter.check_real = True
                    emitter.fecha_verificacion = date.today()
                    summary["verificados"].append(mico)

            db.commit()

            st.markdown("---")
            st.subheader("Resumen")

            st.write("### ✅ Verificados")
            st.write(summary["verificados"])

            st.write("### ⚠️ Ya Verificados")
            st.write(summary["ya_verificados"])

            st.write("### ❌ No Encontrados")
            st.write(summary["no_encontrados"])


            # EXPORTACIONES
            col1, col2 = st.columns(2)

            if col1.button("Exportar CSV"):
                file_csv = export_csv(summary)
                st.success(f"CSV generado: {file_csv}")

            if col2.button("Exportar PDF"):
                file_pdf = export_pdf(summary)
                st.success(f"PDF generado: {file_pdf}")

    # =========================================================
    # TAB 2 - VERIFICACION MASIVA
    # =========================================================
                
    with tab3:

        st.subheader("Gestión de Cuentas Reales")

        emitters = db.query(Emitter).filter(Emitter.check_real == False)

        for emitter in emitters:

            with st.expander(f"MICO ID {emitter.mico_id} - {emitter.nombre}"):

                col1, col2 = st.columns([1,1])

                # ----- Información básica -----
                col1.write(f"Reclutador ID: {emitter.reclutador_id}")
                col1.write(f"Estado Cuenta: {emitter.estado_cuenta}")
                col1.write(f"Fecha Registro: {emitter.fecha_registro}")

                # ----- Checkbox editable -----
                new_check = col2.checkbox(
                    "Cuenta Real",
                    value=emitter.check_real,
                    key=f"check_real_{emitter.id}"
                )

                if new_check != emitter.check_real:
                    emitter.check_real = new_check
                    db.commit()
                    st.success("Actualizado")

                st.markdown("---")

                # ----- Capturas -----
                st.write("### Capturas")
                
                img_cols = st.columns(4)
                
                #--------------------------------
                form_path = get_image_path(emitter.mico_id, emitter.captura_form)
                pago_path = get_image_path(emitter.mico_id, emitter.captura_pago)
                trans_path = get_image_path(emitter.mico_id, emitter.captura_transmision)
                chat_path = get_image_path(emitter.mico_id, emitter.captura_chat)
                
                if form_path:
                    img_cols[0].image(form_path, caption="Formulario", width=150)
                else:
                    img_cols[0].warning("No encontrado")

                if pago_path:
                    img_cols[1].image(pago_path, caption="Pago", width=150)
                else:
                    img_cols[1].warning("No encontrado")

                if trans_path:
                    img_cols[2].image(trans_path, caption="Transmisión", width=150)
                else:
                    img_cols[2].warning("No encontrado")

                if chat_path:
                    img_cols[3].image(chat_path, caption="Chat", width=150)
                else:
                    img_cols[3].warning("No encontrado")
                #--------------------------------

    # =========================================================
    # TAB 4 - EMITORES NO VERIFICADOS
    # =========================================================
    with tab4: #st.tab("Emitters No Verificados"):

        st.subheader("Lista de Emisores No Verificados")

        # Traer todos los emisores cuyo estado de cuenta NO sea "Verificada"
        no_verificados = db.query(Emitter).filter(Emitter.estado_cuenta != "Verificada").all()

        if not no_verificados:
            st.success("Todos los emisores están verificados ✅")
        else:
            # Generar lista de MICO IDs
            mico_ids = [e.mico_id for e in no_verificados]
            lista_texto = "\n".join(mico_ids)

            st.text_area(
                "MICO IDs (para verificación masiva)",
                value=lista_texto,
                height=200
            )

            # Botón para copiar al portapapeles usando HTML/JS
            components.html(f"""
                <button onclick="navigator.clipboard.writeText(`{lista_texto}`)">
                    📋 Copiar al portapapeles
                </button>
                <script>
                    // Optional: feedback cuando se copia
                    const btn = document.querySelector("button");
                    btn.addEventListener("click", () => {{
                        btn.innerText = "✅ Copiado";
                        setTimeout(() => {{ btn.innerText = "📋 Copiar al portapapeles"; }}, 1500);
                    }});
                </script>
            """, height=50)

            # Mostrar cantidad
            st.info(f"Total de emisores no verificados: {len(no_verificados)}")