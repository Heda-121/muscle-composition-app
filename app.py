import streamlit as st  # Importa Streamlit para la interfaz web
import pandas as pd  # Importa Pandas para leer y filtrar el Excel
from vistas import inicio, pacientes, nueva_evaluacion, evolucion  # Importa los 4 archivos de la carpeta 'vistas'

# 1. Configuración general de la página
st.set_page_config(
    page_title="BioTrack | Composición Corporal",  # Título en la pestaña del navegador
    page_icon="🧬",  # Ícono de la pestaña
    layout="wide"  # Usa todo el ancho disponible de la pantalla
)

# 2. Lectura de la base de datos en Excel
RUTA_EXCEL = "base_datos_composicion_corporal.xlsx"  # Ruta del archivo Excel

df_pacientes = pd.read_excel(RUTA_EXCEL, sheet_name="Pacientes", header=3)  # Carga la hoja 'Pacientes' desde la fila 4
df_pacientes = df_pacientes.dropna(subset=["id_paciente"])  # Limpia filas vacías al final

df_eval = pd.read_excel(RUTA_EXCEL, sheet_name="Evaluaciones", header=3)  # Carga la hoja 'Evaluaciones' desde la fila 4
df_eval = df_eval.dropna(subset=["id_evaluacion"])  # Limpia filas vacías al final

# 3. Menú lateral de navegación
st.sidebar.title("🧬 LexCorpus")  # Título del menú lateral
st.sidebar.caption("Control de Composición Corporal")  # Subtítulo del menú lateral
st.sidebar.divider()  # Línea separadora

vista_actual = st.sidebar.radio(  # Selector de pantalla en la barra izquierda
    "Navegación:",
    options=["Inicio", "Pacientes", "Nueva Evaluación", "Evolución"]
)
st.sidebar.divider()

# 4. Barra superior con título y buscador predictivo
col_titulo, col_buscador = st.columns([3, 2])  # Divide el espacio superior (60% izquierda, 40% derecha)

with col_titulo:
    st.title("Control de Composición Corporal")  # Título principal

with col_buscador:
    indice = st.selectbox(  # Buscador global de pacientes
        "Paciente activo (escribe nombre, documento o deporte):",
        options=df_pacientes.index,
        format_func=lambda i: (
            f"{df_pacientes.loc[i, 'nombre_completo']} — "
            f"Doc: {str(df_pacientes.loc[i, 'documento']).replace('.0', '')} "
            f"({df_pacientes.loc[i, 'disciplina_deportiva']})"
        )
    )

# 5. Datos filtrados del paciente activo (se envían a la vista que esté abierta)
paciente = df_pacientes.loc[indice]  # Fila completa del paciente elegido
eval_paciente = df_eval[df_eval["id_paciente"] == paciente["id_paciente"]]  # Evaluaciones solo de ese paciente

st.sidebar.markdown(f"**Paciente activo:**  \n{paciente['nombre_completo']}")  # Muestra el nombre en el panel izquierdo
st.sidebar.write(f"Disciplina: {paciente['disciplina_deportiva']}")  # Muestra el deporte
st.sidebar.write(f"Evaluaciones: {len(eval_paciente)}")  # Muestra cuántas mediciones tiene

st.divider()

# 6. Llama al archivo correspondiente según lo que el usuario eligió en el menú
if vista_actual == "Inicio":
    inicio.mostrar(df_pacientes, df_eval, paciente, eval_paciente, RUTA_EXCEL)  # Ejecuta la función mostrar() de vistas/inicio.py

elif vista_actual == "Pacientes":
    pacientes.mostrar(df_pacientes, df_eval, paciente, eval_paciente, RUTA_EXCEL)  # Ejecuta la función mostrar() de vistas/pacientes.py

elif vista_actual == "Nueva Evaluación":
    nueva_evaluacion.mostrar(df_pacientes, df_eval, paciente, eval_paciente, RUTA_EXCEL)  # Ejecuta la función mostrar() de vistas/nueva_evaluacion.py

elif vista_actual == "Evolución":
    evolucion.mostrar(df_pacientes, df_eval, paciente, eval_paciente, RUTA_EXCEL)  # Ejecuta la función mostrar() de vistas/evolucion.py