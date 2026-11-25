import streamlit as st  # Importa Streamlit para dibujar tarjetas, columnas y alertas en esta vista


def construir_mapa_svg(ultima_eval):  # Función auxiliar que arma el dibujo vectorial del cuerpo según los estados del Excel
    colores = {  # Diccionario que traduce cada estado clínico de la base de datos a un color hexadecimal
        "Optimo": "#22c55e",     # Verde: estado muscular e hídrico normal
        "Atencion": "#eab308",   # Amarillo: fatiga leve o seguimiento requerido
        "Alerta": "#ef4444",     # Rojo: sobrecarga o riesgo de lesión
        "Retencion": "#3b82f6"   # Azul: acumulación de agua extracelular
    }

    c_tronco = colores.get(ultima_eval["estado_tronco"], "#94a3b8")        # Busca el color del tronco (gris si no coincide)
    c_brazo_der = colores.get(ultima_eval["estado_brazo_der"], "#94a3b8")  # Busca el color del brazo derecho
    c_brazo_izq = colores.get(ultima_eval["estado_brazo_izq"], "#94a3b8")  # Busca el color del brazo izquierdo
    c_pierna_der = colores.get(ultima_eval["estado_pierna_der"], "#94a3b8")# Busca el color de la pierna derecha
    c_pierna_izq = colores.get(ultima_eval["estado_pierna_izq"], "#94a3b8")# Busca el color de la pierna izquierda

    svg = f"""
    <div style="display:flex; flex-direction:column; align-items:center; background:#0f172a; padding:18px; border-radius:12px; border:1px solid #1e293b;">
        <svg width="230" height="330" viewBox="0 0 230 330">
            <!-- Cabeza (referencia anatómica neutra) -->
            <circle cx="115" cy="35" r="22" fill="#475569" />
            <!-- Brazo derecho (a la izquierda en vista frontal anatómica) -->
            <rect x="42" y="68" width="24" height="95" rx="12" fill="{c_brazo_der}" />
            <!-- Tronco -->
            <rect x="74" y="65" width="82" height="115" rx="16" fill="{c_tronco}" />
            <!-- Brazo izquierdo (a la derecha en vista frontal anatómica) -->
            <rect x="164" y="68" width="24" height="95" rx="12" fill="{c_brazo_izq}" />
            <!-- Pierna derecha -->
            <rect x="76" y="188" width="32" height="118" rx="14" fill="{c_pierna_der}" />
            <!-- Pierna izquierda -->
            <rect x="122" y="188" width="32" height="118" rx="14" fill="{c_pierna_izq}" />
            <!-- Etiquetas de orientación -->
            <text x="54" y="178" fill="#cbd5e1" font-size="11" text-anchor="middle">Der</text>
            <text x="176" y="178" fill="#cbd5e1" font-size="11" text-anchor="middle">Izq</text>
        </svg>
        <div style="display:flex; gap:12px; flex-wrap:wrap; justify-content:center; margin-top:8px; font-size:12px; color:#e2e8f0;">
            <span>🟢 Óptimo</span>
            <span>🟡 Atención</span>
            <span>🔴 Alerta</span>
            <span>🔵 Retención</span>
        </div>
    </div>
    """  # Cadena HTML/SVG que inserta los 5 colores dinámicos en cada rectángulo del cuerpo
    return svg  # Devuelve el bloque gráfico listo para renderizar


