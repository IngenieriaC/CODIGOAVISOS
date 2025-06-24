import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import io
import numpy as np

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

# --- Inicialización de Session State (¡Importante para evitar AttributeError!) ---
if 'df' not in st.session_state:
    st.session_state.df = None
if 'original_excel_buffer' not in st.session_state: # Para guardar el archivo original
    st.session_state.original_excel_buffer = None
if 'eval_mode' not in st.session_state:
    st.session_state.eval_mode = "Por Tipo de Servicio" # Default evaluation mode
if 'selected_eval_target' not in st.session_state:
    st.session_state.selected_eval_target = None
if 'evaluations' not in st.session_state:
    st.session_state.evaluations = {} # Store user evaluations: {('Categoría', 'Pregunta', 'Target'): valor}
if 'pre_calculated_metrics' not in st.session_state:
    st.session_state.pre_calculated_metrics = None
if 'page' not in st.session_state:
    st.session_state.page = 'Inicio y Carga de Datos'
# `current_analysis_page` should be dynamic per analysis type, initialized later

# Helper function to normalize column names
def normalize_column_name(col_name):
    """
    Normaliza el nombre de una columna para que sea compatible con Python y más fácil de usar.
    Convierte a minúsculas, reemplaza espacios y caracteres especiales por guiones bajos.
    También intenta ser más flexible con "equipo".
    """
    normalized = re.sub(r'[^a-z0-9_]+', '', col_name.strip().lower().replace(' ', '_'))
    
    # Casos específicos para "equipo"
    if 'equipo' in normalized:
        return 'equipo'
    
    return normalized

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
    uploaded_file_buffer.seek(0)
    iw29 = pd.read_excel(uploaded_file_buffer, sheet_name=0)
    uploaded_file_buffer.seek(0)
    iw39 = pd.read_excel(uploaded_file_buffer, sheet_name=1)
    uploaded_file_buffer.seek(0)
    ih08 = pd.read_excel(uploaded_file_buffer, sheet_name=2)
    uploaded_file_buffer.seek(0)
    iw65 = pd.read_excel(uploaded_file_buffer, sheet_name=3)
    uploaded_file_buffer.seek(0)
    zpm015 = pd.read_excel(uploaded_file_buffer, sheet_name=4)

    # Normalizar encabezados inmediatamente después de la carga para todos los DataFrames
    all_raw_dfs = {
        'iw29': iw29, 'iw39': iw39, 'ih08': ih08, 'iw65': iw65, 'zpm015': zpm015
    }
    normalized_dfs = {}
    for name, df_temp in all_raw_dfs.items():
        df_temp.columns = [normalize_column_name(col) for col in df_temp.columns]
        normalized_dfs[name] = df_temp
        st.write(f"Columnas normalizadas para {name.upper()}: {normalized_dfs[name].columns.tolist()}") # Debugging print

    iw29_n = normalized_dfs['iw29']
    iw39_n = normalized_dfs['iw39']
    ih08_n = normalized_dfs['ih08']
    iw65_n = normalized_dfs['iw65']
    zpm015_n = normalized_dfs['zpm015']

    # --- Iniciar Fusiones ---
    # DataFrame base: iw29_n (contiene 'aviso', 'equipo', etc., que son clave)
    df_final = iw29_n.copy()
    
    # 1. Fusionar con IW39 (para 'total_general_real' que se convertirá en 'costes_tot_reales')
    iw39_subset_for_merge = iw39_n[['aviso', 'total_general_real']].copy() if 'total_general_real' in iw39_n.columns else iw39_n[['aviso']].copy()
    df_final = pd.merge(df_final, iw39_subset_for_merge, on="aviso", how="left")

    # 2. Fusionar con IW65 (también por 'aviso').
    df_final = pd.merge(df_final, iw65_n, on="aviso", how="left", suffixes=('', '_iw65'))
    for col in iw65_n.columns:
        if col != 'aviso' and f'{col}_iw65' in df_final.columns and col in df_final.columns:
            df_final.drop(columns=f'{col}_iw65', errors='ignore', inplace=True)

    # 3. Preparar y fusionar IH08: Renombrar 'texto' a 'texto_equipo' ANTES de la fusión.
    ih08_for_merge = ih08_n.copy()
    if 'texto' in ih08_for_merge.columns:
        ih08_for_merge.rename(columns={'texto': 'texto_equipo'}, inplace=True)
    
    ih08_cols_to_merge_base = [
        "equipo", "inicgarantia_prov", "fin_garantia_prov", "indicador_abc",
        "denominacion_de_objeto_tecnico", "cl_objeto_tecnico"
    ]
    if 'texto_equipo' in ih08_for_merge.columns:
        ih08_cols_to_merge_base.append('texto_equipo')

    existing_ih08_cols = [col for col in ih08_cols_to_merge_base if col in ih08_for_merge.columns]

    # **CRÍTICO:** Verificar que 'equipo' esté en IH08_for_merge y df_final antes de la fusión.
    if 'equipo' not in df_final.columns:
        st.error("Error crítico: La columna 'equipo' no se encontró en el DataFrame principal antes de la fusión con IH08. Por favor, verifica el archivo IW29 original y sus nombres de columna.")
        raise KeyError("'equipo' column missing in main DataFrame for IH08 merge.")
    if 'equipo' not in existing_ih08_cols:
        st.error("Error crítico: La columna 'equipo' no se encontró en IH08 después de la normalización. Por favor, verifica el archivo IH08 original y sus nombres de columna.")
        raise KeyError("'equipo' column missing in IH08 after normalization for merge.")

    df_final = pd.merge(df_final, ih08_for_merge[existing_ih08_cols], on="equipo", how="left", suffixes=('', '_ih08_suffix'))
    for col in existing_ih08_cols:
        if col != 'equipo' and f'{col}_ih08_suffix' in df_final.columns and col in df_final.columns:
            df_final.drop(columns=f'{col}_ih08_suffix', errors='ignore', inplace=True)


    # 4. Preparar y fusionar ZPM015 (también por 'equipo')
    zpm015_for_merge = zpm015_n.copy()
    zpm015_cols_to_merge = ["equipo", "tipo_de_servicio"]
    existing_zpm015_cols = [col for col in zpm015_cols_to_merge if col in zpm015_for_merge.columns]

    # **CRÍTICO:** Verificar que 'equipo' esté en ZPM015_for_merge antes de la fusión.
    if 'equipo' not in existing_zpm015_cols:
        st.error("Error crítico: La columna 'equipo' no se encontró en ZPM015 después de la normalización. Por favor, verifica el archivo ZPM015 original y sus nombres de columna.")
        raise KeyError("'equipo' column missing in ZPM015 after normalization for merge.")

    df_final = pd.merge(df_final, zpm015_for_merge[existing_zpm015_cols], on="equipo", how="left", suffixes=('', '_zpm015_suffix'))
    for col in existing_zpm015_cols:
        if col != 'equipo' and f'{col}_zpm015_suffix' in df_final.columns and col in df_final.columns:
            df_final.drop(columns=f'{col}_zpm015_suffix', errors='ignore', inplace=True)


    # Renombrado final para consistencia de salida
    if 'total_general_real' in df_final.columns:
        df_final.rename(columns={'total_general_real': 'costes_tot_reales'}, inplace=True)
    
    if 'denominacion_ejecutante' in df_final.columns:
        df_final.rename(columns={'denominacion_ejecutante': 'proveedor'}, inplace=True)
    
    columnas_finales_deseables = [
        "aviso", "orden", "fecha_de_aviso", "codigo_postal", "status_del_sistema",
        "descripcion", "ubicacion_tecnica", "indicador", "equipo",
        "denominacion_de_objeto_tecnico", "proveedor",
        "duracion_de_parada", "centro_de_coste", "costes_tot_reales",
        "inicgarantia_prov", "fin_garantia_prov", "texto_equipo",
        "indicador_abc", "texto_codigo_accion", "texto_de_accion",
        "texto_grupo_accion", "tipo_de_servicio",
        "clase_de_actividad", "puesto_de_trabajo"
    ]

    final_df = df_final[[col for col in columnas_finales_deseables if col in df_final.columns]].copy()
    final_df = final_df.loc[:,~final_df.columns.duplicated()].copy()

    return final_df

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

