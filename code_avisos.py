import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import re
import numpy as np
import os
import matplotlib.ticker as mticker # Keep for custom formatter

# --- Configuración de la página de Streamlit ---
st.set_page_config(layout="wide", page_title="Análisis y Evaluación de Servicios")

# Set a nice style for plots
sns.set_style('whitegrid')

# --- Data Loading and Preprocessing ---
# En Streamlit, es buena práctica usar st.cache_data para que la carga y
# preprocesamiento de datos se realice una sola vez y se cachee.
file_path = "avisos_filtrados.xlsx" # Asume que el archivo está en la misma carpeta

@st.cache_data
def load_data(path):
    try:
        df = pd.read_excel(path)
        # Normalizar nombres de columnas
        ORIGINAL_EJECUTANTE_COL_NAME = "Denominación ejecutante"
        ORIGINAL_CP_COL_NAME = "Código postal"
        ORIGINAL_OBJETO_TECNICO_COL_NAME = "Denominación de objeto técnico"
        ORIGINAL_TEXTO_CODIGO_ACCION_COL_NAME = "Texto código acción"
        ORIGINAL_TEXTO_ACCION_COL_NAME = "Texto de acción"
        ORIGINAL_TIPO_SERVICIO_COL_NAME = "Tipo de servicio"
        ORIGINAL_COSTOS_COL_NAME = "Costes tot.reales"
        ORIGINAL_DESCRIPTION_COL_NAME = "Descripción"
        ORIGINAL_FECHA_AVISO_COL_NAME = "Fecha de aviso"
        ORIGINAL_TEXTO_POSICION_COL_NAME = "Texto de Posición"
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
            ORIGINAL_TEXTO_POSICION_COL_NAME: "texto_de_posicion",
            ORIGINAL_TEXTO_EQUIPO_COL_NAME: "texto_equipo",
            ORIGINAL_DURACION_PARADA_COL_NAME: "duracion_de_parada",
            ORIGINAL_EQUIPO_COL_NAME: "equipo",
            ORIGINAL_AVISO_COL_NAME: "aviso"
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

        df['PROVEEDOR'] = df['denominacion_ejecutante']
        df['COSTO'] = df['costes_totreales']
        df['TIEMPO PARADA'] = pd.to_numeric(df['duracion_de_parada'], errors='coerce')
        df['EQUIPO'] = pd.to_numeric(df['equipo'], errors='coerce')
        df['AVISO'] = pd.to_numeric(df['aviso'], errors='coerce')
        df['TIPO DE SERVICIO'] = df['tipo_de_servicio']
        df['costes_totreales'] = pd.to_numeric(df['costes_totreales'], errors='coerce')

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
        df['HORARIO'] = df['texto_equipo'].str.strip().str.upper()
        df['HORA/ DIA'] = df['HORARIO'].map(lambda x: horarios_dict.get(x, (None, None))[0])
        df['DIAS/ AÑO'] = df['HORARIO'].map(lambda x: horarios_dict.get(x, (None, None))[1])
        df['DIAS/ AÑO'] = pd.to_numeric(df['DIAS/ AÑO'], errors='coerce')
        df['HORA/ DIA'] = pd.to_numeric(df['HORA/ DIA'], errors='coerce')

        # --- Initial Filtering ---
        df = df.dropna(subset=['EQUIPO'])

        # --- Additional Preprocessing ---
        df["fecha_de_aviso"] = pd.to_datetime(df["fecha_de_aviso"], errors="coerce")
        df["año"] = df["fecha_de_aviso"].dt.year
        df["mes"] = df["fecha_de_aviso"].dt.strftime("%B")

        def extract_description_category(description):
            if pd.isna(description):
                return "Otros"
            match = re.match(r'^([A-Z]{2})/', str(description).strip())
            if match:
                return match.group(1)
            return "Otros"

        df["description_category"] = df['descripcion'].apply(extract_description_category)
        return df

    except FileNotFoundError:
        st.error(f"Error: El archivo '{path}' no fue encontrado. Por favor, asegúrate de que esté en la misma carpeta que la aplicación Streamlit.")
        st.stop() # Detiene la ejecución si el archivo no se encuentra
    except Exception as e:
        st.error(f"Ocurrió un error al cargar o preprocesar los datos: {e}")
        st.stop()

