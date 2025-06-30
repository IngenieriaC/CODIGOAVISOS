
import streamlit as st

import pandas as pd

import matplotlib.pyplot as plt

import seaborn as sns

import re

import io # Importamos io para manejar archivos en memoria

# Estilos CSS para ambientar en amarillo, blanco y azul rey

st.markdown(

  

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

    Aquí podrás **Unir los datos de avisos** para optimizar los procesos.

    Por favor, **sube el archivo `DATA2.XLSX`** para comenzar.

""")



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

    tmp2.drop(columns=["Equipo"], errors='ignore', inplace=True)

    tmp2 = pd.merge(tmp2, equipo_original, on="Aviso", how="left")



    # Unir por 'Equipo' con IH08

    tmp3 = pd.merge(tmp2, ih08[[

        "Equipo", "Inic.garantía prov.", "Fin garantía prov.", "Texto", "Indicador ABC", "Denominación de objeto técnico"

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

        "Texto grupo acción", "TIPO DE SERVICIO"

    ]



    # Filtrar solo las columnas que realmente existen en tmp4

    columnas_finales = [col for col in columnas_finales if col in tmp4.columns]



    return tmp4[columnas_finales]



# --- 3. Uploader y Ejecución ---

uploaded_file = st.file_uploader("Sube tu archivo 'DATA2.XLSX' aquí", type=["xlsx"])



if uploaded_file:

    # Usamos io.BytesIO para pasar el archivo como un buffer en memoria

    # Esto es crucial para que read_excel pueda leer múltiples hojas del mismo archivo

    # sin tener que guardarlo en el disco del servidor de Streamlit.

    file_buffer = io.BytesIO(uploaded_file.getvalue())



    with st.spinner('Cargando y procesando datos... Esto puede tomar un momento.'):

        try:

            df = load_and_merge_data(file_buffer)



            # --- Procesamiento adicional ---

            # Eliminar registros cuyo 'Status del sistema' contenga "PTBO"

            initial_rows = len(df)

            df = df[~df["Status del sistema"].str.contains("PTBO", case=False, na=False)]

            st.info(f"Se eliminaron {initial_rows - len(df)} registros con 'PTBO' en 'Status del sistema'.")



            # Dejar solo una fila con coste por cada aviso

            df['Costes tot.reales'] = df.groupby('Aviso')['Costes tot.reales'].transform(

                lambda x: [x.iloc[0]] + [0]*(len(x)-1)

            )



            st.success("✅ Datos cargados y procesados exitosamente.")

            st.write(f"**Filas finales:** {len(df)} – **Columnas:** {len(df.columns)}")



            # --- Suma del Total de Costo Real y de Avisos ---

            st.markdown("---")

            st.subheader("Resumen de Totales")



            # Asegurarse de que la columna 'Costes tot.reales' sea numérica y manejar NaNs

            df['Costes tot.reales'] = pd.to_numeric(df['Costes tot.reales'], errors='coerce').fillna(0)



            total_costo_real = df['Costes tot.reales'].sum()

            total_avisos = df['Aviso'].nunique() # Contar avisos únicos



            st.metric(label="Total de Costo Real", value=f"${total_costo_real:,.2f}")

            st.metric(label="Total de Avisos Únicos", value=f"{total_avisos:,}")





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

                help="Descarga el archivo en formato XLSX."

            )



            st.markdown("---")

            st.success("¡El procesamiento ha finalizado! Ahora puedes descargar tus datos o seguir explorando.")



        except Exception as e:

            st.error(f"❌ ¡Ups! Ocurrió un error al procesar el archivo: {e}")

            st.warning("Por favor, verifica que el archivo subido sea `DATA2.XLSX` y tenga el formato de hojas esperado.")

            st.exception(e) # Muestra el traceback completo para depuración

else:

    st.info("⬆️ Sube tu archivo `DATA2.XLSX` para empezar con el análisis.")