def mostrar(df_pacientes, df_eval, paciente, eval_paciente, ruta_excel):  # Función principal llamada por app.py
    st.subheader("📊 Inicio — Resumen Clínico y Mapa Segmental")  # Título de la sección

    if eval_paciente.empty:  # Verifica si el paciente seleccionado aún no tiene evaluaciones registradas
        st.warning(f"⚠️ {paciente['nombre_completo']} aún no tiene evaluaciones registradas.")  # Aviso si está vacío
        return  # Detiene la ejecución de esta vista para evitar errores al buscar la última fila

    eval_ordenadas = eval_paciente.sort_values("fecha_evaluacion")  # Ordena cronológicamente de la más antigua a la más reciente
    ultima = eval_ordenadas.iloc[-1]  # Extrae la última fila (la evaluación más reciente del paciente)
    hay_previa = len(eval_ordenadas) >= 2  # Comprueba si existen al menos 2 evaluaciones para calcular cambios
    anterior = eval_ordenadas.iloc[-2] if hay_previa else ultima  # Toma la penúltima evaluación (o la misma si solo hay 1)

    # --- CÁLCULOS BIOMÉDICOS ---
    estatura_m = float(paciente["estatura_cm"]) / 100.0  # Convierte la estatura de centímetros a metros
    peso_actual = float(ultima["peso_kg"])  # Peso de la última evaluación
    peso_previo = float(anterior["peso_kg"])  # Peso de la evaluación anterior

    imc_actual = peso_actual / (estatura_m ** 2)  # Fórmula del Índice de Masa Corporal: peso / estatura²
    imc_previo = peso_previo / (estatura_m ** 2)  # IMC de la evaluación anterior para comparar

    grasa_actual = float(ultima["porcentaje_grasa"])  # Porcentaje de grasa actual
    grasa_previa = float(anterior["porcentaje_grasa"])  # Porcentaje de grasa anterior

    musculo_actual = float(ultima["masa_muscular_kg"])  # Masa muscular actual en kg
    musculo_previo = float(anterior["masa_muscular_kg"])  # Masa muscular anterior en kg

    # --- FILA 1: 4 TARJETAS KPI ---
    c1, c2, c3, c4 = st.columns(4)  # Divide el ancho en 4 columnas iguales para los indicadores

    c1.metric(  # Tarjeta 1: Peso corporal
        label="Peso Corporal",  # Título superior de la tarjeta
        value=f"{peso_actual:.1f} kg",  # Valor grande formateado a 1 decimal
        delta=f"{peso_actual - peso_previo:+.1f} kg" if hay_previa else "Primera medición",  # Diferencia con signo (+ o -)
        delta_color="off"  # Color neutro gris porque subir o bajar peso depende del objetivo deportivo
    )

    c2.metric(  # Tarjeta 2: IMC
        label="IMC",  # Título de la tarjeta
        value=f"{imc_actual:.1f} kg/m²",  # Valor del IMC actual
        delta=f"{imc_actual - imc_previo:+.1f}" if hay_previa else "Sin previa",  # Cambio respecto a la cita anterior
        delta_color="off"  # Color neutro gris
    )

    c3.metric(  # Tarjeta 3: Porcentaje de grasa
        label="Porcentaje de Grasa",  # Título de la tarjeta
        value=f"{grasa_actual:.1f} %",  # Valor actual de grasa
        delta=f"{grasa_actual - grasa_previa:+.1f} %" if hay_previa else "Sin previa",  # Cambio de grasa
        delta_color="inverse"  # Invierte colores: bajar grasa (-) sale en verde y subir (+) sale en rojo
    )

    c4.metric(  # Tarjeta 4: Masa muscular
        label="Masa Muscular",  # Título de la tarjeta
        value=f"{musculo_actual:.1f} kg",  # Valor actual de músculo
        delta=f"{musculo_actual - musculo_previo:+.1f} kg" if hay_previa else "Sin previa",  # Cambio de músculo
        delta_color="normal"  # Normal: ganar músculo (+) sale en verde y perder (-) sale en rojo
    )

    st.divider()  # Línea separadora entre las tarjetas y el mapa corporal

    # --- FILA 2: MAPA CORPORAL (IZQUIERDA) + FICHA Y DIAGNÓSTICO (DERECHA) ---
    col_mapa, col_diag = st.columns([4, 6])  # Divide la fila en 40% para el mapa y 60% para la ficha clínica

    with col_mapa:  # Columna izquierda
        st.markdown("**Mapa de Bioimpedancia Segmental**")  # Subtítulo encima del muñeco
        st.markdown(construir_mapa_svg(ultima), unsafe_allow_html=True)  # Renderiza el código HTML/SVG como gráfico real

    with col_diag:  # Columna derecha
        with st.container(border=True):  # Crea una tarjeta con borde alrededor de los datos del paciente
            st.markdown(f"### 🩺 Ficha Clínica: {paciente['nombre_completo']}")  # Nombre del paciente
            st.write(
                f"**Sexo:** {paciente['sexo']}  |  "
                f"**Edad:** {int(paciente['edad'])} años  |  "
                f"**Estatura:** {paciente['estatura_cm']} cm  |  "
                f"**Disciplina:** {paciente['disciplina_deportiva']}"
            )  # Muestra los 4 datos demográficos en una sola línea
            st.write(
                f"**Última evaluación:** {ultima['fecha_evaluacion']}  |  "
                f"**Agua corporal:** {ultima['agua_corporal_pct']}%  |  "
                f"**Grasa visceral:** Nivel {int(ultima['grasa_visceral'])}"
            )  # Muestra los indicadores secundarios de la última cita

        # Evaluación automática de alertas por segmento
        segmentos = {  # Diccionario con nombres legibles y el valor de cada columna segmental
            "Tronco": ultima["estado_tronco"],
            "Brazo derecho": ultima["estado_brazo_der"],
            "Brazo izquierdo": ultima["estado_brazo_izq"],
            "Pierna derecha": ultima["estado_pierna_der"],
            "Pierna izquierda": ultima["estado_pierna_izq"],
        }
        alterados = [f"**{nombre}** ({estado})" for nombre, estado in segmentos.items() if estado != "Optimo"]  # Filtra los segmentos que no estén óptimos

        if not alterados:  # Si la lista de alterados está vacía
            st.success("✅ **Balance segmental óptimo:** Todos los segmentos presentan buena simetría e hidratación.")  # Caja verde
        else:  # Si hay uno o más segmentos en Atención, Alerta o Retención
            st.warning("⚠️ **Hallazgos segmentales detectados:** " + ", ".join(alterados) + ".")  # Caja amarilla de alerta

        st.info(f"📝 **Observación clínica:** {ultima['observaciones']}")  # Caja azul con la nota médica guardada en Excel