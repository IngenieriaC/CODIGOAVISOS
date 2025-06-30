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
        background-color: #FFD700; /* Amarillo Oro */
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #FFA500; /* Naranja para el hover */
    }
    /* Expander - para secciones colapsables */
    .streamlit-expanderHeader {
        background-color: #4169E1; /* Azul Rey para el encabezado del expander */
        color: white;
        border-radius: 5px;
        padding: 10px;
    }
    .streamlit-expanderContent {
        background-color: #F0F8FF; /* Azul claro para el contenido del expander */
        border-left: 5px solid #4169E1;
        padding: 10px;
    }
    /* Tablas y dataframes */
    .dataframe {
        border: 1px solid #ddd;
        border-collapse: collapse;
        width: 100%;
    }
    .dataframe th, .dataframe td {
        padding: 8px;
        border: 1px solid #ddd;
        text-align: left;
    }
    .dataframe th {
        background-color: #4169E1;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Navegación de la página ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'cargar_datos' # Página inicial

def navigate_to(page_name):
    st.session_state['page'] = page_name
    st.rerun()

st.sidebar.title("Menú Principal")
if st.sidebar.button("Cargar Datos"):
    navigate_to('cargar_datos')
if st.sidebar.button("Costos y Avisos"):
    navigate_to('costos_avisos')
if st.sidebar.button("Evaluación de Proveedores"):
    navigate_to('evaluacion')

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

# --- Funciones y Clases para la segunda parte del código (mantienen su lógica original) ---

def calcular_indicadores(df: pd.DataFrame) -> dict:
    """Calcula indicadores clave para el dashboard de costos y avisos."""
    if df.empty:
        return {
            'total_avisos': 0,
            'costo_total': 0,
            'avisos_con_costo': 0,
            'tiempo_parada_total': 0,
            'avisos_con_tiempo_parada': 0,
            'costo_promedio_aviso': 0,
            'tiempo_parada_promedio_aviso': 0
        }

    total_avisos = df['aviso'].nunique()
    costo_total = df['COSTO'].sum()
    avisos_con_costo = df[df['COSTO'].notna() & (df['COSTO'] > 0)]['aviso'].nunique()
    tiempo_parada_total = df['TIEMPO PARADA'].sum()
    avisos_con_tiempo_parada = df[df['TIEMPO PARADA'].notna() & (df['TIEMPO PARADA'] > 0)]['aviso'].nunique()

    costo_promedio_aviso = costo_total / avisos_con_costo if avisos_con_costo > 0 else 0
    tiempo_parada_promedio_aviso = tiempo_parada_total / avisos_con_tiempo_parada if avisos_con_tiempo_parada > 0 else 0

    return {
        'total_avisos': total_avisos,
        'costo_total': costo_total,
        'avisos_con_costo': avisos_con_costo,
        'tiempo_parada_total': tiempo_parada_total,
        'avisos_con_tiempo_parada': avisos_con_tiempo_parada,
        'costo_promedio_aviso': costo_promedio_aviso,
        'tiempo_parada_promedio_aviso': tiempo_parada_promedio_aviso
    }

def rangos_detallados(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula rangos detallados de costos y tiempo de parada."""
    if df.empty:
        return pd.DataFrame(columns=[
            'Rango Costos', 'Cantidad Avisos', '% Avisos', 'Costo Acumulado', '% Costo Acumulado',
            'Rango Tiempo Parada', 'Cantidad Avisos Parada', '% Avisos Parada', 'Tiempo Parada Acumulado', '% Tiempo Parada Acumulado'
        ])

    df_costo_sorted = df.dropna(subset=['COSTO']).sort_values(by='COSTO', ascending=False)
    df_tiempo_sorted = df.dropna(subset=['TIEMPO PARADA']).sort_values(by='TIEMPO PARADA', ascending=False)

    total_avisos_costo = df_costo_sorted['aviso'].nunique()
    total_costo = df_costo_sorted['COSTO'].sum()

    total_avisos_parada = df_tiempo_sorted['aviso'].nunique()
    total_tiempo_parada = df_tiempo_sorted['TIEMPO PARADA'].sum()

    # Rangos de costo
    cost_bins = [0, 500, 1000, 5000, 10000, 50000, np.inf]
    cost_labels = ['0-500', '501-1K', '1K-5K', '5K-10K', '10K-50K', '>50K']
    df_costo_sorted['Rango Costos'] = pd.cut(df_costo_sorted['COSTO'], bins=cost_bins, labels=cost_labels, right=True)

    cost_summary = df_costo_sorted.groupby('Rango Costos').agg(
        Cantidad_Avisos=('aviso', 'nunique'),
        Costo_Acumulado=('COSTO', 'sum')
    ).reset_index()

    cost_summary['% Avisos'] = (cost_summary['Cantidad_Avisos'] / total_avisos_costo * 100).fillna(0)
    cost_summary['% Costo Acumulado'] = (cost_summary['Costo_Acumulado'] / total_costo * 100).fillna(0)

    # Rangos de tiempo de parada
    time_bins = [0, 1, 5, 10, 24, 48, np.inf] # Horas
    time_labels = ['0-1hr', '1-5hrs', '5-10hrs', '10-24hrs', '24-48hrs', '>48hrs']
    df_tiempo_sorted['Rango Tiempo Parada'] = pd.cut(df_tiempo_sorted['TIEMPO PARADA'], bins=time_bins, labels=time_labels, right=True)

    time_summary = df_tiempo_sorted.groupby('Rango Tiempo Parada').agg(
        Cantidad_Avisos_Parada=('aviso', 'nunique'),
        Tiempo_Parada_Acumulado=('TIEMPO PARADA', 'sum')
    ).reset_index()

    time_summary['% Avisos Parada'] = (time_summary['Cantidad_Avisos_Parada'] / total_avisos_parada * 100).fillna(0)
    time_summary['% Tiempo Parada Acumulado'] = (time_summary['Tiempo_Parada_Acumulado'] / total_tiempo_parada * 100).fillna(0)

    # Unir ambos resúmenes para mostrar juntos
    full_summary = pd.merge(cost_summary, time_summary, how='outer', left_index=True, right_index=True)

    # CORRECCIÓN: Rellenar NaN solo en columnas numéricas para evitar TypeError con CategoricalDtype
    numeric_cols = full_summary.select_dtypes(include=np.number).columns
    full_summary[numeric_cols] = full_summary[numeric_cols].fillna(0)

    return full_summary


class CostosAvisosApp:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def display_costos_avisos_dashboard(self):
        st.header("Análisis de Costos y Avisos")

        if self.df.empty:
            st.warning("No hay datos para mostrar. Por favor, carga los datos primero.")
            return

        st.subheader("Filtros")
        col1, col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox(
                "Selecciona el Año",
                options=['Todos'] + sorted(self.df['año'].dropna().unique().astype(int).tolist(), reverse=True)
            )
        with col2:
            available_months = ['Todos']
            if selected_year != 'Todos':
                available_months += sorted(self.df[self.df['año'] == selected_year]['mes'].dropna().unique().tolist())
            else:
                available_months += sorted(self.df['mes'].dropna().unique().tolist())

            selected_month = st.selectbox(
                "Selecciona el Mes",
                options=available_months
            )

        filtered_df = self.df.copy()
        if selected_year != 'Todos':
            filtered_df = filtered_df[filtered_df['año'] == selected_year]
        if selected_month != 'Todos':
            filtered_df = filtered_df[filtered_df['mes'] == selected_month]

        indicadores = calcular_indicadores(filtered_df)

        st.subheader("Indicadores Clave")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Avisos Únicos", f"{indicadores['total_avisos']:,}")
        col2.metric("Costo Total (€)", f"{indicadores['costo_total']:.2f}€")
        col3.metric("Tiempo de Parada Total (Horas)", f"{indicadores['tiempo_parada_total']:.2f} hrs")
        col4.metric("Costo Promedio por Aviso (€)", f"{indicadores['costo_promedio_aviso']:.2f}€")

        st.subheader("Desglose por Categoría de Descripción")
        if 'description_category' in filtered_df.columns and not filtered_df.empty:
            category_summary = filtered_df.groupby('description_category').agg(
                Total_Costos=('COSTO', 'sum'),
                Total_Tiempo_Parada=('TIEMPO PARADA', 'sum'),
                Cantidad_Avisos=('aviso', 'nunique')
            ).sort_values(by='Total_Costos', ascending=False).reset_index()

            st.dataframe(category_summary.style.format({
                'Total_Costos': "{:.2f}€",
                'Total_Tiempo_Parada': "{:.2f} hrs"
            }), use_container_width=True)

            fig1, ax1 = plt.subplots(figsize=(10, 6))
            sns.barplot(x='description_category', y='Total_Costos', data=category_summary, ax=ax1, palette='viridis')
            ax1.set_title('Costos por Categoría de Descripción')
            ax1.set_xlabel('Categoría de Descripción')
            ax1.set_ylabel('Costo Total (€)')
            ax1.tick_params(axis='x', rotation=45)
            st.pyplot(fig1)

            fig2, ax2 = plt.subplots(figsize=(10, 6))
            sns.barplot(x='description_category', y='Total_Tiempo_Parada', data=category_summary, ax=ax2, palette='magma')
            ax2.set_title('Tiempo de Parada por Categoría de Descripción')
            ax2.set_xlabel('Categoría de Descripción')
            ax2.set_ylabel('Tiempo de Parada Total (Horas)')
            ax2.tick_params(axis='x', rotation=45)
            st.pyplot(fig2)
        else:
            st.info("No hay datos de categoría de descripción disponibles o la columna no existe.")


        st.subheader("Análisis de Rangos de Costos y Tiempos de Parada")
        if not filtered_df.empty:
            rangos_df = rangos_detallados(filtered_df)
            st.dataframe(rangos_df.style.format({
                'Costo Acumulado': "{:.2f}€",
                '% Costo Acumulado': "{:.2f}%",
                'Tiempo Parada Acumulado': "{:.2f} hrs",
                '% Tiempo Parada Acumulado': "{:.2f}%"
            }), use_container_width=True)
        else:
            st.info("No hay datos para analizar rangos.")

        st.subheader("Tendencia de Costos y Avisos por Mes")
        if 'fecha_de_aviso' in filtered_df.columns and not filtered_df.empty:
            # Asegurarse de que la columna sea de tipo datetime y manejar NaT
            filtered_df_valid_dates = filtered_df.dropna(subset=['fecha_de_aviso']).copy()
            if not filtered_df_valid_dates.empty:
                filtered_df_valid_dates['Mes_Año'] = filtered_df_valid_dates['fecha_de_aviso'].dt.to_period('M')
                monthly_summary = filtered_df_valid_dates.groupby('Mes_Año').agg(
                    Total_Costos=('COSTO', 'sum'),
                    Cantidad_Avisos=('aviso', 'nunique')
                ).reset_index()
                monthly_summary['Mes_Año'] = monthly_summary['Mes_Año'].astype(str) # Para graficar mejor

                fig3, ax3 = plt.subplots(figsize=(12, 6))
                sns.lineplot(x='Mes_Año', y='Total_Costos', data=monthly_summary, marker='o', ax=ax3, label='Costo Total')
                ax4 = ax3.twinx()
                sns.lineplot(x='Mes_Año', y='Cantidad_Avisos', data=monthly_summary, marker='x', color='red', ax=ax4, label='Cantidad de Avisos')
                ax3.set_title('Tendencia Mensual de Costos y Cantidad de Avisos')
                ax3.set_xlabel('Mes y Año')
                ax3.set_ylabel('Costo Total (€)', color=sns.color_palette('viridis')[0])
                ax4.set_ylabel('Cantidad de Avisos', color='red')
                fig3.legend(loc="upper left", bbox_to_anchor=(0.1,0.9))
                ax3.tick_params(axis='x', rotation=45)
                st.pyplot(fig3)
            else:
                st.info("No hay datos de fecha de aviso válidos para mostrar la tendencia.")
        else:
            st.info("La columna 'fecha_de_aviso' no está disponible o no hay datos para mostrar la tendencia.")


class EvaluacionProveedoresApp:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def display_evaluacion_proveedores(self):
        st.header("Evaluación de Proveedores")

        if self.df.empty:
            st.warning("No hay datos para mostrar. Por favor, carga los datos primero.")
            return

        st.subheader("Filtros")
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_year = st.selectbox(
                "Año para Evaluación",
                options=['Todos'] + sorted(self.df['año'].dropna().unique().astype(int).tolist(), reverse=True),
                key='eval_year_select'
            )
        with col2:
            available_months = ['Todos']
            if selected_year != 'Todos':
                available_months += sorted(self.df[self.df['año'] == selected_year]['mes'].dropna().unique().tolist())
            else:
                available_months += sorted(self.df['mes'].dropna().unique().tolist())

            selected_month = st.selectbox(
                "Mes para Evaluación",
                options=available_months,
                key='eval_month_select'
            )
        with col3:
            # Asegurarse de que 'PROVEEDOR' existe y no está vacío
            unique_proveedores = self.df['PROVEEDOR'].dropna().unique().tolist()
            if unique_proveedores:
                selected_proveedor = st.selectbox(
                    "Selecciona un Proveedor",
                    options=['Todos'] + sorted(unique_proveedores),
                    key='eval_proveedor_select'
                )
            else:
                selected_proveedor = 'Todos'
                st.info("No hay proveedores disponibles para seleccionar.")


        filtered_df = self.df.copy()
        if selected_year != 'Todos':
            filtered_df = filtered_df[filtered_df['año'] == selected_year]
        if selected_month != 'Todos':
            filtered_df = filtered_df[filtered_df['mes'] == selected_month]
        if selected_proveedor != 'Todos':
            filtered_df = filtered_df[filtered_df['PROVEEDOR'] == selected_proveedor]

        if filtered_df.empty:
            st.info("No hay datos para los filtros seleccionados.")
            return

        # Resumen por proveedor
        st.subheader("Rendimiento General de Proveedores")
        proveedor_summary = filtered_df.groupby('PROVEEDOR').agg(
            Total_Avisos=('aviso', 'nunique'),
            Costo_Total=('COSTO', 'sum'),
            Tiempo_Parada_Total=('TIEMPO PARADA', 'sum'),
            Costo_Promedio_Aviso=('COSTO', lambda x: x[x > 0].mean()), # Promedio solo de costos > 0
            Tiempo_Parada_Promedio_Aviso=('TIEMPO PARADA', lambda x: x[x > 0].mean()) # Promedio solo de tiempo > 0
        ).fillna(0).sort_values(by='Costo_Total', ascending=False).reset_index()

        st.dataframe(proveedor_summary.style.format({
            'Costo_Total': "{:.2f}€",
            'Tiempo_Parada_Total': "{:.2f} hrs",
            'Costo_Promedio_Aviso': "{:.2f}€",
            'Tiempo_Parada_Promedio_Aviso': "{:.2f} hrs"
        }), use_container_width=True)

        st.subheader("Detalle por Proveedor (si aplica el filtro)")
        if selected_proveedor != 'Todos' and not filtered_df.empty:
            st.write(f"Detalle para el proveedor: **{selected_proveedor}**")

            # Desglose de avisos del proveedor por tipo de servicio
            if 'tipo_de_servicio' in filtered_df.columns:
                service_type_summary = filtered_df.groupby('tipo_de_servicio').agg(
                    Cantidad_Avisos=('aviso', 'nunique'),
                    Costo_Total=('COSTO', 'sum'),
                    Tiempo_Parada_Total=('TIEMPO PARADA', 'sum')
                ).fillna(0).sort_values(by='Costo_Total', ascending=False).reset_index()
                st.write("Avisos por Tipo de Servicio:")
                st.dataframe(service_type_summary.style.format({
                    'Costo_Total': "{:.2f}€",
                    'Tiempo_Parada_Total': "{:.2f} hrs"
                }), use_container_width=True)
            else:
                st.info("La columna 'tipo_de_servicio' no está disponible para el desglose.")


            # Desglose de avisos por ubicación o equipo (ejemplo)
            if 'ubicacion_tecnica' in filtered_df.columns:
                location_summary = filtered_df.groupby('ubicacion_tecnica').agg(
                    Cantidad_Avisos=('aviso', 'nunique'),
                    Costo_Total=('COSTO', 'sum')
                ).fillna(0).sort_values(by='Costo_Total', ascending=False).reset_index()
                st.write("Avisos por Ubicación Técnica:")
                st.dataframe(location_summary.style.format({'Costo_Total': "{:.2f}€"}), use_container_width=True)
            else:
                st.info("La columna 'ubicacion_tecnica' no está disponible para el desglose.")


            # Gráficos específicos para el proveedor seleccionado
            if 'fecha_de_aviso' in filtered_df.columns and not filtered_df.empty:
                filtered_df_valid_dates = filtered_df.dropna(subset=['fecha_de_aviso']).copy()
                if not filtered_df_valid_dates.empty:
                    filtered_df_valid_dates['Mes_Año'] = filtered_df_valid_dates['fecha_de_aviso'].dt.to_period('M')
                    monthly_prov_summary = filtered_df_valid_dates.groupby('Mes_Año').agg(
                        Costo_Total=('COSTO', 'sum'),
                        Cantidad_Avisos=('aviso', 'nunique')
                    ).reset_index()
                    monthly_prov_summary['Mes_Año'] = monthly_prov_summary['Mes_Año'].astype(str)

                    fig_prov, ax_prov = plt.subplots(figsize=(12, 6))
                    sns.lineplot(x='Mes_Año', y='Costo_Total', data=monthly_prov_summary, marker='o', ax=ax_prov, label='Costo Total')
                    ax_prov_twin = ax_prov.twinx()
                    sns.lineplot(x='Mes_Año', y='Cantidad_Avisos', data=monthly_prov_summary, marker='x', color='red', ax=ax_prov_twin, label='Cantidad de Avisos')
                    ax_prov.set_title(f'Tendencia Mensual de Costos y Avisos para {selected_proveedor}')
                    ax_prov.set_xlabel('Mes y Año')
                    ax_prov.set_ylabel('Costo Total (€)', color=sns.color_palette('viridis')[0])
                    ax_prov_twin.set_ylabel('Cantidad de Avisos', color='red')
                    fig_prov.legend(loc="upper left", bbox_to_anchor=(0.1,0.9))
                    ax_prov.tick_params(axis='x', rotation=45)
                    st.pyplot(fig_prov)
                else:
                    st.info("No hay datos de fecha de aviso válidos para mostrar la tendencia del proveedor.")
            else:
                st.info("La columna 'fecha_de_aviso' no está disponible o no hay datos para la tendencia del proveedor.")

        elif selected_proveedor == 'Todos':
            st.info("Selecciona un proveedor específico en el filtro superior para ver un detalle más granular.")


# --- Lógica principal de la aplicación Streamlit ---
if st.session_state['page'] == 'cargar_datos':
    st.header("Cargar Datos de Avisos")
    st.write("Sube tu archivo Excel consolidado que contenga todas las columnas de avisos. Asegúrate de que todas las columnas necesarias estén en la primera hoja.")

    uploaded_file = st.file_uploader("Sube tu archivo Excel consolidado (.xlsx)", type=["xlsx"])

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
            st.warning("Asegúrate de que el archivo Excel contenga las columnas correctas y los formatos esperados. Consulta la descripción de columnas requeridas.")

elif st.session_state['page'] == 'costos_avisos':
    if 'df' in st.session_state and st.session_state['df'] is not None and not st.session_state['df'].empty:
        costos_avisos_app = CostosAvisosApp(st.session_state['df'])
        costos_avisos_app.display_costos_avisos_dashboard()
    else:
        st.warning("Por favor, carga los datos primero desde la sección 'Cargar Datos'.")

elif st.session_state['page'] == 'evaluacion':
    if 'df' in st.session_state and st.session_state['df'] is not None and not st.session_state['df'].empty:
        eval_app = EvaluacionProveedoresApp(st.session_state['df'])
        eval_app.display_evaluacion_proveedores()
    else:
        st.warning("Por favor, carga los datos primero desde la sección 'Cargar Datos'.")
