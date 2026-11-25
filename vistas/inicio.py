import streamlit as st

def mostrar(df_pacientes, df_eval, paciente, eval_paciente, ruta_excel):
    st.subheader("📊 Inicio — Resumen y Mapa Corporal")
    st.info(f"Vista lista para programar las tarjetas KPI de {paciente['nombre_completo']}.")