df = load_data(file_path)

# --- FUNCIONES DE CÁLCULO DE INDICADORES (Se mantienen igual) ---
def calcular_indicadores_servicio(df_sub):
    if df_sub.empty:
        return pd.Series(dtype=object), pd.Series(dtype=object), pd.Series(dtype=object), pd.Series(dtype=object), pd.Series(dtype=object), pd.Series(dtype=object)

    cnt = df_sub['TIPO DE SERVICIO'].value_counts()
    cost = df_sub.groupby('TIPO DE SERVICIO')['COSTO'].sum()
    mttr = df_sub.groupby('TIPO DE SERVICIO')['TIEMPO PARADA'].mean()

    ttot = df_sub.groupby('TIPO DE SERVICIO').apply(
        lambda g: (g['DIAS/ AÑO'].mean() * g['HORA/ DIA'].mean()) if not g['DIAS/ AÑO'].isnull().all() and not g['HORA/ DIA'].isnull().all() else np.nan
    )

    down = df_sub.groupby('TIPO DE SERVICIO')['TIEMPO PARADA'].sum()
    fails = df_sub.groupby('TIPO DE SERVICIO')['AVISO'].count()
    mtbf = (ttot - down) / fails.replace(0, np.nan)

    disp = (mtbf / (mtbf + mttr)).replace([np.inf, -np.inf], np.nan) * 100
    rend = disp.apply(lambda v: 'Alto' if v >= 90 else ('Medio' if v >= 75 else 'Bajo') if not pd.isna(v) else np.nan)
    return cnt, cost, mttr, mtbf, disp, rend

def calcular_indicadores_equipo(df_sub):
    if df_sub.empty:
        return pd.Series(dtype=object), pd.Series(dtype=object), pd.Series(dtype=object), pd.Series(dtype=object), pd.Series(dtype=object), pd.Series(dtype=object), pd.Series(dtype=object)

    cnt_equipo = df_sub['EQUIPO'].value_counts()
    cost_equipo = df_sub.groupby('EQUIPO')['COSTO'].sum()
    mttr_equipo = df_sub.groupby('EQUIPO')['TIEMPO PARADA'].mean()

    desc_category_equipo = df_sub.groupby('EQUIPO')['description_category'].first().fillna('Desconocido')

    ttot_equipo = df_sub.groupby('EQUIPO').apply(
        lambda g: (g['DIAS/ AÑO'].mean() * g['HORA/ DIA'].mean()) if not g['DIAS/ AÑO'].isnull().all() and not g['HORA/ DIA'].isnull().all() else np.nan
    )

    down_equipo = df_sub.groupby('EQUIPO')['TIEMPO PARADA'].sum()
    fails_equipo = df_sub.groupby('EQUIPO')['AVISO'].count()
    mtbf_equipo = (ttot_equipo - down_equipo) / fails_equipo.replace(0, np.nan)

    disp_equipo = (mtbf_equipo / (mtbf_equipo + mttr_equipo)).replace([np.inf, -np.inf], np.nan) * 100
    rend_equipo = disp_equipo.apply(lambda v: 'Alto' if v >= 90 else ('Medio' if v >= 75 else 'Bajo') if not pd.isna(v) else np.nan)
    return cnt_equipo, cost_equipo, mttr_equipo, mtbf_equipo, disp_equipo, rend_equipo, desc_category_equipo

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

# --- Funciones Auxiliares para CostosAvisosApp (Streamlit) ---
def formato_coste_display(valor):
    if pd.isna(valor):
        return "N/A"
    return f"$ {valor:,.0f}COP".replace(",", ".")

def custom_cost_formatter_plot(x, pos):
    if x >= 1e9:
        return f"${x*1e-9:.0f}B"
    elif x >= 1e6:
        return f"${x*1e-6:.0f}M"
    elif x >= 1e3:
        return f"${x*1e-3:.0f}K"
    else:
        return f"${x:.0f}"

