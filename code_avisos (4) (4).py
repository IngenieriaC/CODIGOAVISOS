import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import io # Importamos io para manejar archivos en memoria
import numpy as np # Import numpy for numerical operations like inf, nan

# --- Configuración de la página (temática Sura) ---
st.set_page_config(
    page_title="Gerencia de Gestión Administrativa - Sura",
    layout="wide",
    initial_sidebar_state="expanded",
    # Icono de la página (opcional, puedes cambiar '📈' por el tuyo)

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
st.header("Proyecto de **Gerencia de Gestión Administrativa** en Ingeniería Clínica")
st.markdown("""
    Aquí podrás **analizar y gestionar los datos de avisos** para optimizar los procesos.
    Por favor, **sube el archivo `DATA2.XLSX`** para comenzar.
""")

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


# --- Función de carga & unión (optimizada para Streamlit) ---
@st.cache_data
def load_and_merge_data(uploaded_file_buffer: io.BytesIO) -> pd.DataFrame:
    """
    Carga y fusiona los datos de las diferentes hojas de un archivo Excel.
    Estandariza los nombres de las columnas a minúsculas con guiones bajos.

    Args:
        uploaded_file_buffer (io.BytesIO): Buffer del archivo Excel subido por el usuario.

    Returns:
        pd.DataFrame: El DataFrame combinado y limpio con nombres de columna estandarizados.
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

    # Limpiar encabezados y estandarizar a lowercase con underscores
    def standardize_cols(df_temp):
        df_temp.columns = df_temp.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('.', '').str.replace('(', '').str.replace(')', '')
        return df_temp

    iw29 = standardize_cols(iw29)
    iw39 = standardize_cols(iw39)
    ih08 = standardize_cols(ih08)
    iw65 = standardize_cols(iw65)
    zpm015 = standardize_cols(zpm015)

    # Guardar "equipo" original desde iw29 para evitar pérdida
    equipo_original = iw29[["aviso", "equipo", "duracion_de_parada", "descripcion"]].copy()

    # Extraer solo columnas necesarias de iw39 para el merge (incluyendo 'total_general_real')
    iw39_subset = iw39[["aviso", "total_general_real"]]

    # Unir por 'aviso'
    tmp1 = pd.merge(iw29, iw39_subset, on="aviso", how="left")
    tmp2 = pd.merge(tmp1, iw65, on="aviso", how="left")

    # Restaurar el valor original de "equipo" de iw29 después del merge
    tmp2.drop(columns=["equipo"], errors='ignore', inplace=True)
    tmp2 = pd.merge(tmp2, equipo_original, on="aviso", how="left")

    # Unir por 'equipo' con ih08
    tmp3 = pd.merge(tmp2, ih08[[
        "equipo", "inicgarantia_prov", "fin_garantia_prov", "texto", "indicador_abc", "denominacion_de_objeto_tecnico"
    ]], on="equipo", how="left")

    # Unir por 'equipo' con zpm015
    tmp4 = pd.merge(tmp3, zpm015[["equipo", "tipo_de_servicio"]], on="equipo", how="left")

    # Renombrar columnas para la estandarización final
    tmp4.rename(columns={
        "texto": "texto_equipo",
        "total_general_real": "costes_totreales",
        "denominacion_ejecutante": "denominacion_ejecutante", # This column name is correct now
        "duracion_de_parada": "tiempo_parada"
    }, inplace=True)

    # Define final columns with standardized names
    columnas_finales = [
        "aviso", "orden", "fecha_de_aviso", "codigo_postal", "status_del_sistema",
        "descripcion", "ubicacion_tecnica", "indicador", "equipo",
        "denominacion_de_objeto_tecnico", "denominacion_ejecutante", # Using standardized name
        "tiempo_parada", "centro_de_coste", "costes_totreales", # Using standardized names
        "inicgarantia_prov", "fin_garantia_prov", "texto_equipo",
        "indicador_abc", "texto_codigo_accion", "texto_de_accion",
        "texto_grupo_accion", "tipo_de_servicio"
    ]

    # Filter only the columns that actually exist in tmp4
    columnas_finales = [col for col in columnas_finales if col in tmp4.columns]

    df = tmp4[columnas_finales].copy() # Create a copy to avoid SettingWithCopyWarning

    # --- Add HORARIO, HORA/ DIA, DIAS/ AÑO columns ---
    df['horario'] = df['texto_equipo'].str.strip().str.upper()
    df['hora/_dia'] = df['horario'].map(lambda x: horarios_dict.get(x, (np.nan, np.nan))[0]) # Use np.nan for missing values
    df['dias/_año'] = df['horario'].map(lambda x: horarios_dict.get(x, (np.nan, np.nan))[1]) # Use np.nan for missing values

    df['dias/_año'] = pd.to_numeric(df['dias/_año'], errors='coerce')
    df['hora/_dia'] = pd.to_numeric(df['hora/_dia'], errors='coerce')

    # Ensure 'equipo' is not NaN for core calculations
    df['equipo'] = df['equipo'].fillna(0)

    # --- Additional Preprocessing ---
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

# --- DEFINICIÓN DE PREGUNTAS PARA EVALUACIÓN (kept for completeness) ---
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

# --- Definición de las preguntas y rangos DETALLADOS (kept for completeness) ---
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
        "¿La facturación refleja correctamente lo ejecutado y acordado?": { # Corrected this line
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
def calcular_indicadores(df_filtered_data, group_col='denominacion_ejecutante'):
    """
    Calcula indicadores de servicio (MTTR, MTBF, Disp, Rendimiento) agrupados por una columna.
    Args:
        df_filtered_data (pd.DataFrame): DataFrame filtrado.
        group_col (str): Columna por la cual agrupar (e.g., 'denominacion_ejecutante' or 'tipo_de_servicio').
    Returns:
        pd.DataFrame: DataFrame con los indicadores calculados.
    """
    if df_filtered_data.empty:
        return pd.DataFrame(columns=[group_col, 'Avisos', 'Costo Total', 'MTTR Promedio (hrs)', 'MTBF Promedio (hrs)', 'Disponibilidad Promedio (%)', 'Rendimiento'])

    # Ensure required columns are present
    required_cols = [group_col, 'tiempo_parada', 'costes_totreales', 'aviso', 'hora/_dia', 'dias/_año']
    missing_cols = [col for col in required_cols if col not in df_filtered_data.columns]
    if missing_cols:
        st.error(f"Faltan columnas requeridas para calcular indicadores: {', '.join(missing_cols)}")
        return pd.DataFrame(columns=[group_col, 'Avisos', 'Costo Total', 'MTTR Promedio (hrs)', 'MTBF Promedio (hrs)', 'Disponibilidad Promedio (%)', 'Rendimiento'])

    # Convert numeric columns, coercing errors to NaN
    df_filtered_data['tiempo_parada'] = pd.to_numeric(df_filtered_data['tiempo_parada'], errors='coerce').fillna(0)
    df_filtered_data['costes_totreales'] = pd.to_numeric(df_filtered_data['costes_totreales'], errors='coerce').fillna(0)
    df_filtered_data['hora/_dia'] = pd.to_numeric(df_filtered_data['hora/_dia'], errors='coerce').fillna(0)
    df_filtered_data['dias/_año'] = pd.to_numeric(df_filtered_data['dias/_año'], errors='coerce').fillna(0)


    # Group by the specified column
    grouped_data = df_filtered_data.groupby(group_col).agg(
        Avisos=('aviso', 'nunique'),
        Costo_Total=('costes_totreales', 'sum'),
        Tiempo_Parada_Total=('tiempo_parada', 'sum'),
        Mean_Tiempo_Parada=('tiempo_parada', 'mean'),
        # For ttot, we need to average HORA/DIA and DIAS/AÑO within each group
        Avg_Hora_Dia=('hora/_dia', 'mean'),
        Avg_Dias_Anio=('dias/_año', 'mean')
    ).reset_index()

    grouped_data.rename(columns={
        'Avisos': 'Avisos',
        'Costo_Total': 'Costo Total'
    }, inplace=True)

    # Calculate MTTR
    grouped_data['MTTR Promedio (hrs)'] = grouped_data['Mean_Tiempo_Parada']

    # Calculate Ttot (Total Operating Time)
    grouped_data['Ttot (hrs)'] = grouped_data['Avg_Hora_Dia'] * grouped_data['Avg_Dias_Anio']

    # Calculate MTBF
    # Use grouped_data['Avisos'] for 'fails'
    grouped_data['MTBF Promedio (hrs)'] = (grouped_data['Ttot (hrs)'] - grouped_data['Tiempo_Parada_Total']) / grouped_data['Avisos'].replace(0, np.nan)
    grouped_data['MTBF Promedio (hrs)'] = grouped_data['MTBF Promedio (hrs)'].fillna(0).replace([np.inf, -np.inf], 0) # Handle division by zero and inf

    # Calculate Disponibilidad
    # Ensure MTTR is not zero for calculation, or MTBF + MTTR is not zero
    grouped_data['Disponibilidad Promedio (%)'] = (grouped_data['MTBF Promedio (hrs)'] / (grouped_data['MTBF Promedio (hrs)'] + grouped_data['MTTR Promedio (hrs)'])).replace([np.inf, -np.inf], np.nan) * 100
    grouped_data['Disponibilidad Promedio (%)'] = grouped_data['Disponibilidad Promedio (%)'].fillna(0) # Fill NaN from division by zero, etc.

    # Calculate Rendimiento
    grouped_data['Rendimiento'] = grouped_data['Disponibilidad Promedio (%)'].apply(
        lambda v: 'Alto' if v >= 90 else ('Medio' if v >= 75 else 'Bajo') if not pd.isna(v) else 'No Aplica'
    )

    # Select and reorder final columns for display
    final_cols = [
        group_col,
        'Avisos',
        'Costo Total',
        'MTTR Promedio (hrs)',
        'MTBF Promedio (hrs)',
        'Disponibilidad Promedio (%)',
        'Rendimiento'
    ]
    return grouped_data[final_cols]


# --- COSTOS Y AVISOS APP ---
class CostosAvisosApp:
    def __init__(self, df):
        self.df = df
        # Standardized column names used throughout the class
        self.EJECUTANTE_COL_NAME_NORMALIZED = 'denominacion_ejecutante'
        self.COL_COSTOS_NORMALIZED = 'costes_totreales'
        self.COL_AVISO_NORMALIZED = 'aviso'
        self.COL_FECHA_AVISO_NORMALIZED = 'fecha_de_aviso'
        self.COL_TIEMPO_PARADA_NORMALIZED = 'tiempo_parada' # Added for detail table

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

        # Display raw total cost from the loaded df before any dashboard filters
        st.subheader("Totales de Datos Cargados (Antes de Filtros del Dashboard)")
        st.write(f"Total de Costos Reales (Datos Cargados): ${self.df[self.COL_COSTOS_NORMALIZED].sum():,.2f} COP")
        st.write(f"Total de Avisos Únicos (Datos Cargados): {self.df[self.COL_AVISO_NORMALIZED].nunique():,}")
        st.markdown("---")


        # Sidebar filters for Costos y Avisos
        st.sidebar.markdown("---")
        st.sidebar.header("Filtros para Análisis")
        all_providers = ['Todos'] + sorted(self.df[self.EJECUTANTE_COL_NAME_NORMALIZED].dropna().unique().tolist())
        selected_provider_costos = st.sidebar.selectbox("Selecciona Proveedor:", all_providers, key='costos_provider_filter')

        all_service_types = ['Todos'] + sorted(self.df['tipo_de_servicio'].dropna().unique().tolist())
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
            filtered_df_costos = filtered_df_costos[filtered_df_costos[self.EJECUTANTE_COL_NAME_NORMALIZED] == selected_provider_costos]
        if selected_service_type_costos != 'Todos':
            filtered_df_costos = filtered_df_costos[filtered_df_costos['tipo_de_servicio'] == selected_service_type_costos]

        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df_costos = filtered_df_costos[
                (filtered_df_costos[self.COL_FECHA_AVISO_NORMALIZED].dt.date >= start_date) &
                (filtered_df_costos[self.COL_FECHA_AVISO_NORMALIZED].dt.date <= end_date)
            ]

        if filtered_df_costos.empty:
            st.warning("No hay datos para los filtros seleccionados.")
            return

        st.markdown("### Resumen General de Costos y Avisos (Aplicando Filtros del Dashboard)")

        total_costos_filtered = filtered_df_costos[self.COL_COSTOS_NORMALIZED].sum()
        total_avisos_filtered = filtered_df_costos[self.COL_AVISO_NORMALIZED].nunique()
        avg_costo_por_aviso_filtered = total_costos_filtered / total_avisos_filtered if total_avisos_filtered > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Costos Reales", f"${total_costos_filtered:,.2f} COP")
        with col2:
            st.metric("Total de Avisos Únicos", f"{total_avisos_filtered:,}")
        with col3:
            st.metric("Costo Promedio por Aviso", f"${avg_costo_por_aviso_filtered:,.2f} COP")

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
        # Ensure column names match the standardized ones
        st.dataframe(filtered_df_costos[[self.COL_AVISO_NORMALIZED, self.COL_FECHA_AVISO_NORMALIZED, self.EJECUTANTE_COL_NAME_NORMALIZED, 'tipo_de_servicio', 'descripcion', self.COL_COSTOS_NORMALIZED, self.COL_TIEMPO_PARADA_NORMALIZED]].head(100))


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

    def _display_paged_table_and_plot(self, data_series, title, xlabel, ylabel, analysis_type, color_palette='coolwarm'):
        # Pagination settings
        items_per_page = 10
        total_pages = int(np.ceil(len(data_series) / items_per_page))

        # Ensure analysis_page is within valid bounds
        if 'analysis_page' not in st.session_state or st.session_state['analysis_page'] >= total_pages:
            st.session_state['analysis_page'] = 0

        st.markdown(f"##### Mostrando Página {st.session_state['analysis_page'] + 1} de {total_pages}")

        # Pagination controls
        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.button("Página Anterior", key=f"prev_page_{analysis_type}"):
                if st.session_state['analysis_page'] > 0:
                    st.session_state['analysis_page'] -= 1
                    st.experimental_rerun()
        with col_next:
            if st.button("Página Siguiente", key=f"next_page_{analysis_type}"):
                if st.session_state['analysis_page'] < total_pages - 1:
                    st.session_state['analysis_page'] += 1
                    st.experimental_rerun()

        # Get data for current page
        start_idx = st.session_state['analysis_page'] * items_per_page
        end_idx = start_idx + items_per_page
        current_page_data = data_series.iloc[start_idx:end_idx]

        # Display table
        st.dataframe(current_page_data.reset_index().rename(columns={current_page_data.index.name: xlabel, current_page_data.name: ylabel}), height=300)

        # Display plot
        self._plot_bar_chart(current_page_data, title, xlabel, ylabel, color_palette)

# --- EVALUACIÓN DE PROVEEDORES APP ---
class EvaluacionProveedoresApp:
    def __init__(self, df):
        self.df = df
        self.EJECUTANTE_COL_NAME_NORMALIZED = 'denominacion_ejecutante'
        self.COL_AVISO_NORMALIZED = 'aviso'
        self.COL_COSTOS_NORMALIZED = 'costes_totreales'
        self.COL_TIEMPO_PARADA_NORMALIZED = 'tiempo_parada'
        self.COL_HORA_DIA_NORMALIZED = 'hora/_dia'
        self.COL_DIAS_ANIO_NORMALIZED = 'dias/_año'
        self.COL_SERVICE_TYPE_NORMALIZED = 'tipo_de_servicio'

        # Initialize session state for evaluation specific variables
        if 'all_evaluation_widgets_map' not in st.session_state:
            st.session_state['all_evaluation_widgets_map'] = {}
        if 'evaluation_mode' not in st.session_state:
            st.session_state['evaluation_mode'] = 'Seleccionar...'
        if 'selected_service_type_eval' not in st.session_state:
            st.session_state['selected_service_type_eval'] = 'Seleccionar...'
        if 'selected_provider_eval' not in st.session_state:
            st.session_state['selected_provider_eval'] = 'Seleccionar...'
        if 'current_service_type_metrics' not in st.session_state: # Stores metrics when 'by_service_type'
            st.session_state['current_service_type_metrics'] = {}
        if 'current_provider_service_type_metrics' not in st.session_state: # Stores metrics when 'by_provider'
            st.session_state['current_provider_service_type_metrics'] = {}


    def display_evaluation_form(self):
        st.title("Evaluación de Proveedores")
        st.markdown("Aquí puedes evaluar a los proveedores o tipos de servicio basándote en diferentes criterios.")

        evaluation_modes = ['Seleccionar...', 'Por Tipo de Servicio (Evaluar Proveedores)', 'Por Proveedor (Evaluar Tipos de Servicio)']
        st.session_state['evaluation_mode'] = st.selectbox(
            "Selecciona el modo de evaluación:",
            options=evaluation_modes,
            key='evaluation_mode_selector'
        )

        if st.session_state['evaluation_mode'] == 'Por Tipo de Servicio (Evaluar Proveedores)':
            self._display_evaluation_by_service_type()
        elif st.session_state['evaluation_mode'] == 'Por Proveedor (Evaluar Tipos de Servicio)':
            self._display_evaluation_by_provider()
        else:
            st.info("Por favor, selecciona un modo de evaluación para continuar.")

    def _display_evaluation_by_service_type(self):
        st.subheader("Evaluación de Proveedores por Tipo de Servicio")
        all_service_types = sorted(self.df[self.COL_SERVICE_TYPE_NORMALIZED].dropna().unique().tolist())
        st.session_state['selected_service_type_eval'] = st.selectbox(
            "Selecciona un Tipo de Servicio para evaluar sus Proveedores:",
            options=['Seleccionar...'] + all_service_types,
            key='service_type_eval_selector'
        )

        if st.session_state['selected_service_type_eval'] != 'Seleccionar...':
            service_type_filtered_df = self.df[self.df[self.COL_SERVICE_TYPE_NORMALIZED] == st.session_state['selected_service_type_eval']]
            all_providers_for_service_type = sorted(service_type_filtered_df[self.EJECUTANTE_COL_NAME_NORMALIZED].dropna().unique().tolist())
            st.session_state['all_service_providers'] = all_providers_for_service_type # Store for plotting

            if not all_providers_for_service_type:
                st.warning(f"No hay proveedores asociados al tipo de servicio '{st.session_state['selected_service_type_eval']}'.")
                return

            st.markdown(f"##### Evaluando Proveedores para: **{st.session_state['selected_service_type_eval']}**")
            st.markdown("---")

            # Calculate and store metrics for the selected service type and its providers
            indicadores_result = calcular_indicadores(service_type_filtered_df, group_col=self.EJECUTANTE_COL_NAME_NORMALIZED)

            # Convert to dictionary of series for easy access in summary, indexed by provider
            cnt = indicadores_result.set_index(self.EJECUTANTE_COL_NAME_NORMALIZED)['Avisos'] if not indicadores_result.empty else pd.Series(dtype=int)
            cost = indicadores_result.set_index(self.EJECUTANTE_COL_NAME_NORMALIZED)['Costo Total'] if not indicadores_result.empty else pd.Series(dtype=float)
            mttr = indicadores_result.set_index(self.EJECUTANTE_COL_NAME_NORMALIZED)['MTTR Promedio (hrs)'] if not indicadores_result.empty else pd.Series(dtype=float)
            mtbf = indicadores_result.set_index(self.EJECUTANTE_COL_NAME_NORMALIZED)['MTBF Promedio (hrs)'] if not indicadores_result.empty else pd.Series(dtype=float)
            disp = indicadores_result.set_index(self.EJECUTANTE_COL_NAME_NORMALIZED)['Disponibilidad Promedio (%)'] if not indicadores_result.empty else pd.Series(dtype=float)
            rend = indicadores_result.set_index(self.EJECUTANTE_COL_NAME_NORMALIZED)['Rendimiento'] if not indicadores_result.empty else pd.Series(dtype=str)


            st.session_state['current_service_type_metrics'] = {
                'cnt': cnt, 'cost': cost, 'mttr': mttr, 'mtbf': mtbf, 'disp': disp, 'rend': rend
            }

            for provider in all_providers_for_service_type:
                st.markdown(f"#### Proveedor: {provider}")
                st.markdown("---")
                
                # Display quantitative metrics for this provider
                st.markdown(f"**Métricas de Desempeño ({provider}):**")
                cols = st.columns(4)
                cols[0].metric("Avisos", f"{cnt.get(provider, 0):,}")
                cols[1].metric("Costo Total", f"${cost.get(provider, 0.0):,.2f}")
                cols[2].metric("MTTR (hrs)", f"{mttr.get(provider, np.nan):.2f}" if pd.notna(mttr.get(provider, np.nan)) else "N/A")
                cols[3].metric("MTBF (hrs)", f"{mtbf.get(provider, np.nan):.2f}" if pd.notna(mtbf.get(provider, np.nan)) else "N/A")
                st.metric("Disponibilidad (%)", f"{disp.get(provider, np.nan):.2f}%" if pd.notna(disp.get(provider, np.nan)) else "N/A")
                st.metric("Rendimiento", rend.get(provider, 'No Aplica'))


                st.markdown("---")
                st.markdown(f"**Calificación Cualitativa para {provider}:**")
                for category, question_text, scale in preguntas:
                    if scale != "auto": # Only display qualitative questions here
                        options = [int(x) for x in scale.split(',')]
                        # Generate a unique key for each widget to avoid conflicts
                        unique_key = f"by_service_type-{st.session_state['selected_service_type_eval']}-{category}-{question_text}-{provider}"
                        
                        st.session_state['all_evaluation_widgets_map'][unique_key] = st.radio(
                            f"**{category}** - {question_text}",
                            options=options,
                            format_func=lambda x: rangos_detallados[category][question_text][x],
                            key=unique_key
                        )
                st.markdown("---")

            if st.button(f"Generar Resumen de Evaluación para {st.session_state['selected_service_type_eval']}", key="generate_summary_by_service_type"):
                self.generar_resumen_evaluacion(service_type_filtered_df, st.session_state['selected_service_type_eval'], 'by_service_type')
                self.graficar_rendimiento(rend)
                self.graficar_resumen_proveedor(mttr, mtbf, disp, axis_label='Proveedor')


    def _display_evaluation_by_provider(self):
        st.subheader("Evaluación de Tipos de Servicio por Proveedor")
        all_providers = sorted(self.df[self.EJECUTANTE_COL_NAME_NORMALIZED].dropna().unique().tolist())
        st.session_state['selected_provider_eval'] = st.selectbox(
            "Selecciona un Proveedor para evaluar sus Tipos de Servicio:",
            options=['Seleccionar...'] + all_providers,
            key='provider_eval_selector'
        )

        if st.session_state['selected_provider_eval'] != 'Seleccionar...':
            provider_filtered_df = self.df[self.df[self.EJECUTANTE_COL_NAME_NORMALIZED] == st.session_state['selected_provider_eval']]
            all_service_types_for_provider = sorted(provider_filtered_df[self.COL_SERVICE_TYPE_NORMALIZED].dropna().unique().tolist())
            
            if not all_service_types_for_provider:
                st.warning(f"No hay tipos de servicio asociados al proveedor '{st.session_state['selected_provider_eval']}'.")
                return

            st.markdown(f"##### Evaluando Tipos de Servicio para: **{st.session_state['selected_provider_eval']}**")
            st.markdown("---")

            st.session_state['current_provider_service_type_metrics'] = {}
            for service_type in all_service_types_for_provider:
                st.markdown(f"#### Tipo de Servicio: {service_type}")
                st.markdown("---")
                
                # Filter for this specific service type under the selected provider
                specific_sts_df = provider_filtered_df[provider_filtered_df[self.COL_SERVICE_TYPE_NORMALIZED] == service_type]
                
                # Calculate and store metrics for this specific service type
                indicadores_result = calcular_indicadores(specific_sts_df, group_col=self.COL_SERVICE_TYPE_NORMALIZED)

                # Extract scalar values from the indicators_result DataFrame (which will have one row)
                if not indicadores_result.empty:
                    sts_metrics = {
                        'cnt': indicadores_result['Avisos'].iloc[0],
                        'cost': indicadores_result['Costo Total'].iloc[0],
                        'mttr': indicadores_result['MTTR Promedio (hrs)'].iloc[0],
                        'mtbf': indicadores_result['MTBF Promedio (hrs)'].iloc[0],
                        'disp': indicadores_result['Disponibilidad Promedio (%)'].iloc[0],
                        'rend': indicadores_result['Rendimiento'].iloc[0]
                    }
                else:
                    sts_metrics = {
                        'cnt': 0, 'cost': 0.0, 'mttr': np.nan, 'mtbf': np.nan, 'disp': np.nan, 'rend': 'No Aplica'
                    }

                st.session_state['current_provider_service_type_metrics'][service_type] = sts_metrics

                # Display quantitative metrics for this service type
                st.markdown(f"**Métricas de Desempeño ({service_type}):**")
                cols = st.columns(4)
                cols[0].metric("Avisos", f"{sts_metrics['cnt']:,}")
                cols[1].metric("Costo Total", f"${sts_metrics['cost']:,.2f}")
                cols[2].metric("MTTR (hrs)", f"{sts_metrics['mttr']:.2f}" if pd.notna(sts_metrics['mttr']) else "N/A")
                cols[3].metric("MTBF (hrs)", f"{sts_metrics['mtbf']:.2f}" if pd.notna(sts_metrics['mtbf']) else "N/A")
                st.metric("Disponibilidad (%)", f"{sts_metrics['disp']:.2f}%" if pd.notna(sts_metrics['disp']) else "N/A")
                st.metric("Rendimiento", sts_metrics['rend'])

                st.markdown("---")
                st.markdown(f"**Calificación Cualitativa para {service_type}:**")
                for category, question_text, scale in preguntas:
                    if scale != "auto":
                        options = [int(x) for x in scale.split(',')]
                        unique_key = f"by_provider-{st.session_state['selected_provider_eval']}-{category}-{question_text}-{service_type}"
                        st.session_state['all_evaluation_widgets_map'][unique_key] = st.radio(
                            f"**{category}** - {question_text}",
                            options=options,
                            format_func=lambda x: rangos_detallados[category][question_text][x],
                            key=unique_key
                        )
                st.markdown("---")

            if st.button(f"Generar Resumen de Evaluación para {st.session_state['selected_provider_eval']}", key="generate_summary_by_provider"):
                self.generar_resumen_evaluacion(provider_filtered_df, st.session_state['selected_provider_eval'], 'by_provider')
                
                # Prepare data for plotting from current_provider_service_type_metrics
                # Ensure these series are correctly built from the stored dictionary of metrics
                mttr_series = pd.Series({k: v['mttr'] for k, v in st.session_state['current_provider_service_type_metrics'].items()})
                mtbf_series = pd.Series({k: v['mtbf'] for k, v in st.session_state['current_provider_service_type_metrics'].items()})
                disp_series = pd.Series({k: v['disp'] for k, v in st.session_state['current_provider_service_type_metrics'].items()})
                rend_series = pd.Series({k: v['rend'] for k, v in st.session_state['current_provider_service_type_metrics'].items()})

                self.graficar_rendimiento(rend_series)
                self.graficar_resumen_proveedor(mttr_series, mtbf_series, disp_series, axis_label='Tipo de Servicio')

    def generar_resumen_evaluacion(self, df_filtered, identifier, mode):
        st.subheader("Generando resumen de evaluación...")

        if not st.session_state.get('all_evaluation_widgets_map'):
            st.warning("No hay evaluaciones para resumir. Selecciona un modo de evaluación y completa las evaluaciones.")
            return

        summary_data = []
        quantitative_metrics_data = {
            'Identificador de Evaluación': [],
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
            all_providers_for_st = sorted(df_filtered[self.EJECUTANTE_COL_NAME_NORMALIZED].dropna().unique().tolist())
            
            # Prepare summary_df_calificacion
            for cat, texto, escala in preguntas:
                if escala != "auto": # Only process qualitative questions for this table
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
                quantitative_metrics_data['Identificador de Evaluación'].append(st_identifier)
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
            all_service_types_for_prov = sorted(df_filtered[self.COL_SERVICE_TYPE_NORMALIZED].dropna().unique().tolist())

            # Prepare summary_df_calificacion
            for cat, texto, escala in preguntas:
                if escala != "auto": # Only process qualitative questions for this table
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
                quantitative_metrics_data['Identificador de Evaluación'].append(prov_identifier)
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
                # Adjust column widths for qualitative metrics
                if sheet_name == 'Calificaciones por Pregunta':
                    # Manually set width for MultiIndex columns
                    worksheet.set_column(0, 0, 20) # Categoría
                    worksheet.set_column(1, 1, 60) # Pregunta
                    # Dynamically set width for provider/service type columns
                    for col_idx in range(2, len(summary_df_calificacion.columns) + 2):
                        max_len = max(
                            len(str(summary_df_calificacion.columns[col_idx-2])),
                            (summary_df_calificacion.iloc[:, col_idx-2].astype(str).map(len).max() if not summary_df_calificacion.iloc[:, col_idx-2].empty else 0)
                        ) + 2
                        worksheet.set_column(col_idx, col_idx, max_len)
                # Adjust column widths for quantitative metrics
                elif sheet_name == 'Metricas Cuantitativas':
                    for col_idx, col_name in enumerate(quantitative_metrics_df.columns):
                        max_len = max(
                            len(str(col_name)),
                            (quantitative_metrics_df[col_name].astype(str).map(len).max() if not quantitative_metrics_df[col_name].empty else 0)
                        ) + 2
                        worksheet.set_column(col_idx, col_idx, max_len)


        st.download_button(
            label="Descargar Resumen de Evaluación como Excel",
            data=output.getvalue(),
            file_name=f"Resumen_Evaluacion_{identifier.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"download_button_{mode}_{identifier}"
        )


    def graficar_rendimiento(self, rendimiento_series):
        st.markdown("### Gráfico de Distribución de Rendimiento")
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


    def graficar_resumen_proveedor(self, mttr_series, mtbf_series, disp_series, axis_label='denominacion_ejecutante'):
        st.markdown(f"### Gráficos de Métricas Clave de Desempeño por {axis_label.replace('_', ' ').title()}")
        
        # Combine all relevant series into one DataFrame for easy plotting
        plot_df = pd.DataFrame({
            'MTTR (hrs)': mttr_series,
            'MTBF (hrs)': mtbf_series,
            'Disponibilidad (%)': disp_series
        })
        
        # Ensure plot_df has all relevant identifiers, even if some have NaN for certain metrics
        if axis_label == self.EJECUTANTE_COL_NAME_NORMALIZED and 'all_service_providers' in st.session_state:
            plot_df = plot_df.reindex(st.session_state['all_service_providers'])
        elif axis_label == self.COL_SERVICE_TYPE_NORMALIZED and st.session_state.get('selected_provider_eval') != "Seleccionar...":
            # Recreate all_service_types_for_provider based on the selected provider.
            if 'df' in st.session_state and st.session_state['df'] is not None:
                current_df_for_provider = st.session_state['df'][
                    st.session_state['df'][self.EJECUTANTE_COL_NAME_NORMALIZED] == st.session_state['selected_provider_eval']
                ]
                all_service_types_for_current_provider = sorted(
                    current_df_for_provider[self.COL_SERVICE_TYPE_NORMALIZED].dropna().unique().tolist()
                )
                plot_df = plot_df.reindex(all_service_types_for_current_provider)


        plot_df = plot_df.fillna(0) # Fill NaN with 0 for plotting purposes if a metric is not available

        if plot_df.empty or len(plot_df) == 0:
            st.info(f"No hay datos suficientes para graficar métricas clave de desempeño por {axis_label.replace('_', ' ').title()}.")
            return

        # Adjust figsize based on number of items to avoid squashing labels
        num_items = len(plot_df)
        fig_height = max(10, num_items * 0.8) # Min height 10, grows with number of items
        fig, axes = plt.subplots(3, 1, figsize=(12, fig_height), sharex=True)
        fig.suptitle(f'Métricas Clave de Desempeño por {axis_label.replace("_", " ").title()}', fontsize=16)

        # MTTR Plot
        sns.barplot(x=plot_df.index, y='MTTR (hrs)', data=plot_df, ax=axes[0], palette='viridis')
        axes[0].set_title(f'MTTR Promedio por {axis_label.replace("_", " ").title()}')
        axes[0].set_ylabel('MTTR (hrs)')
        axes[0].tick_params(axis='x', rotation=45)

        # MTBF Plot
        sns.barplot(x=plot_df.index, y='MTBF (hrs)', data=plot_df, ax=axes[1], palette='plasma')
        axes[1].set_title(f'MTBF Promedio por {axis_label.replace("_", " ").title()}')
        axes[1].set_ylabel('MTBF (hrs)')
        axes[1].tick_params(axis='x', rotation=45)

        # Disponibilidad Plot
        sns.barplot(x=plot_df.index, y='Disponibilidad (%)', data=plot_df, ax=axes[2], palette='cividis')
        axes[2].set_title(f'Disponibilidad Promedio por {axis_label.replace("_", " ").title()}')
        axes[2].set_ylabel('Disponibilidad (%)')
        axes[2].tick_params(axis='x', rotation=45)
        
        # Set x-axis label only for the bottom plot
        axes[2].set_xlabel(axis_label.replace('_', ' ').title())

        plt.tight_layout(rect=[0, 0.03, 1, 0.96]) # Adjust layout to prevent title overlap
        st.pyplot(fig)

# --- Main Application Logic (using Streamlit's new structure) ---

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state['page'] = 'upload'

def navigate_to(page):
    st.session_state['page'] = page
    st.experimental_rerun() # Using experimental_rerun for consistency

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
            file_buffer = io.BytesIO(uploaded_file.getvalue())
            df = load_and_merge_data(file_buffer)
            
            # --- Procesamiento adicional ---
            # Eliminar registros cuyo 'status_del_sistema' contenga "PTBO"
            initial_rows = len(df)
            df = df[~df["status_del_sistema"].str.contains("PTBO", case=False, na=False)]
            st.info(f"Se eliminaron {initial_rows - len(df)} registros con 'PTBO' en 'status_del_sistema'.")

            # Dejar solo una fila con coste por cada aviso
            # Ensure 'costes_totreales' is numeric before transforming
            df['costes_totreales'] = pd.to_numeric(df['costes_totreales'], errors='coerce').fillna(0)
            df['costes_totreales'] = df.groupby('aviso')['costes_totreales'].transform(
                lambda x: [x.iloc[0]] + [0]*(len(x)-1) if len(x) > 0 else [0]
            )

            st.success("✅ Datos cargados y procesados exitosamente.")
            st.write(f"**Filas finales:** {len(df)} – **Columnas:** {len(df.columns)}")

            # Asegurarse de que la columna 'costes_totreales' sea numérica y manejar NaNs
            df['costes_totreales'] = pd.to_numeric(df['costes_totreales'], errors='coerce').fillna(0)

            # --- Suma del Total de Costo Real y de Avisos para la pantalla de carga ---
            st.markdown("---")
            st.subheader("Resumen de Totales de Datos Cargados")
            total_costo_real_upload = df['costes_totreales'].sum()
            total_avisos_upload = df['aviso'].nunique()

            st.metric(label="Total de Costo Real (Carga)", value=f"${total_costo_real_upload:,.2f}")
            st.metric(label="Total de Avisos Únicos (Carga)", value=f"{total_avisos_upload:,}")
            
            st.session_state['df'] = df # Store the processed df in session state
            
            # --- Visualización y Descarga ---
            st.markdown("---")
            st.subheader("Vista previa de los datos procesados:")
            st.dataframe(df.head(10)) # Mostrar más filas para una mejor vista previa

            st.markdown("---")
            st.subheader("Descarga de Datos Procesados")

            # Preparar CSV para descarga
            csv_output = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar como CSV",
                data=csv_output,
                file_name="avisos_filtrados.csv",
                mime="text/csv",
                help="Descarga el archivo en formato CSV."
            )

            # Preparar Excel para descarga
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer.seek(0) # Rebobinar el buffer antes de enviarlo
            st.download_button(
                label="Descargar como Excel",
                data=excel_buffer,
                file_name="avisos_filtrados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_excel_upload_page" # Unique key for download button
            )

            st.markdown("---")
            st.success("¡El procesamiento ha finalizado! Ahora puedes descargar tus datos o seguir explorando.")

        except Exception as e:
            st.error(f"❌ ¡Ups! Ocurrió un error al procesar el archivo: {e}")
            st.warning("Por favor, verifica que el archivo subido sea `DATA2.XLSX` y tenga el formato de hojas esperado.")
            st.exception(e) # Muestra el traceback completo para depuración

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
