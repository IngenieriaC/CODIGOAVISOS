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
# You should replace this with your actual horarios_dict
horarios_dict = {
    'equipo_a': (8, 365),
    'equipo_b': (16, 300),
    'equipo_c': (24, 365),
}

# --- Funciones para cargar y preprocesar datos (Consolidada y mejorada) ---
@st.cache_data
def load_and_merge_data(uploaded_file_buffer: io.BytesIO) -> pd.DataFrame:
    """
    Carga y fusiona los datos de las diferentes hojas de un archivo Excel,
    y normaliza los nombres de las columnas.

    Args:
        uploaded_file_buffer (io.BytesIO): Buffer del archivo Excel subido por el usuario.

    Returns:
        pd.DataFrame: El DataFrame combinado y limpio con columnas normalizadas.
    """
    # Cargar hojas directamente desde el buffer
    # Usamos try-except para manejar casos donde una hoja no exista
    sheets_data = {}
    sheet_names = ["IW29", "IW39", "IH08", "IW65", "ZPM015"] # Assuming these are the sheet names

    for i, sheet_name in enumerate(sheet_names):
        try:
            # Rebobinar el buffer antes de cada lectura de hoja
            uploaded_file_buffer.seek(0)
            df_temp = pd.read_excel(uploaded_file_buffer, sheet_name=i)
            # Normalize column names immediately after loading
            df_temp.columns = [
                col.lower().replace(' ', '_').replace('.', '').replace('(', '').replace(')', '').replace('ó', 'o').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ú', 'u')
                for col in df_temp.columns
            ]
            sheets_data[sheet_name.lower()] = df_temp
        except Exception as e:
            st.warning(f"No se pudo cargar la hoja {sheet_name} (índice {i}): {e}. Esta hoja será ignorada.")
            sheets_data[sheet_name.lower()] = pd.DataFrame() # Provide an empty DataFrame

    iw29 = sheets_data.get('iw29', pd.DataFrame())
    iw39 = sheets_data.get('iw39', pd.DataFrame())
    ih08 = sheets_data.get('ih08', pd.DataFrame())
    iw65 = sheets_data.get('iw65', pd.DataFrame())
    zpm015 = sheets_data.get('zpm015', pd.DataFrame())

    # Ensure essential columns exist, add them if missing
    for df_name, df_obj in {"iw29": iw29, "iw39": iw39, "ih08": ih08, "iw65": iw65, "zpm015": zpm015}.items():
        if df_obj.empty: # Skip if DataFrame is empty
            continue
        if "aviso" not in df_obj.columns:
            st.warning(f"La columna 'aviso' no se encontró en la hoja {df_name.upper()}. Algunos merges podrían fallar.")
            df_obj['aviso'] = np.arange(len(df_obj)) # Add dummy avisos
        if "equipo" not in df_obj.columns:
            st.warning(f"La columna 'equipo' no se encontró en la hoja {df_name.upper()}. Algunos merges podrían fallar.")
            df_obj['equipo'] = 'sin_equipo_' + df_obj['aviso'].astype(str) # Dummy equipo

    # Guardar "equipo" original desde IW29 para evitar pérdida en el primer merge si 'equipo' está en ambos
    equipo_original = pd.DataFrame()
    if not iw29.empty and "aviso" in iw29.columns and "equipo" in iw29.columns and "duracion_de_parada" in iw29.columns and "descripcion" in iw29.columns:
        equipo_original = iw29[["aviso", "equipo", "duracion_de_parada", "descripcion"]].copy()
    else:
        st.warning("IW29 no contiene todas las columnas esperadas (aviso, equipo, duracion_de_parada, descripcion).")

    # Extraer solo columnas necesarias de iw39 para el merge (incluyendo 'total_general_(real)')
    iw39_subset = pd.DataFrame()
    if not iw39.empty and "aviso" in iw39.columns and "total_general_real" in iw39.columns:
        iw39_subset = iw39[["aviso", "total_general_real"]]
    else:
        st.warning("IW39 no contiene 'aviso' o 'total_general_real'. Los costos reales podrían no unirse.")

    # Unir por 'aviso'
    tmp1 = iw29.copy()
    if not iw39_subset.empty:
        tmp1 = pd.merge(tmp1, iw39_subset, on="aviso", how="left")
    else:
        tmp1['total_general_real'] = np.nan # Add the column if it wasn't merged

    if not iw65.empty and "aviso" in iw65.columns:
        tmp2 = pd.merge(tmp1, iw65, on="aviso", how="left", suffixes=('_iw29', '_iw65'))
    else:
        tmp2 = tmp1.copy()
        st.warning("IW65 no contiene 'aviso'. No se unirá.")

    # Restaurar el valor original de "equipo" de IW29 después del merge si es necesario
    # Esto maneja el caso donde 'equipo' podría haber sido sobrescrito si existía en IW65
    if not equipo_original.empty and "equipo_iw29" in tmp2.columns: # Check for the suffixed column if it exists
        tmp2.drop(columns=["equipo_iw29", "equipo"], errors='ignore', inplace=True) # Drop both original and suffixed if they exist
        tmp2 = pd.merge(tmp2, equipo_original, on="aviso", how="left")
    elif not equipo_original.empty and "equipo" in tmp2.columns: # If no suffix, just replace
         tmp2.drop(columns=["equipo"], errors='ignore', inplace=True)
         tmp2 = pd.merge(tmp2, equipo_original, on="aviso", how="left")
    elif not equipo_original.empty: # If 'equipo' wasn't there at all, add it
        tmp2 = pd.merge(tmp2, equipo_original, on="aviso", how="left")


    # Unir por 'equipo' con IH08
    ih08_cols_to_merge = ["equipo", "inicgarantia_prov", "fin_garantia_prov", "texto", "indicador_abc", "denominacion_de_objeto_tecnico"]
    ih08_cols_to_merge = [col for col in ih08_cols_to_merge if col in ih08.columns] # Filter existing columns

    tmp3 = tmp2.copy()
    if not ih08.empty and "equipo" in ih08.columns:
        tmp3 = pd.merge(tmp2, ih08[ih08_cols_to_merge], on="equipo", how="left", suffixes=('_tmp2', '_ih08'))
    else:
        st.warning("IH08 no contiene 'equipo'. No se unirá.")
        # Add these columns with NaNs if not merged to ensure schema consistency
        for col in ["inicgarantia_prov", "fin_garantia_prov", "texto", "indicador_abc", "denominacion_de_objeto_tecnico"]:
            if col not in tmp3.columns:
                tmp3[col] = np.nan

    # Unir por 'equipo' con ZPM015
    zpm015_cols_to_merge = ["equipo", "tipo_de_servicio"]
    zpm015_cols_to_merge = [col for col in zpm015_cols_to_merge if col in zpm015.columns] # Filter existing columns

    tmp4 = tmp3.copy()
    if not zpm015.empty and "equipo" in zpm015.columns:
        tmp4 = pd.merge(tmp3, zpm015[zpm015_cols_to_merge], on="equipo", how="left", suffixes=('_tmp3', '_zpm015'))
    else:
        st.warning("ZPM015 no contiene 'equipo'. No se unirá.")
        if "tipo_de_servicio" not in tmp4.columns:
            tmp4["tipo_de_servicio"] = np.nan

    # Renombrar columnas a los nombres normalizados finales
    final_rename_map = {
        "texto": "texto_equipo", # From IH08
        "total_general_real": "costes_tot_reales", # From IW39
        "denominacion_ejecutante": "proveedor" # Assuming this comes from IW29 or similar
    }
    # Apply renames safely
    for old_name, new_name in final_rename_map.items():
        if old_name in tmp4.columns:
            tmp4.rename(columns={old_name: new_name}, inplace=True)

    # Ensure all expected columns exist even if they couldn't be merged or renamed
    expected_final_columns = [
        "aviso", "orden", "fecha_de_aviso", "codigo_postal", "status_del_sistema",
        "descripcion", "ubicacion_tecnica", "indicador", "equipo",
        "denominacion_de_objeto_tecnico", "proveedor", # 'denominacion_ejecutante' becomes 'proveedor'
        "duracion_de_parada", "centro_de_coste", "costes_tot_reales",
        "inicgarantia_prov", "fin_garantia_prov", "texto_equipo",
        "indicador_abc", "texto_codigo_accion", "texto_de_accion",
        "texto_grupo_accion", "tipo_de_servicio"
    ]

    for col in expected_final_columns:
        if col not in tmp4.columns:
            tmp4[col] = np.nan # Add missing columns with NaN

    # Ensure 'costes_tot_reales' and 'duracion_de_parada' are numeric
    tmp4['costes_tot_reales'] = pd.to_numeric(tmp4['costes_tot_reales'], errors='coerce').fillna(0)
    tmp4['duracion_de_parada'] = pd.to_numeric(tmp4['duracion_de_parada'], errors='coerce').fillna(0)

    # Ensure 'proveedor' exists
    if 'proveedor' not in tmp4.columns:
        tmp4['proveedor'] = 'Desconocido'

    # Ensure 'aviso' exists and is unique for counting
    if 'aviso' not in tmp4.columns:
        tmp4['aviso'] = np.arange(len(tmp4))
    tmp4['aviso'] = tmp4['aviso'].astype(str) # Ensure aviso is string for consistent grouping

    # Filter only the desired final columns and return
    # Filter only the columns that actually exist in tmp4 and are in our desired list
    final_columns_present = [col for col in expected_final_columns if col in tmp4.columns]
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
            if not self.df[value_col].isnull().all():
                grouped_data = self.df.groupby(group_col)[value_col].sum().sort_values(ascending=False)
                title = f"Costos Totales por {analysis_type.split(' por ')[1].replace('por', 'según')}"
                y_label = "Costo Total Real"
            else:
                st.info(f"La columna '{value_col}' está vacía o contiene solo valores nulos. No se pueden calcular costos.")
                return
        elif analysis_metric == "avisos":
            if 'aviso' in self.df.columns and not self.df['aviso'].isnull().all():
                grouped_data = self.df.groupby(group_col)['aviso'].nunique().sort_values(ascending=False)
                title = f"Cantidad de Avisos por {analysis_type.split(' por ')[1].replace('por', 'según')}"
                y_label = "Cantidad de Avisos"
            else:
                st.info("La columna 'aviso' está vacía o contiene solo valores nulos. No se pueden contar avisos.")
                return
        else:
            st.error("Métrica de análisis no reconocida.")
            return

        if grouped_data.empty:
            st.info("No hay datos para mostrar para el análisis seleccionado.")
            return

        # Paginación
        items_per_page = 15
        total_items = len(grouped_data)
        total_pages = (total_items + items_per_page - 1) // items_per_page

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
            sns.barplot(x=paginated_data.values, y=paginated_data.index, ax=ax, palette='viridis')
            ax.set_title(title)
            ax.set_xlabel(y_label)
            ax.set_ylabel(group_col)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No hay datos para mostrar en esta página.")


