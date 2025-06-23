# -*- coding: utf-8 -*-
# app_completa_sura.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import io

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

# --- 1. Definición de Mapeo de Columnas (desde tu código de evaluación) ---
ORIGINAL_EJECUTANTE_COL_NAME = "Denominación ejecutante"
ORIGINAL_CP_COL_NAME = "Código postal"
ORIGINAL_OBJETO_TECNICO_COL_NAME = "Denominación de objeto técnico"
ORIGINAL_TEXTO_CODIGO_ACCION_COL_NAME = "Texto código acción"
ORIGINAL_TEXTO_ACCION_COL_NAME = "Texto de acción"
ORIGINAL_TIPO_SERVICIO_COL_NAME = "Tipo de servicio" # Este es el que usaremos en la evaluación
ORIGINAL_COSTOS_COL_NAME = "Costes tot.reales"
ORIGINAL_DESCRIPTION_COL_NAME = "Descripción"
ORIGINAL_FECHA_AVISO_COL_NAME = "Fecha de aviso"
ORIGINAL_TEXTO_POSICION_COL_NAME = "Texto de posición" # Actualizado para coincidir con el error
ORIGINAL_TEXTO_EQUIPO_COL_NAME = "Texto_equipo"
ORIGINAL_DURACION_PARADA_COL_NAME = "Duración de parada"
ORIGINAL_EQUIPO_COL_NAME = "Equipo"
ORIGINAL_AVISO_COL_NAME = "Aviso"

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
    ORIGINAL_TEXTO_POSICION_COL_NAME: "texto_de_posicion", # Actualizado aquí también
    ORIGINAL_TEXTO_EQUIPO_COL_NAME: "texto_equipo",
    ORIGINAL_DURACION_PARADA_COL_NAME: "duracion_de_parada",
    ORIGINAL_EQUIPO_COL_NAME: "equipo",
    ORIGINAL_AVISO_COL_NAME: "aviso"
}

# --- 2. Definición de Rangos de Respuesta Detallados (desde tu código de evaluación) ---
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

# --- 3. Lista de Preguntas para la Evaluación (desde tu código de evaluación) ---
preguntas = [
    ("Calidad", "¿Las soluciones propuestas son coherentes con el diagnóstico y causa raíz del problema?", "fixed"),
    ("Calidad", "¿El trabajo entregado tiene materiales nuevos, originales y de marcas reconocidas?", "fixed"),
    ("Calidad", "¿Cuenta con acabados homogéneos, limpios y pulidos?", "fixed"),
    ("Calidad", "¿El trabajo entregado corresponde completamente con lo contratado?", "fixed"),
    ("Calidad", "¿La facturación refleja correctamente lo ejecutado y acordado?", "fixed"),
    ("Oportunidad", "¿La entrega de cotizaciones fue oportuna, según el contrato?", "fixed"),
    ("Oportunidad", "¿El reporte del servicio fue entregado oportunamente, según el contrato?", "fixed"),
    ("Oportunidad", "¿Cumple las fechas y horas programadas para los trabajos, según el contrato?", "fixed"),
    ("Oportunidad", "¿Responde de forma efectiva ante eventualidades emergentes, según el contrato?", "fixed"),
    ("Oportunidad", "¿Soluciona rápidamente reclamos o inquietudes por garantía, según el contrato?", "fixed"),
    ("Oportunidad", "¿Dispone de los repuestos requeridos en los tiempos necesarios, según el contrato?", "fixed"),
    ("Oportunidad", "¿Entrega las facturas en los tiempos convenidos, según el contrato?", "fixed"),
    ("Precio", "¿Los precios ofrecidos para equipos son competitivos respecto al mercado?", "fixed"),
    ("Precio", "¿Los precios ofrecidos para repuestos son competitivos respecto al mercado?", "fixed"),
    ("Precio", "Facilita llegar a una negociación (precios)", "fixed"),
    ("Precio", "Pone en consideración contratos y trabajos adjudicados en el último periodo de tiempo", "fixed"),
    ("Precio", "¿Los precios ofrecidos para mantenimientos son competitivos respecto al mercado?", "fixed"),
    ("Precio", "¿Los precios ofrecidos para insumos son competitivos respecto al mercado?", "fixed"),
    ("Postventa", "¿Tiene disposición y actitud de servicio frente a solicitudes?", "fixed"),
    ("Postventa", "¿Conoce necesidades y ofrece alternativas adecuadas?", "fixed"),
    ("Postventa", "¿Realiza seguimiento a los resultados de los trabajos?", "fixed"),
    ("Postventa", "¿Ofrece capacitaciones para el manejo de los equipos?", "fixed"),
    ("Postventa", "¿Los métodos de capacitación ofrecidos son efectivos y adecuados?", "fixed"),
    ("Desempeño técnico", "Disponibilidad promedio (%)", "auto"),
    ("Desempeño técnico", "MTTR promedio (hrs)", "auto"),
    ("Desempeño técnico", "MTBF promedio (hrs)", "auto"),
    ("Desempeño técnico", "Rendimiento promedio equipos", "auto")
]

