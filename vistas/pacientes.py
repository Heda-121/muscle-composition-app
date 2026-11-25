import streamlit as st  # Necesario en cada archivo que dibuje elementos en pantalla
import openpyxl  # Necesario aquí porque esta vista guarda pacientes nuevos en Excel


def mostrar(df_pacientes, df_eval, paciente, eval_paciente, ruta_excel):  # Función principal que llama app.py
    st.subheader("👥 Gestión y Registro de Pacientes")

    with st.form("form_nuevo_paciente", clear_on_submit=True):
        st.markdown("**Registrar nuevo paciente**")

        col1, col2, col3 = st.columns(3)
        nuevo_nombre = col1.text_input("Nombre completo:", placeholder="Ej. Camila Torres")
        nuevo_doc = col2.text_input("Documento de identidad:", placeholder="Ej. 1053889900")
        nueva_disp = col3.text_input("Disciplina deportiva:", value="General")

        col4, col5, col6 = st.columns(3)
        nuevo_sexo = col4.selectbox("Sexo biológico:", options=["F", "M"])
        nueva_edad = col5.number_input("Edad (años):", min_value=10, max_value=95, value=22, step=1)
        nueva_estatura = col6.number_input("Estatura (cm):", min_value=100.0, max_value=230.0, value=170.0, step=0.5)

        boton_guardar = st.form_submit_button("💾 Guardar Paciente", type="primary")

    if boton_guardar:
        docs_existentes = df_pacientes["documento"].astype(str).str.replace(".0", "", regex=False).tolist()

        if not nuevo_nombre.strip() or not nuevo_doc.strip():
            st.error("⚠️ El nombre completo y el documento son obligatorios.")
        elif nuevo_doc.strip() in docs_existentes:
            st.warning("⚠️ Ya existe un paciente registrado con ese número de documento.")
        else:
            try:
                nuevo_id = int(df_pacientes["id_paciente"].max()) + 1 if not df_pacientes.empty else 1
                libro = openpyxl.load_workbook(ruta_excel)
                hoja = libro["Pacientes"]
                hoja.append([
                    nuevo_id,
                    nuevo_nombre.strip(),
                    nuevo_doc.strip(),
                    nuevo_sexo,
                    int(nueva_edad),
                    round(float(nueva_estatura), 1),
                    nueva_disp.strip() or "General"
                ])
                libro.save(ruta_excel)
                st.rerun()
            except PermissionError:
                st.error("❌ Cierra el archivo Excel antes de guardar un paciente nuevo.")

    st.divider()
    st.subheader(f"📋 Directorio de Pacientes ({len(df_pacientes)} registrados)")

    filtro = st.text_input("Filtrar tabla por nombre, documento o deporte:", placeholder="Escribe para filtrar...")

    df_mostrar = df_pacientes.copy()
    df_mostrar["documento"] = df_mostrar["documento"].astype(str).str.replace(".0", "", regex=False)

    if filtro.strip():
        texto = filtro.strip()
        condicion = (
            df_mostrar["nombre_completo"].str.contains(texto, case=False, na=False) |
            df_mostrar["documento"].str.contains(texto, case=False, na=False) |
            df_mostrar["disciplina_deportiva"].str.contains(texto, case=False, na=False)
        )
        df_mostrar = df_mostrar[condicion]

    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)