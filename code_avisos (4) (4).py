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
            -1: "Por encima del mercado"
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
            -1: "Por encima del mercado"
        },
        "¿Los precios ofrecidos para insumos son competitivos respecto al mercado?": {
            2: "Muy por debajo del precio promedio de mercado",
            1: "Por debajo del promedio de mercado",
            0: "Igual al promedio de mercado",
            -1: "Por encima del mercado"
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
            "Avisos por ubicación técnica": ("ubicacion_tecnica", self.COL_AVISO_NORMALIZED, "avisos_count"),
            "Avisos por estado": ("status_del_sistema", self.COL_AVISO_NORMALIZED, "avisos_count"),
            "Avisos por tipo de servicio": ("tipo_de_servicio", self.COL_AVISO_NORMALIZED, "avisos_count"),
            "Costos por tipo de servicio": ("tipo_de_servicio", self.COL_COSTOS_NORMALIZED, "costos"),
            "Costos por año": ("año", self.COL_COSTOS_NORMALIZED, "costos"),
            "Costos por mes": ("mes", self.COL_COSTOS_NORMALIZED, "costos"),
            "Avisos por categoría de descripción": ("description_category", self.COL_AVISO_NORMALIZED, "avisos_count"),
        }

    def display_costos_avisos_dashboard(self):
        st.header("Análisis de Costos y Avisos")
        st.markdown("---")

        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            years = sorted(self.df['año'].dropna().unique().tolist())
            selected_year = st.selectbox("Selecciona Año", ["Todos"] + years)
        with col2:
            months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            selected_month = st.selectbox("Selecciona Mes", ["Todos"] + months)
        with col3:
            proveedores = sorted(self.df[self.EJECUTANTE_COL_NAME_NORMALIZED].dropna().unique().tolist())
            selected_proveedor = st.selectbox("Selecciona Proveedor", ["Todos"] + proveedores)

        df_filtered = self.df.copy()

        if selected_year != "Todos":
            df_filtered = df_filtered[df_filtered['año'] == selected_year]
        if selected_month != "Todos":
            df_filtered = df_filtered[df_filtered['mes'] == selected_month]
        if selected_proveedor != "Todos":
            df_filtered = df_filtered[df_filtered[self.EJECUTANTE_COL_NAME_NORMALIZED] == selected_proveedor]

        if df_filtered.empty:
            st.warning("No hay datos para los filtros seleccionados.")
            return

        # KPIs Generales
        total_avisos = df_filtered[self.COL_AVISO_NORMALIZED].nunique()
        total_costos = df_filtered[self.COL_COSTOS_NORMALIZED].sum()
        costo_promedio_aviso = total_costos / total_avisos if total_avisos > 0 else 0

        st.subheader("Indicadores Clave")
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("Total de Avisos", f"{total_avisos:,}")
        with kpi2:
            st.metric("Costo Total", f"${total_costos:,.2f}")
        with kpi3:
            st.metric("Costo Promedio por Aviso", f"${costo_promedio_aviso:,.2f}")

        st.markdown("---")

        # Gráficos y Tablas
        st.subheader("Análisis Detallado")
        opcion_analisis = st.selectbox(
            "Selecciona una opción de análisis:",
            list(self.opciones_menu.keys())
        )

        group_col, value_col, analysis_type = self.opciones_menu[opcion_analisis]

        if analysis_type == "costos":
            data_to_plot = df_filtered.groupby(group_col)[value_col].sum().sort_values(ascending=False)
            title = f"Costos por {opcion_analisis.split(' por ')[1].capitalize()}"
            ylabel = "Costo Total"
        elif analysis_type == "avisos_count":
            data_to_plot = df_filtered.groupby(group_col)[value_col].nunique().sort_values(ascending=False)
            title = f"Número de Avisos por {opcion_analisis.split(' por ')[1].capitalize()}"
            ylabel = "Número de Avisos"

        if not data_to_plot.empty:
            # Gráfico de barras
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x=data_to_plot.index, y=data_to_plot.values, ax=ax, palette="viridis")
            ax.set_title(title)
            ax.set_xlabel(group_col.replace('_', ' ').title())
            ax.set_ylabel(ylabel)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)

            # Tabla de datos
            st.write(f"Datos de {opcion_analisis}:")
            st.dataframe(data_to_plot)
        else:
            st.info(f"No hay datos para mostrar para '{opcion_analisis}' con los filtros actuales.")