# --- Funciones para calcular indicadores de desempeño técnico ---
def calcular_disponibilidad(df_subset: pd.DataFrame, horarios: dict, group_by_col: str) -> pd.Series:
    """Calcula la disponibilidad promedio por la columna de agrupación."""
    # Asegurarse de trabajar en una copia para evitar SettingWithCopyWarning
    df_subset_cleaned = df_subset.copy()

    # Validar que las columnas necesarias existan
    required_cols = ['equipo', 'duracion_de_parada', 'denominacion_de_objeto_tecnico']
    if not all(col in df_subset_cleaned.columns for col in required_cols):
        st.warning(f"Columnas necesarias para disponibilidad no encontradas: {', '.join([col for col in required_cols if col not in df_subset_cleaned.columns])}")
        return pd.Series(dtype=float)

    df_subset_cleaned = df_subset_cleaned.dropna(subset=['equipo']).copy()
    if df_subset_cleaned.empty:
        return pd.Series(dtype=float)

    # Convertir 'duracion_de_parada' a numérico
    df_subset_cleaned['duracion_de_parada'] = pd.to_numeric(df_subset_cleaned['duracion_de_parada'], errors='coerce').fillna(0)

    # Buscar la clave de horario en 'denominacion_de_objeto_tecnico' usando regex
    def find_horario_key(text):
        match = re.search(r'(HORARIO_\d+)', str(text).upper())
        return match.group(1) if match else None

    df_subset_cleaned['horario_key'] = df_subset_cleaned['denominacion_de_objeto_tecnico'].apply(find_horario_key)

    # Valores por defecto en caso de que horarios_dict esté vacío o la clave no se encuentre
    default_horas_dia = np.mean([h[0] for h in horarios.values()]) if horarios else 8
    default_dias_anio = np.mean([h[1] for h in horarios.values()]) if horarios else 250

    df_subset_cleaned['horas_dia_equipo'] = df_subset_cleaned.apply(
        lambda row: horarios[row['horario_key']][0] if row['horario_key'] in horarios else default_horas_dia,
        axis=1
    )
    df_subset_cleaned['dias_anio_equipo'] = df_subset_cleaned.apply(
        lambda row: horarios[row['horario_key']][1] if row['horario_key'] in horarios else default_dias_anio,
        axis=1
    )

    df_subset_cleaned['horas_operativas_totales'] = df_subset_cleaned['horas_dia_equipo'] * df_subset_cleaned['dias_anio_equipo']

    sum_parada_equipo = df_subset_cleaned.groupby('equipo')['duracion_de_parada'].sum()

    horas_op_equipo = df_subset_cleaned.drop_duplicates(subset='equipo').set_index('equipo')['horas_operativas_totales']

    # Reindex para asegurar que ambos Series tengan el mismo índice
    horas_op_equipo = horas_op_equipo.reindex(sum_parada_equipo.index).fillna(0)

    # Evitar división por cero y manejar valores infinitos/NaN
    disponibilidad_equipo = (horas_op_equipo - sum_parada_equipo) / horas_op_equipo
    disponibilidad_equipo = disponibilidad_equipo.replace([-np.inf, np.inf], np.nan).fillna(0) * 100 # Convertir a porcentaje

    # Agregamos por la columna de agrupación seleccionada
    if group_by_col not in df_subset_cleaned.columns:
        st.warning(f"La columna de agrupación '{group_by_col}' no se encontró para calcular la disponibilidad.")
        return pd.Series(dtype=float)

    disponibilidad_agrupada = df_subset_cleaned.groupby(group_by_col)['equipo'].apply(
        lambda equipos: disponibilidad_equipo[equipos.unique().intersection(disponibilidad_equipo.index)].mean()
        if not equipos.unique().intersection(disponibilidad_equipo.index).empty else 0
    )
    return disponibilidad_agrupada

