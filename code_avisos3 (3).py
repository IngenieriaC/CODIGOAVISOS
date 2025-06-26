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
            "Costos por código postal": ("codigo_postal", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por código postal": ("codigo_postal", None, "avisos"),
            "Costos por descripción de categoría": ("description_category", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por descripción de categoría": ("description_category", None, "avisos"),
            "Costos por mes": ("mes", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por mes": ("mes", None, "avisos")
        }

    def display_costos_avisos_dashboard(self):
        st.header("Análisis de Costos y Avisos")

        st.sidebar.subheader("Filtros de Análisis")
        selected_year = st.sidebar.selectbox("Selecciona Año", ["Todos"] + sorted(self.df['año'].unique().tolist(), reverse=True))
        selected_ejecutante = st.sidebar.selectbox("Selecciona Ejecutante", ["Todos"] + sorted(self.df[self.EJECUTANTE_COL_NAME_NORMALIZED].unique().tolist()))
        selected_objeto_tecnico = st.sidebar.selectbox("Selecciona Objeto Técnico", ["Todos"] + sorted(self.df['denominacion_de_objeto_tecnico'].unique().tolist()))
        selected_description_category = st.sidebar.selectbox("Selecciona Categoría de Descripción", ["Todos"] + sorted(self.df['description_category'].unique().tolist()))

        df_filtered = self.df.copy()

        if selected_year != "Todos":
            df_filtered = df_filtered[df_filtered['año'] == selected_year]
        if selected_ejecutante != "Todos":
            df_filtered = df_filtered[df_filtered[self.EJECUTANTE_COL_NAME_NORMALIZED] == selected_ejecutante]
        if selected_objeto_tecnico != "Todos":
            df_filtered = df_filtered[df_filtered['denominacion_de_objeto_tecnico'] == selected_objeto_tecnico]
        if selected_description_category != "Todos":
            df_filtered = df_filtered[df_filtered['description_category'] == selected_description_category]

        st.subheader("Selecciona el tipo de análisis:")
        selected_analysis_type = st.selectbox(
            "Análisis por:",
            list(self.opciones_menu.keys())
        )

        group_col, value_col, analysis_type = self.opciones_menu[selected_analysis_type]

        if analysis_type == "costos":
            if value_col is None:
                st.warning(f"No se puede realizar un análisis de costos para '{selected_analysis_type}'. Selecciona una opción con costos.")
            else:
                self._display_cost_analysis(df_filtered, group_col, value_col)
        elif analysis_type == "avisos":
            self._display_avisos_analysis(df_filtered, group_col)

    def _display_cost_analysis(self, df_filtered, group_col, value_col):
        st.write(f"### Análisis de Costos por {group_col.replace('_', ' ').title()}")
        if not df_filtered.empty:
            costos_por_grupo = df_filtered.groupby(group_col)[value_col].sum().sort_values(ascending=False).reset_index()
            st.dataframe(costos_por_grupo, use_container_width=True)

            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x=value_col, y=group_col, data=costos_por_grupo.head(10), ax=ax, palette='viridis')
            ax.set_title(f'Top 10 Costos por {group_col.replace("_", " ").title()}')
            ax.set_xlabel('Costos Totales (COP)')
            ax.set_ylabel(group_col.replace('_', ' ').title())
            st.pyplot(fig)
        else:
            st.info("No hay datos para mostrar con los filtros seleccionados.")

    def _display_avisos_analysis(self, df_filtered, group_col):
        st.write(f"### Análisis de Avisos por {group_col.replace('_', ' ').title()}")
        if not df_filtered.empty:
            avisos_por_grupo = df_filtered.groupby(group_col)[self.COL_AVISO_NORMALIZED].nunique().sort_values(ascending=False).reset_index()
            avisos_por_grupo.rename(columns={self.COL_AVISO_NORMALIZED: 'Número de Avisos'}, inplace=True)
            st.dataframe(avisos_por_grupo, use_container_width=True)

            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x='Número de Avisos', y=group_col, data=avisos_por_grupo.head(10), ax=ax, palette='plasma')
            ax.set_title(f'Top 10 Número de Avisos por {group_col.replace("_", " ").title()}')
            ax.set_xlabel('Número de Avisos')
            ax.set_ylabel(group_col.replace('_', ' ').title())
            st.pyplot(fig)
        else:
            st.info("No hay datos para mostrar con los filtros seleccionados.")

