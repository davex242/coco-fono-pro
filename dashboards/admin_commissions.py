import streamlit as st
from datetime import datetime, date
from models.schema import Emitter, CommissionRule, CommissionHistory
import matplotlib.pyplot as plt
import pandas as pd
from services.commission_engine import registrar_historial_comision

def render_admin_commissions(db):

    st.title("💰 Panel de Comisiones PRO+")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["⚙️ Motor", "🧮 Simulación", "📋 Detalle", "📊 Historial"]
    )

    # =====================================================
    # TAB 1 - MOTOR
    # =====================================================
    with tab1:

        st.subheader("Configuración del Motor")

        rule = db.query(CommissionRule).first()

        if not rule:
            st.error("No existe configuración en CommissionRule")
            return

        col1, col2 = st.columns(2)

        with col1:
            rule.monto_base = st.number_input(
                "Monto base por cuenta",
                value=float(rule.monto_base),
                step=1.0
            )

            rule.bonus_real = st.number_input(
                "Bonus por cuenta real",
                value=float(rule.bonus_real),
                step=1.0
            )

        with col2:
            rule.meta_minima = st.number_input(
                "Meta mínima",
                value=int(rule.meta_minima),
                step=1
            )

            rule.multiplicador = st.number_input(
                "Multiplicador",
                value=float(rule.multiplicador),
                step=0.1
            )

        if st.button("💾 Guardar Configuración"):
            db.commit()
            st.success("Configuración actualizada")
            st.rerun()

    # =====================================================
    # TAB 2 - SIMULACIÓN
    # =====================================================
    with tab2:

        st.subheader("Simulación de Comisión")

        rule = db.query(CommissionRule).first()
        if not rule:
            st.error("No existe configuración en CommissionRule")
            return

        # ---------------------------
        # Filtros
        # ---------------------------
        ver_todos_reclutadores = st.checkbox("📌 Ver todos los reclutadores", value=False)
        ignorar_fechas = st.checkbox("📌 Ignorar rango de fechas", value=False)

        recruiters = db.query(Emitter.reclutador_id).filter(Emitter.estado_comision != "Pagada").distinct().all()
        recruiter_ids = [r[0] for r in recruiters]

        selected = None
        if not ver_todos_reclutadores:
            selected = st.selectbox("Seleccionar Reclutador", recruiter_ids)

        fecha_inicio, fecha_fin = (None, None)
        if not ignorar_fechas:
            fecha_inicio, fecha_fin = st.date_input(
                "Rango de fechas",
                value=(datetime.now().replace(day=1), datetime.now())
            )

        # ---------------------------
        # Filtrar emisores verificados según filtros
        # ---------------------------
        query = db.query(Emitter).filter(
            Emitter.estado_cuenta == "Verificada",
            Emitter.check_real == True,
            Emitter.estado_comision != "Pagada"
        )

        if not ver_todos_reclutadores:
            query = query.filter(Emitter.reclutador_id == selected)

        if not ignorar_fechas:
            query = query.filter(
                Emitter.fecha_verificacion >= fecha_inicio,
                Emitter.fecha_verificacion <= fecha_fin
            )
        cuentas = query.all()

        total_cuentas = len(cuentas)
        cuentas_reales = len([c for c in cuentas if c.check_real])

        base_total = total_cuentas * rule.monto_base
        bonus_total = cuentas_reales * rule.bonus_real
        multiplicador_aplicado = rule.multiplicador if total_cuentas >= rule.meta_minima else 1
        subtotal = base_total + bonus_total
        total_final = subtotal * multiplicador_aplicado

        st.markdown("### 📊 Cómo se calculó")
        #st.write(f"Total cuentas verificadas: {total_cuentas}")
        st.write(f"Cuentas reales: {cuentas_reales}")
        st.write(f"Base = {total_cuentas} × {rule.monto_base}")
        st.write(f"Bonus = {cuentas_reales} × {rule.bonus_real}")
        st.write(f"Multiplicador aplicado: {multiplicador_aplicado}")
        st.markdown("---")
        st.success(f"💰 Total Comisión: ${total_final}")

        # ---------------------------
        # Botón Cerrar Comisión Global
        # ---------------------------
        cerrar_disabled = ver_todos_reclutadores

        if cerrar_disabled:
            st.warning("⚠️ Para cerrar comisión debes seleccionar un reclutador específico.")

        if st.button("🔒 Cerrar Comisión", disabled=cerrar_disabled):
            # Aplicar mismos filtros para emisores pendientes
            query = db.query(Emitter).filter(
                Emitter.estado_cuenta == "Verificada",
                Emitter.estado_comision != "Pagada"
            )
            if not ver_todos_reclutadores:
                query = query.filter(Emitter.reclutador_id == selected)
            if not ignorar_fechas:
                query = query.filter(
                    Emitter.fecha_verificacion >= fecha_inicio,
                    Emitter.fecha_verificacion <= fecha_fin
                )
            emisores_cierre = query.all()
            if not emisores_cierre:
                st.warning("No hay comisiones pendientes para cerrar")
                return

            if any(e.reclutador_id != selected for e in emisores_cierre):
                st.error("⚠️ Error: Se detectaron emisores de otro reclutador.")
                return
            total_cierre = 0
            cuentas_reales_cierre = 0

            for e in emisores_cierre:
                base = rule.monto_base
                bonus = rule.bonus_real if e.check_real else 0
                monto = base + bonus

                if len(emisores_cierre) >= rule.meta_minima:
                    monto *= rule.multiplicador

                total_cierre += monto

                if e.check_real:
                    cuentas_reales_cierre += 1

            if not emisores_cierre:
                st.warning("No hay comisiones pendientes para cerrar")
            else:
                history = CommissionHistory(
                    recruiter_id=selected,
                    total_cuentas=len(emisores_cierre),
                    cuentas_reales=cuentas_reales_cierre,
                    monto_base=rule.monto_base,
                    bonus_real=rule.bonus_real,
                    multiplicador=rule.multiplicador,
                    total_pagado=total_cierre,
                    fecha=datetime.now(),
                    pagado=False
                )
                db.add(history)

                for e in emisores_cierre:

                    base = rule.monto_base
                    bonus = rule.bonus_real if e.check_real else 0

                    monto = base + bonus

                    if len(emisores_cierre) >= rule.meta_minima:
                        monto *= rule.multiplicador

                    e.monto_comision = monto
                    e.estado_comision = "Pagada"
                    e.fecha_pago_comision = date.today()

                db.commit()
                st.success("Comisión cerrada y guardada ✅")
                registrar_historial_comision(db, emisores_cierre, tipo="global")

        # ---------------------------
        # Cuentas pendientes en modo edición
        # ---------------------------
        st.divider()
        st.subheader("💰 Cuentas Pendientes de Pago de Comisión")

        query = db.query(Emitter).filter(Emitter.estado_comision != "Pagada", Emitter.check_real != False)
        if not ver_todos_reclutadores:
            query = query.filter(Emitter.reclutador_id == selected)
        if not ignorar_fechas:
            query = query.filter(
                Emitter.fecha_verificacion >= fecha_inicio,
                Emitter.fecha_verificacion <= fecha_fin
            )
        pending_emitters = query.all()

        if not pending_emitters:
            st.success("No hay comisiones pendientes 🎉")
        else:
            data = []
            for e in pending_emitters:
                data.append({
                    "ID": e.id,
                    "Nombre": e.nombre,
                    "Mico ID": e.mico_id,
                    "Estado Comisión": e.estado_comision,
                    "Monto Comisión": e.monto_comision if hasattr(e, "monto_comision") else 0,
                    "Fecha Verificación": e.fecha_verificacion,
                    "Marcar Pagada": False,
                    "check_real":e.check_real,
                    "monto_comision":e.monto_comision
                })

            df = pd.DataFrame(data)
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "ID": st.column_config.NumberColumn(disabled=True),
                    "Nombre": st.column_config.TextColumn(disabled=True),
                    "Mico ID": st.column_config.TextColumn(disabled=True),
                    "Monto Comisión": st.column_config.NumberColumn(disabled=True),
                    "Estado Comisión": st.column_config.SelectboxColumn(
                        options=["Pendiente", "Aprobada", "Pagada"]
                    ),
                    "Fecha Verificación": st.column_config.DateColumn(format="DD/MM/YYYY"),
                    "Marcar Pagada": st.column_config.CheckboxColumn()
                }
            )

            if st.button("💾 Guardar Cambios"):
                emisores_para_historial = []
                for _, row in edited_df.iterrows():
                    emitter = db.query(Emitter).get(int(row["ID"]))
                    if emitter:
                        emitter.estado_comision = row["Estado Comisión"]
                        emitter.fecha_verificacion = row["Fecha Verificación"] if row["Fecha Verificación"] else None

                        if row["Marcar Pagada"]:
                            emitter.estado_comision = "Pagada"
                            emitter.fecha_pago_comision = date.today()
                            #--------------------------
                            base = rule.monto_base
                            bonus = rule.bonus_real if emitter.check_real else 0
                            monto = base + bonus

                            if len(emisores_para_historial) >= rule.meta_minima:
                                monto *= rule.multiplicador

                            emitter.monto_comision = monto
                            #--------------------------
                            emisores_para_historial.append(emitter)

                db.commit()
                st.success("Cambios guardados correctamente ✅")
                st.rerun()

                if emisores_para_historial:
                    registrar_historial_comision(db, emisores_para_historial, tipo="manual")


    # =====================================================
    # TAB 3 - DETALLE
    # =====================================================
    with tab3:

        st.subheader("Detalle de Cuentas")

        recruiters = db.query(Emitter.reclutador_id).distinct().all()

        if not recruiters:
            st.warning("No hay datos")
            return

        recruiter_ids = [r[0] for r in recruiters]

        selected = st.selectbox("Seleccionar Reclutador", recruiter_ids, key="detalle")

        cuentas = db.query(Emitter).filter(
            Emitter.reclutador_id == selected,
            Emitter.estado_cuenta == "Verificada"
        ).all()

        data = []

        for c in cuentas:
            data.append({
                "Mico ID": c.mico_id,
                "Nombre": c.nombre,
                "Cuenta Real": c.check_real,
                "Fecha Verificación": c.fecha_verificacion
            })

        st.dataframe(data, use_container_width=True)

    # =====================================================
    # TAB 4 - HISTORIAL + GRAFICO
    # =====================================================
    with tab4:

        st.subheader("Historial de Comisiones")

        histories = db.query(CommissionHistory).all()

        if not histories:
            st.info("No hay comisiones cerradas aún.")
            return

        data = []

        for h in histories:

            col1, col2 = st.columns([4,1])

            col1.write(
                f"Recruiter {h.recruiter_id} | Total: {h.total_pagado} | Fecha: {h.fecha}"
            )

            if not h.pagado:
                if col2.button("Marcar Pagado", key=f"pay_{h.id}"):
                    h.pagado = True
                    h.fecha_pago = datetime.now()
                    db.commit()
                    st.success("Marcado como pagado")
                    st.rerun()
            else:
                col2.success("Pagado")

            data.append((h.fecha.month, h.total_pagado))

        # ----- GRÁFICO MENSUAL -----
        meses = {}
        for mes, total in data:
            meses[mes] = meses.get(mes, 0) + total

        fig = plt.figure()
        plt.bar(list(meses.keys()), list(meses.values()))
        plt.xlabel("Mes")
        plt.ylabel("Total Pagado")
        plt.title("Comisiones por Mes")

        st.pyplot(fig)