# --- Initialize session state ---
if 'df' not in st.session_state:
    st.session_state.df = None
if 'evaluations' not in st.session_state:
    st.session_state.evaluations = {}
if 'selected_eval_target' not in st.session_state:
    st.session_state.selected_eval_target = None
if 'eval_mode' not in st.session_state:
    st.session_state.eval_mode = "Por Tipo de Servicio" # Default mode
if 'pre_calculated_metrics' not in st.session_state:
    st.session_state.pre_calculated_metrics = {}
if 'original_excel_buffer' not in st.session_state:
    st.session_state.original_excel_buffer = None
if 'page' not in st.session_state:
    st.session_state.page = "Inicio y Carga de Datos"

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
    st.title("¡Hola, usuario Sura! 👋")
    st.markdown("---")
    st.header("Proyecto de **Gerencia de Gestión Administrativa** en Ingeniería Clínica")
    st.markdown("""
        Aquí podrás **analizar y gestionar los datos de avisos** para optimizar los procesos.
        Por favor, **sube el archivo `BASE DE DATOS.XLSX`** para comenzar.
    """)

    uploaded_file = st.file_uploader("Sube tu archivo 'BASE DE DATOS.XLSX' aquí", type=["xlsx"])

    if uploaded_file:
        # Guardar el buffer del archivo original para descarga
        st.session_state.original_excel_buffer = io.BytesIO(uploaded_file.getvalue())
        st.session_state.original_excel_buffer.seek(0) # Rebobinar para futuras lecturas

        file_buffer = io.BytesIO(uploaded_file.getvalue())

        with st.spinner('Cargando y procesando datos... Esto puede tomar un momento.'):
            try:
                df_processed = load_and_merge_data(file_buffer)

                initial_rows = len(df_processed)
                # Asegúrate de usar el nombre de columna normalizado 'status_del_sistema'
                if 'status_del_sistema' in df_processed.columns:
                    df_processed = df_processed[~df_processed["status_del_sistema"].str.contains("PTBO", case=False, na=False)]
                    st.info(f"Se eliminaron {initial_rows - len(df_processed)} registros con 'PTBO' en 'Status del sistema'.")

                # Dejar solo una fila con coste por cada aviso (considerando el costo total para el aviso)
                # This transformation seems specific. If multiple cost entries for an aviso should be summed,
                # a simple groupby().sum() would be more appropriate earlier in the merge process.
                # Keeping it as per original logic but note for potential review.
                if 'costes_tot_reales' in df_processed.columns and 'aviso' in df_processed.columns:
                    df_processed['costes_tot_reales'] = df_processed.groupby('aviso')['costes_tot_reales'].transform(
                        lambda x: [x.iloc[0]] + [0]*(len(x)-1) if len(x) > 1 else [x.iloc[0]]
                    )
                    st.info("Se ajustaron los costes para que cada aviso tenga solo un valor de coste principal.")


                st.session_state.df = df_processed

                # Pre-calculate all technical metrics once after data load
                st.session_state.pre_calculated_metrics = {}

                st.session_state.pre_calculated_metrics['disponibilidad'] = calcular_disponibilidad(st.session_state.df, horarios_dict)
                st.session_state.pre_calculated_metrics['mttr'] = calcular_mttr(st.session_state.df)
                st.session_state.pre_calculated_metrics['mtbf'] = calcular_mtbf(st.session_state.df, horarios_dict)
                st.session_state.pre_calculated_metrics['rendimiento'] = clasificar_rendimiento(st.session_state.pre_calculated_metrics['disponibilidad'])

                st.success("✅ Datos cargados y procesados exitosamente.")
                st.write(f"**Filas finales:** {len(st.session_state.df)} – **Columnas:** {len(st.session_state.df.columns)}")

                st.markdown("---")
                st.subheader("Descarga de Datos")

                # Botón para descargar el archivo Excel original
                if st.session_state.original_excel_buffer:
                    st.download_button(
                        label="Descargar Excel Original",
                        data=st.session_state.original_excel_buffer,
                        file_name="BASE_DE_DATOS_original.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_original_excel"
                    )

                csv_output = st.session_state.df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar Datos Procesados (CSV)",
                    data=csv_output,
                    file_name="avisos_filtrados.csv",
                    mime="text/csv",
                    help="Descarga el archivo procesado en formato CSV."
                )

                excel_buffer_processed = io.BytesIO()
                st.session_state.df.to_excel(excel_buffer_processed, index=False, engine='openpyxl')
                excel_buffer_processed.seek(0)
                st.download_button(
                    label="Descargar Datos Procesados (Excel)",
                    data=excel_buffer_processed,
                    file_name="avisos_filtrados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Descarga el archivo procesado en formato XLSX."
                )

                st.markdown("---")
                st.success("¡El procesamiento ha finalizado! Ahora puedes descargar tus datos o seguir explorando otras secciones.")

            except Exception as e:
                st.error(f"❌ ¡Ups! Ocurrió un error al procesar el archivo: {e}")
                st.warning("Por favor, verifica que el archivo subido sea `BASE DE DATOS.XLSX` y tenga el formato de hojas esperado.")
                st.exception(e)
    else:
        st.info("⬆️ Sube tu archivo `BASE DE DATOS.XLSX` para empezar con el análisis.")

