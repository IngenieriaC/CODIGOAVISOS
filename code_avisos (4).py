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
        background-color: #FFD700; /* Amarillo dorado para los botones */
        color: white; /* Texto blanco en botones */
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #FFA500; /* Amarillo naranja al pasar el ratón */
    }
    /* Contenedores de markdown */
    .stMarkdown {
        color: #333333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Funciones de procesamiento de datos ---
def clean_column_names(df):
    """Limpia y estandariza los nombres de las columnas de un DataFrame."""
    cols = df.columns
    new_cols = []
    for col in cols:
        new_col = re.sub(r'[^a-zA-Z0-9_]', '', col) # Elimina caracteres especiales
        new_col = new_col.lower() # Convierte a minúsculas
        new_col = new_col.replace(' ', '_') # Reemplaza espacios con guiones bajos
        new_cols.append(new_col)
    df.columns = new_cols
    return df

def clean_excel_data(df):
    """
    Limpia un DataFrame cargado desde Excel, manejando combinaciones de celdas
    y filas de cabecera duplicadas.
    """
    # Eliminar filas donde todas las celdas sean NaN
    df.dropna(how='all', inplace=True)

    # Convertir todas las columnas a string para la búsqueda
    df_str = df.astype(str)

    # Buscar la fila que contiene 'Aviso' y 'Texto'
    header_row_index = -1
    for index, row in df_str.iterrows():
        # Ajusta las condiciones de búsqueda según los nombres reales de tus columnas
        # Asegúrate de que estos nombres son exactamente como aparecen en tu Excel
        if 'Aviso' in row.values and ('Texto' in row.values or 'Texto breve' in row.values):
            header_row_index = index
            break

    if header_row_index != -1:
        # La nueva cabecera es la fila encontrada
        new_header = df.iloc[header_row_index]
        df = df[header_row_index+1:] # Tomar los datos de la fila siguiente en adelante
        df.columns = new_header # Asignar la fila como cabecera
        df.reset_index(drop=True, inplace=True)
    else:
        st.warning("No se encontró la fila de cabecera esperada ('Aviso' y 'Texto'). Se intentará procesar con la primera fila.")
        # Si no se encuentra la cabecera esperada, asumimos que la primera fila es la cabecera
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)

    # Limpiar nombres de columnas nuevamente después de la asignación de la nueva cabecera
    df = clean_column_names(df)
    return df