# --- Clase EvaluacionProveedoresApp (anteriormente al final del archivo) ---
# Esta clase se define aquí para que pueda ser instanciada por la lógica principal
# después de cargar los datos.

class EvaluacionProveedoresApp:
    def __init__(self, df):
        self.df = df
        self.preguntas = preguntas # Usar las preguntas definidas globalmente
        self.rangos_detallados = rangos_detallados # Usar los rangos detallados definidos globalmente

    def display_evaluacion_dashboard(self):
        st.header("Evaluación de Proveedores")
        st.markdown("---")

        proveedores_disponibles = self.df['PROVEEDOR'].unique().tolist()
        if not proveedores_disponibles:
            st.warning("No hay proveedores disponibles en los datos cargados.")
            return

        selected_proveedor = st.selectbox("Selecciona un Proveedor para evaluar", ["Todos"] + sorted(proveedores_disponibles))

        filtered_df = self.df.copy()
        if selected_proveedor != "Todos":
            filtered_df = self.df[self.df['PROVEEDOR'] == selected_proveedor]

        if filtered_df.empty:
            st.warning(f"No hay datos para el proveedor seleccionado: {selected_proveedor}")
            return

        # Calcular indicadores de desempeño técnico solo si hay datos válidos
        try:
            cnt, cost, mttr, mtbf, disp, rend = calcular_indicadores(filtered_df, group_col='PROVEEDOR')
        except Exception as e:
            st.error(f"Error al calcular indicadores de desempeño técnico: {e}")
            cnt, cost, mttr, mtbf, disp, rend = (pd.Series(dtype=int), pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=object))


        # Sección de preguntas cualitativas
        st.subheader("Evaluación Cualitativa")
        st.markdown("Por favor, puntúa de 2 a -1 (2: Excelente, 1: Bueno, 0: Regular, -1: Deficiente) o 'auto' para métricas calculadas.")

        resultados_cualitativos = {}
        for categoria, pregunta_texto, _ in self.preguntas:
            if _ == "auto":
                continue # Skip auto-calculated metrics here

            st.markdown(f"**{categoria}:**")
            opciones_puntaje = {"2": "2 - Excelente", "1": "1 - Bueno", "0": "0 - Regular", "-1": "-1 - Deficiente"}
            default_value = list(opciones_puntaje.values())[2] # Default to 0
            if pregunta_texto in resultados_cualitativos:
                # If already answered, set default to previous answer
                for k, v in opciones_puntaje.items():
                    if k == str(resultados_cualitativos[pregunta_texto]):
                        default_value = v
                        break

            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(pregunta_texto)
                if categoria in self.rangos_detallados and pregunta_texto in self.rangos_detallados[categoria]:
                    with st.expander("Ver criterios de puntuación"):
                        for score, criterio in self.rangos_detallados[categoria][pregunta_texto].items():
                            st.write(f"**{score}:** {criterio}")

            with col2:
                respuesta = st.radio(
                    f"Puntuación para {pregunta_texto}",
                    options=list(opciones_puntaje.values()),
                    index=list(opciones_puntaje.values()).index(default_value),
                    key=f"pregunta_{categoria}_{pregunta_texto}"
                )
                resultados_cualitativos[pregunta_texto] = int(respuesta.split(" ")[0]) # Extract numeric score

        # Sección de indicadores de desempeño técnico
        st.subheader("Evaluación de Desempeño Técnico (Calculado)")

        df_indicadores = pd.DataFrame({
            "Métrica": ["Disponibilidad promedio (%)", "MTTR promedio (hrs)", "MTBF promedio (hrs)", "Rendimiento promedio equipos"],
            "Valor": [
                disp.get(selected_proveedor, 0) if selected_proveedor != "Todos" else disp.mean(),
                mttr.get(selected_proveedor, 0) if selected_proveedor != "Todos" else mttr.mean(),
                mtbf.get(selected_proveedor, 0) if selected_proveedor != "Todos" else mtbf.mean(),
                rend.get(selected_proveedor, 'No Aplica') if selected_proveedor != "Todos" else 'No Aplica' # Rendimiento is categorical
            ]
        })
        st.dataframe(df_indicadores)

        # Calculate final qualitative score
        total_preguntas_cualitativas = len([p for p in self.preguntas if p[2] != "auto"])
        if total_preguntas_cualitativas > 0:
            puntuacion_total_cualitativa = sum(resultados_cualitativos.values())
            porcentaje_cualitativo = (puntuacion_total_cualitativa / (total_preguntas_cualitativas * 2)) * 100 # Max score for each question is 2
            st.subheader("Resumen de Evaluación Cualitativa")
            st.info(f"Puntuación Cualitativa Total: {puntuacion_total_cualitativa} / {total_preguntas_cualitativas * 2}")
            st.metric("Porcentaje de Cumplimiento Cualitativo", f"{porcentaje_cualitativo:.2f}%")
        else:
            st.warning("No hay preguntas cualitativas definidas para calcular el porcentaje.")