def calcular_mttr(df_subset: pd.DataFrame, group_by_col: str) -> pd.Series:
    """Calcula el MTTR promedio por la columna de agrupación."""
    df_subset_cleaned = df_subset.copy()

    required_cols = ['equipo', 'aviso', 'duracion_de_parada']
    if not all(col in df_subset_cleaned.columns for col in required_cols):
        st.warning(f"Columnas necesarias para MTTR no encontradas: {', '.join([col for col in required_cols if col not in df_subset_cleaned.columns])}")
        return pd.Series(dtype=float)

    df_subset_cleaned = df_subset_cleaned.dropna(subset=['equipo', 'aviso']).copy()
    if df_subset_cleaned.empty:
        return pd.Series(dtype=float)

    df_subset_cleaned['duracion_de_parada'] = pd.to_numeric(df_subset_cleaned['duracion_de_parada'], errors='coerce').fillna(0)

    # Asegurarse de que group_by_col existe
    if group_by_col not in df_subset_cleaned.columns:
        st.warning(f"La columna de agrupación '{group_by_col}' no se encontró para calcular el MTTR.")
        return pd.Series(dtype=float)

    mttr = df_subset_cleaned.groupby(group_by_col).apply(
        lambda x: x['duracion_de_parada'].sum() / x['aviso'].nunique() if x['aviso'].nunique() > 0 else 0
    )
    return mttr.replace([np.inf, -np.inf], np.nan).fillna(0)

