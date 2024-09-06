import pandas as pd
import re
import streamlit as st
import plotly.express as px

# Función para limpiar la columna 'Valor'
def limpiar_valor(valor):
    # Eliminar unidades usando una expresión regular
    if isinstance(valor, str):
        valor = re.sub(r'[^\d.]+', '', valor)
    return valor

# Función para leer el archivo Excel y preparar los datos
def preparar_datos(df):
    # Imprimir nombres de las columnas para depuración
    st.write(f"Columnas en el archivo: {df.columns.tolist()}")
    
    # Intentar convertir la columna de fecha y hora a datetime
    if 'FechaHora' in df.columns:
        df['FechaHora'] = pd.to_datetime(df['FechaHora'])
    elif 'Fecha' in df.columns:
        df['FechaHora'] = pd.to_datetime(df['Fecha'])
    else:
        st.error("El archivo debe contener una columna 'FechaHora' o 'Fecha'")
        return None
    
    # Limpiar y convertir la columna 'Valor' a numérica
    df['Valor'] = df['Valor'].apply(limpiar_valor)
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    
    # Eliminar filas con valores 'Valor' NaN
    df = df.dropna(subset=['Valor'])
    
    # Ordenar los datos por fecha y hora
    df = df.sort_values(by='FechaHora')
    
    return df

# Función para graficar los datos de dos dataframes
def graficar_datos(df1, df2):
    # Obtener los identificadores únicos de ambos dataframes
    identificadores = set(df1['Descripción'].unique()).union(set(df2['Descripción'].unique()))
    
    # Colores para las series de datos
    colores = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black']
    
    # Graficar cada identificador por separado
    for i, identificador in enumerate(identificadores):
        # Filtrar los datos por identificador en ambos dataframes
        df1_identificador = df1[df1['Descripción'] == identificador]
        df2_identificador = df2[df2['Descripción'] == identificador]
        
        # Crear un gráfico interactivo usando Plotly
        fig = px.line(title=f'Comparación de valores para: {identificador}')
        
        # Agregar datos del primer dataframe
        if not df1_identificador.empty:
            fig.add_scatter(x=df1_identificador['FechaHora'], y=df1_identificador['Valor'], mode='lines+markers', name=f'{identificador} (Archivo 1)', line=dict(color=colores[i % len(colores)]))
        
        # Agregar datos del segundo dataframe
        if not df2_identificador.empty:
            fig.add_scatter(x=df2_identificador['FechaHora'], y=df2_identificador['Valor'], mode='lines+markers', name=f'{identificador} (Archivo 2)', line=dict(color=colores[(i + 1) % len(colores)]))
        
        # Configurar etiquetas y título
        fig.update_layout(
            xaxis_title='Fecha y Hora',
            yaxis_title='Valor',
            title=f'Comparación de valores por identificador: {identificador}'
        )
        
        # Mostrar el gráfico en la aplicación Streamlit
        st.plotly_chart(fig)

# Título de la aplicación
st.title("Comparación de Datos con Plotly y Streamlit")

# Cargar archivos Excel usando Streamlit
uploaded_file1 = st.file_uploader("Selecciona el primer archivo Excel", type=["xlsx", "xls"], key='file1')
uploaded_file2 = st.file_uploader("Selecciona el segundo archivo Excel", type=["xlsx", "xls"], key='file2')

# Procesar los archivos si se han cargado
if uploaded_file1 and uploaded_file2:
    df1 = pd.read_excel(uploaded_file1)
    df2 = pd.read_excel(uploaded_file2)
    
    # Preparar los datos
    df1 = preparar_datos(df1)
    df2 = preparar_datos(df2)
    
    if df1 is not None and df2 is not None:
        # Graficar los datos
        graficar_datos(df1, df2)