# --- Initial page navigation setup ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'cargar_datos' # Default page

# --- Sidebar navigation ---
def navigate_to(page_name):
    st.session_state['page'] = page_name
    st.experimental_rerun()

with st.sidebar:
    st.image("https://github.com/NaidaLopez/imagen_aplicacion_gestion_avisos/blob/main/logo_sura.png?raw=true", width=200) # Logo de Sura
    st.title("Navegación")
    if st.button("Cargar Datos"):
        navigate_to('cargar_datos')
    if st.button("Costos y Avisos"):
        navigate_to('costos_avisos')
    if st.button("Evaluación de Proveedores"):
        navigate_to('evaluacion')
    st.markdown("---")
    st.write("Desarrollado por Naida López")

# --- Main app logic ---
if st.session_state['page'] == 'cargar_datos':
    st.header("Cargar Datos")
    st.write("Sube aquí tu archivo Excel ya listo para iniciar el análisis.")

    uploaded_file = st.file_uploader("Arrastra y suelta tu archivo Excel o haz click para buscar", type=["xlsx"])

    if uploaded_file:
        st.info("Archivo cargando y procesando. Esto puede tardar unos segundos...")
        try:
            # Directly read the Excel file, assuming it's already in the desired format
            df = pd.read_excel(uploaded_file)

            # Apply the necessary post-processing steps that were previously in load_and_merge_data
            # Normalize column names more robustly
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


            st.session_state['df'] = df
            st.success("¡Datos cargados y procesados exitosamente!")
            st.write("Vista previa de los datos:")
            st.dataframe(df.head())
            st.info("Ahora puedes navegar a las secciones de análisis y evaluación desde el menú lateral.")
            # Automatically navigate to Costos y Avisos for initial display
            navigate_to('costos_avisos')
        except Exception as e:
            st.error(f"Hubo un error al procesar el archivo: {e}")
            st.warning("Asegúrate de que el archivo Excel esté en un formato válido y contenga los datos esperados.")

elif st.session_state['page'] == 'costos_avisos':
    if 'df' in st.session_state and st.session_state['df'] is not None:
        costos_avisos_app = CostosAvisosApp(st.session_state['df'])
        costos_avisos_app.display_costos_avisos_dashboard()
    else:
        st.warning("Por favor, carga los datos primero desde la sección 'Cargar Datos'.")

elif st.session_state['page'] == 'evaluacion':
    if 'df' in st.session_state and st.session_state['df'] is not None:
        eval_app = EvaluacionProveedoresApp(st.session_state['df'])
        eval_app.display_evaluacion_dashboard()
    else:
        st.warning("Por favor, carga los datos primero desde la sección 'Cargar Datos'.")
