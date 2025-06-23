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
    if "Equipo" in tmp2.columns:
        tmp2.drop(columns=["Equipo"], errors='ignore', inplace=True)
    tmp2 = pd.merge(tmp2, equipo_original, on="Aviso", how="left")

   # Unir por 'Equipo' con IH08
    tmp3 = pd.merge(tmp2, ih08[[
        "Equipo", "Inic.garantía prov.", "Fin garantía prov.", "Texto", "Indicador ABC",
        "Denominación de objeto técnico", "Cl.objeto técnico"
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
        "Texto grupo acción", "TIPO DE SERVICIO",
        "Clase de actividad", "Puesto de trabajo"
    ]

    # Filtrar solo las columnas que realmente existen en tmp4
    columnas_finales = [col for col in columnas_finales if col in tmp4.columns]

    return tmp4[columnas_finales]

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
    """Calcula la disponibilidad promedio por Equipo."""
    if df_subset.empty:
        return pd.Series(dtype=float)

    df_subset['Duración de parada'] = pd.to_numeric(df_subset['Duración de parada'], errors='coerce').fillna(0)

    df_subset['Horario_Key'] = df_subset['Denominación de objeto técnico'].apply(
        lambda x: next((key for key in horarios.keys() if key.lower() in str(x).lower()), None)
    )

    default_horas_dia = np.mean([h[0] for h in horarios.values()])
    default_dias_anio = np.mean([h[1] for h in horarios.values()])

    df_subset['Horas_Dia_Equipo'] = df_subset.apply(
        lambda row: horarios[row['Horario_Key']][0] if row['Horario_Key'] in horarios else default_horas_dia,
        axis=1
    )
    df_subset['Dias_Anio_Equipo'] = df_subset.apply(
        lambda row: horarios[row['Horario_Key']][1] if row['Horario_Key'] in horarios else default_dias_anio,
        axis=1
    )

    df_subset['Horas_Operativas_Totales'] = df_subset['Horas_Dia_Equipo'] * df_subset['Dias_Anio_Equipo']

    sum_parada_equipo = df_subset.groupby('Equipo')['Duración de parada'].sum()

    horas_op_equipo = df_subset.drop_duplicates(subset='Equipo').set_index('Equipo')['Horas_Operativas_Totales']

    horas_op_equipo = horas_op_equipo.reindex(sum_parada_equipo.index).fillna(0)

    disponibilidad_equipo = (horas_op_equipo - sum_parada_equipo) / horas_op_equipo * 100
    disponibilidad_equipo = disponibilidad_equipo.replace([-np.inf, np.inf], np.nan).fillna(0)

    # Si la evaluación es por TIPO DE SERVICIO, promediamos la disponibilidad de los equipos por servicio
    disponibilidad_por_servicio = df_subset.groupby('TIPO DE SERVICIO')['Equipo'].apply(
        lambda equipos: disponibilidad_equipo[equipos.unique()].mean()
    )
    return disponibilidad_por_servicio

def calcular_mttr(df_subset: pd.DataFrame) -> pd.Series:
    """Calcula el MTTR promedio por Tipo de Servicio."""
    if df_subset.empty:
        return pd.Series(dtype=float)
    df_subset['Duración de parada'] = pd.to_numeric(df_subset['Duración de parada'], errors='coerce').fillna(0)
    mttr = df_subset.groupby('TIPO DE SERVICIO').apply(
        lambda x: x['Duración de parada'].sum() / x['Aviso'].nunique() if x['Aviso'].nunique() > 0 else 0
    )
    return mttr.replace([np.inf, -np.inf], np.nan).fillna(0)

def calcular_mtbf(df_subset: pd.DataFrame, horarios: dict) -> pd.Series:
    """Calcula el MTBF promedio por Tipo de Servicio."""
    if df_subset.empty:
        return pd.Series(dtype=float)

    df_subset['Duración de parada'] = pd.to_numeric(df_subset['Duración de parada'], errors='coerce').fillna(0)

    df_subset['Horario_Key'] = df_subset['Denominación de objeto técnico'].apply(
        lambda x: next((key for key in horarios.keys() if key.lower() in str(x).lower()), None)
    )
    default_horas_dia = np.mean([h[0] for h in horarios.values()])
    default_dias_anio = np.mean([h[1] for h in horarios.values()])

    df_subset['Horas_Dia_Equipo'] = df_subset.apply(
        lambda row: horarios[row['Horario_Key']][0] if row['Horario_Key'] in horarios else default_horas_dia,
        axis=1
    )
    df_subset['Dias_Anio_Equipo'] = df_subset.apply(
        lambda row: horarios[row['Horario_Key']][1] if row['Horario_Key'] in horarios else default_dias_anio,
        axis=1
    )
    df_subset['Horas_Operativas_Totales_Equipo'] = df_subset['Horas_Dia_Equipo'] * df_subset['Dias_Anio_Equipo']

    total_parada_por_equipo = df_subset.groupby('Equipo')['Duración de parada'].sum()

    num_avisos_por_equipo = df_subset.groupby('Equipo')['Aviso'].nunique()

    horas_op_unicas_equipo = df_subset.drop_duplicates(subset='Equipo').set_index('Equipo')['Horas_Operativas_Totales_Equipo']

    total_parada_por_equipo = total_parada_por_equipo.reindex(horas_op_unicas_equipo.index).fillna(0)
    num_avisos_por_equipo = num_avisos_por_equipo.reindex(horas_op_unicas_equipo.index).fillna(0)

    mtbf_equipo = (horas_op_unicas_equipo - total_parada_por_equipo) / num_avisos_por_equipo
    mtbf_equipo = mtbf_equipo.replace([np.inf, -np.inf], np.nan).fillna(0)

    mtbf_por_servicio = df_subset.groupby('TIPO DE SERVICIO')['Equipo'].apply(
        lambda equipos: mtbf_equipo[equipos.unique()].mean()
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

# --- Estado de la sesión para el menú ---
if 'page' not in st.session_state:
    st.session_state.page = 'Inicio y Carga de Datos'

# --- Sidebar para navegación ---
st.sidebar.title("Menú Principal")
page_options = [
    "Inicio y Carga de Datos",
    "Evaluación de Desempeño",
    "Análisis de Costos",
    "Análisis de Duración de Parada"
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
        Por favor, **sube el archivo `DATA2.XLSX`** para comenzar.
    """)

    uploaded_file = st.file_uploader("Sube tu archivo 'DATA2.XLSX' aquí", type=["xlsx"])

    if uploaded_file:
        file_buffer = io.BytesIO(uploaded_file.getvalue())

        with st.spinner('Cargando y procesando datos... Esto puede tomar un momento.'):
            try:
                df_processed = load_and_merge_data(file_buffer)

                initial_rows = len(df_processed)
                df_processed = df_processed[~df_processed["Status del sistema"].str.contains("PTBO", case=False, na=False)]
                st.info(f"Se eliminaron {initial_rows - len(df_processed)} registros con 'PTBO' en 'Status del sistema'.")

                df_processed['Costes tot.reales'] = pd.to_numeric(df_processed['Costes tot.reales'], errors='coerce').fillna(0)
                df_processed['Duración de parada'] = pd.to_numeric(df_processed['Duración de parada'], errors='coerce').fillna(0)

                if 'Denominación ejecutante' in df_processed.columns:
                    df_processed.rename(columns={'Denominación ejecutante': 'PROVEEDOR'}, inplace=True)
                else:
                    st.warning("La columna 'Denominación ejecutante' no se encontró para usar como 'PROVEEDOR'. Se usará 'Desconocido'.")
                    df_processed['PROVEEDOR'] = 'Desconocido'

                st.session_state.df = df_processed

                # Pre-calculate all technical metrics once after data load
                st.session_state.pre_calculated_metrics = {}
                if 'TIPO DE SERVICIO' in st.session_state.df.columns and not st.session_state.df['TIPO DE SERVICIO'].isnull().all():
                    st.session_state.pre_calculated_metrics['disponibilidad_servicio'] = calcular_disponibilidad(st.session_state.df, horarios_dict)
                    st.session_state.pre_calculated_metrics['mttr_servicio'] = calcular_mttr(st.session_state.df)
                    st.session_state.pre_calculated_metrics['mtbf_servicio'] = calcular_mtbf(st.session_state.df, horarios_dict)
                    st.session_state.pre_calculated_metrics['rendimiento_servicio'] = clasificar_rendimiento(st.session_state.pre_calculated_metrics['disponibilidad_servicio'])
                else:
                    st.warning("La columna 'TIPO DE SERVICIO' no está disponible o está vacía para el cálculo de métricas técnicas por servicio.")

                st.success("✅ Datos cargados y procesados exitosamente.")
                st.write(f"**Filas finales:** {len(st.session_state.df)} – **Columnas:** {len(st.session_state.df.columns)}")

                st.markdown("---")
                st.subheader("Vista previa de los datos procesados:")
                st.dataframe(st.session_state.df.head(10))

                st.markdown("---")
                st.subheader("Descarga de Datos Procesados")

                csv_output = st.session_state.df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar como CSV",
                    data=csv_output,
                    file_name="avisos_filtrados.csv",
                    mime="text/csv",
                    help="Descarga el archivo en formato CSV."
                )

                excel_buffer = io.BytesIO()
                st.session_state.df.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)
                st.download_button(
                    label="Descargar como Excel",
                    data=excel_buffer,
                    file_name="avisos_filtrados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Descarga el archivo en formato XLSX."
                )

                st.markdown("---")
                st.success("¡El procesamiento ha finalizado! Ahora puedes descargar tus datos o seguir explorando otras secciones.")

            except Exception as e:
                st.error(f"❌ ¡Ups! Ocurrió un error al procesar el archivo: {e}")
                st.warning("Por favor, verifica que el archivo subido sea `DATA2.XLSX` y tenga el formato de hojas esperado.")
                st.exception(e)
    else:
        st.info("⬆️ Sube tu archivo `DATA2.XLSX` para empezar con el análisis.")

# --- Sección de Evaluación de Desempeño ---
elif st.session_state.page == "Evaluación de Desempeño":
    st.title("📊 Evaluación de Desempeño")
    st.markdown("""
        Utiliza esta sección para evaluar el desempeño de los **proveedores** o **tipos de servicio**
        basado en criterios de calidad, oportunidad, precio y postventa, además de visualizar métricas de desempeño técnico.
    """)

    if st.session_state.df is None or st.session_state.df.empty:
        st.warning("Por favor, carga el archivo `DATA2.XLSX` en la sección 'Inicio y Carga de Datos' para acceder a la evaluación.")
    else:
        # Selección del modo de evaluación
        st.session_state.eval_mode = st.radio(
            "Selecciona el modo de evaluación:",
            ("Por Tipo de Servicio", "Por Proveedor"),
            index=0 if st.session_state.eval_mode == "Por Tipo de Servicio" else 1,
            key="eval_mode_radio"
        )

        if st.session_state.eval_mode == "Por Tipo de Servicio":
            if 'TIPO DE SERVICIO' in st.session_state.df.columns and not st.session_state.df['TIPO DE SERVICIO'].isnull().all():
                eval_targets = sorted(st.session_state.df['TIPO DE SERVICIO'].dropna().unique().tolist())
                target_column_name = 'TIPO DE SERVICIO'
            else:
                eval_targets = []
                st.warning("No hay 'TIPO DE SERVICIO' válidos para evaluar.")
        else: # Por Proveedor
            if 'PROVEEDOR' in st.session_state.df.columns and not st.session_state.df['PROVEEDOR'].isnull().all():
                eval_targets = sorted(st.session_state.df['PROVEEDOR'].dropna().unique().tolist())
                target_column_name = 'PROVEEDOR'
            else:
                eval_targets = []
                st.warning("No hay 'PROVEEDOR' válidos para evaluar.")

        if not eval_targets:
            st.info("No hay objetivos de evaluación disponibles. Sube un archivo con datos válidos.")
        else:
            # Selección del objetivo de evaluación
            selected_target_index = 0
            if st.session_state.selected_eval_target in eval_targets:
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
                        default_index = option_values.index(current_value) if current_value is not None else 0
                    except ValueError:
                        default_index = 0

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

            all_evaluated_targets = sorted(list(set([k[2] for k in st.session_state.evaluations.keys()])))

            matrix_data = {}
            index_names = []

            # Add manual evaluation questions as rows
            for category, questions in rangos_detallados.items():
                if category == "Desempeño técnico":
                    continue
                for question in questions:
                    full_question_name = f"**{category}**<br>{question}"
                    index_names.append(full_question_name)
                    matrix_data[full_question_name] = {}
                    for target in all_evaluated_targets:
                        score = st.session_state.evaluations.get((category, question, target), "N/A")
                        matrix_data[full_question_name][target] = score

            # Add technical metrics as rows if applicable
            if st.session_state.eval_mode == "Por Tipo de Servicio" and st.session_state.pre_calculated_metrics:
                tech_category = "Desempeño técnico"
                for tech_question, ranges in rangos_detallados[tech_category].items():
                    full_question_name = f"**{tech_category}**<br>{tech_question}"
                    index_names.append(full_question_name)
                    matrix_data[full_question_name] = {}
                    for target in all_evaluated_targets:
                        if target_column_name == 'TIPO DE SERVICIO':
                            if tech_question == "Disponibilidad promedio (%)":
                                value = st.session_state.pre_calculated_metrics['disponibilidad_servicio'].get(target, 0)
                                matrix_data[full_question_name][target] = f"{value:.2f}%"
                            elif tech_question == "MTTR promedio (hrs)":
                                value = st.session_state.pre_calculated_metrics['mttr_servicio'].get(target, 0)
                                matrix_data[full_question_name][target] = f"{value:.2f} hrs"
                            elif tech_question == "MTBF promedio (hrs)":
                                value = st.session_state.pre_calculated_metrics['mtbf_servicio'].get(target, 0)
                                matrix_data[full_question_name][target] = f"{value:.2f} hrs"
                            elif tech_question == "Rendimiento promedio equipos":
                                value = st.session_state.pre_calculated_metrics['rendimiento_servicio'].get(target, 'N/A')
                                matrix_data[full_question_name][target] = value
                            else:
                                matrix_data[full_question_name][target] = "N/A"
                        else:
                            matrix_data[full_question_name][target] = "N/A (Solo para servicios)"

            # Add a row for "Associated Providers" if evaluating by service type
            if st.session_state.eval_mode == "Por Tipo de Servicio":
                full_question_name = "**Proveedores Asociados**"
                index_names.append(full_question_name)
                matrix_data[full_question_name] = {}
                for target in all_evaluated_targets:
                    target_df_for_providers = st.session_state.df[st.session_state.df['TIPO DE SERVICIO'] == target]
                    if 'PROVEEDOR' in target_df_for_providers.columns:
                        associated_providers_for_target = target_df_for_providers['PROVEEDOR'].dropna().unique().tolist()
                        matrix_data[full_question_name][target] = ", ".join(associated_providers_for_target) if associated_providers_for_target else "Ninguno"
                    else:
                        matrix_data[full_question_name][target] = "N/A (Columna 'PROVEEDOR' no encontrada)"


            if matrix_data:
                consolidated_matrix_df = pd.DataFrame(matrix_data).T
                consolidated_matrix_df.index.name = "Criterio / Pregunta"

                st.markdown(consolidated_matrix_df.to_html(escape=False), unsafe_allow_html=True)

                csv_consolidated = consolidated_matrix_df.to_csv().encode('utf-8')
                st.download_button(
                    label="Descargar Matriz de Evaluaciones CSV",
                    data=csv_consolidated,
                    file_name="matriz_evaluaciones.csv",
                    mime="text/csv",
                    key="download_consolidated_evals_matrix"
                )
            else:
                st.info("No hay evaluaciones guardadas aún. Realiza algunas evaluaciones para ver la matriz aquí.")

# --- Sección de Análisis de Costos ---
elif st.session_state.page == "Análisis de Costos":
    st.title("💸 Análisis de Costos")
    st.markdown("---")

    if st.session_state.df is None or st.session_state.df.empty:
        st.warning("Por favor, carga el archivo `DATA2.XLSX` en la sección 'Inicio y Carga de Datos' para acceder al análisis de costos.")
    else:
        if 'PROVEEDOR' in st.session_state.df.columns and not st.session_state.df['PROVEEDOR'].isnull().all():
            costo_proveedor = st.session_state.df.groupby('PROVEEDOR')['Costes tot.reales'].sum().sort_values(ascending=False)
            st.write("### Costos Totales por Proveedor")
            st.dataframe(costo_proveedor.reset_index().rename(columns={'Costes tot.reales': 'Costo Total Real'}))

            fig_costo_proveedor, ax_costo_proveedor = plt.subplots(figsize=(10, 6))
            sns.barplot(x=costo_proveedor.index, y=costo_proveedor.values, ax=ax_costo_proveedor, palette='viridis')
            ax_costo_proveedor.set_title('Costos Totales por Proveedor')
            ax_costo_proveedor.set_xlabel('Proveedor')
            ax_costo_proveedor.set_ylabel('Costo Total Real')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig_costo_proveedor)
        else:
            st.info("No hay datos de 'PROVEEDOR' para el análisis de costos por proveedor.")

        st.markdown("---")

        if 'TIPO DE SERVICIO' in st.session_state.df.columns and not st.session_state.df['TIPO DE SERVICIO'].isnull().all():
            costo_servicio = st.session_state.df.groupby('TIPO DE SERVICIO')['Costes tot.reales'].sum().sort_values(ascending=False)
            st.write("### Costos Totales por Tipo de Servicio")
            st.dataframe(costo_servicio.reset_index().rename(columns={'Costes tot.reales': 'Costo Total Real'}))

            fig_costo_servicio, ax_costo_servicio = plt.subplots(figsize=(10, 6))
            sns.barplot(x=costo_servicio.index, y=costo_servicio.values, ax=ax_costo_servicio, palette='magma')
            ax_costo_servicio.set_title('Costos Totales por Tipo de Servicio')
            ax_costo_servicio.set_xlabel('Tipo de Servicio')
            ax_costo_servicio.set_ylabel('Costo Total Real')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig_costo_servicio)
        else:
            st.info("No hay datos de 'TIPO DE SERVICIO' para el análisis de costos por tipo de servicio.")

# --- Sección de Análisis de Duración de Parada ---
elif st.session_state.page == "Análisis de Duración de Parada":
    st.title("⏱️ Análisis de Duración de Parada")
    st.markdown("---")

    if st.session_state.df is None or st.session_state.df.empty:
        st.warning("Por favor, carga el archivo `DATA2.XLSX` en la sección 'Inicio y Carga de Datos' para acceder al análisis de duración de parada.")
    else:
        if 'TIPO DE SERVICIO' in st.session_state.df.columns and not st.session_state.df['TIPO DE SERVICIO'].isnull().all():
            parada_servicio = st.session_state.df.groupby('TIPO DE SERVICIO')['Duración de parada'].sum().sort_values(ascending=False)
            st.write("### Duración de Parada Total por Tipo de Servicio (horas)")
            st.dataframe(parada_servicio.reset_index().rename(columns={'Duración de parada': 'Duración Total de Parada (hrs)'}))

            fig_parada_servicio, ax_parada_servicio = plt.subplots(figsize=(10, 6))
            sns.barplot(x=parada_servicio.index, y=parada_servicio.values, ax=ax_parada_servicio, palette='cubehelix')
            ax_parada_servicio.set_title('Duración de Parada Total por Tipo de Servicio')
            ax_parada_servicio.set_xlabel('Tipo de Servicio')
            ax_parada_servicio.set_ylabel('Duración Total de Parada (hrs)')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig_parada_servicio)
        else:
            st.info("No hay datos de 'TIPO DE SERVICIO' para el análisis de duración de parada por tipo de servicio.")

        st.markdown("---")

        if 'PROVEEDOR' in st.session_state.df.columns and not st.session_state.df['PROVEEDOR'].isnull().all():
            parada_proveedor = st.session_state.df.groupby('PROVEEDOR')['Duración de parada'].sum().sort_values(ascending=False)
            st.write("### Duración de Parada Total por Proveedor (horas)")
            st.dataframe(parada_proveedor.reset_index().rename(columns={'Duración de parada': 'Duración Total de Parada (hrs)'}))

            fig_parada_proveedor, ax_parada_proveedor = plt.subplots(figsize=(10, 6))
            sns.barplot(x=parada_proveedor.index, y=parada_proveedor.values, ax=ax_parada_proveedor, palette='rocket')
            ax_parada_proveedor.set_title('Duración de Parada Total por Proveedor')
            ax_parada_proveedor.set_xlabel('Proveedor')
            ax_parada_proveedor.set_ylabel('Duración Total de Parada (hrs)')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig_parada_proveedor)
        else:
            st.info("No hay datos de 'PROVEEDOR' para el análisis de duración de parada por proveedor.")
