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
    /* Sidebar - Nota: Las clases como st-emotion-cache-XXXX son internas de Streamlit y pueden cambiar */
    .st-emotion-cache-1oe6z58 {
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
    /* Contenedores de contenido principal - Nota: Las clases como st-emotion-cache-XXXX son internas de Streamlit y pueden cambiar */
    .st-emotion-cache-z5fcl4, .st-emotion-cache-1c7y2kl, .st-emotion-cache-nahz7x {
        background-color: rgba(255, 255, 255, 0.9); /* Blanco semitransparente */
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Corregido: box_shadow -> box-shadow */
        margin-bottom: 1rem; /* Corregido: margin_bottom -> margin-bottom */
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
if 'current_analysis_page' not in st.session_state: # Para la paginación en análisis
    st.session_state.current_analysis_page = 0


# --- Función de carga & unión (optimizada para Streamlit) ---
@st.cache_data
def load_and_merge_data(uploaded_file_buffer: io.BytesIO) -> pd.DataFrame:
    """
    Carga y fusiona los datos de las diferentes hojas de un archivo Excel.
    Normaliza los nombres de las columnas para consistencia.

    Args:
        uploaded_file_buffer (io.BytesIO): Buffer del archivo Excel subido por el usuario.

    Returns:
        pd.DataFrame: El DataFrame combinado y limpio con columnas normalizadas.
    """
    # Cargar hojas directamente desde el buffer
    uploaded_file_buffer.seek(0) # Asegurarse de que el buffer esté al inicio
    iw29 = pd.read_excel(uploaded_file_buffer, sheet_name=0)
    uploaded_file_buffer.seek(0)
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

    # Guardar "Equipo" original desde IW29 para evitar pérdida en merges
    equipo_original = iw29[["Aviso", "Equipo", "Duración de parada", "Descripción"]].copy()

    # Extraer solo columnas necesarias de iw39 para el merge (incluyendo 'Total general (real)')
    iw39_subset = iw39[["Aviso", "Total general (real)"]]

    # Unir por 'Aviso'
    tmp1 = pd.merge(iw29, iw39_subset, on="Aviso", how="left")
    tmp2 = pd.merge(tmp1, iw65, on="Aviso", how="left")

    # Restaurar el valor original de "Equipo" de IW29 después del merge con IW65
    # Eliminar columna 'Equipo' si ya existe en tmp2 para evitar sufijos (_x, _y)
    if "Equipo" in tmp2.columns and "Equipo_y" in tmp2.columns: # Check for possible duplicates from merge
        tmp2.drop(columns=["Equipo_x", "Equipo_y"], errors='ignore', inplace=True)
    elif "Equipo" in tmp2.columns:
        tmp2.drop(columns=["Equipo"], errors='ignore', inplace=True)

    tmp2 = pd.merge(tmp2, equipo_original, on="Aviso", how="left")
    
    # Unir por 'Equipo' con IH08
    tmp3 = pd.merge(tmp2, ih08[[
        "Equipo", "Inic.garantía prov.", "Fin garantía prov.", "Texto", "Indicador ABC",
        "Denominación de objeto técnico", "Cl.objeto técnico"
    ]], on="Equipo", how="left")

    # Unir por 'Equipo' con ZPM015
    tmp4 = pd.merge(tmp3, zpm015[["Equipo", "TIPO DE SERVICIO"]], on="Equipo", how="left")
    
    # Renombrar columnas a un formato snake_case consistente para el resto de la aplicación
    final_df = tmp4.rename(columns={
        "Texto": "texto_equipo", # Originalmente "Texto_equipo"
        "Total general (real)": "costes_tot_reales", # Originalmente "Costes tot.reales"
        "Aviso": "aviso",
        "Orden": "orden",
        "Fecha de aviso": "fecha_de_aviso",
        "Código postal": "codigo_postal",
        "Status del sistema": "status_del_sistema",
        "Descripción": "descripcion",
        "Ubicación técnica": "ubicacion_tecnica",
        "Indicador": "indicador",
        "Equipo": "equipo",
        "Denominación de objeto técnico": "denominacion_de_objeto_tecnico",
        "Denominación ejecutante": "proveedor", # Renombrado a 'proveedor' para consistencia
        "Duración de parada": "duracion_de_parada", # Normalizado
        "Centro de coste": "centro_de_coste",
        "Inic.garantía prov.": "inic_garantia_prov",
        "Fin garantía prov.": "fin_garantia_prov",
        "Indicador ABC": "indicador_abc",
        "Texto código acción": "texto_codigo_accion",
        "Texto de acción": "texto_de_accion",
        "Texto grupo acción": "texto_grupo_accion",
        "TIPO DE SERVICIO": "tipo_de_servicio", # Normalizado
        "Clase de actividad": "clase_de_actividad",
        "Puesto de trabajo": "puesto_de_trabajo",
        "Cl.objeto técnico": "cl_objeto_tecnico" # Asegurar que esta también se incluya si es relevante
    })

    columnas_finales = [
        "aviso", "orden", "fecha_de_aviso", "codigo_postal", "status_del_sistema",
        "descripcion", "ubicacion_tecnica", "indicador", "equipo",
        "denominacion_de_objeto_tecnico", "proveedor", # Usar el nombre normalizado
        "duracion_de_parada", "centro_de_coste", "costes_tot_reales",
        "inic_garantia_prov", "fin_garantia_prov", "texto_equipo",
        "indicador_abc", "texto_codigo_accion", "texto_de_accion",
        "texto_grupo_accion", "tipo_de_servicio",
        "clase_de_actividad", "puesto_de_trabajo", "cl_objeto_tecnico"
    ]

    # Filtrar solo las columnas que realmente existen en el DataFrame final_df
    columnas_finales = [col for col in columnas_finales if col in final_df.columns]

    return final_df[columnas_finales]

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

def calcular_disponibilidad(df_subset: pd.DataFrame, horarios: dict) -> pd.Series:
    """Calcula la disponibilidad promedio por Tipo de Servicio.
    Asume que las columnas 'duracion_de_parada', 'denominacion_de_objeto_tecnico',
    'equipo' y 'tipo_de_servicio' existen y están normalizadas.
    """
    if df_subset.empty:
        return pd.Series(dtype=float)

    # Asegurarse de que 'duracion_de_parada' es numérica
    df_subset['duracion_de_parada'] = pd.to_numeric(df_subset['duracion_de_parada'], errors='coerce').fillna(0)

    # Mapeo de horarios basado en 'denominacion_de_objeto_tecnico'
    df_subset['Horario_Key'] = df_subset['denominacion_de_objeto_tecnico'].apply(
        lambda x: next((key for key in horarios.keys() if key.lower() in str(x).lower()), None)
    )

    # Calcular promedios de horas/día y días/año para valores por defecto
    default_horas_dia = np.mean([h[0] for h in horarios.values()])
    default_dias_anio = np.mean([h[1] for h in horarios.values()])

    df_subset['Horas_Dia_Equipo'] = df_subset.apply(
        lambda row: horarios[row['Horario_Key']][0] if row['Horario_Key'] in horarios and row['Horario_Key'] is not None else default_horas_dia,
        axis=1
    )
    df_subset['Dias_Anio_Equipo'] = df_subset.apply(
        lambda row: horarios[row['Horario_Key']][1] if row['Horario_Key'] in horarios and row['Horario_Key'] is not None else default_dias_anio,
        axis=1
    )

    df_subset['Horas_Operativas_Totales'] = df_subset['Horas_Dia_Equipo'] * df_subset['Dias_Anio_Equipo']

    # Suma de la duración de parada por equipo
    sum_parada_equipo = df_subset.groupby('equipo')['duracion_de_parada'].sum()

    # Horas operativas totales únicas por equipo
    horas_op_equipo = df_subset.drop_duplicates(subset='equipo').set_index('equipo')['Horas_Operativas_Totales']

    # Asegurarse de que los índices coincidan
    horas_op_equipo = horas_op_equipo.reindex(sum_parada_equipo.index).fillna(0)

    # Calcular disponibilidad por equipo
    # Evitar división por cero
    disponibilidad_equipo = (horas_op_equipo - sum_parada_equipo) / horas_op_equipo
    disponibilidad_equipo = disponibilidad_equipo.replace([-np.inf, np.inf], np.nan).fillna(0) * 100 # Convertir a porcentaje

    # Si la evaluación es por TIPO DE SERVICIO, promediamos la disponibilidad de los equipos por servicio
    disponibilidad_por_servicio = df_subset.groupby('tipo_de_servicio')['equipo'].apply(
        lambda equipos: disponibilidad_equipo[equipos.unique()].mean() if not equipos.empty else 0
    )
    return disponibilidad_por_servicio

def calcular_mttr(df_subset: pd.DataFrame) -> pd.Series:
    """Calcula el MTTR promedio por Tipo de Servicio.
    Asume que las columnas 'duracion_de_parada', 'aviso' y 'tipo_de_servicio' existen y están normalizadas.
    """
    if df_subset.empty:
        return pd.Series(dtype=float)
    df_subset['duracion_de_parada'] = pd.to_numeric(df_subset['duracion_de_parada'], errors='coerce').fillna(0)
    mttr = df_subset.groupby('tipo_de_servicio').apply(
        lambda x: x['duracion_de_parada'].sum() / x['aviso'].nunique() if x['aviso'].nunique() > 0 else 0
    )
    return mttr.replace([np.inf, -np.inf], np.nan).fillna(0)

def calcular_mtbf(df_subset: pd.DataFrame, horarios: dict) -> pd.Series:
    """Calcula el MTBF promedio por Tipo de Servicio.
    Asume que las columnas 'duracion_de_parada', 'denominacion_de_objeto_tecnico',
    'equipo', 'aviso' y 'tipo_de_servicio' existen y están normalizadas.
    """
    if df_subset.empty:
        return pd.Series(dtype=float)

    df_subset['duracion_de_parada'] = pd.to_numeric(df_subset['duracion_de_parada'], errors='coerce').fillna(0)

    df_subset['Horario_Key'] = df_subset['denominacion_de_objeto_tecnico'].apply(
        lambda x: next((key for key in horarios.keys() if key.lower() in str(x).lower()), None)
    )
    default_horas_dia = np.mean([h[0] for h in horarios.values()])
    default_dias_anio = np.mean([h[1] for h in horarios.values()])

    df_subset['Horas_Dia_Equipo'] = df_subset.apply(
        lambda row: horarios[row['Horario_Key']][0] if row['Horario_Key'] in horarios and row['Horario_Key'] is not None else default_horas_dia,
        axis=1
    )
    df_subset['Dias_Anio_Equipo'] = df_subset.apply(
        lambda row: horarios[row['Horario_Key']][1] if row['Horario_Key'] in horarios and row['Horario_Key'] is not None else default_dias_anio,
        axis=1
    )
    df_subset['Horas_Operativas_Totales_Equipo'] = df_subset['Horas_Dia_Equipo'] * df_subset['Dias_Anio_Equipo']

    total_parada_por_equipo = df_subset.groupby('equipo')['duracion_de_parada'].sum()
    num_avisos_por_equipo = df_subset.groupby('equipo')['aviso'].nunique()
    horas_op_unicas_equipo = df_subset.drop_duplicates(subset='equipo').set_index('equipo')['Horas_Operativas_Totales_Equipo']

    # Reindexar para asegurar que todos los equipos estén alineados
    common_index = horas_op_unicas_equipo.index.intersection(total_parada_por_equipo.index).intersection(num_avisos_por_equipo.index)
    
    horas_op_unicas_equipo = horas_op_unicas_equipo.reindex(common_index).fillna(0)
    total_parada_por_equipo = total_parada_por_equipo.reindex(common_index).fillna(0)
    num_avisos_por_equipo = num_avisos_por_equipo.reindex(common_index).fillna(0)

    # Calcular MTBF por equipo, manejando división por cero
    mtbf_equipo = (horas_op_unicas_equipo - total_parada_por_equipo) / num_avisos_por_equipo
    mtbf_equipo = mtbf_equipo.replace([np.inf, -np.inf], np.nan).fillna(0) # Manejar divisiones por cero

    # Promediar MTBF de los equipos por servicio
    mtbf_por_servicio = df_subset.groupby('tipo_de_servicio')['equipo'].apply(
        lambda equipos: mtbf_equipo[equipos.unique()].mean() if not equipos.empty else 0
    )
    return mtbf_por_servicio

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
        self.df = df
        # Usar nombres de columnas normalizados
        self.EJECUTANTE_COL_NAME_NORMALIZED = "proveedor"
        self.COL_COSTOS_NORMALIZED = "costes_tot_reales"
        self.COL_DURACION_PARADA_NORMALIZED = "duracion_de_parada"

        # Categorización de descripción
        if 'descripcion' in self.df.columns:
            self.df['description_category'] = self.df['descripcion'].apply(self._categorize_description)
        else:
            self.df['description_category'] = "Sin Categoría" # Fallback si 'descripcion' no existe

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
            if (v[0] in self.df.columns or v[0] == "description_category") # 'description_category' es creada
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

        analysis_type = st.selectbox(
            "Selecciona el tipo de análisis:",
            list(self.opciones_menu.keys()),
            key="analysis_type_select"
        )

        group_col, value_col, analysis_metric = self.opciones_menu[analysis_type]

        # Asegurarse que la columna de agrupación exista (excepto para 'description_category' que es nueva)
        if group_col not in self.df.columns and group_col != "description_category":
            st.warning(f"La columna '{group_col}' no se encontró en los datos para este análisis. Por favor, verifica tu archivo Excel.")
            return

        if analysis_metric == "costos":
            if value_col not in self.df.columns:
                st.warning(f"La columna de costos '{value_col}' no se encontró en los datos para este análisis. Por favor, verifica tu archivo Excel.")
                return
            grouped_data = self.df.groupby(group_col)[value_col].sum().sort_values(ascending=False)
            title = f"Costos Totales por {analysis_type.split(' por ')[1].replace('por', 'según')}"
            y_label = "Costo Total Real"
        elif analysis_metric == "avisos":
            # Asegurarse que la columna 'aviso' exista
            if 'aviso' not in self.df.columns:
                 st.warning(f"La columna 'aviso' no se encontró en los datos para el conteo. Por favor, verifica tu archivo Excel.")
                 return
            grouped_data = self.df.groupby(group_col)['aviso'].nunique().sort_values(ascending=False)
            title = f"Cantidad de Avisos por {analysis_type.split(' por ')[1].replace('por', 'según')}"
            y_label = "Cantidad de Avisos"
        else:
            st.error("Métrica de análisis no reconocida.")
            return

        # Paginación
        items_per_page = 15
        total_items = len(grouped_data)
        total_pages = (total_items + items_per_page - 1) // items_per_page

        # Inicializa la página actual si no existe o si se cambia el tipo de análisis
        if f'analysis_page_{analysis_type}' not in st.session_state:
            st.session_state[f'analysis_page_{analysis_type}'] = 0
            
        current_page = st.session_state[f'analysis_page_{analysis_type}']

        start_idx = current_page * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        paginated_data = grouped_data.iloc[start_idx:end_idx]

        st.write(f"### {title}")
        st.dataframe(paginated_data.reset_index().rename(columns={grouped_data.name: y_label}))

        # Controles de paginación
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("Página Anterior", key=f"prev_page_{analysis_type}"):
                if current_page > 0:
                    st.session_state[f'analysis_page_{analysis_type}'] -= 1
                    st.rerun()
        with col2:
            st.write(f"Página {current_page + 1} de {total_pages}")
        with col3:
            if st.button("Página Siguiente", key=f"next_page_{analysis_type}"):
                if current_page < total_pages - 1:
                    st.session_state[f'analysis_page_{analysis_type}'] += 1
                    st.rerun()

        # Gráfico
        if not paginated_data.empty:
            fig, ax = plt.subplots(figsize=(10, max(6, len(paginated_data) * 0.5)))
            # Usar paginated_data.index para las etiquetas del eje Y
            sns.barplot(x=paginated_data.values, y=paginated_data.index, ax=ax, palette='viridis') 
            ax.set_title(title)
            ax.set_xlabel(y_label)
            ax.set_ylabel(group_col.replace('_', ' ').title()) # Mejorar la etiqueta del eje Y
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No hay datos para mostrar en esta página.")

# --- Funciones de navegación para las vistas ---
def show_home_and_data_upload_page():
    st.title("¡Hola, usuario Sura! 👋")
    st.markdown("---")
    st.header("Proyecto de **Gerencia de Gestión Administrativa** en Ingeniería Clínica")
    st.markdown("""
        Aquí podrás **analizar y gestionar eficientemente los datos** de tus operaciones en Ingeniería Clínica.
        Esta aplicación te permitirá cargar tus archivos Excel, visualizar información clave y evaluar el desempeño de tus proveedores.
    """)

    st.subheader("Carga de Archivo Excel")
    uploaded_file = st.file_uploader(
        "Sube tu archivo Excel (que contenga las 5 hojas: IW29, IW39, IH08, IW65, ZPM015)",
        type=["xlsx"],
        help="El archivo debe contener las hojas 'IW29', 'IW39', 'IH08', 'IW65', 'ZPM015' en ese orden."
    )

    if uploaded_file is not None:
        st.session_state.original_excel_buffer = io.BytesIO(uploaded_file.getvalue())
        try:
            with st.spinner('Cargando y procesando datos...'):
                st.session_state.df = load_and_merge_data(st.session_state.original_excel_buffer)
            st.success("Archivo cargado y datos procesados exitosamente. ¡Puedes proceder al análisis o evaluación!")
            st.info(f"Se han cargado {len(st.session_state.df)} registros.")
            # Mostrar una previsualización de los datos cargados
            if st.checkbox("Mostrar previsualización de los datos cargados"):
                st.dataframe(st.session_state.df.head())
        except Exception as e:
            st.error(f"Ocurrió un error al cargar o procesar el archivo: {e}")
            st.info("Asegúrate de que el archivo es un Excel válido y contiene las hojas esperadas.")
            st.session_state.df = None # Reset df on error

def show_performance_evaluation_page():
    st.title("Evaluación de Desempeño de Proveedores")
    st.markdown("---")

    if st.session_state.df is None:
        st.warning("Por favor, carga un archivo Excel en la sección 'Inicio y Carga de Datos' para acceder a la evaluación.")
        return

    st.subheader("Selecciona el tipo de evaluación")
    eval_mode_options = ["Por Tipo de Servicio", "Por Proveedor"]
    st.session_state.eval_mode = st.radio(
        "Evaluar por:",
        eval_mode_options,
        key="eval_mode_radio"
    )

    df_filtered = st.session_state.df.copy()

    # Pre-calcular métricas técnicas si no se han calculado o si se ha cambiado el modo de evaluación
    if st.session_state.pre_calculated_metrics is None or 'last_eval_mode' not in st.session_state or st.session_state.last_eval_mode != st.session_state.eval_mode:
        with st.spinner("Calculando métricas de desempeño técnico..."):
            disponibilidad_series = calcular_disponibilidad(df_filtered, horarios_dict)
            mttr_series = calcular_mttr(df_filtered)
            mtbf_series = calcular_mtbf(df_filtered, horarios_dict)

            # Unificar los índices para asegurar que todos los servicios/proveedores estén presentes
            all_targets = pd.Index(list(disponibilidad_series.index) + 
                                   list(mttr_series.index) + 
                                   list(mtbf_series.index)).unique()

            pre_calculated_metrics_df = pd.DataFrame(index=all_targets)
            pre_calculated_metrics_df['Disponibilidad promedio (%)'] = disponibilidad_series
            pre_calculated_metrics_df['MTTR promedio (hrs)'] = mttr_series
            pre_calculated_metrics_df['MTBF promedio (hrs)'] = mtbf_series
            pre_calculated_metrics_df['Rendimiento promedio equipos'] = clasificar_rendimiento(disponibilidad_series)
            
            # Rellenar NaN con 0 o un valor apropiado para métricas numéricas
            numeric_cols = ['Disponibilidad promedio (%)', 'MTTR promedio (hrs)', 'MTBF promedio (hrs)']
            for col in numeric_cols:
                pre_calculated_metrics_df[col] = pre_calculated_metrics_df[col].fillna(0)
            
            # Para la columna de rendimiento, rellenar con 'No Disponible' si no hay disponibilidad
            pre_calculated_metrics_df['Rendimiento promedio equipos'] = pre_calculated_metrics_df['Rendimiento promedio equipos'].fillna('No Disponible')


            st.session_state.pre_calculated_metrics = pre_calculated_metrics_df
            st.session_state.last_eval_mode = st.session_state.eval_mode
        st.success("Métricas técnicas calculadas.")

    # Selección del objetivo de evaluación
    if st.session_state.eval_mode == "Por Tipo de Servicio":
        if 'tipo_de_servicio' in df_filtered.columns:
            target_options = ['Todos los Tipos de Servicio'] + sorted(df_filtered['tipo_de_servicio'].unique().astype(str).tolist())
        else:
            st.warning("La columna 'tipo_de_servicio' no se encontró. No se puede evaluar por Tipo de Servicio.")
            target_options = []
    else: # Por Proveedor
        if 'proveedor' in df_filtered.columns:
            target_options = ['Todos los Proveedores'] + sorted(df_filtered['proveedor'].unique().astype(str).tolist())
        else:
            st.warning("La columna 'proveedor' (Denominación ejecutante) no se encontró. No se puede evaluar por Proveedor.")
            target_options = []

    if not target_options:
        st.error("No hay opciones disponibles para la evaluación. Por favor, asegúrate de que tu archivo Excel contenga los datos necesarios.")
        return

    st.session_state.selected_eval_target = st.selectbox(
        f"Selecciona el {st.session_state.eval_mode.split(' ')[1]} a evaluar:",
        target_options,
        key="eval_target_select"
    )

    if st.session_state.selected_eval_target == 'Todos los Tipos de Servicio' or st.session_state.selected_eval_target == 'Todos los Proveedores':
        st.info(f"Mostrando métricas consolidadas para {st.session_state.selected_eval_target}. Para evaluar individualmente, selecciona una opción específica.")
        current_metrics_df = st.session_state.pre_calculated_metrics
    else:
        current_metrics_df = st.session_state.pre_calculated_metrics.loc[[st.session_state.selected_eval_target]]

    st.subheader("Métricas de Desempeño Técnico Calculadas:")
    st.dataframe(current_metrics_df)

    st.subheader("Formulario de Evaluación Manual")
    st.markdown("Por favor, asigna una puntuación a cada pregunta de acuerdo con los rangos definidos.")

    current_target = st.session_state.selected_eval_target

    total_score = 0
    max_possible_score = 0
    questions_evaluated = 0

    for category, questions in rangos_detallados.items():
        st.markdown(f"#### {category}")
        with st.container(border=True):
            for question, score_map in questions.items():
                if category == "Desempeño técnico":
                    metric_value = None
                    if current_target in st.session_state.pre_calculated_metrics.index:
                        metric_value = st.session_state.pre_calculated_metrics.loc[current_target, question]

                    if metric_value is not None and not pd.isna(metric_value):
                        # Muestra el valor de la métrica y preselecciona la opción
                        st.markdown(f"**{question}** (Valor calculado: `{metric_value:.2f}`)" if isinstance(metric_value, (int, float)) else f"**{question}** (Valor calculado: `{metric_value}`)")

                        # Determinar la opción de score que coincide con el valor de la métrica
                        pre_selected_score_value = None
                        if isinstance(metric_value, (int, float)): # Para disponibilidad, MTTR, MTBF
                            for score, desc in score_map.items():
                                if "Disponibilidad" in question:
                                    if score == 2 and metric_value >= 98: pre_selected_score_value = score
                                    elif score == 1 and (metric_value >= 75 and metric_value < 98): pre_selected_score_value = score
                                    elif score == 0 and metric_value < 75: pre_selected_score_value = score
                                elif "MTTR" in question:
                                    if score == 2 and metric_value <= 5: pre_selected_score_value = score
                                    elif score == 1 and (metric_value > 5 and metric_value <= 20): pre_selected_score_value = score
                                    elif score == 0 and metric_value > 20: pre_selected_score_value = score
                                elif "MTBF" in question:
                                    if score == 2 and metric_value > 1000: pre_selected_score_value = score
                                    elif score == 1 and (metric_value >= 100 and metric_value <= 1000): pre_selected_score_value = score
                                    elif score == 0 and metric_value < 100: pre_selected_score_value = score
                        elif isinstance(metric_value, str): # Para Rendimiento promedio equipos
                            for score, desc in score_map.items():
                                if "Rendimiento" in question:
                                    if score == 2 and "Alto" in metric_value: pre_selected_score_value = score
                                    elif score == 1 and "Medio" in metric_value: pre_selected_score_value = score
                                    elif score == 0 and "Bajo" in metric_value: pre_selected_score_value = score

                        # Convertir el score_map para usar en radio
                        options_for_radio = [f"{desc} (Puntos: {s})" for s, desc in score_map.items()]
                        default_index = 0
                        if pre_selected_score_value is not None:
                            try:
                                default_index = [s for s, desc in score_map.items()].index(pre_selected_score_value)
                            except ValueError:
                                default_index = 0 # Fallback if not found

                        selected_option_str = st.radio(
                            "Selecciona la puntuación:",
                            options_for_radio,
                            index=default_index,
                            key=f"{category}_{question}_{current_target}",
                            help="Esta métrica se calcula automáticamente."
                        )
                        # Extraer el score numérico de la cadena seleccionada
                        match = re.search(r'\(Puntos: (-?\d+)\)', selected_option_str)
                        score = int(match.group(1)) if match else 0
                    else:
                        st.markdown(f"**{question}** (Datos insuficientes para calcular)")
                        options_for_radio = [f"{desc} (Puntos: {s})" for s, desc in score_map.items()]
                        selected_option_str = st.radio(
                            "Selecciona la puntuación:",
                            options_for_radio,
                            key=f"{category}_{question}_{current_target}"
                        )
                        match = re.search(r'\(Puntos: (-?\d+)\)', selected_option_str)
                        score = int(match.group(1)) if match else 0

                else: # Preguntas de evaluación manual
                    st.markdown(f"**{question}**")
                    options_for_radio = [f"{desc} (Puntos: {s})" for s, desc in score_map.items()]
                    
                    # Cargar la evaluación previa si existe
                    previous_evaluation_key = (category, question, current_target)
                    default_index = 0
                    if previous_evaluation_key in st.session_state.evaluations:
                        prev_score = st.session_state.evaluations[previous_evaluation_key]
                        try:
                            # Encontrar el índice de la opción que coincide con el score previo
                            default_index = [s for s, desc in score_map.items()].index(prev_score)
                        except ValueError:
                            default_index = 0 # Fallback si el score previo no es válido

                    selected_option_str = st.radio(
                        "Selecciona la puntuación:",
                        options_for_radio,
                        index=default_index,
                        key=f"{category}_{question}_{current_target}"
                    )
                    # Extraer el score numérico de la cadena seleccionada
                    match = re.search(r'\(Puntos: (-?\d+)\)', selected_option_str)
                    score = int(match.group(1)) if match else 0

                # Guardar la evaluación
                st.session_state.evaluations[(category, question, current_target)] = score

                total_score += score
                max_possible_score += 2 # Score máximo posible por pregunta
                questions_evaluated += 1

    if questions_evaluated > 0:
        overall_percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        st.markdown("---")
        st.subheader("Resultados de la Evaluación")
        st.info(f"Puntuación Total para **{current_target}**: {total_score} / {max_possible_score}")
        st.progress(overall_percentage / 100, text=f"Porcentaje de Cumplimiento: **{overall_percentage:.2f}%**")
        st.metric(label="Calificación General", value=f"{overall_percentage:.2f}%")
    else:
        st.warning("No hay preguntas disponibles para evaluar o no se ha seleccionado un objetivo de evaluación válido.")

    st.markdown("---")
    st.subheader("Historial de Evaluaciones")
    if st.session_state.evaluations:
        eval_data = []
        for (category, question, target), score in st.session_state.evaluations.items():
            # Obtener la descripción del score
            description = rangos_detallados.get(category, {}).get(question, {}).get(score, "N/A")
            eval_data.append([target, category, question, score, description])
        
        eval_df = pd.DataFrame(eval_data, columns=['Objetivo de Evaluación', 'Categoría', 'Pregunta', 'Puntuación', 'Descripción'])
        st.dataframe(eval_df)
    else:
        st.info("Aún no se han registrado evaluaciones.")

def show_general_analysis_page():
    st.title("Análisis General de Datos")
    st.markdown("---")
    if st.session_state.df is None:
        st.warning("Por favor, carga un archivo Excel en la sección 'Inicio y Carga de Datos' para acceder al análisis.")
        return
    
    # Crear una instancia de AnalysisApp con el DataFrame actual
    analysis_app_instance = AnalysisApp(st.session_state.df)
    analysis_app_instance.display_analysis()


# --- Sidebar para navegación ---
st.sidebar.title("Menú Principal")
page_options = [
    "Inicio y Carga de Datos",
    "Evaluación de Desempeño",
    "Análisis General",
]
selected_page = st.sidebar.radio("Ir a:", page_options, key="main_menu_selection")
st.session_state.page = selected_page

# --- Contenido de la página ---
if st.session_state.page == "Inicio y Carga de Datos":
    show_home_and_data_upload_page()
elif st.session_state.page == "Evaluación de Desempeño":
    show_performance_evaluation_page()
elif st.session_state.page == "Análisis General":
    show_general_analysis_page()