# --- Funciones de Carga y Procesamiento de Datos (combinadas y optimizadas) ---
@st.cache_data
def load_and_merge_data(uploaded_file_buffer: io.BytesIO) -> pd.DataFrame:
    """
    Carga y fusiona los datos de las diferentes hojas de un archivo Excel.
    Aplica el mapeo de columnas directamente después de la fusión.

    Args:
        uploaded_file_buffer (io.BytesIO): Buffer del archivo Excel subido por el usuario.

    Returns:
        pd.DataFrame: El DataFrame combinado, limpio y con columnas renombradas.
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

    # Limpiar encabezados de todas las hojas
    for df_temp in (iw29, iw39, ih08, iw65, zpm015):
        df_temp.columns = df_temp.columns.str.strip()

    # Guardar "Equipo" y "Duración de parada" original desde IW29 para evitar pérdida en merges
    equipo_duracion_original = iw29[["Aviso", "Equipo", "Duración de parada", "Descripción", "Fecha de aviso"]].copy()

    # Extraer solo columnas necesarias de iw39 para el merge (incluyendo 'Total general (real)')
    iw39_subset = iw39[["Aviso", "Total general (real)"]]

    # Unir por 'Aviso'
    tmp1 = pd.merge(iw29, iw39_subset, on="Aviso", how="left")
    tmp2 = pd.merge(tmp1, iw65, on="Aviso", how="left")

    # Restaurar los valores originales de "Equipo", "Duración de parada", "Descripción", "Fecha de aviso" de IW29
    # Esto es crucial porque IW65 podría no tener estas columnas o tener NaNs
    tmp2.drop(columns=["Equipo", "Duración de parada", "Descripción", "Fecha de aviso"], errors='ignore', inplace=True)
    tmp2 = pd.merge(tmp2, equipo_duracion_original, on="Aviso", how="left")

    # Unir por 'Equipo' con IH08
    ih08_cols_to_merge = [
        "Equipo", "Inic.garantía prov.", "Fin garantía prov.", "Texto", "Indicador ABC", "Denominación de objeto técnico"
    ]
    # ¡Aquí el ajuste clave! Solo añade "Texto de posición" si existe en ih08
    if "Texto de posición" in ih08.columns:
        ih08_cols_to_merge.append("Texto de posición")
    else:
        st.warning("La columna 'Texto de posición' no se encontró en la hoja 'ih08'. No se incluirá en la fusión.")

    tmp3 = pd.merge(tmp2, ih08[ih08_cols_to_merge], on="Equipo", how="left")


    # Unir por 'Equipo' con ZPM015
    tmp4 = pd.merge(tmp3, zpm015[["Equipo", "TIPO DE SERVICIO"]], on="Equipo", how="left")

    # Renombrar columnas ANTES de filtrar y procesar para usar nombres normalizados
    tmp4.rename(columns={
        "Texto": "Texto_equipo",
        "Total general (real)": "Costes tot.reales",
        "Texto de posición": "Texto de posición" # Asegurar que este nombre sea el esperado por el mapping
    }, inplace=True)

    # Aplicar el mapeo de columnas final aquí para tener nombres consistentes
    final_df = tmp4.rename(columns=column_mapping)

    # Convertir 'fecha_de_aviso' a datetime y 'duracion_de_parada' a numérica
    if 'fecha_de_aviso' in final_df.columns:
        final_df['fecha_de_aviso'] = pd.to_datetime(final_df['fecha_de_aviso'], errors='coerce')
    if 'duracion_de_parada' in final_df.columns:
        final_df['duracion_de_parada'] = pd.to_numeric(final_df['duracion_de_parada'], errors='coerce')

    # Asegurar que las columnas clave para la evaluación de desempeño existan
    required_cols_eval = [
        "denominacion_ejecutante", "tipo_de_servicio", "duracion_de_parada", "aviso", "fecha_de_aviso"
    ]
    for col in required_cols_eval:
        if col not in final_df.columns:
            st.warning(f"La columna mapeada '{col}' es crucial y no se encontró en el archivo combinado. Algunas funcionalidades podrían verse afectadas.")
            # Si una columna crucial falta, podríamos llenar con NaNs o valores por defecto para evitar errores
            final_df[col] = None # Añadirla como None para evitar KeyError más adelante

    return final_df

def process_data_after_load(df: pd.DataFrame) -> pd.DataFrame:
    """
    Realiza los pasos de procesamiento y limpieza final sobre el DataFrame cargado.
    """
    if df.empty:
        return df

    # Eliminar registros cuyo 'Status del sistema' contenga "PTBO"
    initial_rows = len(df)
    if 'Status del sistema' in df.columns:
        df = df[~df["Status del sistema"].str.contains("PTBO", case=False, na=False)]
        st.info(f"Se eliminaron {initial_rows - len(df)} registros con 'PTBO' en 'Status del sistema'.")
    else:
        st.warning("La columna 'Status del sistema' no se encontró. No se aplicó el filtro 'PTBO'.")

    # Dejar solo una fila con coste por cada aviso
    # Asegúrate de que 'aviso' y 'costes_totreales' existan y sean del tipo correcto
    if 'aviso' in df.columns and 'costes_totreales' in df.columns:
        df['costes_totreales'] = pd.to_numeric(df['costes_totreales'], errors='coerce')
        # Crear una máscara para identificar la primera ocurrencia de cada aviso
        df['is_first_avisos_entry'] = df.groupby('aviso').cumcount() == 0
        # Multiplicar los costes solo para la primera entrada, el resto a 0
        df['costes_totreales'] = df['costes_totreales'].where(df['is_first_avisos_entry'], 0)
        df.drop(columns=['is_first_avisos_entry'], inplace=True)
    else:
        st.warning("Las columnas 'aviso' o 'costes_totreales' no se encontraron para el procesamiento de costes.")

    return df

def calculate_technical_performance(df_filtered: pd.DataFrame):
    """
    Calcula las métricas de desempeño técnico (Disponibilidad, MTTR, MTBF, Rendimiento)
    para cada tipo de servicio dentro del DataFrame filtrado.
    """
    disp = {}
    mttr = {}
    mtbf = {}
    rend = {}

    if df_filtered.empty:
        return disp, mttr, mtbf, rend

    # Asegurarse de que 'tipo_de_servicio' sea una columna válida antes de agrupar
    if 'tipo_de_servicio' not in df_filtered.columns:
        st.error("La columna 'tipo_de_servicio' no está disponible para calcular el desempeño técnico.")
        return disp, mttr, mtbf, rend

    grouped_by_service = df_filtered.groupby('tipo_de_servicio')

    for service_type, group_df in grouped_by_service:
        # MTTR: Mean Time To Repair (Duración promedio de parada)
        # Convertir a numérica, ignorando errores
        group_df['duracion_de_parada'] = pd.to_numeric(group_df['duracion_de_parada'], errors='coerce')
        mean_mttr = group_df['duracion_de_parada'].mean()
        if pd.isna(mean_mttr): mean_mttr = 0.0 # Default si no hay datos válidos

        # MTBF: Mean Time Between Failures (Tiempo promedio entre avisos/fallas)
        # Esto requiere que 'fecha_de_aviso' esté en formato datetime
        mean_mtbf = 0.0 # Default
        if 'fecha_de_aviso' in group_df.columns and not group_df['fecha_de_aviso'].empty:
            valid_dates = group_df['fecha_de_aviso'].dropna().sort_values().unique() # Fechas únicas para evitar duplicados por merges
            if len(valid_dates) > 1:
                # Calcular la diferencia de tiempo entre avisos consecutivos
                time_diffs = pd.Series(valid_dates).diff().dt.total_seconds() / 3600 # Diferencia en horas
                mean_mtbf = time_diffs.mean()
                if pd.isna(mean_mtbf): mean_mtbf = 0.0
        
        # Disponibilidad (ejemplo simplificado: basado en MTTR y MTBF)
        # Si MTTR es 0, asumimos alta disponibilidad (o no hay fallas para reparar)
        # Si MTBF es 0, no hay tiempo entre fallas (fallas constantes o no hay datos)
        availability = 0.0 # Default
        if mean_mttr is not None and mean_mtbf is not None:
            if mean_mttr > 0 and mean_mtbf > 0:
                availability = (mean_mtbf / (mean_mtbf + mean_mttr)) * 100
            elif mean_mttr == 0 and mean_mtbf > 0: # Muchas horas entre fallas y no hay tiempo de reparación
                availability = 100.0
            elif mean_mttr > 0 and mean_mtbf == 0: # Siempre fallando y lleva tiempo reparar
                availability = 0.0
            else: # MTTR y MTBF son 0 (no hay fallas o no hay datos)
                availability = 100.0
        
        # Clasificar Rendimiento
        perf_class = 'Bajo' # Default
        if availability >= 90:
            perf_class = 'Alto'
        elif availability >= 75:
            perf_class = 'Medio'
        
        disp[service_type] = availability
        mttr[service_type] = mean_mttr
        mtbf[service_type] = mean_mtbf
        rend[service_type] = perf_class

    return disp, mttr, mtbf, rend

def show_evaluation_form_streamlit(df_data: pd.DataFrame, selected_provider: str = None, selected_service_type: str = None):
    """
    Muestra el formulario de evaluación en Streamlit.
    """
    st.markdown("---")
    st.subheader("Formulario de Evaluación de Proveedores")

    # Filtrar datos según las selecciones del usuario
    df_filtered = df_data.copy()
    if selected_provider and selected_provider != "Todos los Proveedores":
        df_filtered = df_filtered[df_filtered['denominacion_ejecutante'] == selected_provider]
    if selected_service_type and selected_service_type != "Todos los Servicios":
        df_filtered = df_filtered[df_filtered['tipo_de_servicio'] == selected_service_type]

    # Calcular métricas de desempeño técnico para los datos filtrados
    disp, mttr, mtbf, rend = calculate_technical_performance(df_filtered)

    # Inicializar el estado de la sesión para los resultados de la evaluación
    if 'evaluation_results' not in st.session_state:
        st.session_state.evaluation_results = {}

    st.markdown("---")
    st.subheader("Evaluación por Categoría y Pregunta")

    # Obtener tipos de servicio únicos para los datos filtrados (columnas de la tabla)
    service_types_on_page = sorted(df_filtered['tipo_de_servicio'].dropna().unique().tolist())
    
    if not service_types_on_page:
        st.warning("No hay datos o tipos de servicio disponibles para la selección actual. Por favor, sube un archivo o ajusta los filtros.")
        return

    # Mostrar mapeo de tipos de servicio si hay más de uno visible
    if len(service_types_on_page) > 1:
        st.info("Tipos de Servicio en esta tabla:")
        for i, st_label in enumerate(service_types_on_page):
            st.write(f"  **Servicio {i+1}:** {st_label}")
        st.markdown("---")

    # Crear encabezados de columna para las preguntas y los tipos de servicio
    cols = st.columns([0.4] + [0.15 for _ in service_types_on_page])
    cols[0].write("**Pregunta**")
    for i, st_label in enumerate(service_types_on_page):
        cols[i+1].write(f"**{st_label}**") # Muestra el nombre del servicio en el encabezado

    # Iterar sobre cada pregunta y crear los widgets de entrada
    for cat, texto, escala in preguntas:
        row_cols = st.columns([0.4] + [0.15 for _ in service_types_on_page])
        row_cols[0].write(f"**[{cat}]** {texto}")

        for i, st_original in enumerate(service_types_on_page):
            # Crear una clave única y segura para el widget de Streamlit
            # Reemplazar caracteres especiales y espacios
            unique_key = f"eval_{selected_provider}_{st_original}_{cat}_{texto}".replace(" ", "_").replace(".", "").replace("?", "").replace("(", "").replace(")", "").replace("%", "")

            if escala == "auto":
                # Lógica para calcular automáticamente el valor para Desempeño Técnico
                val = 0 # Valor por defecto
                display_val = "N/A (0)" # Por defecto para visualización

                if 'Disponibilidad' in texto and st_original in disp:
                    mean_disp = disp[st_original]
                    val = 2 if mean_disp >= 98 else (1 if mean_disp >= 75 else 0)
                    display_val = f"{mean_disp:.2f}% ({val})"
                elif 'MTTR' in texto and st_original in mttr:
                    mean_mttr = mttr[st_original]
                    val = 2 if mean_mttr <= 5 else (1 if mean_mttr <= 20 else 0)
                    display_val = f"{mean_mttr:.2f} hrs ({val})"
                elif 'MTBF' in texto and st_original in mtbf:
                    mean_mtbf = mtbf[st_original]
                    val = 2 if mean_mtbf > 1000 else (1 if mean_mtbf >= 100 else 0)
                    display_val = f"{mean_mtbf:.2f} hrs ({val})"
                elif 'Rendimiento' in texto and st_original in rend:
                    perf_class = rend[st_original]
                    if perf_class == 'Alto': val = 2
                    elif perf_class == 'Medio': val = 1
                    elif perf_class == 'Bajo': val = 0
                    display_val = f"{perf_class} ({val})"
                
                row_cols[i+1].markdown(f"**{display_val}**")
                st.session_state.evaluation_results[unique_key] = val

            else:
                # Opciones para la escala fija (manual)
                opts = [('Sobresaliente (2)', 2), ('Bueno (1)', 1), ('Indiferente (0)', 0), ('Malo (-1)', -1)]
                # Obtener el valor actual del estado de la sesión, o 0 si no existe
                current_value = st.session_state.evaluation_results.get(unique_key, 0)
                
                # Encontrar el índice de la opción que corresponde al valor actual
                try:
                    index_current_value = [opt[1] for opt in opts].index(current_value)
                except ValueError:
                    index_current_value = 2 # Default to 'Indiferente (0)' if current_value is not in options

                selected_value = row_cols[i+1].selectbox(
                    label="Selecciona",
                    options=opts,
                    index=index_current_value,
                    format_func=lambda x: x[0], # Mostrar solo el texto de la opción
                    key=unique_key,
                    label_visibility="collapsed" # Ocultar la etiqueta, ya está en el encabezado de la pregunta
                )
                st.session_state.evaluation_results[unique_key] = selected_value

    st.markdown("---")
    if st.button("Generar Resumen de Evaluación"):
        st.subheader("Resultados de la Evaluación (Resumen)")
        
        results_list = []
        for key, score in st.session_state.evaluation_results.items():
            # Intentar parsear la clave para extraer la información
            # Formato de clave: eval_ProveedorX_TipoDeServicioY_CategoriaZ_PreguntaA
            parts = key.replace("eval_", "").split('_')
            
            # Asumir que las primeras partes son proveedor y tipo de servicio
            # Esto puede ser complejo si los nombres contienen guiones bajos
            # Una forma más robusta sería pasar estos datos explícitamente a evaluation_results
            
            # Simple parsing:
            provider = "N/A"
            service_type = "N/A"
            category = "N/A"
            question = "N/A"

            # Intentar extraer proveedor y servicio si la clave lo permite
            if len(parts) >= 2:
                # El proveedor es la primera parte
                provider = parts[0]
                
                # Reconstruir el tipo de servicio y la categoría/pregunta
                # Buscamos la categoría primero, que divide el tipo de servicio de la pregunta
                temp_st_parts = []
                temp_q_parts = []
                found_category_index = -1

                for idx, part in enumerate(parts[1:]): # Empezamos desde la segunda parte (después del proveedor)
                    if part in rangos_detallados.keys():
                        category = part
                        found_category_index = idx + 1 # +1 porque estamos iterando sobre parts[1:]
                        break
                    temp_st_parts.append(part)

                service_type = "_".join(temp_st_parts)
                
                # Si se encontró la categoría, el resto son partes de la pregunta
                if found_category_index != -1:
                    temp_q_parts = parts[found_category_index + 1:]
                    question_reconstructed = " ".join(temp_q_parts).replace("_", " ") # Reemplazar guiones bajos por espacios
                    
                    # Intentar matchear la pregunta reconstruida con las preguntas originales
                    # para obtener la formulación exacta
                    for cat_orig, q_orig, _ in preguntas:
                        # Limpiamos ambas cadenas para una comparación más robusta
                        cleaned_q_orig = re.sub(r'[¿?().% ]', '', q_orig).lower()
                        cleaned_q_reconstructed = re.sub(r'[¿?().% ]', '', question_reconstructed).lower()
                        
                        if cleaned_q_orig == cleaned_q_reconstructed:
                            question = q_orig
                            break
                    if question == "N/A": # Si no se encontró un match perfecto
                        question = question_reconstructed # Usar la reconstruida tal cual

            results_list.append({
                'Proveedor': provider,
                'Tipo de Servicio': service_type.replace("De", "de").replace("Totreales", "tot.reales").replace("Posicion", "Posición"), # Limpieza básica
                'Categoría': category,
                'Pregunta': question,
                'Puntuación': score
            })

        results_df = pd.DataFrame(results_list)

        if not results_df.empty:
            st.dataframe(results_df)
            
            # Ejemplo: Promedio por Categoría
            avg_by_category = results_df.groupby('Categoría')['Puntuación'].mean().reset_index()
            st.subheader("Puntuación Promedio por Categoría")
            st.dataframe(avg_by_category.style.format({"Puntuación": "{:.2f}"}))

            # Ejemplo: Promedio General por Proveedor y Tipo de Servicio
            avg_by_prov_service = results_df.groupby(['Proveedor', 'Tipo de Servicio'])['Puntuación'].mean().reset_index()
            st.subheader("Puntuación Promedio por Proveedor y Tipo de Servicio")
            st.dataframe(avg_by_prov_service.style.format({"Puntuación": "{:.2f}"}))

            # Un cálculo más complejo para un resumen por proveedor
            st.subheader("Resumen Agregado por Proveedor")
            summary_prov = results_df.groupby('Proveedor').agg(
                Puntuacion_Promedio=('Puntuación', 'mean'),
                Numero_Evaluaciones=('Pregunta', 'count'),
                Max_Puntuacion=('Puntuación', 'max'),
                Min_Puntuacion=('Puntuación', 'min')
            ).reset_index()
            st.dataframe(summary_prov.style.format({
                "Puntuacion_Promedio": "{:.2f}",
                "Max_Puntuacion": "{:.0f}",
                "Min_Puntuacion": "{:.0f}"
            }))

        else:
            st.info("No hay resultados de evaluación para generar un resumen.")


# --- Aplicación Streamlit Principal ---
def main():
    st.title("¡Hola, usuario Sura! 👋")
    st.markdown("---")
    st.header("Proyecto de **Gerencia de Gestión Administrativa** en Ingeniería Clínica")
    st.markdown("""
        Aquí podrás **analizar y gestionar los datos de avisos** para optimizar los procesos
        y **evaluar a tus proveedores**.
        Por favor, **sube el archivo `DATA2.XLSX`** para comenzar.
    """)

    st.sidebar.header("Carga de Datos")
    uploaded_file = st.sidebar.file_uploader("Sube tu archivo 'DATA2.XLSX' aquí", type=["xlsx"])

    df_data = pd.DataFrame()
    if uploaded_file:
        file_buffer = io.BytesIO(uploaded_file.getvalue())
        with st.spinner('Cargando y procesando datos...'):
            try:
                df_loaded = load_and_merge_data(file_buffer)
                df_processed = process_data_after_load(df_loaded.copy()) # Pasa una copia para evitar SettingWithCopyWarning
                df_data = df_processed

                st.success("✅ Datos cargados y procesados exitosamente.")
                st.write(f"**Filas finales:** {len(df_data)} – **Columnas:** {len(df_data.columns)}")

                st.markdown("---")
                st.subheader("Vista previa de los datos procesados:")
                st.dataframe(df_data.head(10))

                st.markdown("---")
                st.subheader("Descarga de Datos Procesados")
                csv_output = df_data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar como CSV",
                    data=csv_output,
                    file_name="avisos_filtrados.csv",
                    mime="text/csv",
                    help="Descarga el archivo en formato CSV."
                )
                excel_buffer = io.BytesIO()
                df_data.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)
                st.download_button(
                    label="Descargar como Excel",
                    data=excel_buffer,
                    file_name="avisos_filtrados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Descarga el archivo en formato XLSX."
                )

                st.markdown("---")
                st.success("¡El procesamiento ha finalizado! Ahora puedes descargar tus datos o seguir explorando.")

            except Exception as e:
                st.error(f"❌ ¡Ups! Ocurrió un error al procesar el archivo: {e}")
                st.warning("Por favor, verifica que el archivo subido sea `DATA2.XLSX` y tenga el formato de hojas esperado.")
                st.exception(e) # Muestra el traceback completo para depuración
    else:
        st.info("⬆️ Sube tu archivo `DATA2.XLSX` para empezar con el análisis y la evaluación.")

    # --- Sección de Evaluación (visible solo si hay datos cargados) ---
    if not df_data.empty:
        st.sidebar.markdown("---")
        st.sidebar.header("Opciones de Evaluación")

        all_providers = sorted(df_data['denominacion_ejecutante'].dropna().unique().tolist())
        all_service_types = sorted(df_data['tipo_de_servicio'].dropna().unique().tolist())

        selected_provider = st.sidebar.selectbox(
            "Filtrar por proveedor para evaluar:",
            ["Todos los Proveedores"] + all_providers,
            key='provider_select'
        )
        # No se necesita modificar selected_provider si es "Todos los Proveedores" aquí,
        # la función show_evaluation_form_streamlit ya lo maneja

        selected_service_type = st.sidebar.selectbox(
            "Filtrar por tipo de servicio (opcional):",
            ["Todos los Servicios"] + all_service_types,
            key='service_type_select'
        )
        # No se necesita modificar selected_service_type si es "Todos los Servicios" aquí,
        # la función show_evaluation_form_streamlit ya lo maneja

        if st.sidebar.button("Mostrar Rangos de Evaluación"):
            st.markdown("---")
            st.subheader("Rangos de Respuesta Detallados para la Evaluación")
            st.markdown("**Escala General:**")
            st.write("2: Sobresaliente")
            st.write("1: Bueno")
            st.write("0: Indiferente")
            st.write("-1: Malo")
            st.markdown("--- Preguntas y sus rangos ---")

            for cat, texto, escala in preguntas:
                st.write(f"\n**[{cat}] {texto}:**")
                if cat in rangos_detallados and texto in rangos_detallados[cat]:
                    for val, desc in rangos_detallados[cat][texto].items():
                        st.write(f"   - {val}: {desc}")
                else:
                    st.write("   (Rangos definidos automáticamente por el sistema o no encontrados)")

            st.write("\nPara continuar con la evaluación, ajusta los filtros y usa el formulario de abajo.")
        
        # Mostrar el formulario de evaluación
        show_evaluation_form_streamlit(df_data, selected_provider, selected_service_type)

if __name__ == "__main__":
    main()
