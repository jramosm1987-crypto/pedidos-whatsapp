import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval

# Configuración de página
st.set_page_config(page_title="Gestión Comonli con Mapa", page_icon="📍", layout="wide")

# --- CONEXIÓN ---
def conectar_google():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        return gspread.authorize(creds)
    except: return None

def obtener_datos():
    client = conectar_google()
    if client:
        try:
            hoja = client.open("Registro de Pedidos").sheet1
            return hoja.get_all_records()
        except: return []
    return []

# --- FUNCIONES ---
def limpiar_campos():
    for key in ["sector", "ubica", "cel", "monto", "prod"]:
        st.session_state[key] = ""

def formatear_mensaje(p):
    return (f"✅ *NUEVO PEDIDO*\n---\n📦 *Prod:* {p.get('Productos')}\n💰 *Monto:* ${p.get('Monto')}\n"
            f"📍 *Sector:* {p.get('Sector')}\n📱 *Cel:* {p.get('Celular')}\n🗺️ *Ubicación:* {p.get('Ubicación')}")

# --- INTERFAZ ---
st.title("📍 Sistema de Entregas con Mapa")

datos = obtener_datos()
fecha_hoy = datetime.now().strftime("%d/%m/%Y")
pedidos_hoy = [fila for fila in datos if fecha_hoy in str(fila.get('Fecha y Hora', ''))]

# --- 1. MAPA GENERAL ---
st.subheader("🗺️ Mapa de Entregas del Día")
if pedidos_hoy:
    # Crear dataframe con pedidos que tengan coordenadas
    df = pd.DataFrame(pedidos_hoy)
    # Limpiar datos vacíos de lat/lon
    df_mapa = df[df['Latitud'].astype(str).str.contains(r'-?\d+')].copy()
    
    if not df_mapa.empty:
        m = folium.Map(location=[df_mapa['Latitud'].iloc[0], df_mapa['Longitud'].iloc[0]], zoom_start=12)
        
        for _, row in df_mapa.iterrows():
            color = 'red' if row['Estado'] == 'Pendiente' else 'orange' if row['Estado'] == 'En Camino' else 'green'
            folium.Marker(
                [row['Latitud'], row['Longitud']],
                popup=f"{row['Sector']} - {row['Estado']}",
                tooltip=row['Productos'],
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(m)
        
        st_folium(m, width=1200, height=400)
    else:
        st.info("Aún no hay pedidos con coordenadas GPS capturadas para mostrar en el mapa.")
else:
    st.info("No hay pedidos registrados hoy.")

st.divider()

# --- 2. GESTIÓN Y WHATSAPP ---
st.subheader("🔄 Gestión de Pedidos")
# (Aquí va la misma lógica de los botones 💬, OK y 🗑️ de la versión anterior)
# ... [Se mantiene igual para no alargar el texto] ...

st.divider()

# --- 3. FORMULARIO CON CAPTURA GPS ---
st.subheader("📝 Nuevo Pedido")

# Botón mágico para GPS
st.write("Presiona este botón si estás en el lugar de entrega o con el cliente:")
loc = streamlit_js_eval(key='loc', function_name='getCurrentPosition')

if loc:
    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    st.success(f"📍 GPS Capturado: {lat}, {lon}")
else:
    lat, lon = "", ""

col1, col2 = st.columns(2)
with col1:
    sector = st.text_input("📍 Sector:", key="sector")
    ubica = st.text_input("🗺️ Link Ubicación:", key="ubica")
    cel = st.text_input("📱 Celular:", key="cel")
with col2:
    monto = st.text_input("💰 Monto ($):", key="monto")
    prod = st.text_area("📦 Productos:", key="prod")

if st.button("GENERAR Y GUARDAR"):
    if sector and prod:
        fecha_f = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        # Guardamos incluyendo Latitud (Columna 8) y Longitud (Columna 9)
        datos_fila = [fecha_f, sector, ubica, cel, monto, prod, "Pendiente", lat, lon]
        
        try:
            client = conectar_google(); hoja = client.open("Registro de Pedidos").sheet1
            hoja.append_row(datos_fila)
            st.success("✅ Guardado con éxito")
            st.code(formatear_mensaje({"Productos":prod, "Monto":monto, "Sector":sector, "Celular":cel, "Ubicación":ubica}), language="text")
            st.button("Limpiar formulario", on_click=limpiar_campos)
        except: st.error("Error al conectar con Google Sheets")
