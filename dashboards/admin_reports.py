# dashboards/admin_reports.py

import streamlit as st
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from models.schema import Emitter, User
from datetime import datetime, date
import pandas as pd

import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def render_admin_reports(db):

    st.title("📊 Reporte General de Emisores")
    st.markdown("---")

    # =====================================================
    # 🔎 FILTROS
    # =====================================================

    st.subheader("Filtros")

    col1, col2, col3 = st.columns(3)

    # Obtener reclutadores
    #recruiters = db.query(User).filter(User.role == "user").all()
    recruiters = db.query(User).all()
    recruiter_options = {f"{r.username} (ID {r.mico_id})": r.mico_id for r in recruiters}
    recruiter_options["Todos"] = None

    selected_recruiter_label = col1.selectbox(
        "Reclutador",
        list(recruiter_options.keys())
    )

    selected_recruiter_id = recruiter_options[selected_recruiter_label]

    estado_cuenta = col2.selectbox(
        "Estado de Cuenta",
        ["Todos", "Pendiente", "Verificada", "Rechazada", "Cancelada"]
    )

    estado_comision = col3.selectbox(
        "Estado de Comisión",
        ["Todos", "Pendiente", "Pagada"]
    )

    col4, col5 = st.columns(2)

    fecha_inicio = col4.date_input("Fecha Desde", value=None)
    fecha_fin = col5.date_input("Fecha Hasta", value=None)

    real_filter = st.selectbox(
        "Cuentas Reales",
        ["Todas", "Solo Reales", "Solo No Reales"]
    )

    st.markdown("---")

    # =====================================================
    # 📦 CONSTRUIR QUERY DINÁMICA
    # =====================================================

    query = db.query(Emitter).options(joinedload(Emitter.reclutador))

    filtros = []

    if selected_recruiter_id:
        filtros.append(Emitter.reclutador_id == selected_recruiter_id)

    if estado_cuenta != "Todos":
        filtros.append(Emitter.estado_cuenta == estado_cuenta)

    if estado_comision != "Todos":
        filtros.append(Emitter.estado_comision == estado_comision)

    if fecha_inicio:
        filtros.append(Emitter.fecha_registro >= fecha_inicio)

    if fecha_fin:
        filtros.append(Emitter.fecha_registro <= fecha_fin)

    if real_filter == "Solo Reales":
        filtros.append(Emitter.check_real == True)

    if real_filter == "Solo No Reales":
        filtros.append(Emitter.check_real == False)

    if filtros:
        query = query.filter(and_(*filtros))

    emitters = query.all()

    # =====================================================
    # 📈 MÉTRICAS
    # =====================================================

    total_emitters = len(emitters)
    verificadas = len([e for e in emitters if e.estado_cuenta == "Verificada"])
    pagadas = len([e for e in emitters if e.estado_comision == "Pagada"])
    reales = len([e for e in emitters if e.check_real])
    
    total_comisiones = sum(
        e.monto_comision if e.monto_comision else 0
        for e in emitters
    )

    st.markdown("---")

    # =====================================================
    # 📋 TABLA DE RESULTADOS
    # =====================================================

    if not emitters:
        st.warning("No se encontraron registros con esos filtros.")
        return

    # ================================
    # 1️⃣ Convertimos a DataFrame
    # ================================
    data = []

    for e in emitters:
        data.append({
            "ID": e.id,
            "Nombre": e.nombre,
            "Mico ID": e.mico_id,
            "Teléfono": e.telefono,
            "Reclutador": e.reclutador.username if e.reclutador else None,
            "Reclutador ID": e.reclutador_id,
            "Estado Cuenta": e.estado_cuenta,
            "Fecha Verificación":e.fecha_verificacion,
            "Estado Comisión": e.estado_comision,
            "monto_comision":e.monto_comision,
            "Real": e.check_real,
            "Fecha Registro": e.fecha_registro,
            "Método Pago": e.metodo_pago,
            "Pago ID": e.pago_id
        })

    df = pd.DataFrame(data)
    
    # 🔹 Convertir columnas datetime a solo fecha
    if "Fecha Verificación" in df.columns:
        df["Fecha Verificación"] = pd.to_datetime(
            df["Fecha Verificación"], errors="coerce"
        ).dt.date

    if "Fecha Registro" in df.columns:
        df["Fecha Registro"] = pd.to_datetime(
            df["Fecha Registro"], errors="coerce"
        ).dt.date    

        # =====================================================
        # 🧾 HEADER EN UNA SOLA LÍNEA
        # =====================================================

        # Calcular métricas
        pendientes = len([e for e in emitters if e.estado_comision != "Pagada"])
        total_comisiones = sum(e.monto_comision or 0 for e in emitters)

        col_logo, col_title, col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns(
            [0.6, 2.5, 1, 1, 1, 1, 1.2]
        )

        # Logo
        with col_logo:
            st.image("assets/logo.jpeg", width=60)

        # Título
        with col_title:
            st.markdown(
                "<h1 style='color:#0A3D91; margin-bottom:0;'>COCO & FONO</h1>",
                unsafe_allow_html=True
            )

        # Totales (todos en la misma línea)
        col_t1.metric("Total", total_emitters)
        col_t2.metric("Verificadas", verificadas)
        col_t3.metric("Pagadas", pagadas)
        col_t4.metric("Pendientes", pendientes)
        col_t5.metric("Comisión $", f"{total_comisiones:,.2f}")

        st.markdown("---")
