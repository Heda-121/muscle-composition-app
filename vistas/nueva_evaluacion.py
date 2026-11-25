from datetime import date
import openpyxl
import pandas as pd
import streamlit as st


def _generar_nuevo_id(df_eval: pd.DataFrame) -> str:
    """Genera el siguiente ID automático (ej. EVAL-001, EVAL-002) según el historial."""
    if df_eval.empty or "id_evaluacion" not in df_eval.columns:
        return "EVAL-001"

    numeros = []
    for valor in df_eval["id_evaluacion"].dropna().astype(str):
        digitos = "".join(ch for ch in valor if ch.isdigit())
        if digitos:
            numeros.append(int(digitos))

    siguiente = max(numeros) + 1 if numeros else 1
    return f"EVAL-{siguiente:03d}"


def _guardar_en_excel(ruta_excel: str, nombre_hoja: str, nueva_fila: dict, fila_encabezado: int = 4) -> None:
    """Agrega una nueva evaluación al final de la hoja respetando la fila de encabezados."""
    wb = openpyxl.load_workbook(ruta_excel)
    ws = wb[nombre_hoja]

    encabezados = {
        str(ws.cell(row=fila_encabezado, column=col).value).strip(): col
        for col in range(1, ws.max_column + 1)
        if ws.cell(row=fila_encabezado, column=col).value is not None
    }

    fila_destino = fila_encabezado + 1
    while ws.cell(row=fila_destino, column=1).value not in (None, ""):
        fila_destino += 1

    for campo, valor in nueva_fila.items():
        if campo in encabezados:
            ws.cell(row=fila_destino, column=encabezados[campo], value=valor)

    wb.save(ruta_excel)


def mostrar(df_pacientes: pd.DataFrame, df_eval: pd.DataFrame, paciente: pd.Series, eval_paciente: pd.DataFrame, ruta_excel: str) -> None:
    st.subheader("📝 Nueva Evaluación de Composición Corporal")

    c1, c2, c3 = st.columns(3)
    c1.metric("Paciente", paciente.get("nombre_completo", "—"))
    c2.metric("Disciplina", paciente.get("disciplina_deportiva", "—"))
    c3.metric("Evaluaciones previas", len(eval_paciente))

    st.divider()

    # ID automático visible pero fijo (no editable)
    id_automatico = _generar_nuevo_id(df_eval)

    with st.form("form_nueva_evaluacion", clear_on_submit=False):
        st.markdown("#### Datos generales")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input(
                "ID Evaluación (automático)",
                value=id_automatico,
                disabled=True,
                help="Se asigna automáticamente de forma consecutiva al guardar."
            )
        with col2:
            fecha_eval = st.date_input("Fecha de evaluación", value=date.today())
        with col3:
            peso_kg = st.number_input("Peso corporal (kg)", min_value=20.0, max_value=300.0, value=75.0, step=0.1, format="%.1f")

        st.markdown("#### Composición corporal y antropometría")
        col4, col5, col6, col7 = st.columns(4)
        with col4:
            grasa_pct = st.number_input("% Grasa corporal", min_value=1.0, max_value=70.0, value=18.0, step=0.1, format="%.1f")
        with col5:
            musculo_kg = st.number_input("Masa muscular (kg)", min_value=5.0, max_value=150.0, value=35.0, step=0.1, format="%.1f")
        with col6:
            cintura_cm = st.number_input("Cintura (cm)", min_value=30.0, max_value=200.0, value=80.0, step=0.5, format="%.1f")
        with col7:
            cadera_cm = st.number_input("Cadera (cm)", min_value=30.0, max_value=200.0, value=95.0, step=0.5, format="%.1f")

        imc_calculado = None
        if "estatura_cm" in paciente and pd.notna(paciente["estatura_cm"]) and float(paciente["estatura_cm"]) > 0:
            altura_m = float(paciente["estatura_cm"]) / 100.0
            imc_calculado = round(peso_kg / (altura_m ** 2), 2)
            st.caption(f"IMC estimado según estatura registrada ({paciente['estatura_cm']} cm): **{imc_calculado}**")

        observaciones = st.text_area("Observaciones / notas clínicas o deportivas", placeholder="Ej. Medición en ayunas, post-entreno, cambios de rutina...")

        submitted = st.form_submit_button("Guardar evaluación", type="primary")

    if submitted:
        # Relee el Excel al guardar para garantizar que el ID no choque con registros recientes
        df_eval_actual = pd.read_excel(ruta_excel, sheet_name="Evaluaciones", header=3).dropna(subset=["id_evaluacion"])
        id_final = _generar_nuevo_id(df_eval_actual)

        nueva_fila = {
            "id_evaluacion": id_final,
            "id_paciente": paciente["id_paciente"],
            "fecha": fecha_eval.isoformat(),
            "peso_kg": float(peso_kg),
            "grasa_pct": float(grasa_pct),
            "musculo_kg": float(musculo_kg),
            "cintura_cm": float(cintura_cm),
            "cadera_cm": float(cadera_cm),
            "imc": imc_calculado,
            "observaciones": observaciones.strip(),
        }

        try:
            _guardar_en_excel(ruta_excel, "Evaluaciones", nueva_fila, fila_encabezado=4)
            st.success(f"Evaluación **{id_final}** guardada para **{paciente['nombre_completo']}**.")
            st.rerun()
        except Exception as e:
            st.error(f"No se pudo guardar en el Excel: {e}")

    if not eval_paciente.empty:
        st.divider()
        st.markdown("#### Últimas evaluaciones del paciente")
        st.dataframe(eval_paciente.tail(5), use_container_width=True, hide_index=True) 