# --- EVALUACIÓN DE PROVEEDORES APP ---
class EvaluacionProveedoresApp:
    def __init__(self, df):
        self.df = df
        if 'eval_scores' not in st.session_state:
            st.session_state['eval_scores'] = {}
        if 'selected_provider_eval' not in st.session_state:
            st.session_state['selected_provider_eval'] = None
        if 'selected_service_type_eval' not in st.session_state:
            st.session_state['selected_service_type_eval'] = None
        if 'selected_aviso_eval' not in st.session_state:
            st.session_state['selected_aviso_eval'] = None

    def display_evaluation_form(self):
        st.header("Evaluación de Proveedores")
        st.markdown("""
            Aquí podrás **analizar y gestionar los datos de avisos** para optimizar los procesos.
        """)

        eval_option = st.sidebar.radio(
            "Selecciona una opción de evaluación:",
            ["Evaluación por Proveedor Individual", "Evaluación General de Proveedores"]
        )

        if eval_option == "Evaluación por Proveedor Individual":
            self._display_evaluation_by_provider()
        elif eval_option == "Evaluación General de Proveedores":
            self._display_overall_evaluation()

    def _display_overall_evaluation(self):
        st.subheader("Evaluación General de Proveedores")
        st.write("Esta sección muestra un resumen de las calificaciones de todos los proveedores.")

        if st.button("Generar Resumen de Evaluación y Exportar a Excel"):
            self.generar_resumen_evaluacion(self.df, None, mode='overall')

        # Display overall summary table if available
        if 'overall_ranking_df' in st.session_state and not st.session_state['overall_ranking_df'].empty:
            st.write("### Resumen de Calificación General de Todos los Proveedores")
            st.dataframe(st.session_state['overall_ranking_df'], use_container_width=True)
            self._export_to_excel_button(st.session_state['overall_ranking_df'], "resumen_general_evaluacion_proveedores.xlsx")
        else:
            st.info("Haz clic en 'Generar Resumen de Evaluación' para ver la evaluación general.")

    def _export_to_excel_button(self, df_to_export, filename):
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df_to_export.to_excel(writer, sheet_name='Resumen_Evaluacion', index=True)
        writer.close()
        output.seek(0)
        st.download_button(
            label="Descargar Resumen a Excel",
            data=output,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    def _display_evaluation_by_provider(self):
        st.subheader("Evaluación por Proveedor Individual")

        # Select provider
        providers = ["Seleccionar Proveedor"] + sorted(self.df['PROVEEDOR'].unique().tolist())
        selected_provider = st.selectbox("Selecciona un Proveedor", providers, key='provider_selector_eval')

        if selected_provider != "Seleccionar Proveedor":
            st.session_state['selected_provider_eval'] = selected_provider
            df_filtered_by_provider = self.df[self.df['PROVEEDOR'] == selected_provider].copy()

            # Select service type for the chosen provider
            service_types = ["Seleccionar Tipo de Servicio"] + sorted(df_filtered_by_provider['TIPO DE SERVICIO'].unique().tolist())
            selected_service_type = st.selectbox("Selecciona un Tipo de Servicio", service_types, key='service_type_selector_eval')

            if selected_service_type != "Seleccionar Tipo de Servicio":
                st.session_state['selected_service_type_eval'] = selected_service_type
                df_filtered_by_service_type = df_filtered_by_provider[df_filtered_by_provider['TIPO DE SERVICIO'] == selected_service_type].copy()

                # Select Aviso for the chosen provider and service type
                avisos = ["Seleccionar Aviso"] + sorted(df_filtered_by_service_type['AVISO'].unique().tolist())
                selected_aviso = st.selectbox("Selecciona un Aviso para calificar", avisos, key='aviso_selector_eval')

                if selected_aviso != "Seleccionar Aviso":
                    st.session_state['selected_aviso_eval'] = selected_aviso
                    st.write(f"#### Calificación de Preguntas para el Proveedor: **{selected_provider}**")
                    st.write(f"##### Tipo de Servicio: **{selected_service_type}** | Aviso: **{selected_aviso}**")
                    st.markdown("Utiliza los selectores para asignar una puntuación a cada pregunta por tipo de servicio.")
                    st.markdown("Ver mapeo de Tipos de Servicio en esta página")

                    self._display_question_form(df_filtered_by_service_type, selected_provider, selected_service_type, selected_aviso)

                else:
                    st.info("Por favor, selecciona un Aviso para calificar.")
            else:
                st.info("Por favor, selecciona un Tipo de Servicio para el proveedor.")
        else:
            st.info("Por favor, selecciona un Proveedor para iniciar la evaluación.")

        # Button to generate evaluation summary for the selected provider
        if st.session_state['selected_provider_eval'] and st.button("Generar Resumen de Evaluación y Exportar a Excel"):
            df_filtered_for_summary = self.df[self.df['PROVEEDOR'] == st.session_state['selected_provider_eval']].copy()
            self.generar_resumen_evaluacion(df_filtered_for_summary, st.session_state['selected_provider_eval'], mode='by_provider')

    def _display_question_form(self, df_filtered_by_service_type, selected_provider, selected_service_type, selected_aviso):
        """Displays the question form for evaluation."""
        current_aviso_data = df_filtered_by_service_type[df_filtered_by_service_type['AVISO'] == selected_aviso]

        st.markdown("### Pregunta")

        # Unique key for session state to store scores for each Aviso-Provider combination
        scores_key = f"scores_{selected_aviso}_{selected_provider}"
        if scores_key not in st.session_state:
            st.session_state[scores_key] = {q[1]: 0 for q in preguntas} # Initialize all scores to 0

        col1, col2, col3, col4, col5 = st.columns([0.4, 0.15, 0.15, 0.15, 0.15]) # Adjust column widths

        col1.write("**Categoría y Pregunta**")
        col2.write("**Puntuación**")
        col3.write("**Descripción**")
        col4.write("**Valor Calculado**") # For technical performance indicators
        col5.write("**Valor Ideal**") # For technical performance indicators

        for q_category, question_text, score_type in preguntas:
            with st.container():
                st.markdown("---") # Separador visual para cada pregunta

                cols = st.columns([0.4, 0.15, 0.15, 0.15, 0.15]) # Ensure columns are defined within the loop for fresh layout

                cols[0].markdown(f"**[{q_category}]** {question_text}")

                if score_type == "auto":
                    # Display calculated technical performance indicators
                    if question_text == "Disponibilidad promedio (%)":
                        # Filter for the specific aviso's data to calculate availability for it
                        # Since we're evaluating a single aviso here, we need to calculate its metrics
                        # Note: 'calcular_indicadores' expects a DataFrame, so we pass current_aviso_data
                        _, _, mttr_val, mtbf_val, disp_val, _ = calcular_indicadores(current_aviso_data, group_col='AVISO')
                        display_val = disp_val.iloc[0] if not disp_val.empty else 0
                        cols[3].metric(label="", value=f"{display_val:.2f}%") # Display in column 3
                        # Display range description in column 2 (Puntuación)
                        if 98 <= display_val :
                            cols[2].markdown(f"<p style='color:green;'>{rangos_detallados['Desempeño técnico'][question_text][2]}</p>", unsafe_allow_html=True)
                            st.session_state[scores_key][question_text] = 2
                        elif 75 <= display_val < 98:
                            cols[2].markdown(f"<p style='color:orange;'>{rangos_detallados['Desempeño técnico'][question_text][1]}</p>", unsafe_allow_html=True)
                            st.session_state[scores_key][question_text] = 1
                        else:
                            cols[2].markdown(f"<p style='color:red;'>{rangos_detallados['Desempeño técnico'][question_text][0]}</p>", unsafe_allow_html=True)
                            st.session_state[scores_key][question_text] = 0

                        cols[4].write(">= 98%") # Ideal value in column 4

                    elif question_text == "MTTR promedio (hrs)":
                        _, _, mttr_val, _, _, _ = calcular_indicadores(current_aviso_data, group_col='AVISO')
                        display_val = mttr_val.iloc[0] if not mttr_val.empty else 0
                        cols[3].metric(label="", value=f"{display_val:.2f} hrs")
                        if display_val <= 5 and display_val > 0: # MTTR should ideally be low
                            cols[2].markdown(f"<p style='color:green;'>{rangos_detallados['Desempeño técnico'][question_text][2]}</p>", unsafe_allow_html=True)
                            st.session_state[scores_key][question_text] = 2
                        elif 5 < display_val <= 20:
                            cols[2].markdown(f"<p style='color:orange;'>{rangos_detallados['Desempeño técnico'][question_text][1]}</p>", unsafe_allow_html=True)
                            st.session_state[scores_key][question_text] = 1
                        else: # display_val > 20
                            cols[2].markdown(f"<p style='color:red;'>{rangos_detallados['Desempeño técnico'][question_text][0]}</p>", unsafe_allow_html=True)
                            st.session_state[scores_key][question_text] = 0
                        cols[4].write("<= 5 hrs")

                    elif question_text == "MTBF promedio (hrs)":
                        _, _, _, mtbf_val, _, _ = calcular_indicadores(current_aviso_data, group_col='AVISO')
                        display_val = mtbf_val.iloc[0] if not mtbf_val.empty else 0
                        cols[3].metric(label="", value=f"{display_val:.2f} hrs")
                        if display_val > 1000: # MTBF should ideally be high
                            cols[2].markdown(f"<p style='color:green;'>{rangos_detallados['Desempeño técnico'][question_text][2]}</p>", unsafe_allow_html=True)
                            st.session_state[scores_key][question_text] = 2
                        elif 100 <= display_val <= 1000:
                            cols[2].markdown(f"<p style='color:orange;'>{rangos_detallados['Desempeño técnico'][question_text][1]}</p>", unsafe_allow_html=True)
                            st.session_state[scores_key][question_text] = 1
                        else: # display_val < 100
                            cols[2].markdown(f"<p style='color:red;'>{rangos_detallados['Desempeño técnico'][question_text][0]}</p>", unsafe_allow_html=True)
                            st.session_state[scores_key][question_text] = 0
                        cols[4].write("> 1000 hrs")

                    elif question_text == "Rendimiento promedio equipos":
                        _, _, _, _, disp_val, rend_val = calcular_indicadores(current_aviso_data, group_col='AVISO')
                        display_val = rend_val.iloc[0] if not rend_val.empty else 'N/A'
                        cols[3].metric(label="", value=display_val)
                        # Map rendimiento text to score for consistency
                        if display_val == 'Alto':
                            cols[2].markdown(f"<p style='color:green;'>{rangos_detallados['Desempeño técnico'][question_text][2]}</p>", unsafe_allow_html=True)
                            st.session_state[scores_key][question_text] = 2
                        elif display_val == 'Medio':
                            cols[2].markdown(f"<p style='color:orange;'>{rangos_detallados['Desempeño técnico'][question_text][1]}</p>", unsafe_allow_html=True)
                            st.session_state[scores_key][question_text] = 1
                        else: # Bajo or N/A
                            cols[2].markdown(f"<p style='color:red;'>{rangos_detallados['Desempeño técnico'][question_text][0]}</p>", unsafe_allow_html=True)
                            st.session_state[scores_key][question_text] = 0
                        cols[4].write("Alto (Disp. >= 90%)")

                else:
                    # Manual selection for Quality, Opportunity, Price, Postventa
                    options = list(rangos_detallados[q_category][question_text].keys())
                    options_display = [f"{k}: {rangos_detallados[q_category][question_text][k]}" for k in options]
                    
                    # Find the index of the previously selected score for this question
                    current_score = st.session_state[scores_key].get(question_text, 0)
                    try:
                        default_index = options.index(current_score)
                    except ValueError:
                        default_index = 0 # Default to 0 if not found

                    selected_score = cols[1].selectbox(
                        "Puntuación",
                        options=options,
                        index=default_index,
                        key=f"{selected_aviso}_{selected_provider}_{question_text}" # Unique key for each selectbox
                    )
                    st.session_state[scores_key][question_text] = selected_score
                    cols[2].write(rangos_detallados[q_category][question_text][selected_score])
                    cols[3].write("N/A") # No calculated value for manual questions
                    cols[4].write("N/A") # No ideal value for manual questions

        st.markdown("---") # End of question form separator

    def generar_resumen_evaluacion(self, df_filtered, selected_item, mode='by_provider'):
        st.subheader("Generando resumen de evaluación...")

        # Initialize total_scores_by_provider to an empty dictionary
        # This resolves the UnboundLocalError if 'mode' is not 'by_provider'
        total_scores_by_provider = {}

        if mode == 'by_provider':
            st.write(f"### Resumen de Calificación por Pregunta para {selected_item}")

            # Define the structure for storing scores by question and service type
            question_scores_by_service_type = {}
            for service_type in df_filtered['tipo_de_servicio'].unique():
                question_scores_by_service_type[service_type] = {q[1]: [] for q in preguntas}

            # Group by 'Aviso' to process each record
            for index, row in df_filtered.iterrows():
                aviso_id = row['aviso']
                service_type = row['tipo_de_servicio']

                # Ensure service_type exists in our structure
                if service_type not in question_scores_by_service_type:
                    question_scores_by_service_type[service_type] = {q[1]: [] for q in preguntas}

                # Retrieve scores for the current aviso, for the selected provider
                if f"scores_{aviso_id}_{selected_item}" in st.session_state:
                    scores_for_aviso = st.session_state[f"scores_{aviso_id}_{selected_item}"]

                    for q_category, question_text, q_type in preguntas:
                        if question_text in scores_for_aviso:
                            score = scores_for_aviso[question_text]
                            question_scores_by_service_type[service_type][question_text].append(score)

            # Calculate average score per question per service type
            avg_scores_display = []
            for service_type, questions_data in question_scores_by_service_type.items():
                for question_text, scores_list in questions_data.items():
                    if scores_list:
                        avg_score = np.mean(scores_list)
                        avg_scores_display.append({
                            "Tipo de Servicio": service_type,
                            "Pregunta": question_text,
                            "Puntuación Promedio": f"{avg_score:.2f}"
                        })

            if avg_scores_display:
                df_avg_scores = pd.DataFrame(avg_scores_display)
                st.dataframe(df_avg_scores, use_container_width=True)
            else:
                st.info("No hay calificaciones para mostrar para este proveedor.")

            # Calculate total scores by provider based on current session state for all relevant avisos
            total_scores_by_provider = {}
            for aviso_id_key in st.session_state.keys():
                if aviso_id_key.startswith("scores_"):
                    # Extract aviso_id and provider_name from the key
                    parts = aviso_id_key.split('_')
                    current_aviso_id = int(parts[1])
                    current_provider_name = '_'.join(parts[2:])

                    # Only process scores for the selected provider for the by_provider mode
                    if current_provider_name == selected_item:
                        scores_for_aviso = st.session_state[aviso_id_key]
                        total_score_aviso = sum(scores_for_aviso.values())

                        if current_provider_name not in total_scores_by_provider:
                            total_scores_by_provider[current_provider_name] = 0
                        total_scores_by_provider[current_provider_name] += total_score_aviso

            if total_scores_by_provider:
                st.write("### Resumen de Calificación General por Proveedor")
                ranking_df = pd.DataFrame({'Puntuación Total': total_scores_by_provider}).sort_values('Puntuación Total', ascending=False)
                st.dataframe(ranking_df, use_container_width=True)
                self._export_to_excel_button(ranking_df, f"resumen_evaluacion_{selected_item.replace(' ', '_')}.xlsx")
            else:
                st.info("No se han registrado calificaciones totales para el proveedor seleccionado.")

        elif mode == 'overall':
            st.write("### Resumen de Calificación General de Todos los Proveedores")
            all_providers_scores = {}

            # Iterate through all avisos and sum up scores for each provider
            for aviso_id_key in st.session_state.keys():
                if aviso_id_key.startswith("scores_"):
                    # Extract aviso_id and provider_name from the key
                    parts = aviso_id_key.split('_')
                    current_aviso_id = int(parts[1])
                    current_provider_name = '_'.join(parts[2:])

                    scores_for_aviso = st.session_state[aviso_id_key]
                    total_score_aviso = sum(scores_for_aviso.values())

                    if current_provider_name not in all_providers_scores:
                        all_providers_scores[current_provider_name] = 0
                    all_providers_scores[current_provider_name] += total_score_aviso

            if all_providers_scores:
                ranking_df = pd.DataFrame({'Puntuación Total': all_providers_scores}).sort_values('Puntuación Total', ascending=False)
                st.session_state['overall_ranking_df'] = ranking_df # Store for later display
                st.dataframe(ranking_df, use_container_width=True)
                self._export_to_excel_button(ranking_df, "resumen_general_evaluacion_proveedores.xlsx")
            else:
                st.info("No se han registrado calificaciones para ningún proveedor.")

        st.success("Resumen de evaluación generado.")


# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navegación")
opciones_navegacion = {
    "Cargar Datos": 'upload',
    "Análisis de Costos y Avisos": 'costos_avisos',
    "Evaluación de Proveedores": 'evaluacion'
}

# Initialize session state for page if not already set
if 'page' not in st.session_state:
    st.session_state['page'] = 'upload'

# Handle navigation clicks
for opcion_display, opcion_key in opciones_navegacion.items():
    if st.sidebar.button(opcion_display, key=f"nav_{opcion_key}"):
        st.session_state['page'] = opcion_key

# --- MAIN CONTENT RENDERING BASED ON PAGE STATE ---
if st.session_state['page'] == 'upload':
    st.header("Cargar Datos para Análisis")
    st.write("Por favor, sube el archivo Excel consolidado de avisos para iniciar el análisis.")
    uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

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


# Dummy function for navigation, replace if using a more complex navigation system
def navigate_to(page_name):
    st.session_state['page'] = page_name
