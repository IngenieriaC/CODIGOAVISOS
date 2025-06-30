# -*- coding: utf-8 -*-
"""avisos_integrado"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import io
import numpy as np
# --- Configuración de la página (temática Sura) ---
st.set_page_config(
    page_title="Gestión Administrativa - Sura",
    layout="wide",
    initial_sidebar_state="expanded",
    # Icono de la página (opcional, puedes cambiar '📈' por el tuyo)
    # Abre este enlace para ver más emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
)

# Estilos CSS para ambientar en amarillo, blanco y azul rey
st.markdown(
    """
    <style>
    /* Estilos generales del fondo con degradado */
    .stApp {
        background: linear-gradient(to right, #FFFFFF, #FFFACD, #4169E1); /* Blanco, Amarillo claro (Cream), Azul Rey */
        color: #333333; /* Color de texto general */
    }
    /* Sidebar */
    .st-emotion-cache-1oe6z58 { /* Esta clase puede cambiar en futuras versiones de Streamlit */
        background-color: #F0F8FF; /* Azul claro para la sidebar */
    }
    /* Títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #4169E1; /* Azul Rey para los títulos */
    }
    /* Botones */
    .stButton>button {
        background-color: #4169E1; /* Azul Rey para los botones */
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #F8D568; /* Amarillo para hover */
        color: #4169E1;
        border: 1px solid #4169E1;
    }
    /* Contenedores de contenido principal */
    .st-emotion-cache-z5fcl4, .st-emotion-cache-1c7y2kl, .st-emotion-cache-nahz7x { /* Clases genéricas para contenedores */
        background-color: rgba(255, 255, 255, 0.9); /* Blanco semitransparente */
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    /* Mejoras para la tabla (dataframe) */
    .streamlit-dataframe {
        border-radius: 0.5rem;
        overflow: hidden; /* Asegura que las esquinas redondeadas se apliquen bien */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Bienvenida y encabezado ---
st.title("¡Hola, usuario Sura! 👋")
st.markdown("---")
st.header("Proyecto de **Gestión Administrativa** en Ingeniería Clínica")
st.markdown("""
    Aquí podrás **analizar y gestionar los datos de avisos** para optimizar los procesos. Creado por Naida López Aprendiz Universitaria.
""")
# Set a nice style for plots
sns.set_style('whitegrid')

# --- Configuración de la página (temática Sura) ---
st.set_page_config(
    page_title="Gerencia de Gestión Administrativa - Sura",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS para ambientar en amarillo, blanco y azul rey
st.markdown(
    """
    <style>
    /* Estilos generales del fondo con degradado */
    .stApp {
        background: linear-gradient(to right, #FFFFFF, #FFFACD, #4169E1); /* Blanco, Amarillo claro (Cream), Azul Rey */
        color: #333333; /* Color de texto general */
    }
    /* Sidebar */
    .st-emotion-cache-1oe6z58 { /* Esta clase puede cambiar en futuras versiones de Streamlit */
        background-color: #F0F8FF; /* Azul claro para la sidebar */
    }
    /* Títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #4169E1; /* Azul Rey para los títulos */
    }
    /* Botones */
    .stButton>button {
        background-color: #4169E1; /* Azul Rey para los botones */
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #F8D568; /* Amarillo para hover */
        color: #4169E1;
        border: 1px solid #4169E1;
    }
    /* Contenedores de contenido principal */
    .st-emotion-cache-z5fcl4, .st-emotion-cache-1c7y2kl, .st-emotion-cache-nahz7x { /* Clases genéricas para contenedores */
        background-color: rgba(255, 255, 255, 0.9); /* Blanco semitransparente */
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    /* Mejoras para la tabla (dataframe) */
    .streamlit-dataframe {
        border-radius: 0.5rem;
        overflow: hidden; /* Asegura que las esquinas redondeadas se apliquen bien */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Función de carga (modificada para no unir) ---
@st.cache_data
def load_and_merge_data(uploaded_file_buffer: io.BytesIO) -> pd.DataFrame:
    """
    Carga los datos de un único archivo Excel. Se asume que el archivo
    contiene todas las columnas necesarias en una sola hoja.

    Args:
        uploaded_file_buffer (io.BytesIO): Buffer del archivo Excel subido por el usuario.

    Returns:
        pd.DataFrame: El DataFrame cargado y limpio.
    """
    # Cargar la primera (o única) hoja del Excel directamente
    try:
        df = pd.read_excel(uploaded_file_buffer, sheet_name=0)
    except Exception as e:
        st.error(f"No se pudo leer el archivo Excel. Asegúrate de que es un archivo .xlsx y contiene datos en la primera hoja: {e}")
        return pd.DataFrame() # Retorna un DataFrame vacío en caso de error

    # Limpiar encabezados
    df.columns = df.columns.str.strip()

    # Columnas esperadas según tu descripción
    # Asegúrate de que estas columnas coincidan exactamente con las de tu Excel
    columnas_esperadas = [
        "Aviso", "Fecha de aviso", "Código postal", "Status del sistema",
        "Descripción", "Ubicación técnica", "Equipo", "Denominación de objeto técnico",
        "Denominación ejecutante", "Duración de parada", "Costes tot.reales",
        "Inic.garantía prov.", "Fin garantía prov.", "Texto_equipo",
        "Texto código acción", "Texto de acción", "Texto grupo acción", "TIPO DE SERVICIO"
    ]

    # Verificar si todas las columnas esperadas están presentes
    missing_columns = [col for col in columnas_esperadas if col not in df.columns]
    if missing_columns:
        st.warning(f"Advertencia: Faltan las siguientes columnas en el archivo Excel: {', '.join(missing_columns)}. El análisis podría verse afectado.")
        # Opcional: puedes decidir si quieres detener la ejecución o continuar con las columnas disponibles
        # Por ahora, continuaremos y las columnas faltantes se manejarán como NaN o errores en pasos posteriores.

    # Seleccionar solo las columnas que el usuario especificó y que existen en el DataFrame
    # Esto también manejará si hay columnas adicionales que no se necesitan
    df = df[[col for col in columnas_esperadas if col in df.columns]].copy()


    # Normalizar los nombres de las columnas (manteniendo la lógica existente)
    ORIGINAL_EJECUTANTE_COL_NAME = "Denominación ejecutante"
    ORIGINAL_CP_COL_NAME = "Código postal"
    ORIGINAL_OBJETO_TECNICO_COL_NAME = "Denominación de objeto técnico"
    ORIGINAL_TEXTO_CODIGO_ACCION_COL_NAME = "Texto código acción"
    ORIGINAL_TEXTO_ACCION_COL_NAME = "Texto de acción"
    ORIGINAL_TIPO_SERVICIO_COL_NAME = "TIPO DE SERVICIO"
    ORIGINAL_COSTOS_COL_NAME = "Costes tot.reales"
    ORIGINAL_DESCRIPTION_COL_NAME = "Descripción"
    ORIGINAL_FECHA_AVISO_COL_NAME = "Fecha de aviso"
    ORIGINAL_TEXTO_EQUIPO_COL_NAME = "Texto_equipo"
    ORIGINAL_DURACION_PARADA_COL_NAME = "Duración de parada"
    ORIGINAL_EQUIPO_COL_COL_NAME = "Equipo"
    ORIGINAL_AVISO_COL_NAME = "Aviso"
    ORIGINAL_STATUS_SISTEMA_COL_NAME = "Status del sistema"

    column_mapping = {
        ORIGINAL_EJECUTANTE_COL_NAME: "denominacion_ejecutante",
        ORIGINAL_CP_COL_NAME: "codigo_postal",
        ORIGINAL_OBJETO_TECNICO_COL_NAME: "denominacion_de_objeto_tecnico",
        ORIGINAL_TEXTO_CODIGO_ACCION_COL_NAME: "texto_codigo_accion",
        ORIGINAL_TEXTO_ACCION_COL_NAME: "texto_de_accion",
        ORIGINAL_TIPO_SERVICIO_COL_NAME: "tipo_de_servicio",
        ORIGINAL_COSTOS_COL_NAME: "costes_totreales",
        ORIGINAL_DESCRIPTION_COL_NAME: "descripcion",
        ORIGINAL_FECHA_AVISO_COL_NAME: "fecha_de_aviso",
        ORIGINAL_TEXTO_EQUIPO_COL_NAME: "texto_equipo",
        ORIGINAL_DURACION_PARADA_COL_NAME: "duracion_de_parada",
        ORIGINAL_EQUIPO_COL_COL_NAME: "equipo",
        ORIGINAL_AVISO_COL_NAME: "aviso",
        ORIGINAL_STATUS_SISTEMA_COL_NAME: "status_del_sistema"
    }

    normalized_df_columns = []
    for col in df.columns:
        found_match = False
        for original, normalized in column_mapping.items():
            if col.strip().lower() == original.strip().lower():
                normalized_df_columns.append(normalized)
                found_match = True
                break
        if not found_match:
            normalized_df_columns.append(
                col.lower()
                .strip()
                .replace(" ", "_")
                .replace(".", "")
                .replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            )
    df.columns = normalized_df_columns

    # Asignar columnas relevantes a nuevos nombres simplificados
    # Asegúrate de que las columnas originales existan después de la normalización
    if 'denominacion_ejecutante' in df.columns:
        df['PROVEEDOR'] = df['denominacion_ejecutante']
    else:
        df['PROVEEDOR'] = np.nan # O maneja el caso de columna faltante apropiadamente

    if 'costes_totreales' in df.columns:
        df['COSTO'] = pd.to_numeric(df['costes_totreales'], errors='coerce')
    else:
        df['COSTO'] = np.nan

    if 'duracion_de_parada' in df.columns:
        df['TIEMPO PARADA'] = pd.to_numeric(df['duracion_de_parada'], errors='coerce')
    else:
        df['TIEMPO PARADA'] = np.nan

    if 'equipo' in df.columns:
        df['EQUIPO'] = pd.to_numeric(df['equipo'], errors='coerce')
        df['EQUIPO'] = df['EQUIPO'].fillna(0) # Asegurar que 'EQUIPO' no sea NaN
    else:
        df['EQUIPO'] = 0

    if 'aviso' in df.columns:
        df['AVISO'] = pd.to_numeric(df['aviso'], errors='coerce')
    else:
        df['AVISO'] = np.nan

    if 'tipo_de_servicio' in df.columns:
        df['TIPO DE SERVICIO'] = df['tipo_de_servicio']
    else:
        df['TIPO DE SERVICIO'] = np.nan

    # Asegurar que 'costes_totreales' es numérico (volver a convertir por si acaso)
    if 'costes_totreales' in df.columns:
        df['costes_totreales'] = pd.to_numeric(df['costes_totreales'], errors='coerce')

    # Lógica de mapeo de HORARIO (se mantiene igual si 'texto_equipo' está presente)
    horarios_dict = {
        "HORARIO_99": (17, 364.91), "HORARIO_98": (14.5, 312.78), "HORARIO_97": (9.818181818, 286.715),
        "HORARIO_96": (14.5, 312.78), "HORARIO_95": (4, 208.52), "HORARIO_93": (13.45454545, 286.715),
        "HORARIO_92": (6, 338.845), "HORARIO_91": (9.25, 312.78), "HORARIO_90": (11, 260.65),
        "HORARIO_9": (16, 312.78), "HORARIO_89": (9.5, 260.65), "HORARIO_88": (14, 260.65),
        "HORARIO_87": (9.333333333, 312.78), "HORARIO_86": (9.666666667, 312.78), "HORARIO_85": (12, 312.78),
        "HORARIO_84": (9.5, 312.78), "HORARIO_83": (8.416666667, 312.78), "HORARIO_82": (6, 312.78),
        "HORARIO_81": (10, 312.78), "HORARIO_80": (8.5, 312.78), "HORARIO_8": (11.6, 260.65),
        "HORARIO_79": (14, 312.78), "HORARIO_78": (12, 312.78), "HORARIO_77": (3, 312.78),
        "HORARIO_76": (16, 312.78), "HORARIO_75": (12.16666667, 312.78), "HORARIO_74": (11.33333333, 312.78),
        "HORARIO_73": (12.66666667, 312.78), "HORARIO_72": (11.83333333, 312.78), "HORARIO_71": (11, 312.78),
        "HORARIO_70": (15.16666667, 312.78), "HORARIO_7": (15.33333333, 312.78), "HORARIO_69": (9.166666667, 312.78),
        "HORARIO_68": (4, 312.78), "HORARIO_67": (10, 260.65), "HORARIO_66": (4, 260.65),
        "HORARIO_65": (16.76923077, 338.845), "HORARIO_64": (17.15384615, 338.845), "HORARIO_63": (22.5, 312.78),
        "HORARIO_62": (12.25, 312.78), "HORARIO_61": (4, 312.78), "HORARIO_60": (13, 312.78),
        "HORARIO_6": (18.46153846, 338.845), "HORARIO_59": (12.66666667, 312.78), "HORARIO_58": (12.33333333, 312.78),
        "HORARIO_57": (13.53846154, 338.845), "HORARIO_56": (12.16666667, 312.78), "HORARIO_55": (6.333333333, 312.78),
        "HORARIO_54": (7.230769231, 338.845), "HORARIO_53": (5.5, 312.78), "HORARIO_52": (4, 312.78),
        "HORARIO_51": (14, 338.845), "HORARIO_50": (15, 312.78), "HORARIO_5": (17, 312.78),
        "HORARIO_49": (15.27272727, 286.715), "HORARIO_48": (14.76923077, 338.845), "HORARIO_47": (14.5, 312.78),
        "HORARIO_46": (14.33333333, 312.78), "HORARIO_45": (14.16666667, 312.78), "HORARIO_44": (13.83333333, 312.78),
        "HORARIO_43": (13.5, 312.78), "HORARIO_42": (13.91666667, 312.78), "HORARIO_41": (15, 364.91),
        "HORARIO_40": (15.81818182, 286.715), "HORARIO_4": (16.16666667, 312.78), "HORARIO_39": (15.27272727, 286.715),
        "HORARIO_38": (13.84615385, 338.845), "HORARIO_37": (15.09090909, 286.715), "HORARIO_36": (14, 364.91),
        "HORARIO_35": (14.30769231, 338.845), "HORARIO_34": (14.90909091, 286.715), "HORARIO_33": (13.55, 312.78),
        "HORARIO_32": (14, 338.845), "HORARIO_31": (14.72727273, 286.715), "HORARIO_30": (13.08333333, 312.78),
        "HORARIO_3": (16, 312.78), "HORARIO_29": (14, 286.715), "HORARIO_28": (13, 364.91),
        "HORARIO_27": (14, 286.715), "HORARIO_26": (12.58333333, 312.78), "HORARIO_25": (12, 312.78),
        "HORARIO_24": (13.27272727, 286.715), "HORARIO_23": (11.83333333, 312.78), "HORARIO_22": (11.91666667, 312.78),
        "HORARIO_21": (13.09090909, 286.715), "HORARIO_20": (5, 312.78), "HORARIO_2": (23.5, 364.91),
        "HORARIO_19": (12.18181818, 286.715), "HORARIO_18": (5, 312.78), "HORARIO_17": (9.75, 312.78),
        "HORARIO_16": (10.36363636, 286.715), "HORARIO_15": (10.18181818, 286.715), "HORARIO_14": (8.5, 312.78),
        "HORARIO_134": (12, 364.91), "HORARIO_133": (12, 260.65), "HORARIO_132": (13, 312.78),
        "HORARIO_131": (10, 312.78), "HORARIO_130": (11, 260.65), "HORARIO_13": (9.454545455, 286.715),
        "HORARIO_129": (9.384615385, 338.845), "HORARIO_128": (12.33333333, 312.78), "HORARIO_127": (9.666666667, 312.78),
        "HORARIO_126": (10.83333333, 312.78), "HORARIO_125": (4, 312.78), "HORARIO_124": (13.66666667, 312.78),
        "HORARIO_123": (16.61538462, 338.845), "HORARIO_122": (11, 260.65), "HORARIO_121": (11.66666667, 312.78),
        "HORARIO_120": (8.25, 312.78), "HORARIO_12": (9.272727273, 286.715), "HORARIO_119": (11.23076923, 338.845),
        "HORARIO_118": (11.27272727, 286.715), "HORARIO_117": (11.41666667, 312.78), "HORARIO_116": (11, 312.78),
        "HORARIO_115": (9.25, 312.78), "HORARIO_114": (23.07692308, 338.845), "HORARIO_113": (20, 338.845),
        "HORARIO_112": (10.61538462, 338.845), "HORARIO_111": (9.454545455, 286.715), "HORARIO_110": (6.833333333, 312.78),
        "HORARIO_11": (8, 312.78), "HORARIO_109": (12.90909091, 286.715), "HORARIO_108": (10.54545455, 286.715),
        "HORARIO_107": (12.61538462, 338.845), "HORARIO_106": (14.76923077, 338.845), "HORARIO_105": (12, 156.39),
        "HORARIO_104": (7.666666667, 312.78), "HORARIO_103": (3, 260.65), "HORARIO_102": (10.16666667, 312.78),
        "HORARIO_101": (12, 260.65), "HORARIO_100": (11.16666667, 312.78), "HORARIO_10": (6, 312.78),
        "HORARIO_1": (24, 364.91),
    }

    if 'texto_equipo' in df.columns:
        df['HORARIO'] = df['texto_equipo'].str.strip().str.upper()
        df['HORA/ DIA'] = df['HORARIO'].map(lambda x: horarios_dict.get(x, (None, None))[0])
        df['DIAS/ AÑO'] = df['HORARIO'].map(lambda x: horarios_dict.get(x, (None, None))[1])
        df['DIAS/ AÑO'] = pd.to_numeric(df['DIAS/ AÑO'], errors='coerce')
        df['HORA/ DIA'] = pd.to_numeric(df['HORA/ DIA'], errors='coerce')
    else:
        df['HORARIO'] = np.nan
        df['HORA/ DIA'] = np.nan
        df['DIAS/ AÑO'] = np.nan

    # Preprocesamiento adicional para requisitos de la segunda parte del código
    if 'fecha_de_aviso' in df.columns:
        df["fecha_de_aviso"] = pd.to_datetime(df["fecha_de_aviso"], errors="coerce")
        df["año"] = df["fecha_de_aviso"].dt.year
        df["mes"] = df["fecha_de_aviso"].dt.strftime("%B")
    else:
        df["fecha_de_aviso"] = pd.NaT # Not a Time
        df["año"] = np.nan
        df["mes"] = np.nan

    def extract_description_category(description):
        if pd.isna(description):
            return "Otros"
        match = re.match(r'^([A-Z]{2})/', str(description).strip())
        if match:
            return match.group(1)
        return "Otros"

    if 'descripcion' in df.columns:
        df["description_category"] = df['descripcion'].apply(extract_description_category)
    else:
        df["description_category"] = "Otros" # O un valor por defecto adecuado

    return df

# --- DEFINICIÓN DE PREGUNTAS PARA EVALUACIÓN ---
preguntas = [
    ("Calidad", "¿Las soluciones propuestas son coherentes con el diagnóstico y causa raíz del problema?", "2,1,0,-1"),
    ("Calidad", "¿El trabajo entregado tiene materiales nuevos, originales y de marcas reconocidas?", "2,1,0,-1"),
    ("Calidad", "¿Cuenta con acabados homogéneos, limpios y pulidos?", "2,1,0,-1"),
    ("Calidad", "¿El trabajo entregado corresponde completamente con lo contratado?", "2,1,0,-1"),
    ("Calidad", "¿La facturación refleja correctamente lo ejecutado y acordado?", "2,1,0,-1"),
    ("Oportunidad", "¿La entrega de cotizaciones fue oportuna, según el contrato?", "2,1,0,-1"),
    ("Oportunidad", "¿El reporte del servicio fue entregado oportunamente, según el contrato?", "2,1,0,-1"),
    ("Oportunidad", "¿Cumple las fechas y horas programadas para los trabajos, según el contrato?", "2,1,0,-1"),
    ("Oportunidad", "¿Responde de forma efectiva ante eventualidades emergentes, según el contrato?", "2,1,0,-1"),
    ("Oportunidad", "¿Soluciona rápidamente reclamos o inquietudes por garantía, según el contrato?", "2,1,0,-1"),
    ("Oportunidad", "¿Dispone de los repuestos requeridos en los tiempos necesarios, según el contrato?", "2,1,0,-1"),
    ("Oportunidad", "¿Entrega las facturas en los tiempos convenidos, según el contrato?", "2,1,0,-1"),
    ("Precio", "¿Los precios ofrecidos para equipos son competitivos respecto al mercado?", "2,1,0,-1"),
    ("Precio", "¿Los precios ofrecidos para repuestos son competitivos respecto al mercado?", "2,1,0,-1"),
    ("Precio", "¿Los precios ofrecidos para mantenimientos son competitivos respecto al mercado?", "2,1,0,-1"),
    ("Precio", "¿Los precios ofrecidos para insumos son competitivos respecto al mercado?", "2,1,0,-1"),
    ("Postventa", "¿Tiene disposición y actitud de servicio frente a solicitudes?", "2,1,0,-1"),
    ("Postventa", "¿Conoce necesidades y ofrece alternativas adecuadas?", "2,1,0,-1"),
    ("Postventa", "¿Realiza seguimiento a los resultados de los trabajos?", "2,1,0,-1"),
    ("Postventa", "¿Ofrece capacitaciones para el manejo de los equipos?", "2,1,0,-1"),
    ("Postventa", "¿Los métodos de capacitación ofrecidos son efectivos y adecuados?", "2,1,0,-1"),
    ("Desempeño técnico", "Disponibilidad promedio (%)", "auto"),
    ("Desempeño técnico", "MTTR promedio (hrs)", "auto"),
    ("Desempeño técnico", "MTBF promedio (hrs)", "auto"),
    ("Desempeño técnico", "Rendimiento promedio equipos", "auto"),
]

# --- Definición de las preguntas y rangos DETALLADOS ---
rangos_detallados = {
    "Calidad": {
        "¿Las soluciones propuestas son coherentes con el diagnóstico y causa raíz del problema?": {
            2: "Total coherencia con el diagnóstico y causas identificadas",
            1: "Coherencia razonable, con pequeños ajustes necesarios",
            0: "Cumple con lo básico, pero con limitaciones relevantes",
            -1: "No guarda coherencia o es deficiente respecto al diagnóstico"
        },
        "¿El trabajo entregado tiene materiales nuevos, originales y de marcas reconocidas?": {
            2: "Todos los materiales son nuevos, originales y de marcas reconocidas",
            1: "La mayoría de los materiales cumplen esas condiciones",
            0: "Algunos materiales no son nuevos o no están certificados",
            -1: "Materiales genéricos, usados o sin respaldo de marca"
        },
        "¿Cuenta con acabados homogéneos, limpios y pulidos?": {
            2: "Acabados uniformes, bien presentados y profesionales",
            1: "En general, los acabados son aceptables y limpios",
            0: "Presenta inconsistencias notorias en algunos acabados",
            -1: "Acabados descuidados, sucios o sin terminación adecuada"
        },
        "¿El trabajo entregado corresponde completamente con lo contratado?": {
            2: "Cumple en su totalidad con lo contratado y acordado",
            1: "Cumple en gran parte con lo contratado, con mínimos desvíos",
            0: "Cumple con los requisitos mínimos establecidos",
            -1: "No corresponde con lo contratado o presenta deficiencias importantes"
        },
        "¿La facturación refleja correctamente lo ejecutado y acordado?": {
            2: "Facturación precisa, sin errores y con toda la información requerida",
            1: "Facturación con pequeños errores que no afectan el control",
            0: "Facturación con errores importantes (por ejemplo, precios)",
            -1: "Facturación incorrecta, incompleta o que requiere ser repetida"
        }
    },
    "Oportunidad": {
        "¿La entrega de cotizaciones fue oportuna, según el contrato?": {
            2: "Siempre entrega cotizaciones en los tiempos establecidos",
            1: "Generalmente cumple con los plazos establecidos",
            0: "A veces entrega fuera del tiempo estipulado",
            -1: "Frecuentemente incumple los tiempos o no entrega"
        },
        "¿El reporte del servicio fue entregado oportunamente, según el contrato?": {
            2: "Siempre entrega los reportes a tiempo, según lo acordado",
            1: "Entrega los reportes con mínimos retrasos",
            0: "Entrega con demoras ocasionales",
            -1: "Entrega tardía constante o no entrega"
        },
        "¿Cumple las fechas y horas programadas para los trabajos, según el contrato?": {
            2: "Puntualidad absoluta en fechas y horarios de ejecución",
            1: "Puntualidad general con excepciones menores",
            0: "Cumplimiento parcial o con retrasos frecuentes",
            -1: "Incumplimiento reiterado de horarios o fechas"
        },
        "¿Responde de forma efectiva ante eventualidades emergentes, según el contrato?": {
            2: "Respuesta inmediata y eficaz ante cualquier eventualidad",
            1: "Respuesta adecuada en la mayoría de los casos",
            0: "Respuesta tardía o poco efectiva en varias situaciones",
            -1: "No responde adecuadamente o ignora emergencias"
        },
        "¿Soluciona rápidamente reclamos o inquietudes por garantía, según el contrato?": {
            2: "Soluciona siempre con rapidez y eficacia",
            1: "Responde satisfactoriamente en la mayoría de los casos",
            0: "Respuesta variable, con demoras ocasionales",
            -1: "Soluciones lentas o sin resolver adecuadamente"
        },
        "¿Dispone de los repuestos requeridos en los tiempos necesarios, según el contrato?": {
            2: "Siempre cuenta con repuestos disponibles en el tiempo requerido",
            1: "Generalmente cumple con la disponibilidad de repuestos",
            0: "Disponibilidad intermitente o con retrasos",
            -1: "No garantiza disponibilidad o presenta retrasos constantes"
        },
        "¿Entrega las facturas en los tiempos convenidos, según el contrato?": {
            2: "Entrega siempre puntual de facturas",
            1: "Entrega generalmente puntual con pocas excepciones",
            0: "Entrega ocasionalmente fuera del tiempo acordado",
            -1: "Entrega tarde con frecuencia o no entrega"
        }
    },
    "Precio": {
        "¿Los precios ofrecidos para equipos son competitivos respecto al mercado?": {
            2: "Muy por debajo del precio promedio de mercado",
            1: "Por debajo del promedio de mercado",
            0: "Igual al promedio de mercado",
            -1: "Por encima del promedio de mercado"
        },
        "¿Los precios ofrecidos para repuestos son competitivos respecto al mercado?": {
            2: "Muy por debajo del precio promedio de mercado",
            1: "Por debajo del promedio de mercado",
            0: "Igual al promedio de mercado",
            -1: "Por encima del promedio de mercado"
        },
        "Facilita llegar a una negociación (precios)": {
            2: "Siempre está dispuesto a negociar de manera flexible",
            1: "En general muestra disposición al diálogo",
            0: "Ocasionalmente permite negociar",
            -1: "Poco o nada dispuesto a negociar"
        },
        "Pone en consideración contratos y trabajos adjudicados en el último periodo de tiempo": {
            2: "Siempre toma en cuenta la relación comercial previa",
            1: "Generalmente considera trabajos anteriores",
            0: "Solo ocasionalmente lo toma en cuenta",
            -1: "No muestra continuidad ni reconocimiento de antecedentes"
        },
        "¿Los precios ofrecidos para mantenimientos son competitivos respecto al mercado?": {
            2: "Muy por debajo del precio promedio de mercado",
            1: "Por debajo del promedio de mercado",
            0: "Igual al promedio de mercado",
            -1: "Por encima del promedio de mercado"
        },
        "¿Los precios ofrecidos para insumos son competitivos respecto al mercado?": {
            2: "Muy por debajo del precio promedio de mercado",
            1: "Por debajo del promedio de mercado",
            0: "Igual al promedio de mercado",
            -1: "Por encima del promedio de mercado"
        }
    },
    "Postventa": {
        "¿Tiene disposición y actitud de servicio frente a solicitudes?": {
            2: "Atención proactiva y excelente actitud de servicio",
            1: "Buena actitud y disposición general",
            0: "Actitud pasiva o limitada ante las solicitudes",
            -1: "Falta de disposición o actitudes negativas"
        },
        "¿Conoce necesidades y ofrece alternativas adecuadas?": {
            2: "Conocimiento profundo del cliente y propuestas adecuadas",
            1: "Buen conocimiento y alternativas en general adecuadas",
            0: "Soluciones parcialmente adecuadas",
            -1: "No se adapta a las necesidades o propone soluciones inadecuadas"
        },
        "¿Realiza seguimiento a los resultados de los trabajos?": {
            2: "Hace seguimiento sistemático y detallado",
            1: "Realiza seguimiento general adecuado",
            0: "Seguimiento ocasional o no documentado",
            -1: "No realiza seguimiento posterior"
        },
        "¿Ofrece capacitaciones para el manejo de los equipos?": {
            2: "Capacitaciones constantes y bien estructuradas",
            1: "Capacitaciones ocasionales pero útiles",
            0: "Capacitaciones mínimas o informales",
            -1: "No ofrece capacitaciones"
        },
        "¿Los métodos de capacitación ofrecidos son efectivos y adecuados?": {
            2: "Métodos claros, efectivos y adaptados al usuario",
            1: "Métodos generalmente útiles y comprensibles",
            0: "Métodos poco claros o limitados",
            -1: "Métodos ineficaces o mal estructurados"
        }
    },
    "Desempeño técnico": {
        "Disponibilidad promedio (%)": {
            2: "Disponibilidad >= 98%",
            1: "75% <= Disponibilidad < 98%",
            0: "Disponibilidad < 75%"
        },
        "MTTR promedio (hrs)": {
            2: "MTTR <= 5 hrs",
            1: "5 hrs < MTTR <= 20 hrs",
            0: "MTTR > 20 hrs"
        },
        "MTBF promedio (hrs)": {
            2: "MTBF > 1000 hrs",
            1: "100 hrs <= MTBF <= 1000 hrs",
            0: "MTBF < 100 hrs"
        },
        "Rendimiento promedio equipos": {
            2: "Rendimiento 'Alto' (Disponibilidad >= 90%)",
            1: "Rendimiento 'Medio' (75% <= Disponibilidad < 90%)",
            0: "Rendimiento 'Bajo' (Disponibilidad < 75%)"
        }
    }
}


# --- FUNCIONES DE CÁLCULO DE INDICADORES (Modificadas para calcular por Proveedor dentro de un Tipo de Servicio) ---
def calcular_indicadores(df_filtered_data, group_col='PROVEEDOR'):
    """
    Calcula indicadores de servicio (MTTR, MTBF, Disp, Rendimiento) agrupados por una columna.
    Args:
        df_filtered_data (pd.DataFrame): DataFrame filtrado.
        group_col (str): Columna por la cual agrupar (e.g., 'PROVEEDOR' or 'TIPO DE SERVICIO').
    Returns:
        tuple: Series de Pandas con los indicadores (count, cost, mttr, mtbf, disp, rend) agrupados.
    """
    if df_filtered_data.empty:
        # Return empty Series with appropriate dtypes for robustness
        return (pd.Series(dtype=int), pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=object))

    # Ensure required columns are present
    required_cols = [group_col, 'TIEMPO PARADA', 'COSTO', 'AVISO', 'HORA/ DIA', 'DIAS/ AÑO']
    if not all(col in df_filtered_data.columns for col in required_cols):
        st.error(f"Faltan columnas requeridas para calcular indicadores: {set(required_cols) - set(df_filtered_data.columns)}")
        return (pd.Series(dtype=int), pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=object))

    cnt = df_filtered_data.groupby(group_col)['AVISO'].nunique() # Unique avisos count
    cost = df_filtered_data.groupby(group_col)['COSTO'].sum()
    mttr = df_filtered_data.groupby(group_col)['TIEMPO PARADA'].mean()

    # Calculate ttot (total operating time for a service type for each group)
    ttot = df_filtered_data.groupby(group_col).agg(
        total_horas_anio=('DIAS/ AÑO', 'mean'),
        horas_dia=('HORA/ DIA', 'mean')
    )
    ttot_calculated = (ttot['total_horas_anio'] * ttot['horas_dia']).replace([np.inf, -np.inf], np.nan)
    ttot_calculated = ttot_calculated.fillna(0) # Assume 0 if no valid time info

    down = df_filtered_data.groupby(group_col)['TIEMPO PARADA'].sum()
    fails = df_filtered_data.groupby(group_col)['AVISO'].nunique() # Unique avisos as failures

    # Handle division by zero for MTBF and Disponibilidad
    mtbf = (ttot_calculated - down) / fails.replace(0, np.nan)
    mtbf = mtbf.fillna(0) # Treat as 0 if no failures or ttot is 0

    disp = (mtbf / (mtbf + mttr)).replace([np.inf, -np.inf], np.nan) * 100
    disp = disp.fillna(0) # Treat as 0 if cannot be calculated
    rend = disp.apply(lambda v: 'Alto' if v >= 90 else ('Medio' if v >= 75 else 'Bajo') if not pd.isna(v) else 'No Aplica')

    return cnt, cost, mttr, mtbf, disp, rend

# Function to convert DataFrame to Excel in-memory
def to_excel(df: pd.DataFrame):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# --- COSTOS Y AVISOS APP ---
class CostosAvisosApp:
    def __init__(self, df):
        self.df = df
        self.EJECUTANTE_COL_NAME_NORMALIZED = 'denominacion_ejecutante'
        self.COL_COSTOS_NORMALIZED = 'costes_totreales'
        self.COL_AVISO_NORMALIZED = 'aviso'
        self.COL_FECHA_AVISO_NORMALIZED = 'fecha_de_aviso'
        self.opciones_menu = {
            "Costos por ejecutante": (self.EJECUTANTE_COL_NAME_NORMALIZED, self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por ejecutante": (self.EJECUTANTE_COL_NAME_NORMALIZED, None, "avisos"),
            "Costos por objeto técnico": ("denominacion_de_objeto_tecnico", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por objeto técnico": ("denominacion_de_objeto_tecnico", None, "avisos"),
            "Costos por texto código acción": ("texto_codigo_accion", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por texto código acción": ("texto_codigo_accion", None, "avisos"),
            "Costos por tipo de servicio": ("tipo_de_servicio", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por tipo de servicio": ("tipo_de_servicio", None, "avisos"),
            "Costos por año": ("año", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por año": ("año", None, "avisos"),
            "Costos por mes": ("mes", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por mes": ("mes", None, "avisos"),
            "Costos por categoría de descripción": ("description_category", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por categoría de descripción": ("description_category", None, "avisos"),
        }
        self.tabs_list = ["Análisis General", "Análisis por Tipo de Servicio", "Análisis Detallado de Avisos"]

    def display_costos_avisos_dashboard(self):
        st.header("Dashboard de Costos y Avisos")

        # Add download button here
        if not self.df.empty:
            st.download_button(
                label="Descargar todos los avisos en Excel",
                data=to_excel(self.df),
                file_name="todos_los_avisos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.markdown("---")


        tab_general, tab_tipo_servicio, tab_detallado = st.tabs(self.tabs_list)

        with tab_general:
            self._render_general_analysis_tab()
        with tab_tipo_servicio:
            self._render_service_type_analysis_tab()
        with tab_detallado:
            self._render_detailed_avisos_tab()

    def _render_general_analysis_tab(self):
        st.subheader("Análisis General de Costos y Avisos")

        # Seleccionar la opción de visualización
        st.markdown("**Selecciona un tipo de análisis:**")
        opcion_seleccionada_key = st.selectbox(
            "Visualizar por:",
            list(self.opciones_menu.keys()),
            key="general_analysis_option"
        )
        col_group, col_value, tipo_analisis = self.opciones_menu[opcion_seleccionada_key]

        if self.df.empty:
            st.warning("No hay datos para mostrar. Por favor, carga un archivo primero.")
            return

        if tipo_analisis == "costos":
            st.write(f"#### Costos por {opcion_seleccionada_key.split(' por ')[1].capitalize()}")
            costos_agrupados = self.df.groupby(col_group)[col_value].sum().sort_values(ascending=False).reset_index()
            st.dataframe(costos_agrupados)

            # Plotting
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.barplot(x=col_group, y=col_value, data=costos_agrupados.head(10), ax=ax, palette='viridis')
            ax.set_title(f'Top 10 {opcion_seleccionada_key.split(" por ")[1].capitalize()} por Costos', fontsize=16)
            ax.set_xlabel(opcion_seleccionada_key.split(" por ")[1].capitalize(), fontsize=12)
            ax.set_ylabel('Costos Totales (COP)', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)

        elif tipo_analisis == "avisos":
            st.write(f"#### Cantidad de Avisos por {opcion_seleccionada_key.split(' por ')[1].capitalize()}")
            avisos_agrupados = self.df.groupby(col_group)[self.COL_AVISO_NORMALIZED].nunique().sort_values(ascending=False).reset_index()
            avisos_agrupados.rename(columns={self.COL_AVISO_NORMALIZED: 'Cantidad de Avisos Únicos'}, inplace=True)
            st.dataframe(avisos_agrupados)

            # Plotting
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.barplot(x=col_group, y='Cantidad de Avisos Únicos', data=avisos_agrupados.head(10), ax=ax, palette='mako')
            ax.set_title(f'Top 10 {opcion_seleccionada_key.split(" por ")[1].capitalize()} por Cantidad de Avisos', fontsize=16)
            ax.set_xlabel(opcion_seleccionada_key.split(" por ")[1].capitalize(), fontsize=12)
            ax.set_ylabel('Cantidad de Avisos', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)

    def _render_service_type_analysis_tab(self):
        st.subheader("Análisis de Indicadores por Tipo de Servicio y Proveedor")

        if self.df.empty:
            st.warning("No hay datos para mostrar. Por favor, carga un archivo primero.")
            return

        st.markdown("---")
        st.write("### Indicadores por Tipo de Servicio")
        tipos_servicio = self.df['tipo_de_servicio'].dropna().unique()
        selected_service_type = st.selectbox("Selecciona un Tipo de Servicio para analizar:", tipos_servicio, key="service_type_filter")

        if selected_service_type:
            df_filtered_by_service = self.df[self.df['tipo_de_servicio'] == selected_service_type]
            if not df_filtered_by_service.empty:
                st.write(f"#### Resultados para: {selected_service_type}")
                count, cost, mttr, mtbf, disp, rend = calcular_indicadores(df_filtered_by_service, group_col='PROVEEDOR')

                indicadores_df = pd.DataFrame({
                    'Cantidad de Avisos Únicos': count,
                    'Costo Total': cost,
                    'MTTR Promedio (hrs)': mttr,
                    'MTBF Promedio (hrs)': mtbf,
                    'Disponibilidad (%)': disp,
                    'Rendimiento': rend
                }).reset_index()

                st.dataframe(indicadores_df)

                # Visualización de Indicadores Clave
                st.markdown("---")
                st.write("#### Visualización de Indicadores Clave por Proveedor")

                # Gráfico de Costo Total por Proveedor
                fig1, ax1 = plt.subplots(figsize=(12, 6))
                sns.barplot(x='PROVEEDOR', y='Costo Total', data=indicadores_df.nlargest(10, 'Costo Total'), ax=ax1, palette='coolwarm')
                ax1.set_title(f'Top 10 Proveedores por Costo Total en {selected_service_type}', fontsize=16)
                ax1.set_xlabel('Proveedor', fontsize=12)
                ax1.set_ylabel('Costo Total', fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig1)

                # Gráfico de Disponibilidad por Proveedor
                fig2, ax2 = plt.subplots(figsize=(12, 6))
                sns.barplot(x='PROVEEDOR', y='Disponibilidad (%)', data=indicadores_df.nlargest(10, 'Disponibilidad (%)'), ax=ax2, palette='magma')
                ax2.set_title(f'Top 10 Proveedores por Disponibilidad (%) en {selected_service_type}', fontsize=16)
                ax2.set_xlabel('Proveedor', fontsize=12)
                ax2.set_ylabel('Disponibilidad (%)', fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig2)

            else:
                st.info(f"No hay datos para el tipo de servicio seleccionado: **{selected_service_type}**.")
        else:
            st.info("Por favor, selecciona un tipo de servicio para ver los indicadores.")

    def _render_detailed_avisos_tab(self):
        st.subheader("Análisis Detallado de Avisos")

        if self.df.empty:
            st.warning("No hay datos para mostrar. Por favor, carga un archivo primero.")
            return

        st.markdown("---")
        st.write("### Filtrado y Búsqueda de Avisos")

        col1, col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox(
                "Selecciona un Año:",
                options=[None] + sorted(self.df['año'].dropna().unique().tolist(), reverse=True),
                format_func=lambda x: "Todos los años" if x is None else str(int(x)),
                key="detailed_avisos_year_filter"
            )
        with col2:
            selected_month = st.selectbox(
                "Selecciona un Mes:",
                options=[None] + sorted(self.df['mes'].dropna().unique().tolist()),
                format_func=lambda x: "Todos los meses" if x is None else x,
                key="detailed_avisos_month_filter"
            )

        filtered_df = self.df.copy()
        if selected_year:
            filtered_df = filtered_df[filtered_df['año'] == selected_year]
        if selected_month:
            filtered_df = filtered_df[filtered_df['mes'] == selected_month]

        st.write(f"#### Vista Previa de Avisos (Total: {len(filtered_df)} registros)")
        st.dataframe(filtered_df)

        # Búsqueda por palabra clave en Descripción
        search_query = st.text_input("Buscar en Descripción de Aviso:", key="avisos_search_query")
        if search_query:
            filtered_df = filtered_df[
                filtered_df['descripcion'].astype(str).str.contains(search_query, case=False, na=False)
            ]
            st.write(f"#### Resultados de Búsqueda (Total: {len(filtered_df)} registros)")
            st.dataframe(filtered_df)

# --- SIDEBAR NAVIGATION (existing code) ---
# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state['page'] = 'cargar_datos'

# Sidebar navigation
st.sidebar.title("Menú de Navegación")
if st.sidebar.button("Cargar Datos"):
    st.session_state['page'] = 'cargar_datos'
if st.sidebar.button("Costos y Avisos"):
    st.session_state['page'] = 'costos_avisos'
if st.sidebar.button("Evaluación de Proveedores"):
    st.session_state['page'] = 'evaluacion'

# Define navigation function
def navigate_to(page_name):
    st.session_state['page'] = page_name
    st.experimental_rerun() # Rerun to update page

# --- MAIN APP LOGIC (existing code) ---
if st.session_state['page'] == 'cargar_datos':
    st.header("Cargar Datos de Avisos")
    st.markdown("""
        Por favor, carga aquí tu archivo **Excel (.xlsx)** que contiene las hojas de datos de avisos.
        Asegúrate de que el archivo tenga las hojas `IW29`, `IW39`, `IH08`, `IW65`, y `ZPM015`
        para un correcto procesamiento.
    """)
    uploaded_file = st.file_uploader("Selecciona un archivo Excel", type=["xlsx"])

    if uploaded_file:
        st.info("Archivo cargando y procesando. Esto puede tardar unos segundos...")
        try:
            df = load_and_merge_data(uploaded_file)
            st.session_state['df'] = df
            st.success("¡Datos cargados y procesados exitosamente!")
            st.write("Vista previa de los datos:")
            st.dataframe(df.head())
            st.info("Ahora puedes navegar a las secciones de análisis y evaluación desde el menú lateral.")
            # Automatically navigate to Costos y Avisos for initial display
            navigate_to('costos_avisos')
        except Exception as e:
            st.error(f"Hubo un error al procesar el archivo: {e}")
            st.warning("Asegúrate de que el archivo Excel contenga las hojas correctas y los formatos esperados.")

elif st.session_state['page'] == 'costos_avisos':
    if 'df' in st.session_state and st.session_state['df'] is not None:
        costos_avisos_app = CostosAvisosApp(st.session_state['df'])
        costos_avisos_app.display_costos_avisos_dashboard()
    else:
        st.warning("Por favor, carga los datos primero desde la sección 'Cargar Datos'.")

elif st.session_state['page'] == 'evaluacion':
    # --- EVALUACIÓN DE PROVEEDORES APP ---
    class EvaluacionProveedoresApp:
        def __init__(self, df):
            self.df = df
            self.preguntas_calidad = [p[1] for p in preguntas if p[0] == "Calidad"]
            self.preguntas_oportunidad = [p[1] for p in preguntas if p[0] == "Oportunidad"]
            self.preguntas_precio = [p[1] for p in preguntas if p[0] == "Precio"]
            self.preguntas_postventa = [p[1] for p in preguntas if p[0] == "Postventa"]
            self.preguntas_desempeno_tecnico = [p[1] for p in preguntas if p[0] == "Desempeño técnico"]

        def display_evaluacion_dashboard(self):
            st.header("Evaluación de Proveedores")
            st.markdown("""
                Utiliza esta sección para evaluar a los proveedores basándote en diferentes criterios.
                Selecciona un proveedor y completa las preguntas de evaluación.
            """)

            # Obtener lista de proveedores únicos
            proveedores = self.df['PROVEEDOR'].dropna().unique().tolist()
            if not proveedores:
                st.warning("No hay proveedores disponibles en los datos cargados.")
                return

            selected_proveedor = st.selectbox("Selecciona un Proveedor a evaluar:", proveedores, key="eval_proveedor_select")

            if selected_proveedor:
                st.subheader(f"Evaluación para el Proveedor: **{selected_proveedor}**")

                col_anual, col_mes = st.columns(2)
                with col_anual:
                    selected_eval_year = st.selectbox(
                        "Filtrar por Año:",
                        options=[None] + sorted(self.df['año'].dropna().unique().tolist(), reverse=True),
                        format_func=lambda x: "Todos los años" if x is None else str(int(x)),
                        key="eval_year_filter"
                    )
                with col_mes:
                    selected_eval_month = st.selectbox(
                        "Filtrar por Mes:",
                        options=[None] + sorted(self.df['mes'].dropna().unique().tolist()),
                        format_func=lambda x: "Todos los meses" if x is None else x,
                        key="eval_month_filter"
                    )

                df_proveedor_filtered = self.df[self.df['PROVEEDOR'] == selected_proveedor].copy()

                if selected_eval_year:
                    df_proveedor_filtered = df_proveedor_filtered[df_proveedor_filtered['año'] == selected_eval_year]
                if selected_eval_month:
                    df_proveedor_filtered = df_proveedor_filtered[df_proveedor_filtered['mes'] == selected_eval_month]


                st.markdown("---")
                st.write("### Criterios de Calidad")
                calidad_scores = {}
                for i, pregunta in enumerate(self.preguntas_calidad):
                    opciones_calidad = rangos_detallados["Calidad"][pregunta]
                    valor_seleccionado = st.radio(
                        f"**{pregunta}**",
                        options=list(opciones_calidad.keys()),
                        format_func=lambda x: f"{x} - {opciones_calidad[x]}",
                        key=f"calidad_{i}"
                    )
                    calidad_scores[pregunta] = valor_seleccionado

                st.write("### Criterios de Oportunidad")
                oportunidad_scores = {}
                for i, pregunta in enumerate(self.preguntas_oportunidad):
                    opciones_oportunidad = rangos_detallados["Oportunidad"][pregunta]
                    valor_seleccionado = st.radio(
                        f"**{pregunta}**",
                        options=list(opciones_oportunidad.keys()),
                        format_func=lambda x: f"{x} - {opciones_oportunidad[x]}",
                        key=f"oportunidad_{i}"
                    )
                    oportunidad_scores[pregunta] = valor_seleccionado

                st.write("### Criterios de Precio")
                precio_scores = {}
                for i, pregunta in enumerate(self.preguntas_precio):
                    opciones_precio = rangos_detallados["Precio"][pregunta]
                    valor_seleccionado = st.radio(
                        f"**{pregunta}**",
                        options=list(opciones_precio.keys()),
                        format_func=lambda x: f"{x} - {opciones_precio[x]}",
                        key=f"precio_{i}"
                    )
                    precio_scores[pregunta] = valor_seleccionado

                st.write("### Criterios de Postventa")
                postventa_scores = {}
                for i, pregunta in enumerate(self.preguntas_postventa):
                    opciones_postventa = rangos_detallados["Postventa"][pregunta]
                    valor_seleccionado = st.radio(
                        f"**{pregunta}**",
                        options=list(opciones_postventa.keys()),
                        format_func=lambda x: f"{x} - {opciones_postventa[x]}",
                        key=f"postventa_{i}"
                    )
                    postventa_scores[pregunta] = valor_seleccionado

                # Desempeño técnico (automático)
                st.write("### Criterios de Desempeño Técnico (Calculado Automáticamente)")
                if not df_proveedor_filtered.empty:
                    cnt_prov, cost_prov, mttr_prov, mtbf_prov, disp_prov, rend_prov = calcular_indicadores(df_proveedor_filtered, group_col='PROVEEDOR')

                    desempeno_tecnico_valores = {
                        "Disponibilidad promedio (%)": disp_prov.get(selected_proveedor, 0),
                        "MTTR promedio (hrs)": mttr_prov.get(selected_proveedor, 0),
                        "MTBF promedio (hrs)": mtbf_prov.get(selected_proveedor, 0),
                        "Rendimiento promedio equipos": rend_prov.get(selected_proveedor, "No Aplica")
                    }

                    for pregunta_dt in self.preguntas_desempeno_tecnico:
                        valor_calculado = desempeno_tecnico_valores[pregunta_dt]
                        if pregunta_dt in ["Disponibilidad promedio (%)", "MTTR promedio (hrs)", "MTBF promedio (hrs)"]:
                            st.metric(label=f"**{pregunta_dt}**", value=f"{valor_calculado:.2f}" if isinstance(valor_calculado, (int, float)) else "N/A")
                        else:
                            st.metric(label=f"**{pregunta_dt}**", value=str(valor_calculado))

                else:
                    st.info("No hay datos de desempeño técnico para el proveedor y filtros seleccionados.")

                # Botón para calcular el puntaje total
                if st.button("Calcular Puntaje Total"):
                    total_score = 0
                    num_preguntas_manuales = 0

                    # Sumar puntajes manuales
                    for score_dict in [calidad_scores, oportunidad_scores, precio_scores, postventa_scores]:
                        for score in score_dict.values():
                            if score is not None:
                                total_score += score
                                num_preguntas_manuales += 1

                    # Sumar puntajes de desempeño técnico basados en rangos
                    for pregunta_dt in self.preguntas_desempeno_tecnico:
                        valor_calculado = desempeno_tecnico_valores.get(pregunta_dt)
                        rangos_dt = rangos_detallados["Desempeño técnico"][pregunta_dt]

                        if pregunta_dt == "Disponibilidad promedio (%)":
                            if valor_calculado >= 98:
                                total_score += 2
                            elif 75 <= valor_calculado < 98:
                                total_score += 1
                            else:
                                total_score += 0
                        elif pregunta_dt == "MTTR promedio (hrs)":
                            if valor_calculado <= 5:
                                total_score += 2
                            elif 5 < valor_calculado <= 20:
                                total_score += 1
                            else:
                                total_score += 0
                        elif pregunta_dt == "MTBF promedio (hrs)":
                            if valor_calculado > 1000:
                                total_score += 2
                            elif 100 <= valor_calculado <= 1000:
                                total_score += 1
                            else:
                                total_score += 0
                        elif pregunta_dt == "Rendimiento promedio equipos":
                            if valor_calculado == 'Alto':
                                total_score += 2
                            elif valor_calculado == 'Medio':
                                total_score += 1
                            else:
                                total_score += 0
                        # Increment count for technical performance questions (they are "auto" so always counted)
                        num_preguntas_manuales += 1 # Count as a question contributing to the total

                    st.subheader(f"Puntaje Total para {selected_proveedor}: {total_score} / {num_preguntas_manuales * 2}") # Max score is 2 per question

                    # Determinar el estado general
                    if num_preguntas_manuales > 0:
                        percentage_score = (total_score / (num_preguntas_manuales * 2)) * 100
                        if percentage_score >= 80:
                            st.success(f"**Estado General: Excelente** ({percentage_score:.2f}%)")
                        elif percentage_score >= 60:
                            st.info(f"**Estado General: Bueno** ({percentage_score:.2f}%)")
                        elif percentage_score >= 40:
                            st.warning(f"**Estado General: Regular** ({percentage_score:.2f}%)")
                        else:
                            st.error(f"**Estado General: Deficiente** ({percentage_score:.2f}%)")
                    else:
                        st.info("No se han respondido preguntas para calcular el puntaje.")


            else:
                st.warning("Por favor, selecciona un proveedor para comenzar la evaluación.")

    if 'df' in st.session_state and st.session_state['df'] is not None:
        eval_app = EvaluacionProveedoresApp(st.session_state['df'])
        eval_app.display_evaluacion_dashboard()
    else:
        st.warning("Por favor, carga los datos primero desde la sección 'Cargar Datos'.")