def calcular_mtbf(df_subset: pd.DataFrame, horarios: dict, group_by_col: str) -> pd.Series:
    """Calcula el MTBF promedio por la columna de agrupación."""
    df_subset_cleaned = df_subset.copy()

    required_cols = ['equipo', 'aviso', 'duracion_de_parada', 'denominacion_de_objeto_tecnico']
    if not all(col in df_subset_cleaned.columns for col in required_cols):
        st.warning(f"Columnas necesarias para MTBF no encontradas: {', '.join([col for col in required_cols if col not in df_subset_cleaned.columns])}")
        return pd.Series(dtype=float)

    df_subset_cleaned = df_subset_cleaned.dropna(subset=['equipo', 'aviso']).copy()
    if df_subset_cleaned.empty:
        return pd.Series(dtype=float)

    df_subset_cleaned['duracion_de_parada'] = pd.to_numeric(df_subset_cleaned['duracion_de_parada'], errors='coerce').fillna(0)

    def find_horario_key(text):
        match = re.search(r'(HORARIO_\d+)', str(text).upper())
        return match.group(1) if match else None

    df_subset_cleaned['horario_key'] = df_subset_cleaned['denominacion_de_objeto_tecnico'].apply(find_horario_key)

    default_horas_dia = np.mean([h[0] for h in horarios.values()]) if horarios else 8
    default_dias_anio = np.mean([h[1] for h in horarios.values()]) if horarios else 250

    df_subset_cleaned['horas_dia_equipo'] = df_subset_cleaned.apply(
        lambda row: horarios[row['horario_key']][0] if row['horario_key'] in horarios else default_horas_dia,
        axis=1
    )
    df_subset_cleaned['dias_anio_equipo'] = df_subset_cleaned.apply(
        lambda row: horarios[row['horario_key']][1] if row['horario_key'] in horarios else default_dias_anio,
        axis=1
    )
    df_subset_cleaned['horas_operativas_totales_equipo'] = df_subset_cleaned['horas_dia_equipo'] * df_subset_cleaned['dias_anio_equipo']

    total_parada_por_equipo = df_subset_cleaned.groupby('equipo')['duracion_de_parada'].sum()
    num_avisos_por_equipo = df_subset_cleaned.groupby('equipo')['aviso'].nunique()

    horas_op_unicas_equipo = df_subset_cleaned.drop_duplicates(subset='equipo').set_index('equipo')['horas_operativas_totales_equipo']

    total_parada_por_equipo = total_parada_por_equipo.reindex(horas_op_unicas_equipo.index).fillna(0)
    num_avisos_por_equipo = num_avisos_por_equipo.reindex(horas_op_unicas_equipo.index).fillna(0)

    # Evitar división por cero
    mtbf_equipo = (horas_op_unicas_equipo - total_parada_por_equipo) / num_avisos_por_equipo
    mtbf_equipo = mtbf_equipo.replace([np.inf, -np.inf], np.nan).fillna(0)

    # Asegurarse de que group_by_col existe
    if group_by_col not in df_subset_cleaned.columns:
        st.warning(f"La columna de agrupación '{group_by_col}' no se encontró para calcular el MTBF.")
        return pd.Series(dtype=float)

    mtbf_agrupado = df_subset_cleaned.groupby(group_by_col)['equipo'].apply(
        lambda equipos: mtbf_equipo[equipos.unique().intersection(mtbf_equipo.index)].mean()
        if not equipos.unique().intersection(mtbf_equipo.index).empty else 0
    )
    return mtbf_agrupado


def clasificar_rendimiento(disponibilidad: pd.Series) -> pd.Series:
    """Clasifica el rendimiento en 'Alto', 'Medio' o 'Bajo' basado en la disponibilidad."""
    if disponibilidad.empty:
        return pd.Series(dtype=str)

    return disponibilidad.apply(
        lambda disp: 'Alto' if disp >= 90 else ('Medio' if disp >= 75 else 'Bajo')
    )

# --- Definición de las preguntas y rangos ---
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