def plot_points_with_labels(data, title, xlabel="", ylabel="", color="skyblue"):
    if data.empty:
        st.info(f"No hay datos para graficar: {title}")
        return

    fig, ax = plt.subplots(figsize=(15, 7))
    x_labels = data.index.astype(str)
    x_positions = np.arange(len(data))

    ax.scatter(x_positions, data.values, color=color, zorder=2)

    for i, txt in enumerate(data.values):
        if "avisos" in title.lower():
            label_text = f"{int(txt):,}".replace(",", ".")
        else: # For costs
            label_text = custom_cost_formatter_plot(txt, None)
        ax.text(x_positions[i], txt, label_text, ha='center', va='bottom', fontsize=9, color='black')

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    # Mejorar el espaciado y rotación del eje x
    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, rotation=90, ha="right", fontsize=10) # Rotación de 90 grados

    if "costos" in title.lower():
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(custom_cost_formatter_plot))

    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

# --- Análisis de Costos y Avisos (Streamlit) ---
def run_costos_avisos_app(df):
    st.title("📊 Análisis de Costos y Avisos")

    # Inicializar estado de sesión para paginación y filtros
    if 'costos_page' not in st.session_state:
        st.session_state.costos_page = 0
    if 'costos_grouped_data' not in st.session_state:
        st.session_state.costos_grouped_data = pd.Series()
    if 'costos_current_option' not in st.session_state:
        st.session_state.costos_current_option = "Costos por ejecutante" # Opción por defecto

    EJECUTANTE_COL_NAME_NORMALIZED = "denominacion_ejecutante"
    COL_COSTOS_NORMALIZED = "costes_totreales"
    CP_COL_NAME_NORMALIZED = "codigo_postal"

    # Filtros en la barra lateral
    with st.sidebar:
        st.subheader("Filtros de Análisis")
        ejecutantes = sorted(df[EJECUTANTE_COL_NAME_NORMALIZED].dropna().unique().tolist())
        selected_ejecutantes = st.multiselect("Ejecutante", ejecutantes, default=ejecutantes)

        cps = sorted(df[CP_COL_NAME_NORMALIZED].dropna().unique().tolist())
        selected_cps = st.multiselect("Código postal", cps, default=cps)

        años = sorted(df["año"].dropna().unique().astype(int).tolist())
        selected_año = st.selectbox("Año", ["Todos"] + años)

        meses = sorted(df["mes"].dropna().unique().tolist(), key=lambda x: pd.to_datetime(x, format="%B", errors='coerce').month if pd.notna(x) else 0)
        selected_mes = st.selectbox("Mes", ["Todos"] + meses)

    opciones_menu_costos = {
        "Costos por ejecutante": (EJECUTANTE_COL_NAME_NORMALIZED, COL_COSTOS_NORMALIZED, "costos"),
        "Avisos por ejecutante": (EJECUTANTE_COL_NAME_NORMALIZED, None, "avisos"),
        "Costos por objeto técnico": ("denominacion_de_objeto_tecnico", COL_COSTOS_NORMALIZED, "costos"),
        "Avisos por objeto técnico": ("denominacion_de_objeto_tecnico", None, "avisos"),
        "Costos por texto código acción": ("texto_codigo_accion", COL_COSTOS_NORMALIZED, "costos"),
        "Avisos por texto código acción": ("texto_codigo_accion", None, "avisos"),
        "Costos por texto de acción": ("texto_de_accion", COL_COSTOS_NORMALIZED, "costos"),
        "Avisos por texto de acción": ("texto_de_accion", None, "avisos"),
        "Costos por tipo de servicio": ("tipo_de_servicio", COL_COSTOS_NORMALIZED, "costos"),
        "Avisos por tipo de servicio": ("tipo_de_servicio", None, "avisos"),
        "Costos por categoría de descripción": ("description_category", COL_COSTOS_NORMALIZED, "costos"),
        "Avisos por categoría de descripción": ("description_category", None, "avisos"),
    }

    selected_option = st.selectbox(
        "Selecciona el tipo de análisis:",
        list(opciones_menu_costos.keys()),
        key="costos_menu_dropdown" # Clave única para el widget
    )

    # Si la opción de análisis cambia, resetear la página a 0
    if st.session_state.costos_current_option != selected_option:
        st.session_state.costos_page = 0
        st.session_state.costos_current_option = selected_option


    # --- Lógica de Filtrado ---
    filtered_df = df.copy()
    if selected_ejecutantes:
        filtered_df = filtered_df[filtered_df[EJECUTANTE_COL_NAME_NORMALIZED].isin(selected_ejecutantes)]
    if selected_cps:
        filtered_df = filtered_df[filtered_df[CP_COL_NAME_NORMALIZED].isin(selected_cps)]
    if selected_año != "Todos":
        filtered_df = filtered_df[filtered_df["año"] == selected_año]
    if selected_mes != "Todos":
        filtered_df = filtered_df[filtered_df["mes"] == selected_mes]

    # --- Lógica de Agrupación ---
    col, col_cost, tipo = opciones_menu_costos[selected_option]

    if filtered_df.empty:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")
        st.session_state.costos_grouped_data = pd.Series()
        return

    if col not in filtered_df.columns:
        st.error(f"Error: La columna '{col}' no se encontró en los datos filtrados.")
        st.session_state.costos_grouped_data = pd.Series()
        return

    if tipo == "costos":
        if col_cost not in filtered_df.columns:
            st.error(f"Error: La columna de costos '{col_cost}' no se encontró en los datos filtrados.")
            st.session_state.costos_grouped_data = pd.Series()
            return
        grouped_data = filtered_df.groupby(col)[col_cost].sum().sort_values(ascending=False)
    else:
        grouped_data = filtered_df[col].value_counts().sort_values(ascending=False)

    if grouped_data.empty:
        st.warning(f"No hay datos para mostrar para la opción '{selected_option}' con los filtros actuales.")
        st.session_state.costos_grouped_data = pd.Series()
        return

    st.session_state.costos_grouped_data = grouped_data

    # --- Lógica de Paginación ---
    items_per_page = 20
    total_items = len(st.session_state.costos_grouped_data)
    max_page = max(0, (total_items - 1) // items_per_page)

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("← Página anterior", key="prev_costos_btn", disabled=(st.session_state.costos_page == 0)):
            st.session_state.costos_page -= 1
            st.rerun()
    with col3:
        if st.button("Página siguiente →", key="next_costos_btn", disabled=(st.session_state.costos_page >= max_page)):
            st.session_state.costos_page += 1
            st.rerun()

    with col2:
        st.write(f"Página {st.session_state.costos_page + 1} de {max_page + 1}")

    start_index = st.session_state.costos_page * items_per_page
    end_index = start_index + items_per_page
    data_to_display = st.session_state.costos_grouped_data.iloc[start_index:end_index]

    if data_to_display.empty:
        st.info("No hay datos para mostrar en esta página.")
        return

    # --- Mostrar Tabla ---
    st.subheader(f"Tabla de {selected_option}")
    if tipo == "costos":
        # Formatear para la visualización en st.dataframe
        formatted_df_display = data_to_display.apply(formato_coste_display).to_frame(name=col_cost)
        st.dataframe(formatted_df_display, use_container_width=True)
    else:
        st.dataframe(data_to_display.to_frame(name="Cantidad"), use_container_width=True)

    # --- Mostrar Gráfico ---
    st.subheader(f"Gráfico de {selected_option}")
    plot_points_with_labels(data_to_display, f"Distribución de {selected_option}",
                            xlabel=col, ylabel="Costo Total (COP)" if tipo == "costos" else "Número de Avisos")

# --- Evaluación de Proveedores (Streamlit) ---
def run_evaluacion_proveedores_app(df):
    st.title("⭐ Evaluación de Proveedores")

    # Inicializar variables de estado de sesión para la evaluación
    if 'current_provider_metrics' not in st.session_state:
        st.session_state.current_provider_metrics = {}
    if 'all_provider_service_types' not in st.session_state:
        st.session_state.all_provider_service_types = []
    if 'evaluation_scores' not in st.session_state:
        st.session_state.evaluation_scores = {} # {(category, question_text, service_type): score_value}
    if 'eval_page' not in st.session_state:
        st.session_state.eval_page = 0
    if 'summary_servicio_export' not in st.session_state:
        st.session_state.summary_servicio_export = None
    if 'resumen_equipo_export' not in st.session_state:
        st.session_state.resumen_equipo_export = None
    if 'last_selected_prov_eval' not in st.session_state:
        st.session_state.last_selected_prov_eval = "Todos"


    proveedores = ["Todos"] + sorted(df['PROVEEDOR'].dropna().unique().tolist())
    selected_prov = st.selectbox("Selecciona un Proveedor:", proveedores, key="eval_prov_select")

    # Si el proveedor cambia, recalcular métricas y resetear puntuaciones de evaluación
    if st.session_state.last_selected_prov_eval != selected_prov:
        st.session_state.eval_page = 0 # Resetear página
        st.session_state.evaluation_scores = {} # Resetear puntuaciones
        st.session_state.last_selected_prov_eval = selected_prov # Actualizar último proveedor seleccionado

        sub_df = df.copy()
        if selected_prov != "Todos":
            sub_df = df[df['PROVEEDOR'] == selected_prov].copy()

        if sub_df.empty:
            st.warning(f"No hay datos disponibles para el proveedor '{selected_prov}'.")
            st.session_state.current_provider_metrics = {}
            st.session_state.all_provider_service_types = []
            st.session_state.summary_servicio_export = None
            st.session_state.resumen_equipo_export = None
        else:
            cnt_s, cost_s, mttr_s, mtbf_s, disp_s, rend_s = calcular_indicadores_servicio(sub_df)
            st.session_state.current_provider_metrics = {
                'cnt': cnt_s, 'cost': cost_s, 'mttr': mttr_s, 'mtbf': mtbf_s, 'disp': disp_s, 'rend': rend_s
            }
            st.session_state.all_provider_service_types = sorted(sub_df['TIPO DE SERVICIO'].dropna().unique().tolist())

            # Preparar datos para exportación
            st.session_state.summary_servicio_export = pd.DataFrame({
                'Cantidad de Avisos': cnt_s,
                'Costo Total': cost_s,
                'Disponibilidad (%)': disp_s.round(2) if not disp_s.empty else np.nan,
                'MTTR (hrs)': mttr_s.round(2) if not mttr_s.empty else np.nan,
                'MTBF (hrs)': mtbf_s.round(2) if not mtbf_s.empty else np.nan,
                'Rendimiento': rend_s
            }).reset_index().rename(columns={'index': 'TIPO DE SERVICIO'}).sort_values('Disponibilidad (%)', ascending=False)
            for col_name in ['Disponibilidad (%)', 'MTTR (hrs)', 'MTBF (hrs)']:
                if col_name in st.session_state.summary_servicio_export.columns:
                    st.session_state.summary_servicio_export[col_name] = st.session_state.summary_servicio_export[col_name].fillna(0)

            cnt_e, cost_e, mttr_e, mtbf_e, disp_e, rend_e, desc_category_e = calcular_indicadores_equipo(sub_df)
            st.session_state.resumen_equipo_export = pd.DataFrame({
                'Avisos': cnt_e,
                'Costo total': cost_e,
                'MTTR': mttr_e.round(2) if not mttr_e.empty else np.nan,
                'MTBF': mtbf_e.round(2) if not mtbf_e.empty else np.nan,
                'Disponibilidad (%)': disp_e.round(2) if not disp_e.empty else np.nan,
                'Rendimiento': rend_e,
                'Categoría de Descripción': desc_category_e
            }).reset_index().rename(columns={'index': 'Denominacion'})
            for col_name in ['Disponibilidad (%)', 'MTTR', 'MTBF']:
                if col_name in st.session_state.resumen_equipo_export.columns:
                    st.session_state.resumen_equipo_export[col_name] = st.session_state.resumen_equipo_export[col_name].fillna(0)
        # For evaluation form, ensure scores are initialized to 0 for new provider/reset
        for cat, texto, escala in preguntas:
            for st_original in st.session_state.all_provider_service_types:
                score_key = (cat, texto, st_original)
                if escala != "auto": # Only for manually evaluated questions
                    st.session_state.evaluation_scores[score_key] = st.session_state.evaluation_scores.get(score_key, 0) # Initialize if not present

        st.rerun() # Rerun to apply new metrics and form state

    # Mostrar formulario de evaluación y métricas
    display_evaluation_form_and_metrics(
        st.session_state.current_provider_metrics.get('mttr', pd.Series()),
        st.session_state.current_provider_metrics.get('mtbf', pd.Series()),
        st.session_state.current_provider_metrics.get('disp', pd.Series()),
        st.session_state.current_provider_metrics.get('rend', pd.Series()),
        st.session_state.all_provider_service_types
    )

    # Botón para generar resumen y exportar
    if st.button("Generar Resumen de Evaluación y Exportar a Excel", key="generar_resumen_btn_eval"):
        generate_evaluation_summary_and_export(selected_prov)

def display_evaluation_form_and_metrics(mttr, mtbf, disp, rend, all_provider_service_types):
    if not all_provider_service_types:
        st.info("Por favor, selecciona un proveedor para ver la evaluación.")
        return

    items_per_page = 5
    total_service_types = len(all_provider_service_types)
    max_eval_page = max(0, (total_service_types - 1) // items_per_page)

    start_index = st.session_state.eval_page * items_per_page
    end_index = min(start_index + items_per_page, total_service_types)
    service_types_on_page = all_provider_service_types[start_index:end_index]

    if not service_types_on_page:
        st.info("No hay tipos de servicio para mostrar en esta página.")
        return

    st.subheader("Formulario de Evaluación")

    # Controles de paginación
    col_prev, col_page_info, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("← Anterior", key="eval_prev_btn", disabled=(st.session_state.eval_page == 0)):
            st.session_state.eval_page -= 1
            st.rerun() # Rerun para actualizar la página
    with col_page_info:
        st.write(f"Página {st.session_state.eval_page + 1} de {max_eval_page + 1}")
    with col_next:
        if st.button("Siguiente →", key="eval_next_btn", disabled=(st.session_state.eval_page >= max_eval_page)):
            st.session_state.eval_page += 1
            st.rerun() # Rerun para actualizar la página


    st.markdown("---")
    # Mostrar el mapeo de tipos de servicio para la página actual
    st.write("### Mapeo de Tipos de Servicio en esta página:")
    for i, st_name in enumerate(service_types_on_page):
        global_idx = all_provider_service_types.index(st_name) + 1
        st.write(f"**Servicio {global_idx}:** {st_name}")
    st.markdown("---")

    # Encabezado de la tabla de evaluación
    num_service_cols = len(service_types_on_page)
    # Ajustar anchos de columna: una para la pregunta, el resto para los servicios
    # La pregunta toma el 30%, el resto se divide entre los servicios
    col_widths = [0.4] + [0.6 / num_service_cols] * num_service_cols if num_service_cols > 0 else [1.0]

    header_cols = st.columns(col_widths)
    with header_cols[0]:
        st.markdown("**Pregunta**")
    for i, st_name in enumerate(service_types_on_page):
        global_idx = all_provider_service_types.index(st_name) + 1
        with header_cols[i + 1]:
            st.markdown(f"**Servicio {global_idx}**")

    # Filas de preguntas de evaluación
    for cat, texto, escala in preguntas:
        # Crea una nueva fila de columnas para cada pregunta
        row_cols = st.columns(col_widths)
        with row_cols[0]:
            st.write(f"**[{cat}]** {texto}")

        for i, st_original in enumerate(service_types_on_page):
            with row_cols[i + 1]:
                score_key = (cat, texto, st_original) # Clave para almacenar la puntuación

                if escala == "auto":
                    val = 0
                    if 'Disponibilidad' in texto and st_original in disp and not pd.isna(disp[st_original]):
                        mean_disp = disp[st_original]
                        val = 2 if mean_disp >= 98 else (1 if mean_disp >= 75 else 0)
                    elif 'MTTR' in texto and st_original in mttr and not pd.isna(mttr[st_original]):
                        mean_mttr = mttr[st_original]
                        val = 2 if mean_mttr <= 5 else (1 if mean_mttr <= 20 else 0)
                    elif 'MTBF' in texto and st_original in mtbf and not pd.isna(mtbf[st_original]):
                        mean_mtbf = mtbf[st_original]
                        val = 2 if mean_mtbf > 1000 else (1 if mean_mtbf >= 100 else 0)
                    elif 'Rendimiento' in texto and st_original in rend and not pd.isna(rend[st_original]):
                        perf_class = rend[st_original]
                        if perf_class == 'Alto':
                            val = 2
                        elif perf_class == 'Medio':
                            val = 1
                        elif perf_class == 'Bajo':
                            val = 0
                    st.session_state.evaluation_scores[score_key] = val # Almacena puntuación auto-calculada
                    st.write(str(val)) # Muestra puntuación auto-calculada
                else:
                    opts = [('Sobresaliente (2)', 2), ('Bueno (1)', 1), ('Indiferente (0)', 0), ('Malo (-1)', -1)]
                    # Recupera el valor actual de session_state o usa el por defecto (0)
                    current_value = st.session_state.evaluation_scores.get(score_key, 0)
                    selected_score = st.selectbox(
                        "Selecciona puntuación:",
                        options=opts,
                        index=[v[1] for v in opts].index(current_value), # Asegura que el valor inicial sea correcto
                        key=f"{cat}_{texto.replace(' ', '_')}_{st_original}_score", # Clave única para cada selectbox
                        label_visibility="collapsed" # Oculta la etiqueta predeterminada para una mejor alineación
                    )
                    st.session_state.evaluation_scores[score_key] = selected_score # Actualiza la puntuación en session state

    st.markdown("---") # Separador visual

    # --- Gráficos de Métricas de Rendimiento ---
    st.subheader("Gráficos de Rendimiento")

    # Gráfico de Rendimiento (Pastel)
    if not rend.empty:
        rend_filtered = rend.dropna()
        if not rend_filtered.empty:
            rend_counts = rend_filtered.value_counts().reindex(['Alto', 'Medio', 'Bajo'], fill_value=0)
            if rend_counts.sum() > 0:
                fig_rend, ax_rend = plt.subplots(figsize=(8, 8))
                colores = ['#66bb6a', '#ffee58', '#ef5350']
                active_colors = [color for i, color in enumerate(colores) if rend_counts.iloc[i] > 0]
                labels = [f'{idx} ({val}%)' for idx, val in rend_counts.items() if val > 0]
                sizes = [val for val in rend_counts.values if val > 0]

                if sizes:
                    ax_rend.pie(sizes, autopct='%1.1f%%', colors=active_colors, startangle=90, counterclock=False, pctdistance=0.85)
                    ax_rend.set_title('Distribución Rendimiento por Tipo de Servicio')
                    ax_rend.set_ylabel('')
                    ax_rend.axis('equal')
                    st.pyplot(fig_rend)
                else:
                    st.info("No hay datos de rendimiento para mostrar en el gráfico de pastel.")
            else:
                st.info("No hay datos de rendimiento válidos para graficar después de eliminar NaNs.")
        else:
            st.info("No hay datos de rendimiento válidos para graficar después de eliminar NaNs.")
    else:
        st.info("No hay datos de rendimiento para graficar.")

    # Gráficos de MTTR, MTBF, Disponibilidad (Histogramas)
    plots_to_make = 0
    if not mttr.dropna().empty: plots_to_make += 1
    if not mtbf.dropna().empty: plots_to_make += 1
    if not disp.dropna().empty: plots_to_make += 1

    if plots_to_make > 0:
        fig_metrics, axs_metrics = plt.subplots(plots_to_make, 1, figsize=(15, 5 * plots_to_make))
        if plots_to_make == 1:
            axs_metrics = [axs_metrics] # Asegura que axs_metrics sea siempre una lista para iterar

        plot_idx = 0
        if not mttr.dropna().empty:
            sns.histplot(mttr.dropna(), bins=10, kde=True, ax=axs_metrics[plot_idx], color='skyblue')
            axs_metrics[plot_idx].set_title('MTTR Promedio por Servicio (hrs)')
            axs_metrics[plot_idx].tick_params(axis='x', rotation=45, ha='right')
            plot_idx += 1
        if not mtbf.dropna().empty:
            sns.histplot(mtbf.dropna(), bins=10, kde=True, ax=axs_metrics[plot_idx], color='lightgreen')
            axs_metrics[plot_idx].set_title('MTBF Promedio por Servicio (hrs)')
            axs_metrics[plot_idx].tick_params(axis='x', rotation=45, ha='right')
            plot_idx += 1
        if not disp.dropna().empty:
            sns.histplot(disp.dropna(), bins=10, kde=True, ax=axs_metrics[plot_idx], color='salmon')
            axs_metrics[plot_idx].set_title('Disponibilidad Promedio por Servicio (%)')
            axs_metrics[plot_idx].tick_params(axis='x', rotation=45, ha='right')
            plot_idx += 1

        plt.tight_layout()
        st.pyplot(fig_metrics)
    else:
        st.info("No hay datos de MTTR, MTBF o Disponibilidad para graficar.")

def generate_evaluation_summary_and_export(selected_prov):
    if not st.session_state.evaluation_scores:
        st.warning("No hay evaluaciones para resumir. Por favor, completa la evaluación primero.")
        return

    st.info("Generando resumen de evaluación...")

    # Obtener tipos de servicio únicos que han sido evaluados
    unique_service_types = sorted(list(set([key[2] for key in st.session_state.evaluation_scores.keys()])))

    all_categories = sorted(list(set([p[0] for p in preguntas])))
    category_service_scores = {cat: {st: 0 for st in unique_service_types} for cat in all_categories}

    service_type_totals = {st: 0 for st in unique_service_types}

    for (cat, q_text, st_original), score in st.session_state.evaluation_scores.items():
        if cat in category_service_scores and st_original in category_service_scores[cat]:
            category_service_scores[cat][st_original] += score
            service_type_totals[st_original] += score
        else:
            st.warning(f"Advertencia: Puntuación para '{q_text}' de servicio '{st_original}' con categoría '{cat}' no procesada debido a inconsistencia en la estructura.")

    summary_df_calificacion = pd.DataFrame.from_dict(category_service_scores, orient='index')
    summary_df_calificacion.index.name = 'Categoría'
    summary_df_calificacion.loc['Total por Calificación de Servicio'] = pd.Series(service_type_totals)

    # Asegurarse de que all_provider_service_types esté poblado
    if not st.session_state.all_provider_service_types:
        st.session_state.all_provider_service_types = sorted(df['TIPO DE SERVICIO'].dropna().unique().tolist())

    service_type_display_names_cal = {st: f"Servicio {st.session_state.all_provider_service_types.index(st) + 1} ({st})"
                                      for st in unique_service_types if st in st.session_state.all_provider_service_types}
    for st in unique_service_types:
        if st not in st.session_state.all_provider_service_types:
             service_type_display_names_cal[st] = f"Servicio Nuevo ({st})"

    summary_df_calificacion = summary_df_calificacion.rename(columns=service_type_display_names_cal)
    summary_df_calificacion.columns.name = 'Tipo de Servicio'

    # Exportar a Excel
    prov_name_for_file = selected_prov.replace(" ", "_").replace("/", "-")
    output_filename = f"resumen_evaluacion_{prov_name_for_file}.xlsx"

    # Usar BytesIO para crear el archivo en memoria y luego ofrecerlo para descarga
    import io
    output_buffer = io.BytesIO()
    with pd.ExcelWriter(output_buffer, engine='xlsxwriter') as writer:
        if st.session_state.summary_servicio_export is not None and not st.session_state.summary_servicio_export.empty:
            st.session_state.summary_servicio_export.to_excel(writer, sheet_name='Resumen_Servicio', index=False)
        else:
            st.warning("Advertencia: No se encontró la tabla de resumen por Tipo de Servicio para exportar o está vacía.")

        if st.session_state.resumen_equipo_export is not None and not st.session_state.resumen_equipo_export.empty:
            st.session_state.resumen_equipo_export.to_excel(writer, sheet_name='Resumen_Equipo', index=False)
        else:
            st.warning("Advertencia: No se encontró la tabla de resumen por Equipo para exportar o está vacía.")

        if not summary_df_calificacion.empty:
            summary_df_calificacion.to_excel(writer, sheet_name='Resumen_Calificacion')
        else:
             st.warning("Advertencia: No se encontró la tabla de resumen de Calificación para exportar o está vacía.")

    output_buffer.seek(0) # Regresa al inicio del buffer

    # Proporcionar un botón de descarga para el archivo Excel generado
    st.download_button(
        label="Descargar Resumen de Evaluación (Excel)",
        data=output_buffer,
        file_name=output_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_excel_button"
    )
    st.success(f"Resúmenes generados y listos para descargar como '{output_filename}'.")


# --- Lógica principal de la Aplicación (Punto de entrada de Streamlit) ---
st.sidebar.title("Menú Principal")
app_options = {
    "Evaluación de Proveedores": "evaluacion",
    "Análisis de Costos y Avisos": "costos_avisos"
}
selected_app = st.sidebar.radio("Selecciona una opción:", list(app_options.keys()), key="main_app_selector")

if app_options[selected_app] == "evaluacion":
    run_evaluacion_proveedores_app(df)
elif app_options[selected_app] == "costos_avisos":
    run_costos_avisos_app(df)