# ================================
    # 2️⃣ Editor Editable
    # ================================

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Estado Cuenta": st.column_config.SelectboxColumn(
                "Estado Cuenta",
                options=["Pendiente", "Verificada", "Rechazada"]
            ),
            "Estado Comisión": st.column_config.SelectboxColumn(
                "Estado Comisión",
                options=["Pendiente", "Calculada", "Pagada"]
            ),
            "Real": st.column_config.CheckboxColumn("Cuenta Real"),
        },
        disabled=[
            "ID",
            "Mico ID",
            "Reclutador",
#            "Reclutador ID",
            "Fecha Registro"
        ]
    )

    # ================================
    # 3️⃣ Guardar cambios
    # ================================

    if st.button("💾 Guardar Cambios"):
        
        for _, row in edited_df.iterrows():
            emitter = db.query(Emitter).filter(Emitter.id == row["ID"]).first()
            
            if emitter:
                emitter.nombre = row["Nombre"]
                emitter.telefono = row["Teléfono"]
                emitter.reclutador_id = row["Reclutador ID"]
                emitter.estado_cuenta = row["Estado Cuenta"]
                #emitter.fecha_verificacion = row["Fecha Verificación"]
                fecha = row["Fecha Verificación"]
                if fecha:
                    if isinstance(fecha, str):
                        fecha = date.today() #time.strptime(fecha, "%m/%d/%Y").date()
                    elif isinstance(fecha, pd.Timestamp):
                        fecha = fecha.date()

                    emitter.fecha_verificacion = fecha
                else:
                    emitter.fecha_verificacion = None
                emitter.estado_comision = row["Estado Comisión"]
                emitter.check_real = row["Real"]
                emitter.metodo_pago = row["Método Pago"]
                emitter.pago_id = row["Pago ID"]

        db.commit()
        st.success("Cambios guardados correctamente")
        st.rerun()

    st.success(f"{len(df)} registros encontrados.")
    
    

    # =====================================================
    # 📄 GENERAR PDF PROFESIONAL
    # =====================================================

    if st.button("📄 Generar PDF en Horizontal"):

        folder_path = "PDFs"
        os.makedirs(folder_path, exist_ok=True)

        file_name = f"Reporte_Emisores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(folder_path, file_name)

        doc = SimpleDocTemplate(
            file_path,
            pagesize=landscape(letter)
        )

        elements = []

        styles = getSampleStyleSheet()

        # 🔹 LOGO
        ...
        # 🔹 TÍTULO AZUL PERSONALIZADO
        ...
        # =====================================================
        # 🔹 LOGO + TÍTULO EN LA MISMA FILA
        # =====================================================

        logo_path = "assets/logo.jpeg"  # Ajusta ruta si es necesario

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name="TitleBlue",
            parent=styles["Heading1"],
            textColor=colors.blue,
            fontSize=26,
            spaceAfter=0
        )

        title = Paragraph("COCO & FONO<br/><font size=14>Reporte General de Emisores</font>", title_style)

        if os.path.exists(logo_path):
            logo = Image(logo_path, width=0.5 * inch, height=0.5 * inch)

            header_table = Table(
                [[logo, title]],
                colWidths=[0.7 * inch, 10 * inch]
            )

            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))

            elements.append(header_table)

        else:
            elements.append(title)

        elements.append(Spacer(1, 20))
        
        # =====================================================
        # 🔹 RESUMEN GENERAL
        # =====================================================

        summary_style = ParagraphStyle(
            name="SummaryStyle",
            parent=styles["Normal"],
            fontSize=11,
        )

        summary_data = [
            ["Total Emisores:", total_emitters],
            ["Cuentas Verificadas:", verificadas],
            ["Comisiones Pagadas:", pagadas],
            ["Cuentas Reales:", reales],
            ["Total Comisiones ($):", f"${total_comisiones:,.2f}"],
        ]

        summary_table = Table(summary_data, colWidths=[250, 150])

        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # =====================================================
        # 🔹 TABLA
        # =====================================================
        data_for_pdf = [df.columns.tolist()] + df.astype(str).values.tolist()

        table = Table(data_for_pdf, repeatRows=1)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))

        elements.append(table)

        doc.build(elements)

        st.success("PDF generado correctamente en carpeta PDFs")

        with open(file_path, "rb") as pdf_file:
            st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf_file,
                file_name=file_name,
                mime="application/pdf"
            )