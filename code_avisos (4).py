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

# --- Set a nice style for plots ---
sns.set_style('whitegrid')

# --- Función de carga & unión (optimizada para Streamlit) ---
@st.cache_data
def load_and_merge_data(uploaded_file_buffer: io.BytesIO) -> pd.DataFrame:
    """
    Carga y fusiona los datos de las diferentes hojas de un archivo Excel.
    Esta función ahora solo carga, fusiona y renombra columnas,
    sin aplicar filtros ni transformaciones de costos.

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

    df_loaded = tmp4[columnas_finales]

    # Normalize column names more robustly from code_avisos (1).py
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
    for col in df_loaded.columns:
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
    df_loaded.columns = normalized_df_columns

    # Assign relevant columns to new, simplified names for easier access
    df_loaded['PROVEEDOR'] = df_loaded['denominacion_ejecutante']
    df_loaded['COSTO'] = df_loaded['costes_totreales']
    df_loaded['TIEMPO PARADA'] = pd.to_numeric(df_loaded['duracion_de_parada'], errors='coerce')
    df_loaded['EQUIPO'] = pd.to_numeric(df_loaded['equipo'], errors='coerce')
    df_loaded['AVISO'] = pd.to_numeric(df_loaded['aviso'], errors='coerce')
    df_loaded['TIPO DE SERVICIO'] = df_loaded['tipo_de_servicio']

    # Ensure 'costes_totreales' is numeric
    df_loaded['costes_totreales'] = pd.to_numeric(df_loaded['costes_totreales'], errors='coerce').fillna(0) # Fill NaN with 0

    # --- HORARIO Mapping ---
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
        "HORARIO_43": (13.5, 312.78), "HORARIO_42": (13.916666667, 312.78), "HORARIO_41": (15, 364.91),
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
    df_loaded['HORARIO'] = df_loaded['texto_equipo'].str.strip().str.upper()
    df_loaded['HORA/ DIA'] = df_loaded['HORARIO'].map(lambda x: horarios_dict.get(x, (None, None))[0])
    df_loaded['DIAS/ AÑO'] = df_loaded['HORARIO'].map(lambda x: horarios_dict.get(x, (None, None))[1])
    df_loaded['DIAS/ AÑO'] = pd.to_numeric(df_loaded['DIAS/ AÑO'], errors='coerce')
    df_loaded['HORA/ DIA'] = pd.to_numeric(df_loaded['HORA/ DIA'], errors='coerce')

    # Ensure 'EQUIPO' is not NaN for core calculations
    df_loaded = df_loaded.dropna(subset=['EQUIPO'])

    # Additional Preprocessing
    df_loaded["fecha_de_aviso"] = pd.to_datetime(df_loaded["fecha_de_aviso"], errors="coerce")
    df_loaded["año"] = df_loaded["fecha_de_aviso"].dt.year
    df_loaded["mes"] = df_loaded["fecha_de_aviso"].dt.strftime("%B") # Month name, e.g., 'January'

    def extract_description_category(description):
        if pd.isna(description):
            return "Otros"
        match = re.match(r'^([A-Z]{2})/', str(description).strip())
        if match:
            return match.group(1)
        return "Otros"

    df_loaded["description_category"] = df_loaded['descripcion'].apply(extract_description_category)
    return df_loaded

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
        "Facilita llegar a una negociación (precios)": { # This question is in rangos_detallados but not in preguntas list, kept for consistency
            2: "Siempre está dispuesto a negociar de manera flexible",
            1: "En general muestra disposición al diálogo",
            0: "Ocasionalmente permite negociar",
            -1: "Poco o nada dispuesto a negociar"
        },
        "Pone en consideración contratos y trabajos adjudicados en el último periodo de tiempo": { # This question is in rangos_detallados but not in preguntas list, kept for consistency
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
class EvaluacionProveedoresApp:
    def __init__(self, df):
        self.df = df
        # Initialize session state for this class if not already done
        if 'all_evaluation_widgets_map' not in st.session_state:
            st.session_state['all_evaluation_widgets_map'] = {}
        if 'evaluation_page_providers' not in st.session_state: # Page for providers
            st.session_state['evaluation_page_providers'] = 0
        if 'current_service_type_metrics' not in st.session_state:
            st.session_state['current_service_type_metrics'] = {} # Metrics now store per-provider for selected service type
        if 'all_service_providers' not in st.session_state:
            st.session_state['all_service_providers'] = []
        if 'selected_service_type' not in st.session_state:
             st.session_state['selected_service_type'] = "Seleccionar..." # Initial dummy value
        if 'evaluation_mode' not in st.session_state:
            st.session_state['evaluation_mode'] = 'by_service_type' # Default mode
        if 'selected_provider_eval' not in st.session_state:
            st.session_state['selected_provider_eval'] = "Seleccionar..."
        if 'evaluation_page_service_types_for_provider' not in st.session_state:
            st.session_state['evaluation_page_service_types_for_provider'] = 0
        if 'current_provider_service_type_metrics' not in st.session_state:
            st.session_state['current_provider_service_type_metrics'] = {}


    def display_evaluation_form(self):
        st.title("Evaluación de Proveedores")

        st.sidebar.markdown("---")
        st.sidebar.header("Modo de Evaluación")
        evaluation_mode = st.sidebar.radio(
            "Selecciona cómo quieres evaluar:",
            options=['Por Tipo de Servicio', 'Por Proveedor'],
            key='evaluation_mode_selector',
            index=0 if st.session_state['evaluation_mode'] == 'by_service_type' else 1
        )

        # Update session state based on radio button selection
        new_mode = 'by_service_type' if evaluation_mode == 'Por Tipo de Servicio' else 'by_provider'
        if st.session_state['evaluation_mode'] != new_mode:
            st.session_state['evaluation_mode'] = new_mode
            st.session_state['evaluation_page_providers'] = 0 # Reset page
            st.session_state['selected_service_type'] = "Seleccionar..." # Reset service type
            st.session_state['selected_provider_eval'] = "Seleccionar..." # Reset provider
            st.session_state['all_evaluation_widgets_map'] = {} # Clear map on mode change
            st.session_state['evaluation_page_service_types_for_provider'] = 0
            st.rerun()

        if st.session_state['evaluation_mode'] == 'by_service_type':
            self._display_evaluation_by_service_type()
        elif st.session_state['evaluation_mode'] == 'by_provider':
            self._display_evaluation_by_provider()


    def _display_evaluation_by_service_type(self):
        st.subheader("Evaluación por Tipo de Servicio")
        
        all_service_types_eval = sorted(self.df['TIPO DE SERVICIO'].dropna().unique().tolist())
        service_type_options = ["Seleccionar..."] + all_service_types_eval
        
        try:
            current_index = service_type_options.index(st.session_state['selected_service_type'])
        except ValueError:
            current_index = 0

        selected_service_type_eval = st.sidebar.selectbox(
            "Selecciona Tipo de Servicio para Evaluar:",
            options=service_type_options,
            index=current_index,
            key='eval_service_type_selector_inner'
        )

        if st.session_state['selected_service_type'] != selected_service_type_eval:
            st.session_state['selected_service_type'] = selected_service_type_eval
            st.session_state['evaluation_page_providers'] = 0
            st.session_state['all_evaluation_widgets_map'] = {} # Clear map on service type change
            st.rerun()

        if st.session_state['selected_service_type'] == "Seleccionar...":
            st.info("Por favor, selecciona un 'Tipo de Servicio' en la barra lateral para comenzar la evaluación.")
            return

        df_filtered_by_service = self.df[self.df['TIPO DE SERVICIO'] == st.session_state['selected_service_type']]
        
        # Get unique providers for the selected service type
        all_service_providers = sorted(df_filtered_by_service['PROVEEDOR'].dropna().unique().tolist())
        st.session_state['all_service_providers'] = all_service_providers # Update global list for plots

        if not all_service_providers:
            st.info(f"No se encontraron proveedores para el tipo de servicio '{st.session_state['selected_service_type']}'.")
            st.session_state['all_evaluation_widgets_map'] = {}
            return

        # Recalculate metrics for all providers under this service type
        cnt_p, cost_p, mttr_p, mtbf_p, disp_p, rend_p = calcular_indicadores(df_filtered_by_service, group_col='PROVEEDOR')
        st.session_state['current_service_type_metrics'] = {
            'cnt': cnt_p, 'cost': cost_p, 'mttr': mttr_p,
            'mtbf': mtbf_p, 'disp': disp_p, 'rend': rend_p
        }

        items_per_page = 5 # Number of providers to show per page
        total_providers = len(all_service_providers)
        max_page = max(0, (total_providers - 1) // items_per_page)

        # Ensure current page is valid after filters or service type change
        if st.session_state['evaluation_page_providers'] > max_page:
            st.session_state['evaluation_page_providers'] = max_page
        if st.session_state['evaluation_page_providers'] < 0:
            st.session_state['evaluation_page_providers'] = 0

        start_index = st.session_state['evaluation_page_providers'] * items_per_page
        end_index = min(start_index + items_per_page, total_providers)
        providers_on_page = all_service_providers[start_index:end_index]

        if not providers_on_page:
            st.info("No hay proveedores para mostrar en esta página para el tipo de servicio seleccionado.")
            st.session_state['all_evaluation_widgets_map'] = {}
            return

        st.markdown("---") # Visual separator
        st.markdown("### Calificación de Preguntas por Proveedor")
        st.info("Utiliza los selectores para asignar una puntuación a cada pregunta por proveedor.")

        # Display provider mapping for the current page
        with st.expander("Ver mapeo de Proveedores en esta página"):
            if providers_on_page:
                for prov_val in providers_on_page:
                    idx = all_service_providers.index(prov_val) + 1
                    st.write(f"**Proveedor {idx}:** `{prov_val}`")
            else:
                st.write("No hay proveedores en esta página para mapear.")

        # Create columns dynamically for questions and providers
        col_widths = [0.4] + [(0.6 / len(providers_on_page)) for _ in providers_on_page]
        cols = st.columns(col_widths)

        # Header row
        with cols[0]:
            st.write("**Pregunta**")
        for i, prov_label in enumerate(providers_on_page):
            with cols[i+1]:
                global_idx = all_service_providers.index(prov_label) + 1
                st.write(f"**Proveedor {global_idx}**")
                st.markdown(f"<p style='font-size: small; text-align: center;'>({prov_label})</p>", unsafe_allow_html=True) # Smaller label
                st.write(" ") # Add spacing for alignment with selectboxes below

        # Questions and Selectboxes/Scores
        for cat, texto, escala in preguntas:
            with cols[0]:
                st.markdown(f"**[{cat}]** {texto}")

            for i, prov_original in enumerate(providers_on_page):
                with cols[i+1]:
                    # Key format: {evaluation_mode}-{service_type/provider_identifier}-{category}-{question_text}-{provider_name (if by service type)}
                    # For by_service_type mode, key is {service_type}-{category}-{question_text}-{provider_name}
                    unique_key = f"{st.session_state['evaluation_mode']}-{st.session_state['selected_service_type']}-{cat}-{texto}-{prov_original}"
                    if escala == "auto":
                        val = 0 # Default value if no specific calculation applies
                        metrics = st.session_state['current_service_type_metrics']

                        # Access provider-specific metrics within the selected service type
                        disp_prov = metrics.get('disp', pd.Series()).get(prov_original, np.nan)
                        mttr_prov = metrics.get('mttr', pd.Series()).get(prov_original, np.nan)
                        mtbf_prov = metrics.get('mtbf', pd.Series()).get(prov_original, np.nan)
                        rend_prov = metrics.get('rend', pd.Series()).get(prov_original, 'No Aplica')

                        if 'Disponibilidad' in texto and not pd.isna(disp_prov):
                            val = 2 if disp_prov >= 98 else (1 if disp_prov >= 75 else 0)
                        elif 'MTTR' in texto and not pd.isna(mttr_prov):
                            val = 2 if mttr_prov <= 5 else (1 if mttr_prov <= 20 else 0)
                        elif 'MTBF' in texto and not pd.isna(mtbf_prov):
                            val = 2 if mtbf_prov > 1000 else (1 if mtbf_prov >= 100 else 0)
                        elif 'Rendimiento' in texto:
                            if rend_prov == 'Alto':
                                val = 2
                            elif rend_prov == 'Medio':
                                val = 1
                            elif rend_prov == 'Bajo':
                                val = 0
                        
                        st.write(f"**{val}**") # Display the numerical score for auto questions
                        
                        # Display the detailed description for the auto-calculated score if available
                        if cat in rangos_detallados and texto in rangos_detallados[cat] and val in rangos_detallados[cat][texto]:
                             st.markdown(f"<p style='font-size: smaller; color: grey;'>({rangos_detallados[cat][texto][val]})</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='font-size: smaller; color: grey;'>(Valor calculado automáticamente)</p>", unsafe_allow_html=True)


                        # Store fixed value in session state to persist
                        st.session_state['all_evaluation_widgets_map'][unique_key] = val
                    else:
                        # Get detailed options for manual questions
                        if cat in rangos_detallados and texto in rangos_detallados[cat]:
                            # Map numerical scores to their descriptions for the selectbox
                            options_dict = rangos_detallados[cat][texto]
                            # Create a list of (value, description) tuples, sorted by value descending for display
                            sorted_options = sorted(options_dict.items(), key=lambda item: item[0], reverse=True)
                            
                            # Create a list of descriptions for the selectbox
                            display_options = [desc for val, desc in sorted_options]
                            # Create a mapping from description back to value
                            desc_to_value_map = {desc: val for val, desc in sorted_options}
                            
                            current_value = st.session_state['all_evaluation_widgets_map'].get(unique_key, 0) # Get existing value or default to 0
                            
                            # Find the current description based on the current_value
                            current_description = next((desc for val, desc in sorted_options if val == current_value), display_options[0])
                            
                            # Get the index of the current_description for the selectbox
                            try:
                                current_index = display_options.index(current_description)
                            except ValueError:
                                current_index = 0 # Default to first option if not found
                            
                            selected_description = st.selectbox(
                                label=" ", # Empty label for cleaner UI
                                options=display_options,
                                key=unique_key,
                                index=current_index,
                            )
                            # Store the numerical value corresponding to the selected description
                            st.session_state['all_evaluation_widgets_map'][unique_key] = desc_to_value_map[selected_description]
                        else:
                            # Fallback if no detailed ranges are defined (shouldn't happen with current data)
                            opts = {'Sobresaliente': 2, 'Bueno': 1, 'Indiferente': 0, 'Malo': -1}
                            current_value = st.session_state['all_evaluation_widgets_map'].get(unique_key, 0)
                            current_label = next((label for label, val in opts.items() if val == current_value), 'Indiferente')
                            current_index = list(opts.keys()).index(current_label)
                            selected_label = st.selectbox(
                                label=" ",
                                options=list(opts.keys()),
                                key=unique_key,
                                index=current_index,
                            )
                            st.session_state['all_evaluation_widgets_map'][unique_key] = opts[selected_label]

        # Pagination buttons
        col_prev, col_next = st.columns([1,1])
        with col_prev:
            if st.button("Anterior", key="prev_eval_page_providers_service_type", disabled=(st.session_state['evaluation_page_providers'] == 0)):
                st.session_state['evaluation_page_providers'] -= 1
                st.rerun() # Use rerun here for page changes, as the content structure changes
        with col_next:
            if st.button("Siguiente", key="next_eval_page_providers_service_type", disabled=(end_index >= total_providers)):
                st.session_state['evaluation_page_providers'] += 1
                st.rerun() # Use rerun here for page changes

        st.markdown("---") # Visual separator
        if st.button("Generar Resumen de Evaluación y Exportar a Excel", key="generate_summary_service_type"):
            self.generar_resumen_evaluacion(df_filtered_by_service, st.session_state['selected_service_type'], mode='by_service_type')

        # Plotting if metrics are available for the selected service type
        metrics = st.session_state.get('current_service_type_metrics', {})
        if metrics:
            st.markdown("#### Distribución de Rendimiento por Proveedor")
            rend_data_for_plot = metrics.get('rend', pd.Series()).dropna()
            if not rend_data_for_plot.empty:
                self.graficar_rendimiento(rend_data_for_plot)
            else:
                st.info("No hay datos de rendimiento de proveedores para graficar para este tipo de servicio.")

            st.markdown("#### Métricas Clave de Desempeño por Proveedor")
            mttr_data_for_plot = metrics.get('mttr', pd.Series()).dropna()
            mtbf_data_for_plot = metrics.get('mtbf', pd.Series()).dropna()
            disp_data_for_plot = metrics.get('disp', pd.Series()).dropna()

            plots_exist = not mttr_data_for_plot.empty or not mtbf_data_for_plot.empty or not disp_data_for_plot.empty
            if plots_exist:
                self.graficar_resumen_proveedor(mttr_data_for_plot, mtbf_data_for_plot, disp_data_for_plot)
            else:
                st.info("No hay datos de MTTR, MTBF o Disponibilidad válidos para graficar de los proveedores para este tipo de servicio.")
        else:
            st.info("No hay métricas de desempeño disponibles para los proveedores de este tipo de servicio.")


    def _display_evaluation_by_provider(self):
        st.subheader("Evaluación por Proveedor Individual")

        all_providers_eval = sorted(self.df['PROVEEDOR'].dropna().unique().tolist())
        provider_options = ["Seleccionar..."] + all_providers_eval
        
        try:
            current_index = provider_options.index(st.session_state['selected_provider_eval'])
        except ValueError:
            current_index = 0

        selected_provider_eval = st.sidebar.selectbox(
            "Selecciona Proveedor para Evaluar:",
            options=provider_options,
            index=current_index,
            key='eval_provider_selector_inner'
        )
        
        if st.session_state['selected_provider_eval'] != selected_provider_eval:
            st.session_state['selected_provider_eval'] = selected_provider_eval
            st.session_state['evaluation_page_service_types_for_provider'] = 0 # Reset page for new provider
            st.session_state['all_evaluation_widgets_map'] = {} # Clear map on provider change
            st.rerun() # Rerun to apply the new provider selection

        if st.session_state['selected_provider_eval'] == "Seleccionar...":
            st.info("Por favor, selecciona un 'Proveedor' en la barra lateral para comenzar la evaluación.")
            return

        # Filter DataFrame for the selected provider across all service types
        df_filtered_by_provider = self.df[self.df['PROVEEDOR'] == st.session_state['selected_provider_eval']]
        
        if df_filtered_by_provider.empty:
            st.info(f"No hay datos para el proveedor '{st.session_state['selected_provider_eval']}'.")
            st.session_state['all_evaluation_widgets_map'] = {}
            return

        # Get unique service types for the selected provider
        all_service_types_for_provider = sorted(df_filtered_by_provider['TIPO DE SERVICIO'].dropna().unique().tolist())
        if not all_service_types_for_provider:
            st.info(f"El proveedor '{st.session_state['selected_provider_eval']}' no tiene tipos de servicio asociados en los datos.")
            return

        # Recalculate metrics for all service types for this provider
        # This will give us MTTR, MTBF, Disp per service type for the selected provider
        provider_service_type_metrics = {}
        for service_type in all_service_types_for_provider:
            df_sub = df_filtered_by_provider[df_filtered_by_provider['TIPO DE SERVICIO'] == service_type]
            # Use a dummy group_col if only one row for service_type is expected in results
            # Otherwise, calcular_indicadores will return a Series, and we need to extract the value for 'service_type'
            cnt, cost, mttr, mtbf, disp, rend = calcular_indicadores(df_sub, group_col='TIPO DE SERVICIO')
            
            # Extract scalar values from the Series returned by calcular_indicadores for the specific service_type
            # .get(service_type, default_value) is safe for Series
            provider_service_type_metrics[service_type] = {
                'cnt': cnt.get(service_type, 0),
                'cost': cost.get(service_type, 0.0),
                'mttr': mttr.get(service_type, np.nan),
                'mtbf': mtbf.get(service_type, np.nan),
                'disp': disp.get(service_type, np.nan),
                'rend': rend.get(service_type, 'No Aplica')
            }
        st.session_state['current_provider_service_type_metrics'] = provider_service_type_metrics


        items_per_page_sts = 5 # Number of service types to show per page
        total_service_types = len(all_service_types_for_provider)
        max_page_sts = max(0, (total_service_types - 1) // items_per_page_sts)

        if st.session_state['evaluation_page_service_types_for_provider'] > max_page_sts:
            st.session_state['evaluation_page_service_types_for_provider'] = max_page_sts
        if st.session_state['evaluation_page_service_types_for_provider'] < 0:
            st.session_state['evaluation_page_service_types_for_provider'] = 0

        start_index_sts = st.session_state['evaluation_page_service_types_for_provider'] * items_per_page_sts
        end_index_sts = min(start_index_sts + items_per_page_sts, total_service_types)
        service_types_on_page = all_service_types_for_provider[start_index_sts:end_index_sts]

        if not service_types_on_page:
            st.info("No hay tipos de servicio para mostrar en esta página para el proveedor seleccionado.")
            return


        st.markdown("---")
        st.markdown(f"### Calificación de Preguntas para el Proveedor: {st.session_state['selected_provider_eval']}")
        st.info("Utiliza los selectores para asignar una puntuación a cada pregunta por tipo de servicio.")

        with st.expander("Ver mapeo de Tipos de Servicio en esta página"):
            if service_types_on_page:
                for st_val in service_types_on_page:
                    idx = all_service_types_for_provider.index(st_val) + 1
                    st.write(f"**Tipo de Servicio {idx}:** `{st_val}`")
            else:
                st.write("No hay tipos de servicio en esta página para mapear.")

        # Create columns dynamically for questions and service types
        col_widths_sts = [0.4] + [(0.6 / len(service_types_on_page)) for _ in service_types_on_page]
        cols_sts = st.columns(col_widths_sts)

        # Header row
        with cols_sts[0]:
            st.write("**Pregunta**")
        for i, service_type_label in enumerate(service_types_on_page):
            with cols_sts[i+1]:
                global_idx = all_service_types_for_provider.index(service_type_label) + 1
                st.write(f"**Tipo de Servicio {global_idx}**")
                st.markdown(f"<p style='font-size: small; text-align: center;'>({service_type_label})</p>", unsafe_allow_html=True)
                st.write(" ")

        # Questions and Selectboxes/Scores
        for cat, texto, escala in preguntas:
            with cols_sts[0]:
                st.markdown(f"**[{cat}]** {texto}")

            for i, service_type_original in enumerate(service_types_on_page):
                with cols_sts[i+1]:
                    # Key format: {mode}-{selected_provider_eval}-{category}-{question_text}-{service_type_original}
                    unique_key = f"{st.session_state['evaluation_mode']}-{st.session_state['selected_provider_eval']}-{cat}-{texto}-{service_type_original}"
                    
                    if escala == "auto":
                        val = 0 # Default
                        # Get metrics specific to this service_type for the selected provider
                        metrics = st.session_state['current_provider_service_type_metrics'].get(service_type_original, {})
                        disp_sts = metrics.get('disp', np.nan)
                        mttr_sts = metrics.get('mttr', np.nan)
                        mtbf_sts = metrics.get('mtbf', np.nan)
                        rend_sts = metrics.get('rend', 'No Aplica')

                        if 'Disponibilidad' in texto and not pd.isna(disp_sts):
                            val = 2 if disp_sts >= 98 else (1 if disp_sts >= 75 else 0)
                        elif 'MTTR' in texto and not pd.isna(mttr_sts):
                            val = 2 if mttr_sts <= 5 else (1 if mttr_sts <= 20 else 0)
                        elif 'MTBF' in texto and not pd.isna(mtbf_sts):
                            val = 2 if mtbf_sts > 1000 else (1 if mtbf_sts >= 100 else 0)
                        elif 'Rendimiento' in texto:
                            if rend_sts == 'Alto': val = 2
                            elif rend_sts == 'Medio': val = 1
                            elif rend_sts == 'Bajo': val = 0
                        
                        st.write(f"**{val}**")
                        if cat in rangos_detallados and texto in rangos_detallados[cat] and val in rangos_detallados[cat][texto]:
                            st.markdown(f"<p style='font-size: smaller; color: grey;'>({rangos_detallados[cat][texto][val]})</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='font-size: smaller; color: grey;'>(Valor calculado automáticamente)</p>", unsafe_allow_html=True)
                        st.session_state['all_evaluation_widgets_map'][unique_key] = val

                    else: # Manual questions
                        if cat in rangos_detallados and texto in rangos_detallados[cat]:
                            options_dict = rangos_detallados[cat][texto]
                            sorted_options = sorted(options_dict.items(), key=lambda item: item[0], reverse=True)
                            display_options = [desc for val, desc in sorted_options]
                            desc_to_value_map = {desc: val for val, desc in sorted_options}
                            
                            current_value = st.session_state['all_evaluation_widgets_map'].get(unique_key, 0)
                            current_description = next((desc for val, desc in sorted_options if val == current_value), display_options[0])
                            
                            try:
                                current_index = display_options.index(current_description)
                            except ValueError:
                                current_index = 0
                            
                            selected_description = st.selectbox(
                                label=" ",
                                options=display_options,
                                key=unique_key,
                                index=current_index,
                            )
                            st.session_state['all_evaluation_widgets_map'][unique_key] = desc_to_value_map[selected_description]
                        else: # Fallback
                            opts = {'Sobresaliente': 2, 'Bueno': 1, 'Indiferente': 0, 'Malo': -1}
                            current_value = st.session_state['all_evaluation_widgets_map'].get(unique_key, 0)
                            current_label = next((label for label, val in opts.items() if val == current_value), 'Indiferente')
                            current_index = list(opts.keys()).index(current_label)
                            selected_label = st.selectbox(
                                label=" ",
                                options=list(opts.keys()),
                                key=unique_key,
                                index=current_index,
                            )
                            st.session_state['all_evaluation_widgets_map'][unique_key] = opts[selected_label]
        
        # Pagination for service types within provider evaluation
        col_prev_sts, col_next_sts = st.columns([1,1])
        with col_prev_sts:
            if st.button("Anterior (Tipos de Servicio)", key="prev_eval_page_sts_for_provider", disabled=(st.session_state['evaluation_page_service_types_for_provider'] == 0)):
                st.session_state['evaluation_page_service_types_for_provider'] -= 1
                st.rerun()
        with col_next_sts:
            if st.button("Siguiente (Tipos de Servicio)", key="next_eval_page_sts_for_provider", disabled=(end_index_sts >= total_service_types)):
                st.session_state['evaluation_page_service_types_for_provider'] += 1
                st.rerun()


        st.markdown("---")
        if st.button("Generar Resumen de Evaluación y Exportar a Excel", key="generate_summary_by_provider"):
            # When generating summary for 'by_provider' mode, we consider the overall performance of the selected provider
            # This means summing scores across all their evaluated service types
            self.generar_resumen_evaluacion(df_filtered_by_provider, st.session_state['selected_provider_eval'], mode='by_provider')

        # Plotting of provider metrics per service type
        metrics = st.session_state.get('current_provider_service_type_metrics', {})
        if metrics:
            st.markdown(f"#### Distribución de Rendimiento del Proveedor '{st.session_state['selected_provider_eval']}' por Tipo de Servicio")
            rend_data_for_plot_sts = pd.Series({k: v['rend'] for k, v in metrics.items() if not pd.isna(v.get('rend'))}).dropna()
            if not rend_data_for_plot_sts.empty:
                self.graficar_rendimiento(rend_data_for_plot_sts)
            else:
                st.info("No hay datos de rendimiento por tipo de servicio para este proveedor.")

            st.markdown(f"#### Métricas Clave de Desempeño del Proveedor '{st.session_state['selected_provider_eval']}' por Tipo de Servicio")
            mttr_data_for_plot_sts = pd.Series({k: v['mttr'] for k, v in metrics.items() if not pd.isna(v.get('mttr'))}).dropna()
            mtbf_data_for_plot_sts = pd.Series({k: v['mtbf'] for k, v in metrics.items() if not pd.isna(v.get('mtbf'))}).dropna()
            disp_data_for_plot_sts = pd.Series({k: v['disp'] for k, v in metrics.items() if not pd.isna(v.get('disp'))}).dropna()

            plots_exist_sts = not mttr_data_for_plot_sts.empty or not mtbf_data_for_plot_sts.empty or not disp_data_for_plot_sts.empty
            if plots_exist_sts:
                self.graficar_resumen_proveedor(mttr_data_for_plot_sts, mtbf_data_for_plot_sts, disp_data_for_plot_sts, axis_label='Tipo de Servicio')
            else:
                st.info("No hay datos de MTTR, MTBF o Disponibilidad válidos para graficar de los tipos de servicio para este proveedor.")
        else:
            st.info("No hay métricas de desempeño disponibles por tipo de servicio para este proveedor.")


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

        if mode == 'by_service_type':
            # This mode evaluates PROVEEDORES within a selected TIPO DE SERVICIO
            st_identifier = identifier # This is the service type selected
            all_providers_for_st = sorted(df_filtered['PROVEEDOR'].dropna().unique().tolist())
            
            # Prepare summary_df_calificacion
            for cat, texto, escala in preguntas:
                row = {'Categoría': cat, 'Pregunta': texto}
                for prov in all_providers_for_st:
                    # Key format: {evaluation_mode}-{service_type/provider_identifier}-{category}-{question_text}-{provider_name (if by service type)}
                    unique_key = f"{mode}-{st_identifier}-{cat}-{texto}-{prov}"
                    score = st.session_state['all_evaluation_widgets_map'].get(unique_key, np.nan)
                    row[prov] = score
                summary_data.append(row)
            summary_df_calificacion = pd.DataFrame(summary_data)
            summary_df_calificacion.set_index(['Categoría', 'Pregunta'], inplace=True)
            total_scores_by_provider = summary_df_calificacion.sum(numeric_only=True)
            summary_df_calificacion.loc[('Total General', 'Puntuación Total')] = total_scores_by_provider.astype(int) # Ensure int

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
            for cat, texto, escala in preguntas:
                row = {'Categoría': cat, 'Pregunta': texto}
                for service_type in all_service_types_for_prov:
                    # Key format: {mode}-{selected_provider_eval}-{category}-{question_text}-{service_type_original}
                    unique_key = f"{mode}-{prov_identifier}-{cat}-{texto}-{service_type}"
                    score = st.session_state['all_evaluation_widgets_map'].get(unique_key, np.nan)
                    row[service_type] = score
                summary_data.append(row)
            summary_df_calificacion = pd.DataFrame(summary_data)
            summary_df_calificacion.set_index(['Categoría', 'Pregunta'], inplace=True)
            total_scores_by_service_type = summary_df_calificacion.sum(numeric_only=True)
            summary_df_calificacion.loc[('Total General', 'Puntuación Total')] = total_scores_by_service_type.astype(int) # Ensure int


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


        if summary_df_calificacion.empty:
            st.warning("No se pudieron generar datos de resumen de evaluación.")
            return

        # Display the summary table
        st.markdown("### Resumen de Calificación por Pregunta")
        st.dataframe(summary_df_calificacion.style.format(precision=0, na_rep='N/A'), use_container_width=True)


        # Display quantitative metrics
        st.markdown(f"### Métricas Cuantitativas")
        st.dataframe(quantitative_metrics_df.style.format(precision=2, na_rep='N/A'), use_container_width=True)


        # To Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            summary_df_calificacion.to_excel(writer, sheet_name='Calificaciones por Pregunta')
            quantitative_metrics_df.to_excel(writer, sheet_name='Metricas Cuantitativas', index=False)

            # Optional: Auto-adjust column widths for better readability
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
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


# --- Page Logic (consolidated into a single if-elif-elif structure) ---
if st.session_state['page'] == 'upload':
    st.title("Carga de Datos")
    st.write("Por favor, sube el archivo Excel que contiene las 5 hojas de datos (IW29, IW39, IH08, IW65, ZPM015).")
    uploaded_file = st.file_uploader("Arrastra aquí tu archivo Excel o haz clic para buscar", type=["xlsx"])

    if uploaded_file:
        st.info("Archivo cargando y procesando. Esto puede tardar unos segundos...")
        try:
            # Usamos io.BytesIO para pasar el archivo como un buffer en memoria
            file_buffer = io.BytesIO(uploaded_file.getvalue())
            
            # Cargar y fusionar datos (sin filtros ni transformaciones de costos aún)
            df_raw = load_and_merge_data(file_buffer)

            # --- Información de Depuración de Costos: Antes de filtros y desduplicación ---
            st.subheader("Información de Depuración de Costos: Estado Inicial")
            if 'costes_totreales' in df_raw.columns:
                st.write(f"Tipo de dato de 'costes_totreales' (inicial): `{df_raw['costes_totreales'].dtype}`")
                st.write(f"Valores nulos en 'costes_totreales' (inicial): `{df_raw['costes_totreales'].isnull().sum()}`")
                st.write("Primeras 5 filas de 'costes_totreales' (inicial):")
                st.write(df_raw['costes_totreales'].head())
            else:
                st.warning("Columna 'costes_totreales' no encontrada después de la carga inicial.")

            
            # --- Procesamiento adicional fuera de la función de carga ---
            # Guardar el DataFrame original para calcular el costo antes de deduplicación
            df_for_cost_comparison = df_raw.copy()

            # 1. Eliminar registros cuyo 'Status del sistema' contenga "PTBO"
            initial_rows_before_ptbo = len(df_raw)
            df_raw = df_raw[~df_raw["status_del_sistema"].str.contains("PTBO", case=False, na=False)]
            df_for_cost_comparison = df_for_cost_comparison[~df_for_cost_comparison["status_del_sistema"].str.contains("PTBO", case=False, na=False)]
            st.info(f"Se eliminaron {initial_rows_before_ptbo - len(df_raw)} registros con 'PTBO' en 'Status del sistema'.")

            # --- Información de Depuración de Costos: Después de filtrar 'PTBO' ---
            st.subheader("Información de Depuración de Costos: Después de filtro 'PTBO'")
            if 'costes_totreales' in df_for_cost_comparison.columns:
                st.write(f"Tipo de dato de 'costes_totreales' (post-PTBO): `{df_for_cost_comparison['costes_totreales'].dtype}`")
                st.write(f"Valores nulos en 'costes_totreales' (post-PTBO): `{df_for_cost_comparison['costes_totreales'].isnull().sum()}`")
                st.write("Primeras 5 filas de 'costes_totreales' (post-PTBO):")
                st.write(df_for_cost_comparison['costes_totreales'].head())
            else:
                st.warning("Columna 'costes_totreales' no encontrada después del filtro 'PTBO'.")

            # Calcular el costo total antes de la deduplicación por aviso
            total_cost_before_deduplication = df_for_cost_comparison['costes_totreales'].sum()
            st.success(f"**Total de Costos Reales (Después de filtrar 'PTBO', Antes de desduplicación por Aviso):** ${total_cost_before_deduplication:,.2f} COP")

            # Contar Avisos duplicados antes de la transformación
            if 'aviso' in df_raw.columns:
                num_duplicated_avisos = df_raw.duplicated(subset=['aviso']).sum()
                st.info(f"Número de avisos duplicados (antes de la desduplicación de costos): {num_duplicated_avisos}")
            
            # 2. Dejar solo una fila con coste por cada aviso (transformación de costos)
            # Esta operación puede cambiar el total de costos si un Aviso tiene múltiples entradas de costo.
            initial_rows_after_ptbo = len(df_raw) # This variable name is slightly confusing, it refers to length of df_raw after PTBO filter
            if 'aviso' in df_raw.columns and 'costes_totreales' in df_raw.columns:
                df_raw['costes_totreales'] = df_raw.groupby('aviso')['costes_totreales'].transform(
                    lambda x: [x.iloc[0]] + [0]*(len(x)-1) if not x.empty else x # Handle empty groups
                )
                df_raw['COSTO'] = df_raw['costes_totreales'] # Update the 'COSTO' alias
                st.info(f"Se aplicó la desduplicación de costos por 'Aviso' (manteniendo solo el primer costo por Aviso y el resto en 0).")
            else:
                st.warning("Columnas 'aviso' o 'costes_totreales' no encontradas para la desduplicación. Este paso fue omitido.")

            # --- Información de Depuración de Costos: Después de la desduplicación por Aviso ---
            st.subheader("Información de Depuración de Costos: Después de desduplicación por Aviso")
            if 'costes_totreales' in df_raw.columns:
                st.write(f"Tipo de dato de 'costes_totreales' (final): `{df_raw['costes_totreales'].dtype}`")
                st.write(f"Valores nulos en 'costes_totreales' (final): `{df_raw['costes_totreales'].isnull().sum()}`")
                st.write("Primeras 5 filas de 'costes_totreales' (final):")
                st.write(df_raw['costes_totreales'].head())
            else:
                st.warning("Columna 'costes_totreales' no encontrada después de la desduplicación.")


            st.success("✅ Datos cargados y procesados exitosamente.")
            st.write(f"**Filas finales (después de filtros y desduplicación):** {len(df_raw)} – **Columnas:** {len(df_raw.columns)}")
            
            # Calcular el costo total después de la deduplicación por aviso
            total_cost_after_deduplication = df_raw['costes_totreales'].sum()
            st.success(f"**Total de Costos Reales (Después de desduplicación por Aviso):** ${total_cost_after_deduplication:,.2f} COP")


            st.markdown("---")
            st.subheader("Vista previa de los datos procesados (primeras 10 filas):")
            st.dataframe(df_raw.head(10)) # Mostrar más filas para una mejor vista previa

            st.markdown("---")
            st.subheader("Descarga de Datos Procesados")

            # Preparar CSV para descarga
            csv_output = df_raw.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar como CSV",
                data=csv_output,
                file_name="avisos_filtrados.csv",
                mime="text/csv",
                help="Descarga el archivo en formato CSV."
            )

            # Preparar Excel para descarga
            excel_buffer = io.BytesIO()
            df_raw.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0) # Rebobinar el buffer antes de enviarlo
            st.download_button(
                label="Descargar como Excel",
                data=excel_buffer,
                file_name="avisos_filtrados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Descarga el archivo en formato XLSX."
            )

            st.markdown("---")
            st.success("¡El procesamiento ha finalizado! Ahora puedes descargar tus datos o seguir explorando.")
            
            # Store the final processed DataFrame in session state
            st.session_state['df'] = df_raw

            # Automatically navigate to Costos y Avisos for initial display
            navigate_to('costos_avisos')

        except Exception as e:
            st.error(f"❌ ¡Ups! Ocurrió un error al procesar el archivo: {e}")
            st.warning("Por favor, verifica que el archivo subido sea `DATA2.XLSX` y tenga el formato de hojas esperado.")
            st.exception(e) # Muestra el traceback completo para depuración
    else: # This 'else' belongs to 'if uploaded_file:'
        st.info("⬆️ Sube tu archivo `DATA2.XLSX` para empezar con el análisis.")

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