# --- Sección de Evaluación de Desempeño ---
elif st.session_state.page == "Evaluación de Desempeño":
    st.title("📊 Evaluación de Desempeño")
    st.markdown("""
        Utiliza esta sección para evaluar el desempeño de los **proveedores** o **tipos de servicio**
        basado en criterios de calidad, oportunidad, precio y postventa, además de visualizar métricas de desempeño técnico.
    """)

    if st.session_state.df is None or st.session_state.df.empty:
        st.warning("Por favor, carga el archivo `BASE DE DATOS.XLSX` en la sección 'Inicio y Carga de Datos' para acceder a la evaluación.")
    else:
        # Selección del modo de evaluación
        st.session_state.eval_mode = st.radio(
            "Selecciona el modo de evaluación:",
            ("Por Tipo de Servicio", "Por Proveedor"),
            index=0 if st.session_state.eval_mode == "Por Tipo de Servicio" else 1,
            key="eval_mode_radio"
        )

        target_column_for_evaluation = ''
        eval_targets = []

        if st.session_state.eval_mode == "Por Tipo de Servicio":
            if 'tipo_de_servicio' in st.session_state.df.columns and not st.session_state.df['tipo_de_servicio'].isnull().all():
                eval_targets = sorted(st.session_state.df['tipo_de_servicio'].dropna().unique().tolist())
                target_column_for_evaluation = 'tipo_de_servicio'
            else:
                st.warning("No hay 'Tipo de Servicio' válidos para evaluar. Asegúrate de que la columna exista y no esté vacía.")
        else: # Por Proveedor
            if 'proveedor' in st.session_state.df.columns and not st.session_state.df['proveedor'].isnull().all():
                eval_targets = sorted(st.session_state.df['proveedor'].dropna().unique().tolist())
                target_column_for_evaluation = 'proveedor'
            else:
                st.warning("No hay 'Proveedor' válidos para evaluar. Asegúrate de que la columna exista y no esté vacía.")

        if not eval_targets:
            st.info("No hay objetivos de evaluación disponibles. Sube un archivo con datos válidos.")
        else:
            # Initialize selected_eval_target if it's not set or not in the current eval_targets
            if st.session_state.selected_eval_target not in eval_targets:
                st.session_state.selected_eval_target = eval_targets[0]

            selected_target_index = eval_targets.index(st.session_state.selected_eval_target)

            st.session_state.selected_eval_target = st.selectbox(
                f"Selecciona el {st.session_state.eval_mode.split(' ')[1].lower()} a evaluar:",
                eval_targets,
                index=selected_target_index,
                key="selected_eval_target_box"
            )

            st.markdown(f"### Evaluación para: **{st.session_state.selected_eval_target}**")

            # Display manual evaluation questions for the selected target
            st.subheader("Criterios de Evaluación Manual:")
            for category, questions in rangos_detallados.items():
                if category == "Desempeño técnico":
                    continue
                st.markdown(f"#### {category}")
                for question, options in questions.items():
                    unique_key = f"{category}_{question}_{st.session_state.selected_eval_target}"

                    sorted_options = sorted(options.items(), key=lambda item: item[0], reverse=True)
                    option_labels = [f"{v} ({k})" for k, v in sorted_options]
                    option_values = [k for k, v in sorted_options]

                    current_value = st.session_state.evaluations.get((category, question, st.session_state.selected_eval_target), None)

                    try:
                        # Set default to 0 if current_value is not found in option_values
                        default_index = option_values.index(current_value) if current_value in option_values else 0
                    except ValueError:
                        default_index = 0 # Fallback if value not in options (e.g., if options changed)

                    selected_option = st.radio(
                        question,
                        options=option_values,
                        format_func=lambda x: options[x],
                        index=default_index,
                        key=unique_key
                    )
                    st.session_state.evaluations[(category, question, st.session_state.selected_eval_target)] = selected_option

            st.markdown("---")

            # --- Display Consolidated Evaluation Matrix ---
            st.subheader("Matriz Consolidada de Evaluaciones")

            # Collect all distinct targets that have been evaluated manually or have technical metrics
            all_targets_with_data = set()
            if target_column_for_evaluation in st.session_state.df.columns:
                 all_targets_with_data.update(st.session_state.df[target_column_for_evaluation].dropna().unique().tolist())

            # Add targets from manual evaluations
            all_targets_with_data.update([k[2] for k in st.session_state.evaluations.keys()])

            matrix_targets = sorted(list(all_targets_with_data))

            # Prepare data for the matrix
            matrix_data = []
            categories_order = ["Calidad", "Oportunidad", "Precio", "Postventa", "Desempeño técnico"] # Define a fixed order for categories

            for category in categories_order:
                for question in rangos_detallados[category].keys():
                    row = {"Categoría": category, "Pregunta": question}
                    for target in matrix_targets:
                        if category == "Desempeño técnico":
                            # Get the value for the specific target from the pre-calculated series
                            metric_series = st.session_state.pre_calculated_metrics.get(
                                question.split(" ")[0].lower().replace("disponibilidad", "disponibilidad").replace("mttr", "mttr").replace("mtbf", "mtbf").replace("rendimiento", "rendimiento"),
                                pd.Series()
                            )
                            value = metric_series.get(target, "N/A") # Default to "N/A" if not available
                        else:
                            # Get the value for the specific target and question from manual evaluations
                            value = st.session_state.evaluations.get((category, question, target), None)
                        row[target] = value
                    matrix_data.append(row)

            if matrix_data:
                evaluation_matrix_df = pd.DataFrame(matrix_data)

                # Identify columns that represent targets (i.e., not 'Categoría' or 'Pregunta')
                data_columns = [col for col in evaluation_matrix_df.columns if col not in ["Categoría", "Pregunta"]]

                if not data_columns:
                    st.info("No hay datos de evaluación para mostrar. Por favor, realiza algunas evaluaciones manuales o verifica la carga de datos.")
                else:
                    st.dataframe(evaluation_matrix_df)

                    # Calculate total scores and average scores for manual evaluations
                    score_rows = []
                    for target in data_columns:
                        total_score = 0
                        num_questions = 0

                        for category in ["Calidad", "Oportunidad", "Precio", "Postventa"]: # Only manual categories
                            for question in rangos_detallados[category].keys():
                                score = st.session_state.evaluations.get((category, question, target))
                                if score is not None:
                                    total_score += score
                                    num_questions += 1

                        avg_score = total_score / num_questions if num_questions > 0 else 0
                        score_rows.append({"Categoría": "Total Puntuación Manual", "Pregunta": "", target: total_score})
                        score_rows.append({"Categoría": "Puntuación Promedio Manual", "Pregunta": "", target: f"{avg_score:.2f}"})

                    if score_rows:
                        score_df = pd.DataFrame(score_rows)
                        # Concatenate and display the final matrix with scores
                        final_display_df = pd.concat([evaluation_matrix_df, score_df], ignore_index=True)
                        st.dataframe(final_display_df.set_index(["Categoría", "Pregunta"]))
                    else:
                        st.info("No hay datos suficientes para calcular las puntuaciones manuales totales o promedio.")

            else:
                st.info("No hay datos de evaluación para mostrar. Por favor, realiza algunas evaluaciones manuales o verifica la carga de datos.")

elif st.session_state.page == "Análisis General":
    st.title("📈 Análisis General")
    st.markdown("""
        Explora visualizaciones y desgloses de datos clave como costos y cantidad de avisos por diferentes dimensiones.
    """)
    if st.session_state.df is None or st.session_state.df.empty:
        st.warning("Por favor, carga el archivo `BASE DE DATOS.XLSX` en la sección 'Inicio y Carga de Datos' para acceder a los análisis.")
    else:
        analysis_app = AnalysisApp(st.session_state.df)
        analysis_app.display_analysis()
