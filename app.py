import streamlit as st
import pandas as pd

# 1. Configuración inicial de la página (siempre va de primero)
st.set_page_config(
    page_title="LexCorpus",
    page_icon="🧬",
    layout="wide"
)

# 2. Lectura de las dos hojas del archivo Excel
RUTA_EXCEL = "base_datos_composicion_corporal.xlsx"

df_pacientes = pd.read_excel(RUTA_EXCEL, sheet_name="Pacientes", header=3)
df_pacientes = df_pacientes.dropna(subset=["id_paciente"])

df_eval = pd.read_excel(RUTA_EXCEL, sheet_name="Evaluaciones", header=3)
df_eval = df_eval.dropna(subset=["id_evaluacion"])

# 3. Encabezado y buscador predictivo
st.title("🧬 LexCorpus | Control de Composición Corporal")

indice = st.selectbox(
    "Buscar paciente (escribe nombre, documento o deporte):",
    options=df_pacientes.index,
    format_func=lambda i: (
        f"{df_pacientes.loc[i, 'nombre_completo']} — "
        f"Doc: {str(df_pacientes.loc[i, 'documento']).replace('.0', '')} "
        f"({df_pacientes.loc[i, 'disciplina_deportiva']})"
    )
)

# 4. Filtrar datos del paciente seleccionado
paciente = df_pacientes.loc[indice]
eval_paciente = df_eval[df_eval["id_paciente"] == paciente["id_paciente"]]

# 5. Comprobación visual temporal
st.subheader(f"Paciente activo: {paciente['nombre_completo']}")
st.write(f"Estatura: {paciente['estatura_cm']} cm | Edad: {paciente['edad']} años | Sexo: {paciente['sexo']}")
st.dataframe(eval_paciente, use_container_width=True, hide_index=True)

st.sidebar.title("🧬 BioTrack")  # Dibuja el título de la app dentro del panel lateral izquierdo
st.sidebar.caption("Control de Composición Corporal")  # Agrega un subtítulo pequeño en color gris dentro del panel lateral
st.sidebar.divider()  # Dibuja una línea horizontal separadora dentro de la barra lateral

vista_actual = st.sidebar.radio(  # Crea un menú vertical de selección única y guarda el texto elegido en 'vista_actual'
    "Navegación:",  # Etiqueta que aparece encima de las 4 opciones del menú
    options=["Inicio", "Pacientes", "Nueva Evaluación", "Evolución"]  # Las 4 pantallas exactas del diseño original
)