def load_and_merge_data(uploaded_file):
    """Carga y fusiona los datos de las hojas 'IW29' e 'IW39' del archivo Excel."""
    xls = pd.ExcelFile(uploaded_file)
    
    # Cargar IW29
    iw29 = pd.read_excel(xls, sheet_name='IW29')
    iw29 = clean_excel_data(iw29)

    # Cargar IW39
    iw39 = pd.read_excel(xls, sheet_name='IW39')
    iw39 = clean_excel_data(iw39)

    # Renombrar columnas para estandarizar
    # Asegúrate de que estos nombres 'texto_breve' y 'denominacion_de_ejecutante'
    # coinciden con los nombres limpiados de tus columnas en el Excel
    # Por ejemplo, si en IW29 tienes una columna 'Texto Breve', se limpiará a 'texto_breve'
    # y si en IW39 tienes 'Denominación de ejecutante', se limpiará a 'denominacion_de_ejecutante'
    
    # Validar si las columnas existen antes de renombrar
    if 'texto_breve' in iw29.columns:
        iw29.rename(columns={"texto_breve": "texto"}, inplace=True)
    if 'denominacion_de_ejecutante' in iw39.columns:
        iw39.rename(columns={"denominacion_de_ejecutante": "denominacion_ejecutante"}, inplace=True)
    if 'total_general_real' in iw39.columns:
        iw39.rename(columns={"total_general_real": "total_general_real"}, inplace=True)
    else: # Fallback for common variations
        if 'total_general_real' in iw39.columns:
            iw39.rename(columns={"total_general_real": "total_general_real"}, inplace=True)
        elif 'total_general_cop' in iw39.columns: # Another common name
            iw39.rename(columns={"total_general_cop": "total_general_real"}, inplace=True)
        # Add more fallbacks if needed based on typical column names from your Excel files
    
    # Extraer solo columnas necesarias de iw39 para el merge (incluyendo 'Total general (real)')
    iw39_subset = iw39[["aviso", "total_general_real"]] # Asumimos que 'total_general_real' es el nombre limpio

    # Unir por 'aviso'
    tmp1 = pd.merge(iw29, iw39_subset, on="aviso", how="left")

    # Si hay 'duracion_de_parada_minutos' en tmp1, convertir a minutos
    if 'duracion_de_parada_minutos' in tmp1.columns:
        tmp1.rename(columns={'duracion_de_parada_minutos': 'duracion_de_parada'}, inplace=True)
    elif 'duracion_de_parada' in tmp1.columns: # Si ya viene como 'duracion_de_parada'
        pass
    else:
        tmp1['duracion_de_parada'] = np.nan # Si no existe, crearla con NaN

    # Columnas que deberían ser numéricas
    numeric_cols = ['coste_real', 'coste_previsto', 'duracion_de_parada', 'equipo']
    for col in numeric_cols:
        if col in tmp1.columns:
            tmp1[col] = pd.to_numeric(tmp1[col], errors='coerce')

    # Identificar el tipo de servicio
    def categorize_service(text):
        if pd.isna(text):
            return "OTROS"
        text = str(text).lower()
        if re.search(r'mantenimiento|mtto|correctivo|preventivo|predictivo', text):
            return "MANTENIMIENTO"
        elif re.search(r'instalacion|instala|montaje|montar', text):
            return "INSTALACION"
        elif re.search(r'reparacion|repara|arreglo|arreglar', text):
            return "REPARACION"
        elif re.search(r'revision|revisa', text):
            return "REVISION"
        elif re.search(r'calibracion|calibra', text):
            return "CALIBRACION"
        elif re.search(r'adecuacion|adecuar', text):
            return "ADECUACION"
        elif re.search(r'suministro|suministra|compra|compuerta', text):
            return "SUMINISTRO"
        elif re.search(r'obras|civil', text):
            return "OBRAS CIVIL"
        elif re.search(r'limpieza|limpia|desinfeccion', text):
            return "LIMPIEZA Y DESINFECCION"
        else:
            return "OTROS"

    tmp1['tipo_de_servicio'] = tmp1['texto'].apply(categorize_service)

    # Identificar si es programado o no programado
    def classify_program(text):
        if pd.isna(text):
            return "NO CLASIFICADO"
        text = str(text).lower()
        if re.search(r'programado|preventivo|predictivo|calibracion|revision', text):
            return "PROGRAMADO"
        elif re.search(r'correctivo|urgente|emergencia|no programado', text):
            return "NO PROGRAMADO"
        else:
            return "NO CLASIFICADO"

    tmp1['programacion'] = tmp1['tipo_de_servicio'].apply(classify_program)

    # Filtrar solo las columnas necesarias para el DataFrame final
    # Asegúrate de incluir 'denominacion_ejecutante' si quieres mantenerla para 'PROVEEDOR'
    # y 'total_general_real' para 'Costes tot.reales'
    df = tmp1[['aviso', 'texto', 'fecha_de_aviso', 'denominacion_ejecutante',
               'duracion_de_parada', 'equipo', 'total_general_real', 'tipo_de_servicio',
               'programacion']].copy()

    # Renombrar columnas a los nombres finales
    df.rename(columns={
        "texto": "texto_equipo", # Ya se categorizó 'tipo_de_servicio' de aquí
        "total_general_real": "costes_totreales"
    }, inplace=True)
    
    # Ensure 'costes_totreales' is numeric
    df['costes_totreales'] = pd.to_numeric(df['costes_totreales'], errors='coerce')

    # --- Add this new section to group by 'aviso' and sum 'costes_totreales' ---
    # Group by 'aviso' and sum 'costes_totreales', keeping the first occurrence of other relevant columns.
    # We select key columns to keep, and sum only the 'costes_totreales'.
    # For other columns that should not be summed, we take the first valid entry.
    
    # Identify columns to aggregate (sum) and columns to keep (first non-null value)
    # Exclude 'costes_totreales' from 'columns_to_keep_first' as it will be summed.
    columns_to_keep_first = [col for col in df.columns if col not in ['costes_totreales']]

    # Create a dictionary for aggregation: sum 'costes_totreales', take first for others
    aggregation_dict = {col: 'first' for col in columns_to_keep_first}
    aggregation_dict['costes_totreales'] = 'sum'
    
    df_aggregated = df.groupby('aviso', as_index=False).agg(aggregation_dict)
    
    # If there are any columns you want to ensure are *not* included in the aggregation
    # and you want to explicitly drop them or handle them differently, you would do it here.
    # For now, this approach takes the 'first' for all other columns, which is typically desired
    # when consolidating rows based on a key like 'aviso'.

    df = df_aggregated # Assign the aggregated DataFrame back to df

    # --- End of new section ---

    # Assign relevant columns to new, simplified names for easier access (from first code)
    df['PROVEEDOR'] = df['denominacion_ejecutante']
    df['COSTO'] = df['costes_totreales']
    df['TIEMPO PARADA'] = pd.to_numeric(df['duracion_de_parada'], errors='coerce')
    df['EQUIPO'] = pd.to_numeric(df['equipo'], errors='coerce')
    df['AVISO'] = pd.to_numeric(df['aviso'], errors='coerce')
    df['TIPO DE SERVICIO'] = df['tipo_de_servicio']

    return df

