# -*- coding: utf-8 -*-
"""codeavisos

"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import io # Importamos io para manejar archivos en memoria
import numpy as np # Import numpy

# --- Configuración de la página (temática Sura) ---
st.set_page_config(
    page_title="Gerencia de Gestión Administrativa - Sura",
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

# Dummy horarios_dict for demonstration purposes if not provided in original code
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


# --- Funciones para cargar y preprocesar datos (Consolidada y mejorada) ---
@st.cache_data
def load_and_merge_data(uploaded_file_buffer: io.BytesIO) -> pd.DataFrame:
    """
    Carga y fusiona los datos de las diferentes hojas de un archivo Excel,
    y normaliza los nombres de las columnas. Adapta la lógica del cuaderno original
    a un entorno de Streamlit con carga de archivos.

    Args:
        uploaded_file_buffer (io.BytesIO): Buffer del archivo Excel subido por el usuario.

    Returns:
        pd.DataFrame: El DataFrame combinado y limpio con columnas normalizadas.
    """
    sheet_names_map = {
        0: "IW29",
        1: "IW39",
        2: "IH08",
        3: "IW65",
        4: "ZPM015"
    }

    sheets_data = {}
    for idx, sheet_name_key in sheet_names_map.items():
        try:
            # Rebobinar el buffer antes de cada lectura de hoja
            uploaded_file_buffer.seek(0)
            df_temp = pd.read_excel(uploaded_file_buffer, sheet_name=idx)
            # Normalizar nombres de columnas inmediatamente después de cargar
            df_temp.columns = [
                col.strip().lower().replace(' ', '_').replace('.', '').replace('(', '').replace(')', '').replace('ó', 'o').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ú', 'u')
                for col in df_temp.columns
            ]
            sheets_data[sheet_name_key.lower()] = df_temp
        except Exception as e:
            st.warning(f"No se pudo cargar la hoja {sheet_name_key} (índice {idx}): {e}. Esta hoja será ignorada.")
            sheets_data[sheet_name_key.lower()] = pd.DataFrame() # Proporcionar un DataFrame vacío

    # Asignar DataFrames normalizados
    iw29 = sheets_data.get('iw29', pd.DataFrame())
    iw39 = sheets_data.get('iw39', pd.DataFrame())
    ih08 = sheets_data.get('ih08', pd.DataFrame())
    iw65 = sheets_data.get('iw65', pd.DataFrame())
    zpm015 = sheets_data.get('zpm015', pd.DataFrame())

    # --- Pre-verificación y manejo de columnas esenciales antes de merges ---
    # Esto asegura que las columnas clave para los merges existan o se creen con valores predeterminados
    for df_name, df_obj in {"iw29": iw29, "iw39": iw39, "ih08": ih08, "iw65": iw65, "zpm015": zpm015}.items():
        if df_obj.empty: continue
        if "aviso" not in df_obj.columns:
            st.warning(f"La columna 'aviso' no se encontró en la hoja {df_name.upper()}. Se generarán avisos dummy.")
            df_obj['aviso'] = np.arange(len(df_obj))
        if "equipo" not in df_obj.columns:
            st.warning(f"La columna 'equipo' no se encontró en la hoja {df_name.upper()}. Se generarán equipos dummy.")
            df_obj['equipo'] = 'sin_equipo_' + df_obj['aviso'].astype(str)

    # Guardar "equipo" original y otras columnas clave de IW29 para evitar pérdida en el primer merge
    equipo_original = pd.DataFrame()
    if not iw29.empty and all(col in iw29.columns for col in ["aviso", "equipo", "duracion_de_parada", "descripcion"]):
        equipo_original = iw29[["aviso", "equipo", "duracion_de_parada", "descripcion"]].copy()
    else:
        st.warning("IW29 no contiene todas las columnas esperadas (aviso, equipo, duracion_de_parada, descripcion).")

    # Extraer solo columnas necesarias de iw39 para el merge (ahora con nombres normalizados)
    iw39_subset = pd.DataFrame()
    if not iw39.empty and "aviso" in iw39.columns and "total_general_real" in iw39.columns:
        iw39_subset = iw39[["aviso", "total_general_real"]]
    else:
        st.warning("IW39 no contiene 'aviso' o 'total_general_real'. Los costos reales podrían no unirse.")

    # --- Realizar merges siguiendo la lógica del código original ---
    tmp1 = iw29.copy()
    if not iw39_subset.empty:
        tmp1 = pd.merge(tmp1, iw39_subset, on="aviso", how="left")
    else:
        tmp1['total_general_real'] = np.nan # Añadir la columna si no se unió

    tmp2 = tmp1.copy()
    if not iw65.empty and "aviso" in iw65.columns:
        tmp2 = pd.merge(tmp1, iw65, on="aviso", how="left", suffixes=('_iw29', '_iw65'))
    else:
        st.warning("IW65 no contiene 'aviso'. No se unirá.")

    # Restaurar el valor original de "equipo" de IW29 después del merge si es necesario
    if not equipo_original.empty:
        # Primero, eliminar posibles columnas 'equipo' o 'equipo_iw29' que pudieron crearse
        # o ser sobrescritas por merges anteriores.
        tmp2.drop(columns=[col for col in ['equipo', 'equipo_iw29'] if col in tmp2.columns], errors='ignore', inplace=True)
        # Luego, fusionar el equipo original
        tmp2 = pd.merge(tmp2, equipo_original, on="aviso", how="left")

    # Unir por 'equipo' con IH08 (usando nombres de columnas normalizados)
    ih08_cols_to_merge_norm = [
        "equipo", "inicgarantia_prov", "fin_garantia_prov", "texto", "indicador_abc", "denominacion_de_objeto_tecnico"
    ]
    ih08_cols_to_merge_norm = [col for col in ih08_cols_to_merge_norm if col in ih08.columns]

    tmp3 = tmp2.copy()
    if not ih08.empty and "equipo" in ih08.columns and ih08_cols_to_merge_norm:
        tmp3 = pd.merge(tmp2, ih08[ih08_cols_to_merge_norm], on="equipo", how="left", suffixes=('_tmp2', '_ih08'))
    else:
        st.warning("IH08 no contiene 'equipo' o las columnas esperadas. No se unirá completamente.")
        # Asegurarse de que las columnas existan con NaN si no se unieron
        for col in ["inicgarantia_prov", "fin_garantia_prov", "texto", "indicador_abc", "denominacion_de_objeto_tecnico"]:
            if col not in tmp3.columns:
                tmp3[col] = np.nan


    # Unir por 'equipo' con ZPM015 (usando nombres de columnas normalizados)
    zpm015_cols_to_merge_norm = ["equipo", "tipo_de_servicio"]
    zpm015_cols_to_merge_norm = [col for col in zpm015_cols_to_merge_norm if col in zpm015.columns]

    tmp4 = tmp3.copy()
    if not zpm015.empty and "equipo" in zpm015.columns and zpm015_cols_to_merge_norm:
        tmp4 = pd.merge(tmp3, zpm015[zpm015_cols_to_merge_norm], on="equipo", how="left", suffixes=('_tmp3', '_zpm015'))
    else:
        st.warning("ZPM015 no contiene 'equipo' o las columnas esperadas. No se unirá completamente.")
        if "tipo_de_servicio" not in tmp4.columns:
            tmp4["tipo_de_servicio"] = np.nan

    # Renombrar columnas a los nombres normalizados finales
    final_rename_map = {
        "texto": "texto_equipo", # Desde IH08
        "total_general_real": "costes_tot_reales", # Desde IW39 (nombre normalizado)
        "denominacion_ejecutante": "proveedor", # Asumiendo que viene de IW29 o similar
        "tipo_de_servicio": "tipo_de_servicio" # Desde ZPM015 (nombre normalizado, si se llamó diferente antes)
    }
    # Aplicar renombres de forma segura, solo si la columna existe en el DF actual
    for old_name, new_name in final_rename_map.items():
        if old_name in tmp4.columns:
            tmp4.rename(columns={old_name: new_name}, inplace=True)

    # Definir las columnas finales esperadas (usando los nombres normalizados)
    expected_final_columns = [
        "aviso", "orden", "fecha_de_aviso", "codigo_postal", "status_del_sistema",
        "descripcion", "ubicacion_tecnica", "indicador", "equipo",
        "denominacion_de_objeto_tecnico", "proveedor",
        "duracion_de_parada", "centro_de_coste", "costes_tot_reales",
        "inicgarantia_prov", "fin_garantia_prov", "texto_equipo",
        "indicador_abc", "texto_codigo_accion", "texto_de_accion",
        "texto_grupo_accion", "tipo_de_servicio"
    ]

    # Asegurarse de que todas las columnas esperadas existan, añadiéndolas con NaN si faltan
    for col in expected_final_columns:
        if col not in tmp4.columns:
            tmp4[col] = np.nan

    # Convertir a tipo numérico y manejar NaNs para columnas de cálculos
    tmp4['costes_tot_reales'] = pd.to_numeric(tmp4['costes_tot_reales'], errors='coerce').fillna(0)
    tmp4['duracion_de_parada'] = pd.to_numeric(tmp4['duracion_de_parada'], errors='coerce').fillna(0)

    # Asegurarse de que 'proveedor' exista (si no se mapeó desde 'denominacion_ejecutante')
    if 'proveedor' not in tmp4.columns:
        tmp4['proveedor'] = 'Desconocido'
    
    # Asegurarse de que 'aviso' es tipo string para agrupación consistente
    if 'aviso' not in tmp4.columns:
        tmp4['aviso'] = np.arange(len(tmp4)).astype(str)
    else:
        tmp4['aviso'] = tmp4['aviso'].astype(str)


    # Filtrar registros cuyo 'status_del_sistema' contenga "PTBO" (ahora normalizado)
    if 'status_del_sistema' in tmp4.columns:
        tmp4 = tmp4[~tmp4["status_del_sistema"].str.contains("PTBO", case=False, na=False)]

    # Seleccionar solo las columnas finales presentes en el DataFrame resultante
    final_columns_present = [col for col in expected_final_columns if col in tmp4.columns]
    
    # Manejar duplicados de aviso para costes_tot_reales si persisten después del merge
    # Si un aviso tiene múltiples entradas de coste después de los merges (por ejemplo, si IW29 tuvo duplicados
    # que se combinaron con IW39), la forma más segura es agrupar y sumar los costes por aviso.
    if 'aviso' in tmp4.columns and 'costes_tot_reales' in tmp4.columns:
        # Crear una copia para evitar SettingWithCopyWarning
        tmp4_copy = tmp4.copy()
        
        # Agrupar por 'aviso' y sumar los costes, manteniendo el resto de la información
        # Se asume que para un mismo 'aviso', otras columnas como 'descripcion' o 'equipo'
        # Aquí, simplemente tomamos la primera aparición de otras columnas para el aviso agrupado.
        aggregated_costs = tmp4_copy.groupby('aviso')['costes_tot_reales'].sum().reset_index()
        
        # Merge las columnas agregadas de costes con el DataFrame original (sin duplicados de aviso en costes)
        # Se hace un drop_duplicates en 'aviso' en tmp4_copy para evitar duplicados en la columna 'aviso'
        # si se crearon durante los merges.
        tmp4_copy.drop(columns=['costes_tot_reales'], inplace=True) # Eliminar la columna de costes para evitar duplicados
        tmp4_copy.drop_duplicates(subset=['aviso'], inplace=True) # Asegurarse de que cada aviso sea único para el merge
        
        tmp4 = pd.merge(tmp4_copy, aggregated_costs, on='aviso', how='left')


    return tmp4[final_columns_present]


# --- Funciones para calcular indicadores de desempeño técnico ---
def calcular_disponibilidad(df_subset: pd.DataFrame, horarios: dict) -> pd.Series:
    """
    Calcula la disponibilidad promedio por Tipo de Servicio o Proveedor,
    promediando la disponibilidad de los equipos.
    """
    if df_subset.empty:
        return pd.Series(dtype=float)

    df_subset['duracion_de_parada'] = pd.to_numeric(df_subset['duracion_de_parada'], errors='coerce').fillna(0)

    if 'denominacion_de_objeto_tecnico' not in df_subset.columns:
        df_subset['denominacion_de_objeto_tecnico'] = 'Desconocido'

    # Map equipment to a horario key based on substring match in 'denominacion_de_objeto_tecnico'
    df_subset['horario_key'] = df_subset['denominacion_de_objeto_tecnico'].apply(
        lambda x: next((key for key in horarios.keys() if key.lower() in str(x).lower()), None)
    )

    default_horas_dia = np.mean([h[0] for h in horarios.values()]) if horarios else 8
    default_dias_anio = np.mean([h[1] for h in horarios.values()]) if horarios else 365

    df_subset['horas_dia_equipo'] = df_subset.apply(
        lambda row: horarios[row['horario_key']][0] if row['horario_key'] in horarios else default_horas_dia,
        axis=1
    )
    df_subset['dias_anio_equipo'] = df_subset.apply(
        lambda row: horarios[row['horario_key']][1] if row['horario_key'] in horarios else default_dias_anio,
        axis=1
    )
    df_subset['horas_operativas_totales'] = df_subset['horas_dia_equipo'] * df_subset['dias_anio_equipo']

    group_by_col_eq = 'equipo' if 'equipo' in df_subset.columns else 'denominacion_de_objeto_tecnico'

    sum_parada_equipo = df_subset.groupby(group_by_col_eq)['duracion_de_parada'].sum()
    horas_op_equipo = df_subset.drop_duplicates(subset=group_by_col_eq).set_index(group_by_col_eq)['horas_operativas_totales']

    horas_op_equipo = horas_op_equipo.reindex(sum_parada_equipo.index).fillna(0)

    disponibilidad_equipo = (horas_op_equipo - sum_parada_equipo) / horas_op_equipo * 100
    disponibilidad_equipo = disponibilidad_equipo.replace([-np.inf, np.inf], np.nan).fillna(0)

    group_by_eval_target = None
    if 'tipo_de_servicio' in df_subset.columns and not df_subset['tipo_de_servicio'].isnull().all():
        group_by_eval_target = 'tipo_de_servicio'
    elif 'proveedor' in df_subset.columns and not df_subset['proveedor'].isnull().all():
        group_by_eval_target = 'proveedor'

    if group_by_eval_target:
        disponibilidad_by_eval_target = df_subset.groupby(group_by_eval_target)[group_by_col_eq].apply(
            lambda equipos: disponibilidad_equipo[equipos.unique()].mean() if not equipos.empty and not disponibilidad_equipo[equipos.unique()].empty else 0
        )
    else:
        st.warning("No se encontró la columna 'tipo_de_servicio' o 'proveedor' para la agregación de disponibilidad. Calculando promedio general.")
        disponibilidad_by_eval_target = pd.Series([disponibilidad_equipo.mean()], index=['General'])

    return disponibilidad_by_eval_target.round(2)


def calcular_mttr(df_subset: pd.DataFrame) -> pd.Series:
    """Calcula el MTTR promedio por Tipo de Servicio o Proveedor."""
    if df_subset.empty:
        return pd.Series(dtype=float)
    df_subset['duracion_de_parada'] = pd.to_numeric(df_subset['duracion_de_parada'], errors='coerce').fillna(0)

    group_by_col = None
    if 'tipo_de_servicio' in df_subset.columns and not df_subset['tipo_de_servicio'].isnull().all():
        group_by_col = 'tipo_de_servicio'
    elif 'proveedor' in df_subset.columns and not df_subset['proveedor'].isnull().all():
        group_by_col = 'proveedor'

    if group_by_col:
        mttr = df_subset.groupby(group_by_col).apply(
            lambda x: x['duracion_de_parada'].sum() / x['aviso'].nunique() if x['aviso'].nunique() > 0 else 0
        )
    else:
        st.warning("No se encontró la columna 'tipo_de_servicio' o 'proveedor' para el cálculo de MTTR. Calculando promedio general.")
        mttr = pd.Series([df_subset['duracion_de_parada'].sum() / df_subset['aviso'].nunique() if df_subset['aviso'].nunique() > 0 else 0], index=['General'])

    return mttr.replace([np.inf, -np.inf], np.nan).fillna(0).round(2)

def calcular_mtbf(df_subset: pd.DataFrame, horarios: dict) -> pd.Series:
    """Calcula el MTBF promedio por Tipo de Servicio o Proveedor."""
    if df_subset.empty:
        return pd.Series(dtype=float)

    df_subset['duracion_de_parada'] = pd.to_numeric(df_subset['duracion_de_parada'], errors='coerce').fillna(0)

    if 'denominacion_de_objeto_tecnico' not in df_subset.columns:
        df_subset['denominacion_de_objeto_tecnico'] = 'Desconocido'

    df_subset['horario_key'] = df_subset['denominacion_de_objeto_tecnico'].apply(
        lambda x: next((key for key in horarios.keys() if key.lower() in str(x).lower()), None)
    )
    default_horas_dia = np.mean([h[0] for h in horarios.values()]) if horarios else 8
    default_dias_anio = np.mean([h[1] for h in horarios.values()]) if horarios else 365

    df_subset['horas_dia_equipo'] = df_subset.apply(
        lambda row: horarios[row['horario_key']][0] if row['horario_key'] in horarios else default_horas_dia,
        axis=1
    )
    df_subset['dias_anio_equipo'] = df_subset.apply(
        lambda row: horarios[row['horario_key']][1] if row['horario_key'] in horarios else default_dias_anio,
        axis=1
    )
    df_subset['horas_operativas_totales_equipo'] = df_subset['horas_dia_equipo'] * df_subset['dias_anio_equipo']

    group_by_col_eq = 'equipo' if 'equipo' in df_subset.columns else 'denominacion_de_objeto_tecnico'

    total_parada_por_equipo = df_subset.groupby(group_by_col_eq)['duracion_de_parada'].sum()
    num_avisos_por_equipo = df_subset.groupby(group_by_col_eq)['aviso'].nunique()

    horas_op_unicas_equipo = df_subset.drop_duplicates(subset=group_by_col_eq).set_index(group_by_col_eq)['horas_operativas_totales_equipo']

    total_parada_por_equipo = total_parada_por_equipo.reindex(horas_op_unicas_equipo.index).fillna(0)
    num_avisos_por_equipo = num_avisos_por_equipo.reindex(horas_op_unicas_equipo.index).fillna(0)

    # Avoid division by zero: if num_avisos_por_equipo is 0, MTBF is considered 0
    mtbf_equipo = (horas_op_unicas_equipo - total_parada_por_equipo) / num_avisos_por_equipo
    mtbf_equipo = mtbf_equipo.replace([np.inf, -np.inf], np.nan).fillna(0)

    group_by_eval_target = None
    if 'tipo_de_servicio' in df_subset.columns and not df_subset['tipo_de_servicio'].isnull().all():
        group_by_eval_target = 'tipo_de_servicio'
    elif 'proveedor' in df_subset.columns and not df_subset['proveedor'].isnull().all():
        group_by_eval_target = 'proveedor'

    if group_by_eval_target:
        mtbf_by_eval_target = df_subset.groupby(group_by_eval_target)[group_by_col_eq].apply(
            lambda equipos: mtbf_equipo[equipos.unique()].mean() if not equipos.empty and not mtbf_equipo[equipos.unique()].empty else 0
        )
    else:
        st.warning("No se encontró la columna 'tipo_de_servicio' o 'proveedor' para la agregación de MTBF. Calculando promedio general.")
        mtbf_by_eval_target = pd.Series([mtbf_equipo.mean()], index=['General'])

    return mtbf_by_eval_target.round(2)

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
            self.df['description_category'] = "Sin Categoría"

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

        # Filter options to ensure columns exist in the DataFrame
        self.opciones_menu = {
            k: v for k, v in self.opciones_menu.items()
            if ((v[0] in self.df.columns and not self.df[v[0]].isnull().all()) or v[0] == "description_category") # Check if group column exists and is not all null, or is description_category
            and (v[1] is None or (v[1] in self.df.columns and not self.df[v[1]].isnull().all())) # Check if value column exists and is not all null
        }

        if not self.opciones_menu:
            st.warning("No hay opciones de análisis disponibles. Verifica que las columnas necesarias existan y tengan datos.")

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

        if not self.opciones_menu:
            st.info("No hay opciones de análisis disponibles para mostrar gráficos. Asegúrate de que los datos se hayan cargado correctamente y contengan las columnas necesarias.")
            return

        analysis_type = st.selectbox(
            "Selecciona el tipo de análisis:",
            list(self.opciones_menu.keys()),
            key="analysis_type_select"
        )

        group_col, value_col, analysis_metric = self.opciones_menu[analysis_type]

        if group_col not in self.df.columns and group_col != "description_category":
            st.warning(f"La columna '{group_col}' no se encontró en los datos para este análisis. Por favor, revisa tu archivo.")
            return

        grouped_data = pd.Series() # Initialize as empty Series
        title = ""
        y_label = ""

        if analysis_metric == "costos":
            if value_col not in self.df.columns:
                st.warning(f"La columna de costos '{value_col}' no se encontró en los datos para este análisis.")
                return
            if not self.df[value_col].empty:
                grouped_data = self.df.groupby(group_col)[value_col].sum().sort_values(ascending=False)
                title = f"Costos Totales por {analysis_type.split(' por ')[1]}"
                y_label = "Costos Totales"
            else:
                st.info(f"No hay datos de costos disponibles para '{group_col}'.")
                return
        elif analysis_metric == "avisos":
            if not self.df['aviso'].empty:
                grouped_data = self.df.groupby(group_col)['aviso'].nunique().sort_values(ascending=False)
                title = f"Número de Avisos por {analysis_type.split(' por ')[1]}"
                y_label = "Número de Avisos Únicos"
            else:
                st.info(f"No hay datos de avisos disponibles para '{group_col}'.")
                return

        if not grouped_data.empty:
            # Display metrics for the selected analysis type
            st.markdown(f"### Desglose por {analysis_type.split(' por ')[1]}")
            st.dataframe(grouped_data.reset_index(name=y_label).rename(columns={group_col: analysis_type.split(' por ')[1]}))

            # Display bar chart
            st.markdown(f"### Gráfico de Barras: {title}")
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.barplot(x=grouped_data.index, y=grouped_data.values, ax=ax, palette='viridis')
            ax.set_title(title)
            ax.set_xlabel(analysis_type.split(' por ')[1])
            ax.set_ylabel(y_label)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No hay datos para mostrar el análisis seleccionado.")


# --- Main Application Logic ---
def main():
    st.sidebar.title("Navegación")
    selected_page = st.sidebar.radio(
        "Ir a:",
        ["Carga de Datos", "Evaluación de Proveedores", "Análisis General"],
        index=0 # Default to "Carga de Datos"
    )

    if selected_page == "Carga de Datos":
        st.title("📂 Carga de Datos")
        st.write("Sube tu archivo Excel para comenzar el análisis.")

        uploaded_file = st.file_uploader(
            "Arrastra y suelta tu archivo Excel aquí o haz clic para buscar",
            type=["xlsx"],
            accept_multiple_files=False,
            help="Sube un archivo .xlsx que contenga las hojas: IW29, IW39, IH08, IW65, ZPM015."
        )

        if uploaded_file is not None:
            # Leer el archivo como un buffer para poder pasarlo a la función de carga
            file_buffer = io.BytesIO(uploaded_file.getvalue())
            
            # Mostrar un indicador de carga mientras se procesa el archivo
            with st.spinner('Cargando y procesando datos... Esto puede tardar unos segundos.'):
                df_consolidado = load_and_merge_data(file_buffer)

            if not df_consolidado.empty:
                st.success("Archivo cargado y procesado exitosamente. Se encontraron los siguientes datos:")
                st.dataframe(df_consolidado.head())
                st.session_state['df_consolidado'] = df_consolidado
            else:
                st.error("No se pudo procesar el archivo o las hojas esperadas no contienen datos.")
                st.session_state['df_consolidado'] = pd.DataFrame()
        else:
            st.info("Esperando que subas un archivo.")
            if 'df_consolidado' not in st.session_state:
                st.session_state['df_consolidado'] = pd.DataFrame()

    elif selected_page == "Evaluación de Proveedores":
        st.title("⭐ Evaluación de Proveedores")
        st.markdown("Utiliza esta sección para evaluar a los proveedores, ya sea de forma general, por tipo de servicio o directamente por proveedor.")

        if 'df_consolidado' not in st.session_state or st.session_state['df_consolidado'].empty:
            st.warning("Por favor, carga los datos primero en la sección 'Carga de Datos' para poder realizar la evaluación de proveedores.")
            return

        df_consolidado = st.session_state['df_consolidado']

        # Evaluation type selection
        evaluation_basis = st.radio(
            "¿Cómo deseas evaluar?",
            ["General (todos los proveedores)", "Por Tipo de Servicio", "Por Proveedor Específico"],
            key="eval_basis_select"
        )

        selected_providers = []
        df_filtered_for_eval = pd.DataFrame()

        if evaluation_basis == "General (todos los proveedores)":
            if 'proveedor' in df_consolidado.columns and not df_consolidado['proveedor'].isnull().all():
                selected_providers = df_consolidado['proveedor'].unique().tolist()
                df_filtered_for_eval = df_consolidado
            else:
                st.warning("No se encontraron datos de proveedores en el archivo cargado para una evaluación general.")

        elif evaluation_basis == "Por Tipo de Servicio":
            if 'tipo_de_servicio' in df_consolidado.columns and not df_consolidado['tipo_de_servicio'].isnull().all():
                service_types = df_consolidado['tipo_de_servicio'].unique().tolist()
                if service_types:
                    selected_service_type = st.selectbox(
                        "Selecciona un Tipo de Servicio:",
                        [''] + sorted(service_types), # Add empty string for initial selection
                        key="service_type_select"
                    )
                    if selected_service_type:
                        df_filtered_for_eval = df_consolidado[df_consolidado['tipo_de_servicio'] == selected_service_type]
                        if 'proveedor' in df_filtered_for_eval.columns and not df_filtered_for_eval['proveedor'].isnull().all():
                            selected_providers = df_filtered_for_eval['proveedor'].unique().tolist()
                        else:
                            st.info(f"No se encontraron proveedores para el Tipo de Servicio '{selected_service_type}'.")
                    else:
                        st.info("Por favor, selecciona un Tipo de Servicio para continuar.")
                else:
                    st.warning("No se encontraron tipos de servicio en los datos cargados.")
            else:
                st.warning("La columna 'tipo_de_servicio' no se encontró o está vacía en los datos cargados.")

        elif evaluation_basis == "Por Proveedor Específico":
            if 'proveedor' in df_consolidado.columns and not df_consolidado['proveedor'].isnull().all():
                all_providers = df_consolidado['proveedor'].unique().tolist()
                if all_providers:
                    selected_individual_provider = st.selectbox(
                        "Selecciona un Proveedor:",
                        [''] + sorted(all_providers), # Add empty string for initial selection
                        key="individual_provider_select"
                    )
                    if selected_individual_provider:
                        selected_providers = [selected_individual_provider]
                        df_filtered_for_eval = df_consolidado[df_consolidado['proveedor'] == selected_individual_provider]
                    else:
                        st.info("Por favor, selecciona un Proveedor para continuar.")
                else:
                    st.warning("No se encontraron proveedores en los datos cargados.")
            else:
                st.warning("La columna 'proveedor' no se encontró o está vacía en los datos cargados.")

        # Filter out 'Desempeño técnico' as it's calculated, not user-scored
        categories_for_user_scoring = {k: v for k, v in rangos_detallados.items() if k != "Desempeño técnico"}

        if selected_providers:
            st.markdown(f"### Evaluación para: {', '.join(selected_providers) if len(selected_providers) <= 3 else f'{len(selected_providers)} Proveedores seleccionados'}")

            # Initialize session state for user evaluations if not present or if providers change
            current_eval_key = f"evals_{'_'.join(sorted(selected_providers))}_{evaluation_basis.replace(' ', '_')}"
            
            if current_eval_key not in st.session_state:
                initial_evaluation_data = []
                for category, questions in categories_for_user_scoring.items():
                    for question in questions.keys():
                        row = {"Categoría": category, "Pregunta": question}
                        for provider in selected_providers:
                            row[provider] = None # Initialize score for each provider
                        initial_evaluation_data.append(row)
                st.session_state[current_eval_key] = pd.DataFrame(initial_evaluation_data)

            st.subheader("Criterios de Evaluación (Ingreso Manual)")

            # Prepare column configurations for the data_editor
            column_configs = {
                "Categoría": st.column_config.TextColumn("Categoría", disabled=True),
                "Pregunta": st.column_config.TextColumn("Pregunta", disabled=True)
            }
            for provider in selected_providers:
                column_configs[provider] = st.column_config.SelectboxColumn(
                    provider,
                    help=f"Puntuación para {provider}",
                    options=[-1, 0, 1, 2],
                    required=True,
                )

            edited_eval_df = st.data_editor(
                st.session_state[current_eval_key],
                column_config=column_configs,
                hide_index=True,
                num_rows="fixed",
                use_container_width=True,
                key=f"eval_table_{current_eval_key}"
            )
            st.session_state[current_eval_key] = edited_eval_df # Update session state immediately

            st.markdown("---")
            st.subheader("Desempeño Técnico (Calculado Automáticamente)")
            
            # Calculate technical performance for each selected provider
            tech_performance_data = []
            if not df_filtered_for_eval.empty:
                for provider in selected_providers:
                    df_provider = df_filtered_for_eval[df_filtered_for_eval['proveedor'] == provider].copy()
                    
                    disponibilidad_prov = calcular_disponibilidad(df_provider, horarios_dict)
                    mttr_prov = calcular_mttr(df_provider)
                    mtbf_prov = calcular_mtbf(df_provider, horarios_dict)
                    rendimiento_prov = clasificar_rendimiento(disponibilidad_prov)

                    # Extract the general value if grouped by General, otherwise by provider name
                    disp_val = disponibilidad_prov.iloc[0] if not disponibilidad_prov.empty else 0
                    mttr_val = mttr_prov.iloc[0] if not mttr_prov.empty else 0
                    mtbf_val = mtbf_prov.iloc[0] if not mtbf_prov.empty else 0
                    rend_val = rendimiento_prov.iloc[0] if not rendimiento_prov.empty else 'N/A'

                    tech_performance_data.append({
                        "Proveedor": provider,
                        "Disponibilidad promedio (%)": f"{disp_val:.2f}",
                        "MTTR promedio (hrs)": f"{mttr_val:.2f}",
                        "MTBF promedio (hrs)": f"{mtbf_val:.2f}",
                        "Rendimiento promedio equipos": rend_val
                    })
            
            if tech_performance_data:
                tech_df = pd.DataFrame(tech_performance_data)
                st.dataframe(tech_df, hide_index=True)
            else:
                st.info("No hay datos suficientes para calcular el desempeño técnico de los proveedores seleccionados.")


            if st.button("Calcular Evaluación Final"):
                # Check if all user-scored questions have been answered for all selected providers
                all_answered = True
                for provider in selected_providers:
                    if edited_eval_df[provider].isnull().any():
                        all_answered = False
                        break

                if not all_answered:
                    st.warning("Por favor, asegúrate de responder todas las preguntas para todos los proveedores seleccionados antes de calcular la evaluación final.")
                else:
                    st.success("Evaluación Final de Proveedores:")
                    
                    final_scores = {}
                    max_possible_per_question_score = 2

                    for provider in selected_providers:
                        provider_scores = edited_eval_df[provider]
                        total_score_manual = provider_scores.sum()
                        num_manual_questions = len(edited_eval_df)
                        theoretical_max_manual_score = num_manual_questions * max_possible_per_question_score
                        
                        percentage_score_manual = 0
                        if theoretical_max_manual_score > 0:
                            percentage_score_manual = (total_score_manual / theoretical_max_manual_score) * 100

                        final_scores[provider] = {
                            "Puntuación Total (Manual)": total_score_manual,
                            "Porcentaje de Cumplimiento (Manual)": f"{percentage_score_manual:.2f}%"
                        }
                        
                        # Add technical performance scores if available
                        if not tech_df.empty:
                            tech_row = tech_df[tech_df['Proveedor'] == provider].iloc[0]
                            final_scores[provider]["Disponibilidad promedio (%)"] = tech_row["Disponibilidad promedio (%)"]
                            final_scores[provider]["MTTR promedio (hrs)"] = tech_row["MTTR promedio (hrs)"]
                            final_scores[provider]["MTBF promedio (hrs)"] = tech_row["MTBF promedio (hrs)"]
                            final_scores[provider]["Rendimiento promedio equipos"] = tech_row["Rendimiento promedio equipos"]

                    final_scores_df = pd.DataFrame.from_dict(final_scores, orient='index')
                    final_scores_df.index.name = "Proveedor"
                    st.dataframe(final_scores_df)

                    st.markdown("### Puntuación por Categoría (Manual)")
                    # Calculate scores per category for each provider
                    category_summary_per_provider = {}
                    for provider in selected_providers:
                        category_summary_per_provider[provider] = {}
                        for category in categories_for_user_scoring.keys():
                            category_questions = [q for q in categories_for_user_scoring[category].keys()]
                            
                            # Filter the edited_eval_df for the current category's questions
                            filtered_for_category = edited_eval_df[edited_eval_df['Pregunta'].isin(category_questions)]
                            
                            score_obtained = filtered_for_category[provider].sum()
                            
                            max_cat_score = len(category_questions) * max_possible_per_question_score
                            
                            percentage_cat = 0
                            if max_cat_score > 0:
                                percentage_cat = (score_obtained / max_cat_score) * 100
                            
                            category_summary_per_provider[provider][category] = f"{percentage_cat:.2f}% ({score_obtained}/{max_cat_score})"
                    
                    category_summary_df_display = pd.DataFrame.from_dict(category_summary_per_provider, orient='index')
                    category_summary_df_display.index.name = "Proveedor"
                    st.dataframe(category_summary_df_display)

        else:
            st.info("Por favor, selecciona una opción de evaluación y asegúrate de que haya proveedores disponibles para esa selección.")


    elif selected_page == "Análisis General":
        st.title("📊 Análisis General")
        if 'df_consolidado' in st.session_state and not st.session_state['df_consolidado'].empty:
            app = AnalysisApp(st.session_state['df_consolidado'])
            app.display_analysis()
        else:
            st.info("Por favor, carga los datos primero en la sección 'Carga de Datos' para realizar un análisis.")

if __name__ == "__main__":
    main()
