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

# --- Función de carga & unión (optimizada para Streamlit) ---
@st.cache_data
def load_and_merge_data(uploaded_file_buffer: io.BytesIO) -> pd.DataFrame:
    """
    Carga y fusiona los datos de las diferentes hojas de un archivo Excel.

    Args:
        uploaded_file_buffer (io.BytesIO): Buffer del archivo Excel subido por el usuario.

    Returns:
        pd.DataFrame: El DataFrame combinado y limpio.
    """
    # Cargar hojas directamente desde el buffer
    iw29 = pd.read_excel(uploaded_file_buffer, sheet_name=0)
    uploaded_file_buffer.seek(0) # Rebobinar el buffer para leer la siguiente hoja
    iw39 = pd.read_excel(uploaded_file_buffer, sheet_name=1)
    uploaded_file_buffer.seek(0)
    ih08 = pd.read_excel(uploaded_file_buffer, sheet_name=2)
    uploaded_file_buffer.seek(0)
    iw65 = pd.read_excel(uploaded_file_buffer, sheet_name=3)
    uploaded_file_buffer.seek(0)
    zpm015 = pd.read_excel(uploaded_file_buffer, sheet_name=4)

    # Limpiar encabezados
    for df_temp in (iw29, iw39, ih08, iw65, zpm015):
        df_temp.columns = df_temp.columns.str.strip()

    # Guardar "Equipo" original desde IW29 para evitar pérdida
    equipo_original = iw29[["Aviso", "Equipo", "Duración de parada", "Descripción"]].copy()

    # Extraer solo columnas necesarias de iw39 para el merge (incluyendo 'Total general (real)')
    iw39_subset = iw39[["Aviso", "Total general (real)"]]

    # Unir por 'Aviso'
    tmp1 = pd.merge(iw29, iw39_subset, on="Aviso", how="left")
    tmp2 = pd.merge(tmp1, iw65, on="Aviso", how="left")

    # Restaurar el valor original de "Equipo" de IW29 después del merge
    tmp2.drop(columns=["Equipo"], errors='ignore', inplace=True)
    tmp2 = pd.merge(tmp2, equipo_original, on="Aviso", how="left")

    # Unir por 'Equipo' con IH08
    tmp3 = pd.merge(tmp2, ih08[[
        "Equipo", "Inic.garantía prov.", "Fin garantía prov.", "Texto", "Indicador ABC", "Denominación de objeto técnico"
    ]], on="Equipo", how="left")

    # Unir por 'Equipo' con ZPM015
    tmp4 = pd.merge(tmp3, zpm015[["Equipo", "TIPO DE SERVICIO"]], on="Equipo", how="left")

    # Renombrar columnas
    tmp4.rename(columns={
        "Texto": "Texto_equipo",
        "Total general (real)": "Costes tot.reales"
    }, inplace=True)

    columnas_finales = [
        "Aviso", "Orden", "Fecha de aviso", "Código postal", "Status del sistema",
        "Descripción", "Ubicación técnica", "Indicador", "Equipo",
        "Denominación de objeto técnico", "Denominación ejecutante",
        "Duración de parada", "Centro de coste", "Costes tot.reales",
        "Inic.garantía prov.", "Fin garantía prov.", "Texto_equipo",
        "Indicador ABC", "Texto código acción", "Texto de acción",
        "Texto grupo acción", "TIPO DE SERVICIO"
    ]

    # Filtrar solo las columnas que realmente existen en tmp4
    columnas_finales = [col for col in columnas_finales if col in tmp4.columns]

    df = tmp4[columnas_finales]

    # Normalize column names more robustly from code_avisos (1).py
    ORIGINAL_EJECUTANTE_COL_NAME = "Denominación ejecutante"
    ORIGINAL_CP_COL_NAME = "Código postal"
    ORIGINAL_OBJETO_TECNICO_COL_NAME = "Denominación de objeto técnico"
    ORIGINAL_TEXTO_CODIGO_ACCION_COL_NAME = "Texto código acción"
    ORIGINAL_TEXTO_ACCION_COL_NAME = "Texto de acción"
    ORIGINAL_TIPO_SERVICIO_COL_NAME = "TIPO DE SERVICIO" # Changed to match actual column in ZPM015 sheet
    ORIGINAL_COSTOS_COL_NAME = "Costes tot.reales"
    ORIGINAL_DESCRIPTION_COL_NAME = "Descripción"
    ORIGINAL_FECHA_AVISO_COL_NAME = "Fecha de aviso"
    # ORIGINAL_TEXTO_POSICION_COL_NAME = "Texto de Posición" # This is the missing column, keeping commented
    ORIGINAL_TEXTO_EQUIPO_COL_NAME = "Texto_equipo"
    ORIGINAL_DURACION_PARADA_COL_NAME = "Duración de parada"
    ORIGINAL_EQUIPO_COL_COL_NAME = "Equipo"
    ORIGINAL_AVISO_COL_NAME = "Aviso"
    ORIGINAL_STATUS_SISTEMA_COL_NAME = "Status del sistema" # Added for PTBO filtering

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
        # ORIGINAL_TEXTO_POSICION_COL_NAME: "texto_de_posicion", # If this column exists in your data, uncomment
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
            # Fallback for columns not in mapping: normalize to lowercase, replace spaces with underscores, remove periods, handle accents
            normalized_df_columns.append(
                col.lower()
                .strip()
                .replace(" ", "_")
                .replace(".", "")
                .replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            )
    df.columns = normalized_df_columns

    # Assign relevant columns to new, simplified names for easier access (from first code)
    df['PROVEEDOR'] = df['denominacion_ejecutante']
    df['COSTO'] = df['costes_totreales']
    df['TIEMPO PARADA'] = pd.to_numeric(df['duracion_de_parada'], errors='coerce')
    df['EQUIPO'] = pd.to_numeric(df['equipo'], errors='coerce')
    df['AVISO'] = pd.to_numeric(df['aviso'], errors='coerce')
    df['TIPO DE SERVICIO'] = df['tipo_de_servicio']

    # Ensure 'costes_totreales' is numeric
    df['costes_totreales'] = pd.to_numeric(df['costes_totreales'], errors='coerce')

    # --- HORARIO Mapping (from first code) ---
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
    df['HORARIO'] = df['texto_equipo'].str.strip().str.upper()
    df['HORA/ DIA'] = df['HORARIO'].map(lambda x: horarios_dict.get(x, (None, None))[0])
    df['DIAS/ AÑO'] = df['HORARIO'].map(lambda x: horarios_dict.get(x, (None, None))[1])
    df['DIAS/ AÑO'] = pd.to_numeric(df['DIAS/ AÑO'], errors='coerce')
    df['HORA/ DIA'] = pd.to_numeric(df['HORA/ DIA'], errors='coerce')

    # --- Initial Filtering from first code ---
    # Ensure 'EQUIPO' is not NaN for core calculations
    df = df.dropna(subset=['EQUIPO'])

    # --- Additional Preprocessing for Second Code's requirements ---
    df["fecha_de_aviso"] = pd.to_datetime(df["fecha_de_aviso"], errors="coerce")
    df["año"] = df["fecha_de_aviso"].dt.year
    df["mes"] = df["fecha_de_aviso"].dt.strftime("%B") # Month name, e.g., 'January'

    def extract_description_category(description):
        if pd.isna(description):
            return "Otros"
        match = re.match(r'^([A-Z]{2})/', str(description).strip())
        if match:
            return match.group(1)
        return "Otros"

    df["description_category"] = df['descripcion'].apply(extract_description_category)
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
        return (pd.Series(dtype=int), pd.Series(dtype=float), pd.Series(dtype=float),
                pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=object))

    # Ensure required columns are present
    required_cols = [group_col, 'TIEMPO PARADA', 'COSTO', 'AVISO', 'HORA/ DIA', 'DIAS/ AÑO']
    if not all(col in df_filtered_data.columns for col in required_cols):
        st.error(f"Faltan columnas requeridas para calcular indicadores: {set(required_cols) - set(df_filtered_data.columns)}")
        return (pd.Series(dtype=int), pd.Series(dtype=float), pd.Series(dtype=float),
                pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=object))

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
            "Costos por texto de acción": ("texto_de_accion", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por texto de acción": ("texto_de_accion", None, "avisos"),
            "Costos por tipo de servicio": ("tipo_de_servicio", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por tipo de servicio": ("tipo_de_servicio", None, "avisos"),
            "Costos por categoría de descripción": ("description_category", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por categoría de descripción": ("description_category", None, "avisos"),
        }
        
        # Initialize session state for pagination in analysis
        if 'analysis_page' not in st.session_state:
            st.session_state['analysis_page'] = 0


    def display_costos_avisos_dashboard(self):
        st.title("Análisis de Costos y Avisos")

        # Sidebar filters for Costos y Avisos
        st.sidebar.markdown("---")
        st.sidebar.header("Filtros para Análisis")
        all_providers = ['Todos'] + sorted(self.df['PROVEEDOR'].dropna().unique().tolist())
        selected_provider_costos = st.sidebar.selectbox("Selecciona Proveedor:", all_providers, key='costos_provider_filter')

        all_service_types = ['Todos'] + sorted(self.df['TIPO DE SERVICIO'].dropna().unique().tolist())
        selected_service_type_costos = st.sidebar.selectbox("Selecciona Tipo de Servicio:", all_service_types, key='costos_service_type_filter')

        min_date = self.df[self.COL_FECHA_AVISO_NORMALIZED].min().date() if not self.df[self.COL_FECHA_AVISO_NORMALIZED].empty and pd.notna(self.df[self.COL_FECHA_AVISO_NORMALIZED].min()) else pd.to_datetime('2020-01-01').date()
        max_date = self.df[self.COL_FECHA_AVISO_NORMALIZED].max().date() if not self.df[self.COL_FECHA_AVISO_NORMALIZED].empty and pd.notna(self.df[self.COL_FECHA_AVISO_NORMALIZED].max()) else pd.to_datetime('2024-12-31').date()
        date_range = st.sidebar.date_input(
            "Rango de Fechas:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key='costos_date_filter'
        )

        filtered_df_costos = self.df.copy()
        if selected_provider_costos != 'Todos':
            filtered_df_costos = filtered_df_costos[filtered_df_costos['PROVEEDOR'] == selected_provider_costos]
        if selected_service_type_costos != 'Todos':
            filtered_df_costos = filtered_df_costos[filtered_df_costos['TIPO DE SERVICIO'] == selected_service_type_costos]

        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df_costos = filtered_df_costos[
                (filtered_df_costos[self.COL_FECHA_AVISO_NORMALIZED].dt.date >= start_date) &
                (filtered_df_costos[self.COL_FECHA_AVISO_NORMALIZED].dt.date <= end_date)
            ]

        if filtered_df_costos.empty:
            st.warning("No hay datos para los filtros seleccionados.")
            return

        st.markdown("### Resumen General de Costos y Avisos")

        total_costos = filtered_df_costos[self.COL_COSTOS_NORMALIZED].sum()
        total_avisos = filtered_df_costos[self.COL_AVISO_NORMALIZED].nunique()
        avg_costo_por_aviso = total_costos / total_avisos if total_avisos > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Costos Reales", f"${total_costos:,.2f} COP")
        with col2:
            st.metric("Total de Avisos Únicos", f"{total_avisos:,}")
        with col3:
            st.metric("Costo Promedio por Aviso", f"${avg_costo_por_aviso:,.2f} COP")

        st.markdown("---")
        st.markdown("### Análisis Detallado")

        # Selectbox for analysis type
        selected_analysis_key = st.selectbox(
            "Selecciona el tipo de análisis a visualizar:",
            list(self.opciones_menu.keys()),
            key='analysis_type_selector'
        )

        group_col, value_col, analysis_type = self.opciones_menu[selected_analysis_key]

        if analysis_type == "costos":
            st.markdown(f"#### {selected_analysis_key}")
            # Get full sorted data for pagination
            full_data_sorted = filtered_df_costos.groupby(group_col)[value_col].sum().sort_values(ascending=False)
            title = f'Top {selected_analysis_key}'
            xlabel = group_col.replace("_", " ").title()
            ylabel = 'Costo Total ($COP)'
            self._display_paged_table_and_plot(full_data_sorted, title, xlabel, ylabel, "costos")
        elif analysis_type == "avisos":
            st.markdown(f"#### {selected_analysis_key}")
            # Get full sorted data for pagination
            full_data_sorted = filtered_df_costos.groupby(group_col)[self.COL_AVISO_NORMALIZED].nunique().sort_values(ascending=False)
            title = f'Top {selected_analysis_key}'
            xlabel = group_col.replace("_", " ").title()
            ylabel = 'Número de Avisos'
            self._display_paged_table_and_plot(full_data_sorted, title, xlabel, ylabel, "avisos", color_palette='viridis')

        st.markdown("---")
        st.markdown("### Tendencia Mensual de Costos y Avisos")
        df_monthly = filtered_df_costos.set_index(self.COL_FECHA_AVISO_NORMALIZED).resample('M').agg(
            Total_Costos=(self.COL_COSTOS_NORMALIZED, 'sum'),
            Num_Avisos=(self.COL_AVISO_NORMALIZED, 'nunique')
        ).fillna(0)

        fig_monthly, ax_monthly1 = plt.subplots(figsize=(12, 6))
        color = 'tab:red'
        ax_monthly1.set_xlabel('Fecha')
        ax_monthly1.set_ylabel('Total Costos ($COP)', color=color)
        ax_monthly1.plot(df_monthly.index, df_monthly['Total_Costos'], color=color, marker='o')
        ax_monthly1.tick_params(axis='y', labelcolor=color)

        ax_monthly2 = ax_monthly1.twinx()
        color = 'tab:blue'
        ax_monthly2.set_ylabel('Número de Avisos', color=color)
        ax_monthly2.plot(df_monthly.index, df_monthly['Num_Avisos'], color=color, marker='x', linestyle='--')
        ax_monthly2.tick_params(axis='y', labelcolor=color)

        fig_monthly.autofmt_xdate()
        plt.title('Tendencia Mensual de Costos y Avisos')
        st.pyplot(fig_monthly)

        st.markdown("### Detalle de Datos Filtrados (Primeras 100 Filas)")
        st.dataframe(filtered_df_costos[[self.COL_AVISO_NORMALIZED, self.COL_FECHA_AVISO_NORMALIZED, 'PROVEEDOR', 'TIPO DE SERVICIO', 'descripcion', self.COL_COSTOS_NORMALIZED, 'TIEMPO PARADA']].head(100))


    def _plot_bar_chart(self, data, title, xlabel, ylabel, color_palette='coolwarm'):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=data.index, y=data.values, ax=ax, palette=color_palette)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.ticklabel_format(style='plain', axis='y')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout() # Added for better label spacing
        st.pyplot(fig)
        
    def _display_paged_table_and_plot(self, full_data_sorted, title, xlabel, ylabel, analysis_type, color_palette='coolwarm'):
        items_per_page = 10
        total_items = len(full_data_sorted)
        max_page = max(0, (total_items - 1) // items_per_page)

        # Ensure current page is valid
        if st.session_state['analysis_page'] > max_page:
            st.session_state['analysis_page'] = max_page
        if st.session_state['analysis_page'] < 0:
            st.session_state['analysis_page'] = 0

        start_index = st.session_state['analysis_page'] * items_per_page
        end_index = min(start_index + items_per_page, total_items)
        data_to_display = full_data_sorted.iloc[start_index:end_index]

        st.markdown("#### Tabla de Datos")
        # Format costs in the table if it's a costs analysis
        if analysis_type == "costos":
            formatted_df = data_to_display.to_frame(name=ylabel.replace(" ($COP)", "").strip()) # Remove currency from column name for formatting
            formatted_df[formatted_df.columns[0]] = formatted_df[formatted_df.columns[0]].apply(lambda x: f"${x:,.2f} COP")
            st.dataframe(formatted_df, use_container_width=True)
        else:
            st.dataframe(data_to_display.to_frame(), use_container_width=True) # Convert series to dataframe for better display

        col_prev_table, col_next_table = st.columns([1,1])
        with col_prev_table:
            if st.button("Anterior (Tabla)", key=f"prev_analysis_page_{analysis_type}", disabled=(st.session_state['analysis_page'] == 0)):
                st.session_state['analysis_page'] -= 1
                st.rerun()
        with col_next_table:
            if st.button("Siguiente (Tabla)", key=f"next_analysis_page_{analysis_type}", disabled=(end_index >= total_items)):
                st.session_state['analysis_page'] += 1
                st.rerun()

        st.markdown("#### Gráfico")
        self._plot_bar_chart(data_to_display, title, xlabel, ylabel, color_palette)


# --- EVALUATION APP FOR STREAMLIT ---
class EvaluacionApp:
    def __init__(self):
        # Dummy data for demonstration purposes.
        # In your actual application, 'preguntas' and 'df_filtered'
        # would come from your application's state or data loading.
        self.preguntas = [
            ('Calidad', '¿Qué tan satisfecho está con la calidad del servicio?', 5),
            ('Tiempo de Respuesta', '¿El tiempo de respuesta fue adecuado?', 5),
            ('Costo', '¿El costo del servicio fue razonable?', 5)
        ]
        self.df_filtered = pd.DataFrame({
            'PROVEEDOR': ['Proveedor A', 'Proveedor B', 'Proveedor A', 'Proveedor C'],
            'TIPO DE SERVICIO': ['Electricidad', 'Plomería', 'Electricidad', 'Limpieza'],
            'COSTO REAL': [100, 50, 120, 80],
            'MTTR': [2, 1, 3, 1.5],
            'MTBF': [100, 80, 90, 70],
            'DISPONIBILIDAD': [99, 98, 99.5, 97],
            'RENDIMIENTO': ['Bueno', 'Excelente', 'Bueno', 'Regular']
        })
        st.session_state['all_evaluation_widgets_map'] = {
            'by_service_type-Electricidad-Calidad-¿Qué tan satisfecho está con la calidad del servicio?-Proveedor A': 4,
            'by_service_type-Electricidad-Tiempo de Respuesta-¿El tiempo de respuesta fue adecuado?-Proveedor A': 5,
            'by_service_type-Electricidad-Costo-¿El costo del servicio fue razonable?-Proveedor A': 3,
            'by_service_type-Electricidad-Calidad-¿Qué tan satisfecho está con la calidad del servicio?-Proveedor B': 3,
            'by_service_type-Electricidad-Tiempo de Respuesta-¿El tiempo de respuesta fue adecuado?-Proveedor B': 4,
            'by_service_type-Electricidad-Costo-¿El costo del servicio fue razonable?-Proveedor B': 5,
            'by_provider-Proveedor A-Calidad-¿Qué tan satisfecho está con la calidad del servicio?-Electricidad': 4,
            'by_provider-Proveedor A-Tiempo de Respuesta-¿El tiempo de respuesta fue adecuado?-Electricidad': 5,
            'by_provider-Proveedor A-Costo-¿El costo del servicio fue razonable?-Electricidad': 3
        }

        st.session_state['current_service_type_metrics'] = {
            'cnt': pd.Series({'Proveedor A': 2, 'Proveedor B': 1}),
            'cost': pd.Series({'Proveedor A': 220, 'Proveedor B': 50}),
            'mttr': pd.Series({'Proveedor A': 2.5, 'Proveedor B': 1}),
            'mtbf': pd.Series({'Proveedor A': 95, 'Proveedor B': 80}),
            'disp': pd.Series({'Proveedor A': 99.25, 'Proveedor B': 98}),
            'rend': pd.Series({'Proveedor A': 'Bueno', 'Proveedor B': 'Excelente'})
        }

        st.session_state['current_provider_service_type_metrics'] = {
            'Electricidad': {
                'cnt': 2, 'cost': 220, 'mttr': 2.5, 'mtbf': 95, 'disp': 99.25, 'rend': 'Bueno'
            },
            'Plomería': {
                'cnt': 1, 'cost': 50, 'mttr': 1, 'mtbf': 80, 'disp': 98, 'rend': 'Excelente'
            }
        }


    def display_evaluation_form(self):
        st.title("Formulario de Evaluación")

        # Dummy Streamlit session state for selected_provider_eval for demonstration
        if 'selected_provider_eval' not in st.session_state:
            st.session_state['selected_provider_eval'] = 'Proveedor A'
        if 'selected_service_type_eval' not in st.session_state:
            st.session_state['selected_service_type_eval'] = 'Electricidad'

        eval_mode = st.radio("Seleccione el modo de evaluación:", ['by_provider', 'by_service_type'], key='eval_mode_radio')

        if eval_mode == 'by_provider':
            provider_list = sorted(self.df_filtered['PROVEEDOR'].dropna().unique().tolist())
            selected_provider = st.selectbox("Seleccione el Proveedor a Evaluar:", provider_list, key='selected_provider_eval_sb')
            st.session_state['selected_provider_eval'] = selected_provider
            df_filtered_for_eval = self.df_filtered[self.df_filtered['PROVEEDOR'] == selected_provider]
            self._display_evaluation_by_provider(df_filtered_for_eval, self.preguntas)
        elif eval_mode == 'by_service_type':
            service_type_list = sorted(self.df_filtered['TIPO DE SERVICIO'].dropna().unique().tolist())
            selected_service_type = st.selectbox("Seleccione el Tipo de Servicio a Evaluar:", service_type_list, key='selected_service_type_eval_sb')
            st.session_state['selected_service_type_eval'] = selected_service_type
            df_filtered_for_eval = self.df_filtered[self.df_filtered['TIPO DE SERVICIO'] == selected_service_type]
            self._display_evaluation_by_service_type(df_filtered_for_eval, self.preguntas)


    def _display_evaluation_by_provider(self, df_filtered, preguntas):
        # This function would typically gather evaluation inputs and store them
        # For demonstration, we'll just call generar_resumen_evaluacion directly.
        st.subheader(f"Evaluación para el Proveedor: {st.session_state['selected_provider_eval']}")
        self.generar_resumen_evaluacion(df_filtered, st.session_state['selected_provider_eval'], mode='by_provider')

    def _display_evaluation_by_service_type(self, df_filtered, preguntas):
        # This function would typically gather evaluation inputs and store them
        # For demonstration, we'll just call generar_resumen_evaluacion directly.
        st.subheader(f"Evaluación para el Tipo de Servicio: {st.session_state['selected_service_type_eval']}")
        self.generar_resumen_evaluacion(df_filtered, st.session_state['selected_service_type_eval'], mode='by_service_type')


    def generar_resumen_evaluacion(self, df_filtered, identifier, mode):
        st.subheader("Generando resumen de evaluación...")

        if not st.session_state.get('all_evaluation_widgets_map'):
            st.warning("No hay evaluaciones para resumir. Selecciona un modo de evaluación y completa las evaluaciones.")
            return

        summary_data = []
        quantitative_metrics_data = {
            'Identificador de Evaluación': identifier,
            'Tipo de Elemento Evaluado': [],
            'Elemento Evaluado (Nombre)': [], # Could be Provider or Service Type
            'Número de Avisos': [],
            'Costo Total Real': [],
            'MTTR Promedio (hrs)': [],
            'MTBF Promedio (hrs)': [],
            'Disponibilidad Promedio (%)': [],
            'Rendimiento': []
        }

        # Initialize total_scores_by_provider to None before the conditional blocks
        # This ensures it's always defined, even if no mode is met (though in this case, a mode should always be met)
        total_scores = pd.Series(dtype=int) # Initialize with an empty Series of the correct type

        if mode == 'by_service_type':
            # This mode evaluates PROVEEDORES within a selected TIPO DE SERVICIO
            st_identifier = identifier # This is the service type selected
            all_providers_for_st = sorted(df_filtered['PROVEEDOR'].dropna().unique().tolist())
            
            # Prepare summary_df_calificacion
            for cat, texto, escala in self.preguntas: # Use self.preguntas
                row = {'Categoría': cat, 'Pregunta': texto}
                for prov in all_providers_for_st:
                    # Key format: {evaluation_mode}-{service_type/provider_identifier}-{category}-{question_text}-{provider_name (if by service type)}
                    unique_key = f"{mode}-{st_identifier}-{cat}-{texto}-{prov}"
                    score = st.session_state['all_evaluation_widgets_map'].get(unique_key, np.nan)
                    row[prov] = score
                summary_data.append(row)
            summary_df_calificacion = pd.DataFrame(summary_data)
            summary_df_calificacion.set_index(['Categoría', 'Pregunta'], inplace=True)
            total_scores = summary_df_calificacion.sum(numeric_only=True)
            summary_df_calificacion.loc[('Total General', 'Puntuación Total')] = total_scores.astype(int) # Ensure int

            # Quantitative Metrics
            metrics = st.session_state.get('current_service_type_metrics', {})
            cnt_p = metrics.get('cnt', pd.Series())
            cost_p = metrics.get('cost', pd.Series())
            mttr_p = metrics.get('mttr', pd.Series())
            mtbf_p = metrics.get('mtbf', pd.Series())
            disp_p = metrics.get('disp', pd.Series())
            rend_p = metrics.get('rend', pd.Series())

            for prov in all_providers_for_st:
                quantitative_metrics_data['Tipo de Elemento Evaluado'].append('Proveedor')
                quantitative_metrics_data['Elemento Evaluado (Nombre)'].append(prov)
                quantitative_metrics_data['Número de Avisos'].append(cnt_p.get(prov, 0))
                quantitative_metrics_data['Costo Total Real'].append(cost_p.get(prov, 0))
                quantitative_metrics_data['MTTR Promedio (hrs)'].append(mttr_p.get(prov, np.nan))
                quantitative_metrics_data['MTBF Promedio (hrs)'].append(mtbf_p.get(prov, np.nan))
                quantitative_metrics_data['Disponibilidad Promedio (%)'].append(disp_p.get(prov, np.nan))
                quantitative_metrics_data['Rendimiento'].append(rend_p.get(prov, 'No Aplica'))
            
            quantitative_metrics_df = pd.DataFrame(quantitative_metrics_data)
            col_name_for_scores = 'Proveedor'
            ranking_title = f"Ranking de Proveedores para el Tipo de Servicio: {st_identifier}"

        elif mode == 'by_provider':
            # This mode evaluates TIPO DE SERVICIO for a selected PROVEEDOR
            prov_identifier = identifier # This is the provider selected
            all_service_types_for_prov = sorted(df_filtered['TIPO DE SERVICIO'].dropna().unique().tolist())

            # Prepare summary_df_calificacion
            for cat, texto, escala in self.preguntas: # Use self.preguntas
                row = {'Categoría': cat, 'Pregunta': texto}
                for service_type in all_service_types_for_prov:
                    # Key format: {mode}-{selected_provider_eval}-{category}-{question_text}-{service_type_original}
                    unique_key = f"{mode}-{prov_identifier}-{cat}-{texto}-{service_type}"
                    score = st.session_state['all_evaluation_widgets_map'].get(unique_key, np.nan)
                    row[service_type] = score
                summary_data.append(row)
            summary_df_calificacion = pd.DataFrame(summary_data)
            summary_df_calificacion.set_index(['Categoría', 'Pregunta'], inplace=True)
            total_scores = summary_df_calificacion.sum(numeric_only=True)
            summary_df_calificacion.loc[('Total General', 'Puntuación Total')] = total_scores.astype(int) # Ensure int

            # Quantitative Metrics
            metrics_per_service_type = st.session_state.get('current_provider_service_type_metrics', {})
            for service_type in all_service_types_for_prov:
                sts_metrics = metrics_per_service_type.get(service_type, {})
                quantitative_metrics_data['Tipo de Elemento Evaluado'].append('Tipo de Servicio')
                quantitative_metrics_data['Elemento Evaluado (Nombre)'].append(service_type)
                quantitative_metrics_data['Número de Avisos'].append(sts_metrics.get('cnt', 0))
                quantitative_metrics_data['Costo Total Real'].append(sts_metrics.get('cost', 0.0))
                quantitative_metrics_data['MTTR Promedio (hrs)'].append(sts_metrics.get('mttr', np.nan))
                quantitative_metrics_data['MTBF Promedio (hrs)'].append(sts_metrics.get('mtbf', np.nan))
                quantitative_metrics_data['Disponibilidad Promedio (%)'].append(sts_metrics.get('disp', np.nan))
                quantitative_metrics_data['Rendimiento'].append(sts_metrics.get('rend', 'No Aplica'))
            
            quantitative_metrics_df = pd.DataFrame(quantitative_metrics_data)
            col_name_for_scores = 'Tipo de Servicio'
            ranking_title = f"Puntuación por Tipo de Servicio para el Proveedor: {prov_identifier}"
        else: # Handle cases where mode is neither 'by_service_type' nor 'by_provider'
            st.warning("Modo de evaluación no reconocido. No se puede generar el resumen.")
            return

        if summary_df_calificacion.empty:
            st.warning("No se pudieron generar datos de resumen de evaluación.")
            return

        # Display the summary table
        st.markdown("### Resumen de Calificación por Pregunta")
        st.dataframe(summary_df_calificacion.style.format(precision=0, na_rep='N/A'), use_container_width=True)

        # Generate Ranking (or single score for by_provider mode)
        # Use 'total_scores' which is now guaranteed to be defined
        ranking_df = pd.DataFrame({'Puntuación Total': total_scores}).sort_values('Puntuación Total', ascending=False)
        ranking_df.index.name = col_name_for_scores
        
        if mode == 'by_service_type':
            ranking_df['Ranking'] = ranking_df['Puntuación Total'].rank(method='min', ascending=False).astype(int)
            ranking_df = ranking_df.reset_index().set_index('Ranking')
        else: # mode == 'by_provider'
            ranking_df = ranking_df.reset_index()


        st.markdown(f"### {ranking_title}")
        st.dataframe(ranking_df.style.format(precision=0, na_rep='N/A'), use_container_width=True)

        # Display quantitative metrics
        st.markdown(f"### Métricas Cuantitativas")
        st.dataframe(quantitative_metrics_df.style.format(precision=2, na_rep='N/A'), use_container_width=True)


        # To Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            summary_df_calificacion.to_excel(writer, sheet_name='Calificaciones por Pregunta')
            ranking_df.to_excel(writer, sheet_name='Ranking')
            quantitative_metrics_df.to_excel(writer, sheet_name='Metricas Cuantitativas', index=False)

            # Optional: Auto-adjust column widths for better readability
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                # Adjust for potential empty DataFrame before setting column widths
                if not summary_df_calificacion.empty:
                    for idx, col in enumerate(summary_df_calificacion.columns):
                        max_len = max(
                            len(str(col)),
                            (summary_df_calificacion[col].astype(str).map(len).max() if not summary_df_calificacion[col].empty else 0)
                        ) + 2
                        worksheet.set_column(idx, idx, max_len)
                    # For MultiIndex, adjust first few columns manually if needed
                    if sheet_name == 'Calificaciones por Pregunta':
                        worksheet.set_column(0, 0, 20) # Categoría
                        worksheet.set_column(1, 1, 60) # Pregunta

        st.download_button(
            label="Descargar Resumen de Evaluación como Excel",
            data=output.getvalue(),
            file_name=f"Resumen_Evaluacion_{identifier.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download_button_{mode}_{identifier}"
        )

# To run the app, you would instantiate and call the display method
if __name__ == "__main__":
    eval_app = EvaluacionApp()
    eval_app.display_evaluation_form()

    def graficar_rendimiento(self, rendimiento_series):
        if rendimiento_series.empty:
            st.info("No hay datos de rendimiento para graficar.")
            return

        # Count occurrences of each category
        # Ensure consistent order even if a category has 0 occurrences
        rendimiento_counts = rendimiento_series.value_counts().reindex(['Alto', 'Medio', 'Bajo', 'No Aplica'], fill_value=0)

        fig, ax = plt.subplots(figsize=(10, 6))
        # Ensure colors match the meaning: Green for Alto, Amber for Medio, Red for Bajo, Grey for No Aplica
        colors = ['#4CAF50', '#FFC107', '#FF5722', '#9E9E9E']
        
        # Match colors to reindexed order
        ordered_colors = [colors[0] if c == 'Alto' else colors[1] if c == 'Medio' else colors[2] if c == 'Bajo' else colors[3] for c in rendimiento_counts.index]
        
        bars = ax.bar(rendimiento_counts.index, rendimiento_counts.values, color=ordered_colors)
        ax.set_title('Distribución de Rendimiento')
        ax.set_xlabel('Nivel de Rendimiento')
        ax.set_ylabel('Número de Entidades')
        ax.set_ylim(0, rendimiento_counts.max() * 1.1)

        # Add labels on top of bars
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, round(yval, 0), ha='center', va='bottom', fontsize=9) # Add 0.5 for slight offset

        plt.tight_layout()
        st.pyplot(fig)


    def graficar_resumen_proveedor(self, mttr_series, mtbf_series, disp_series, axis_label='Proveedor'):
        # Combine all relevant series into one DataFrame for easy plotting
        plot_df = pd.DataFrame({
            'MTTR (hrs)': mttr_series,
            'MTBF (hrs)': mtbf_series,
            'Disponibilidad (%)': disp_series
        })
        
        # Ensure plot_df has all relevant identifiers, even if some have NaN for certain metrics
        # If axis_label is 'Proveedor', use all_service_providers, otherwise if 'Tipo de Servicio' use all_service_types_for_provider
        if axis_label == 'Proveedor' and st.session_state.get('all_service_providers'):
            plot_df = plot_df.reindex(st.session_state['all_service_providers'])
        elif axis_label == 'Tipo de Servicio' and st.session_state.get('selected_provider_eval') != "Seleccionar...":
            # Get all service types for the currently selected provider to ensure consistency
            # This logic should retrieve the list from where `all_service_types_for_provider` was populated.
            # In the `_display_evaluation_by_provider` method, it's `all_service_types_for_provider`.
            # We can retrieve it from the session state if needed, or simply re-calculate.
            # For simplicity, let's directly re-calculate from df_filtered_by_provider if needed here.
            # This assumes df_filtered_by_provider is accessible or can be recreated.
            
            # Recreate all_service_types_for_provider based on the selected provider.
            # This is less efficient but ensures correctness if session state is complex.
            if 'df' in st.session_state and st.session_state['df'] is not None:
                current_df_for_provider = st.session_state['df'][
                    st.session_state['df']['PROVEEDOR'] == st.session_state['selected_provider_eval']
                ]
                all_service_types_for_current_provider = sorted(
                    current_df_for_provider['TIPO DE SERVICIO'].dropna().unique().tolist()
                )
                plot_df = plot_df.reindex(all_service_types_for_current_provider)


        plot_df = plot_df.fillna(0) # Fill NaN with 0 for plotting purposes if a metric is not available

        if plot_df.empty or len(plot_df) == 0:
            st.info(f"No hay datos suficientes para graficar métricas clave de desempeño por {axis_label}.")
            return

        # Adjust figsize based on number of items to avoid squashing labels
        num_items = len(plot_df)
        fig_height = max(10, num_items * 0.8) # Min height 10, grows with number of items
        fig, axes = plt.subplots(3, 1, figsize=(12, fig_height), sharex=True)
        fig.suptitle(f'Métricas Clave de Desempeño por {axis_label}', fontsize=16)

        # MTTR Plot
        sns.barplot(x=plot_df.index, y='MTTR (hrs)', data=plot_df, ax=axes[0], palette='viridis')
        axes[0].set_title(f'MTTR Promedio por {axis_label}')
        axes[0].set_ylabel('MTTR (hrs)')
        axes[0].tick_params(axis='x', rotation=45)

        # MTBF Plot
        sns.barplot(x=plot_df.index, y='MTBF (hrs)', data=plot_df, ax=axes[1], palette='plasma')
        axes[1].set_title(f'MTBF Promedio por {axis_label}')
        axes[1].set_ylabel('MTBF (hrs)')
        axes[1].tick_params(axis='x', rotation=45)

        # Disponibilidad Plot
        sns.barplot(x=plot_df.index, y='Disponibilidad (%)', data=plot_df, ax=axes[2], palette='cividis')
        axes[2].set_title(f'Disponibilidad Promedio por {axis_label}')
        axes[2].set_ylabel('Disponibilidad (%)')
        axes[2].tick_params(axis='x', rotation=45)
        
        # Set x-axis label only for the bottom plot
        axes[2].set_xlabel(axis_label)

        plt.tight_layout(rect=[0, 0.03, 1, 0.96]) # Adjust layout to prevent title overlap
        st.pyplot(fig)

# --- Main Application Logic (using Streamlit's new structure) ---

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state['page'] = 'upload'

def navigate_to(page):
    st.session_state['page'] = page
    st.rerun()

# Sidebar for navigation
with st.sidebar:
    st.image("https://www.sura.com/blogs/wp-content/uploads/2018/02/LogoSURA.png", width=200) # Replace with actual Sura logo if available
    st.title("Menú Principal")
    if st.button("Cargar Datos", key="nav_upload"):
        navigate_to('upload')
    if 'df' in st.session_state and st.session_state['df'] is not None:
        if st.button("Análisis de Costos y Avisos", key="nav_costos"):
            navigate_to('costos_avisos')
        if st.button("Evaluación de Proveedores", key="nav_evaluacion"):
            navigate_to('evaluacion')
    else:
        st.warning("Carga datos para habilitar otras secciones.")


# --- Page Logic ---
if st.session_state['page'] == 'upload':
    st.title("Carga de Datos")
    st.write("Por favor, sube el archivo Excel que contiene las 5 hojas de datos (IW29, IW39, IH08, IW65, ZPM015).")
    uploaded_file = st.file_uploader("Arrastra aquí tu archivo Excel o haz clic para buscar", type=["xlsx"])

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
    if 'df' in st.session_state and st.session_state['df'] is not None:
        eval_app = EvaluacionProveedoresApp(st.session_state['df'])
        eval_app.display_evaluation_form()
    else:
        st.warning("Por favor, carga los datos primero desde la sección 'Cargar Datos'.")