# --- Clases para las aplicaciones de Streamlit ---
class CostosAvisosApp:
    def __init__(self, df):
        self.df = df

    def display_costos_avisos_dashboard(self):
        st.header("Análisis de Costos y Avisos")

        st.subheader("Costos Totales Reales por Tipo de Servicio")
        costos_por_tipo = self.df.groupby('TIPO DE SERVICIO')['COSTO'].sum().sort_values(ascending=False)
        st.bar_chart(costos_por_tipo)
        st.write(costos_por_tipo)

        st.subheader("Costos Totales Reales por Programación")
        costos_por_programacion = self.df.groupby('programacion')['COSTO'].sum().sort_values(ascending=False)
        st.bar_chart(costos_por_programacion)
        st.write(costos_por_programacion)

        st.subheader("Tiempo de Parada por Tipo de Servicio")
        tiempo_parada_por_tipo = self.df.groupby('TIPO DE SERVICIO')['TIEMPO PARADA'].sum().sort_values(ascending=False)
        st.bar_chart(tiempo_parada_por_tipo)
        st.write(tiempo_parada_por_tipo)

        st.subheader("Distribución de Costos por Proveedor")
        costos_por_proveedor = self.df.groupby('PROVEEDOR')['COSTO'].sum().sort_values(ascending=False).head(10) # Top 10 proveedores
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=costos_por_proveedor.index, y=costos_por_proveedor.values, ax=ax, palette="viridis")
        ax.set_title('Top 10 Proveedores por Costos Totales Reales')
        ax.set_xlabel('Proveedor')
        ax.set_ylabel('Costo Total Real')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        st.write(costos_por_proveedor)

        st.subheader("Avisos por Equipo")
        avisos_por_equipo = self.df['EQUIPO'].value_counts().head(10)
        st.bar_chart(avisos_por_equipo)
        st.write(avisos_por_equipo)

class EvaluacionProveedoresApp:
    def __init__(self, df):
        self.df = df

    def display_evaluacion_dashboard(self):
        st.header("Evaluación de Proveedores")

        st.write("Esta sección se podría expandir para incluir métricas de evaluación de proveedores como:")
        st.markdown("""
        - Costo promedio por servicio.
        - Tiempo promedio de respuesta.
        - Cantidad de avisos atendidos.
        - Calidad del servicio (si se tuviera un sistema de calificación).
        """)

        st.subheader("Análisis de Eficiencia por Proveedor")
        # Ejemplo: Costo promedio por Aviso por Proveedor
        avg_cost_per_aviso = self.df.groupby('PROVEEDOR')['COSTO'].mean().sort_values(ascending=False)
        st.bar_chart(avg_cost_per_aviso)
        st.write("Costo Promedio por Aviso por Proveedor:")
        st.write(avg_cost_per_aviso)

        # Ejemplo: Número de Avisos por Proveedor
        avisos_count_by_provider = self.df['PROVEEDOR'].value_counts()
        st.bar_chart(avisos_count_by_provider)
        st.write("Número de Avisos Atendidos por Proveedor:")
        st.write(avisos_count_by_provider)

# --- Navegación entre páginas ---
def navigate_to(page_name):
    st.session_state['page'] = page_name

# --- Configuración de la aplicación Streamlit principal ---
if 'page' not in st.session_state:
    st.session_state['page'] = 'cargar_datos'
if 'df' not in st.session_state:
    st.session_state['df'] = None

# Sidebar para la navegación
with st.sidebar:
    st.image("https://www.sura.com/estudios/wp-content/uploads/2021/08/logo-sura.png", width=150) # Reemplaza con el logo de Sura
    st.title("Menú")
    if st.button("Cargar Datos", key="nav_cargar_datos"):
        navigate_to('cargar_datos')
    if st.button("Costos y Avisos", key="nav_costos_avisos"):
        navigate_to('costos_avisos')
    if st.button("Evaluación de Proveedores", key="nav_evaluacion"):
        navigate_to('evaluacion')

# Contenido de las páginas
if st.session_state['page'] == 'cargar_datos':
    st.title("Cargar Datos de Avisos y Costos")
    st.write("Por favor, sube tu archivo Excel con las hojas 'IW29' e 'IW39'.")
    st.warning("Asegúrate de que las columnas 'Aviso' y 'Texto' o 'Texto breve' están presentes en la hoja IW29, y 'Aviso' y 'Total general (real)' en la hoja IW39.")

    uploaded_file = st.file_uploader("Arrastra y suelta tu archivo Excel aquí o haz clic para buscar", type=["xlsx"])

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
            st.warning("Asegúrate de que el archivo Excel contenga las hojas correctas y los formatos esperados.")

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