# --- Clase para el manejo de análisis generalizado y paginación ---
class AnalysisApp:
    def __init__(self, df):
        self.df = df.copy() # Asegurarse de trabajar en una copia para evitar SettingWithCopyWarning

        # Usar nombres de columnas normalizados
        self.EJECUTANTE_COL_NAME_NORMALIZED = "proveedor"
        self.COL_COSTOS_NORMALIZED = "costes_tot_reales"
        self.COL_DURACION_PARADA_NORMALIZED = "duracion_de_parada"

        # Categorización de descripción (ejemplo, puedes refinar esta lógica)
        if 'descripcion' in self.df.columns:
            self.df['description_category'] = self.df['descripcion'].apply(self._categorize_description)
        else:
            self.df['description_category'] = "sin_categoria" # Fallback y nombre normalizado

        # Opciones de análisis dinámicas
        self.opciones_menu = {
            "Costos por Ejecutante": (self.EJECUTANTE_COL_NAME_NORMALIZED, self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por Ejecutante": (self.EJECUTANTE_COL_NAME_NORMALIZED, None, "avisos"),
            "Costos por Objeto Técnico": ("denominacion_de_objeto_tecnico", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por Objeto Técnico": ("denominacion_de_objeto_tecnico", None, "avisos"),
            "Costos por Texto Código Acción": ("texto_codigo_accion", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por Texto Código Acción": ("texto_codigo_accion", None, "avisos"),
            "Costos por Texto de Acción": ("texto_de_accion", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por Texto de Acción": ("texto_de_accion", None, "avisos"),
            "Costos por Tipo de Servicio": ("tipo_de_servicio", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por Tipo de Servicio": ("tipo_de_servicio", None, "avisos"),
            "Costos por Categoría de Descripción": ("description_category", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por Categoría de Descripción": ("description_category", None, "avisos"),
        }
        
        # Filtra las opciones_menu para asegurarse de que las columnas existan en el DataFrame
        # y que las columnas de costo existan para análisis de costos
        self.opciones_menu = {
            k: v for k, v in self.opciones_menu.items()
            if (v[0] in self.df.columns or v[0] == "description_category") 
            and (v[1] is None or v[1] in self.df.columns) 
        }

    def _categorize_description(self, description):
        """Categoriza las descripciones (ejemplo, expande según tus necesidades)."""
        desc = str(description).lower()
        if "reparacion" in desc or "mantenimiento correctivo" in desc:
            return "Reparación/Mantenimiento Correctivo"
        elif "preventivo" in desc or "revision" in desc:
            return "Mantenimiento Preventivo/Revisión"
        elif "instalacion" in desc:
            return "Instalación"
        else:
            return "Otros"

    def display_analysis(self):
        st.subheader("Análisis General de Datos")

        # Obtener la lista de opciones de análisis disponibles
        available_analysis_options = list(self.opciones_menu.keys())

        # Si no hay opciones disponibles, mostrar una advertencia y salir
        if not available_analysis_options:
            st.warning("No hay opciones de análisis disponibles. Asegúrate de que las columnas necesarias existan en los datos cargados.")
            return

        analysis_type = st.selectbox(
            "Selecciona el tipo de análisis:",
            available_analysis_options,
            key="analysis_type_select"
        )

        group_col, value_col, analysis_metric = self.opciones_menu[analysis_type]

        # Asegurarse que la columna de agrupación exista
        if group_col not in self.df.columns and group_col != "description_category":
            st.warning(f"La columna '{group_col}' no se encontró en los datos para este análisis.")
            return

        if analysis_metric == "costos":
            if value_col not in self.df.columns:
                st.warning(f"La columna de costos '{value_col}' no se encontró en los datos para este análisis.")
                return
            # Convertir la columna de costos a numérico, manejando errores
            self.df[value_col] = pd.to_numeric(self.df[value_col], errors='coerce').fillna(0)
            grouped_data = self.df.groupby(group_col)[value_col].sum().sort_values(ascending=False)
            title = f"Costos Totales por {analysis_type.split(' por ')[1].replace('por', 'según')}"
            y_label = "Costo Total Real"
        elif analysis_metric == "avisos":
            # Asegurarse que la columna 'aviso' exista
            if 'aviso' not in self.df.columns:
                st.warning("La columna 'aviso' no se encontró en los datos para el conteo de avisos.")
                return
            grouped_data = self.df.groupby(group_col)['aviso'].nunique().sort_values(ascending=False)
            title = f"Cantidad de Avisos por {analysis_type.split(' por ')[1].replace('por', 'según')}"
            y_label = "Cantidad de Avisos"
        else:
            st.error("Métrica de análisis no reconocida.")
            return

        if grouped_data.empty:
            st.info(f"No hay datos para mostrar para '{analysis_type}'.")
            return

        # Paginación
        items_per_page = 15
        total_items = len(grouped_data)
        total_pages = (total_items + items_per_page - 1) // items_per_page

        # Inicializa la página actual si no existe o si se cambia el tipo de análisis
        # Usar una clave única para el tipo de análisis para resetear la página cuando cambia el análisis
        current_analysis_page_key = f'analysis_page_{analysis_type}'
        if current_analysis_page_key not in st.session_state:
            st.session_state[current_analysis_page_key] = 0

        current_page = st.session_state[current_analysis_page_key]

        start_idx = current_page * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        paginated_data = grouped_data.iloc[start_idx:end_idx]

        st.write(f"### {title}")
        st.dataframe(paginated_data.reset_index().rename(columns={paginated_data.name: y_label}))

        # Controles de paginación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("Página Anterior", key=f"prev_page_{analysis_type}"):
                if current_page > 0:
                    st.session_state[current_analysis_page_key] -= 1
                    st.rerun()
        with col2:
            st.write(f"Página {current_page + 1} de {total_pages}")
        with col3:
            if st.button("Página Siguiente", key=f"next_page_{analysis_type}"):
                if current_page < total_pages - 1:
                    st.session_state[current_analysis_page_key] += 1
                    st.rerun()

        # Gráfico
        if not paginated_data.empty:
            fig, ax = plt.subplots(figsize=(10, max(6, len(paginated_data) * 0.5)))
            sns.barplot(x=paginated_data.values, y=paginated_data.index, ax=ax, palette='viridis')
            ax.set_title(title)
            ax.set_xlabel(y_label)
            ax.set_ylabel(group_col.replace('_', ' ').title()) # Mejorar la etiqueta del eje Y
            plt.tight_layout() # Ajustar el layout para evitar superposición de etiquetas
            st.pyplot(fig) # Mostrar el gráfico en Streamlit

# --- Main App Logic (PAGES) ---
def main():
    st.sidebar.title("Navegación")
    page_options = ['Inicio y Carga de Datos', 'Análisis de Datos', 'Evaluación de Desempeño']
    st.session_state.page = st.sidebar.radio("Ir a:", page_options, index=page_options.index(st.session_state.page))

    if st.session_state.page == 'Inicio y Carga de Datos':
        st.title("¡Hola, usuario Sura! 👋")
        st.markdown("---")
        st.header("Proyecto de **Gerencia de Gestión Administrativa** en Ingeniería Clínica")
        st.markdown("""
            Aquí podrás **analizar y gestionar los datos de avisos** para optimizar los procesos.
            Por favor, **sube el archivo `DATA2.XLSX`** para comenzar.
        """)

        uploaded_file = st.file_uploader("Sube tu archivo 'DATA2.XLSX' aquí", type=["xlsx"], key="file_uploader")

        if uploaded_file:
            file_buffer = io.BytesIO(uploaded_file.getvalue())

            with st.spinner('Cargando y procesando datos... Esto puede tomar un momento.'):
                try:
                    # Cargar y fusionar datos usando la función mejorada
                    df = load_and_merge_data(file_buffer)
                    
                    # --- Procesamiento adicional: Eliminar registros con "PTBO" ---
                    initial_rows = len(df)
                    if 'status_del_sistema' in df.columns:
                        df = df[~df["status_del_sistema"].str.contains("PTBO", case=False, na=False)]
                        st.info(f"Se eliminaron {initial_rows - len(df)} registros con 'PTBO' en 'status_del_sistema'.")
                    else:
                        st.warning("La columna 'status_del_sistema' no se encontró para filtrar 'PTBO'.")

                    # --- Procesamiento adicional: Dejar solo una fila con coste por cada aviso ---
                    # Asegurarse que las columnas existan y manejar el caso de grupos vacíos
                    if 'aviso' in df.columns and 'costes_tot_reales' in df.columns:
                        df['costes_tot_reales'] = df.groupby('aviso')['costes_tot_reales'].transform(
                            lambda x: [x.iloc[0]] + [0]*(len(x)-1) if len(x) > 0 else []
                        )
                    else:
                        st.warning("Las columnas 'aviso' o 'costes_tot_reales' no se encontraron para el procesamiento de costes.")
                    
                    st.session_state.df = df # Asignar el DataFrame procesado a session_state

                    st.success("✅ Datos cargados y procesados exitosamente.")
                    st.write(f"**Filas finales:** {len(st.session_state.df)} – **Columnas:** {len(st.session_state.df.columns)}")

                    # --- Visualización y Descarga ---
                    st.markdown("---")
                    st.subheader("Vista previa de los datos procesados:")
                    st.dataframe(st.session_state.df.head(10)) # Mostrar más filas para una mejor vista previa

                    st.markdown("---")
                    st.subheader("Descarga de Datos Procesados")

                    # Preparar CSV para descarga
                    csv_output = st.session_state.df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Descargar como CSV",
                        data=csv_output,
                        file_name="avisos_filtrados.csv",
                        mime="text/csv",
                        help="Descarga el archivo en formato CSV."
                    )

                    # Preparar Excel para descarga
                    excel_buffer = io.BytesIO()
                    st.session_state.df.to_excel(excel_buffer, index=False, engine='openpyxl')
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
                    
                    # Cambiar automáticamente a la página de Análisis después de una carga exitosa
                    st.session_state.page = 'Análisis de Datos'
                    st.rerun() # Trigger a rerun to show the Analysis page

                except Exception as e:
                    st.error(f"❌ ¡Ups! Ocurrió un error al procesar el archivo: {e}")
                    st.warning("Por favor, verifica que el archivo subido sea `DATA2.XLSX` y tenga el formato de hojas esperado.")
                    st.exception(e) # Muestra el traceback completo para depuración
        else:
            st.info("⬆️ Sube tu archivo `DATA2.XLSX` para empezar con el análisis.")

    elif st.session_state.page == 'Análisis de Datos':
        st.header("Sección de Análisis de Datos")
        if st.session_state.df is not None:
            analysis_app = AnalysisApp(st.session_state.df)
            analysis_app.display_analysis()
        else:
            st.warning("Por favor, carga un archivo Excel en la sección 'Inicio y Carga de Datos' primero.")
            if st.button("Ir a Carga de Datos"):
                st.session_state.page = 'Inicio y Carga de Datos'
                st.rerun()

    elif st.session_state.page == 'Evaluación de Desempeño':
        st.header("Evaluación de Desempeño")
        if st.session_state.df is None:
            st.warning("Por favor, carga un archivo Excel en la sección 'Inicio y Carga de Datos' para realizar la evaluación.")
            if st.button("Ir a Carga de Datos"):
                st.session_state.page = 'Inicio y Carga de Datos'
                st.rerun()
            return

        # Seleccionar modo de evaluación (Por Tipo de Servicio o Por Proveedor)
        st.session_state.eval_mode = st.radio(
            "Evaluar desempeño por:",
            ("Por Tipo de Servicio", "Por Proveedor"),
            key="eval_mode_radio"
        )

        group_col_for_eval = "tipo_de_servicio" if st.session_state.eval_mode == "Por Tipo de Servicio" else "proveedor"

        # Asegurarse de que la columna de agrupación exista para la evaluación
        if group_col_for_eval not in st.session_state.df.columns:
            st.error(f"La columna '{group_col_for_eval}' no se encontró en los datos para la evaluación. Por favor, verifica tus datos.")
            return

        unique_targets = st.session_state.df[group_col_for_eval].dropna().unique().tolist()
        if not unique_targets:
            st.info(f"No se encontraron valores únicos en la columna '{group_col_for_eval}' para evaluar.")
            return

        # Establecer un valor inicial predeterminado para selected_eval_target si no se ha establecido o ya no es válido
        if st.session_state.selected_eval_target not in unique_targets:
            st.session_state.selected_eval_target = unique_targets[0] if unique_targets else None

        selected_target = st.selectbox(
            f"Selecciona {st.session_state.eval_mode.lower().replace('por ', '')} a evaluar:",
            unique_targets,
            index=unique_targets.index(st.session_state.selected_eval_target),
            key="selected_eval_target_select"
        )
        st.session_state.selected_eval_target = selected_target

        # Filtrar el DataFrame para el objetivo seleccionado
        df_target_subset = st.session_state.df[st.session_state.df[group_col_for_eval] == selected_target].copy()

        # Pre-calcular métricas técnicas si no se han calculado o si el objetivo/modo de evaluación ha cambiado
        metrics_key = (st.session_state.eval_mode, st.session_state.selected_eval_target)
        if st.session_state.pre_calculated_metrics is None or metrics_key not in st.session_state.pre_calculated_metrics:
            with st.spinner("Calculando métricas de desempeño técnico..."):
                disponibilidad = calcular_disponibilidad(df_target_subset, horarios_dict, group_by_col_for_eval)
                mttr = calcular_mttr(df_target_subset, group_by_col_for_eval)
                mtbf = calcular_mtbf(df_target_subset, horarios_dict, group_by_col_for_eval)
                rendimiento = clasificar_rendimiento(disponibilidad)

                # Obtener la métrica específica para el objetivo seleccionado
                target_disponibilidad = disponibilidad.get(selected_target, 0.0)
                target_mttr = mttr.get(selected_target, 0.0)
                target_mtbf = mtbf.get(selected_target, 0.0)
                target_rendimiento = rendimiento.get(selected_target, 'Bajo') # Default to 'Bajo' if not found

                if st.session_state.pre_calculated_metrics is None:
                    st.session_state.pre_calculated_metrics = {}
                st.session_state.pre_calculated_metrics[metrics_key] = {
                    "Disponibilidad promedio (%)": target_disponibilidad,
                    "MTTR promedio (hrs)": target_mttr,
                    "MTBF promedio (hrs)": target_mtbf,
                    "Rendimiento promedio equipos": target_rendimiento
                }
        
        # Mostrar métricas pre-calculadas para "Desempeño técnico"
        if metrics_key in st.session_state.pre_calculated_metrics:
            tech_metrics = st.session_state.pre_calculated_metrics[metrics_key]
            st.subheader(f"Métricas de Desempeño Técnico para {selected_target}:")
            for metric, value in tech_metrics.items():
                if isinstance(value, (int, float)):
                    st.metric(label=metric, value=f"{value:.2f}")
                else:
                    st.metric(label=metric, value=str(value))

        # Sección para la evaluación manual
        st.subheader(f"Evaluación Manual para {selected_target}")
        st.write("Califica cada criterio en una escala de -1 a 2:")

        for category, questions in rangos_detallados.items():
            st.markdown(f"#### {category}")
            for question, options in questions.items():
                if category == "Desempeño técnico":
                    # Para el desempeño técnico, usar las métricas pre-calculadas
                    metric_value = st.session_state.pre_calculated_metrics.get(metrics_key, {}).get(question)
                    if metric_value is not None:
                        # Determinar la puntuación basándose en el valor de la métrica y rangos_detallados
                        score = 0 # Valor por defecto
                        if question == "Disponibilidad promedio (%)":
                            if metric_value >= 98: score = 2
                            elif 75 <= metric_value < 98: score = 1
                            else: score = 0
                        elif question == "MTTR promedio (hrs)":
                            if metric_value <= 5: score = 2
                            elif 5 < metric_value <= 20: score = 1
                            else: score = 0
                        elif question == "MTBF promedio (hrs)":
                            if metric_value > 1000: score = 2
                            elif 100 <= metric_value <= 1000: score = 1
                            else: score = 0
                        elif question == "Rendimiento promedio equipos":
                            if metric_value == 'Alto': score = 2
                            elif metric_value == 'Medio': score = 1
                            else: score = 0

                        st.info(f"**{question}**: {metric_value:.2f}" if isinstance(metric_value, (int, float)) else f"**{question}**: {metric_value}")
                        st.write(f"Puntuación automática: **{score}**")
                        st.session_state.evaluations[(category, question, selected_target)] = score
                    else:
                        st.warning(f"Métrica '{question}' no disponible para cálculo automático.")
                        # Todavía proporcionar un slider manual si el cálculo automático falla/no es aplicable
                        default_value = st.session_state.evaluations.get((category, question, selected_target), 0)
                        selected_option = st.slider(
                            question,
                            min_value=-1,
                            max_value=2,
                            value=default_value,
                            step=1,
                            format="%d",
                            key=f"eval_{category}_{question}_{selected_target}"
                        )
                        st.write(f"Descripción: {options.get(selected_option, 'Sin descripción')}")
                        st.session_state.evaluations[(category, question, selected_target)] = selected_option
                else:
                    default_value = st.session_state.evaluations.get((category, question, selected_target), 0)
                    selected_option = st.slider(
                        question,
                        min_value=-1,
                        max_value=2,
                        value=default_value,
                        step=1,
                        format="%d",
                        key=f"eval_{category}_{question}_{selected_target}"
                    )
                    st.write(f"Descripción: {options.get(selected_option, 'Sin descripción')}")
                    st.session_state.evaluations[(category, question, selected_target)] = selected_option

        # Mostrar resumen de evaluaciones
        st.subheader("Resumen de Puntuaciones")
        if st.session_state.evaluations:
            eval_data = []
            for (cat, q, target), score in st.session_state.evaluations.items():
                if target == selected_target: # Solo mostrar para el objetivo actual
                    eval_data.append({"Categoría": cat, "Pregunta": q, "Puntuación": score})
            if eval_data:
                eval_df = pd.DataFrame(eval_data)
                st.dataframe(eval_df)

                # Calcular puntuación total y promedio
                total_score = eval_df['Puntuación'].sum()
                num_questions = len(eval_df)
                average_score = total_score / num_questions if num_questions > 0 else 0

                st.markdown(f"**Puntuación Total para {selected_target}:** {total_score}")
                st.markdown(f"**Puntuación Promedio para {selected_target}:** {average_score:.2f}")

                # Gráfico de barras de las puntuaciones por categoría
                category_scores = eval_df.groupby('Categoría')['Puntuación'].mean().sort_values(ascending=False)
                fig_cat_scores, ax_cat_scores = plt.subplots(figsize=(10, 6))
                sns.barplot(x=category_scores.index, y=category_scores.values, ax=ax_cat_scores, palette='coolwarm')
                ax_cat_scores.set_title(f"Puntuación Promedio por Categoría para {selected_target}")
                ax_cat_scores.set_xlabel("Categoría")
                ax_cat_scores.set_ylabel("Puntuación Promedio")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig_cat_scores)

                # Gráfico de barras de todas las preguntas
                fig_all_scores, ax_all_scores = plt.subplots(figsize=(12, max(8, len(eval_df) * 0.4)))
                sns.barplot(x='Puntuación', y='Pregunta', data=eval_df, ax=ax_all_scores, palette='viridis')
                ax_all_scores.set_title(f"Puntuaciones Individuales por Pregunta para {selected_target}")
                ax_all_scores.set_xlabel("Puntuación")
                ax_all_scores.set_ylabel("Pregunta")
                plt.tight_layout()
                st.pyplot(fig_all_scores)

            else:
                st.info("No hay evaluaciones registradas para el objetivo seleccionado.")
        else:
            st.info("Comienza a evaluar para ver el resumen de puntuaciones.")

# Run the app
if __name__ == "__main__":
    main()
