import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval

# Configuración de página
st.set_page_config(page_title="Comonli Logistics", page_icon="📍", layout="wide")

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

# --- FUNCIONES AUXILIARES ---
def limpiar_campos():
    for k in ["sector", "ubica", "cel", "monto", "prod"]:
        st.session_state[k] = ""

def formatear_mensaje(p):
    return (f"✅ *NUEVO PEDIDO*\n---\n📦 *Prod:* {p.get('Productos')}\n💰 *Monto:* ${p.get('Monto')}\n"
            f"📍 *Sector:* {p.get('Sector')}\n📱 *Cel:* {p.get('Celular')}\n🗺️ *Ubicación:* {p.get('Ubicación')}")

# --- INTERFAZ ---
st.title("🚀 Gestión de Entregas Comonli")

datos = obtener_datos()
fecha_hoy = datetime.now().strftime("%d/%m/%Y")
pedidos_hoy = [fila for fila in datos if fecha_hoy in str(fila.get('Fecha y Hora', ''))]

# --- 1. MAPA CON FILTRO DE SEGURIDAD ---
st.subheader("🗺️ Mapa de Entregas (Hoy)")
if pedidos_hoy:
    df = pd.DataFrame(pedidos_hoy)
    
    # Convertimos lat/lon a números y eliminamos lo que no sirva
    df['Latitud'] = pd.to_numeric(df['Latitud'], errors='coerce')
    df['Longitud'] = pd.to_numeric(df['Longitud'], errors='coerce')
    
    # FILTRO: Solo coordenadas que no sean 0 y que no estén vacías
    df_mapa = df[(df['Latitud'].notnull()) & (df['Latitud'] != 0)].copy()

    if not df_mapa.empty:
        # Iniciamos el mapa en la ubicación del primer pedido válido
        centro = [df_mapa['Latitud'].iloc[0], df_mapa['Longitud'].iloc[0]]
        m = folium.Map(location=centro, zoom_start=13)
        
        for _, row in df_mapa.iterrows():
            # Color por estado
            est = str(row.get('Estado', 'Pendiente'))
            color = 'red' if est == 'Pendiente' else 'orange' if est == 'En Camino' else 'green'
            
            folium.Marker(
                [row['Latitud'], row['Longitud']],
                popup=f"<b>{row['Sector']}</b><br>Estado: {est}",
                tooltip=f"{row['Sector']}",
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(m)
        
        st_folium(m, width=1200, height=450)
    else:
        st.info("ℹ️ No hay coordenadas registradas hoy. El mapa se activará cuando guardes un pedido con GPS.")
else:
    st.info("ℹ️ No hay pedidos registrados para el día de hoy.")

st.divider()

# --- 2. GESTIÓN DE PEDIDOS ---
st.subheader("🔄 Pedidos Registrados")
if pedidos_hoy:
    opciones = ["Pendiente", "En Camino", "Entregado"]
    for idx, p in enumerate(pedidos_hoy):
        c1, c2, c3, c4, c5 = st.columns([3, 2, 0.6, 0.6, 0.6])
        with c1: st.write(f"📍 **{p.get('Sector')}** - {p.get('Productos')[:30]}...")
        with c2:
            est_p = p.get('Estado') if p.get('Estado') in opciones else "Pendiente"
            nuevo_e = st.selectbox(f"e{idx}", opciones, index=opciones.index(est_p), key=f"s{idx}", label_visibility="collapsed")
        with c3:
            if st.button("OK", key=f"ok{idx}"):
                client = conectar_google(); hoja = client.open("Registro de Pedidos").sheet1
                celda = hoja.find(p['Fecha y Hora']); hoja.update_cell(celda.row, 7, nuevo_e); st.rerun()
        with c4:
            if st.button("💬", key=f"msg{idx}"):
                st.session_state.mensaje_copiar = formatear_mensaje({"Productos":p.get('Productos'), "Monto":p.get('Monto Total', p.get('Monto')), "Sector":p.get('Sector'), "Celular":p.get('Celular Cliente', p.get('Celular')), "Ubicación":p.get('Ubicación (Google Maps)', p.get('Ubicación'))})
        with c5:
            if st.button("🗑️", key=f"del{idx}"):
                client = conectar_google(); hoja = client.open("Registro de Pedidos").sheet1
                celda = hoja.find(p['Fecha y Hora']); hoja.delete_rows(celda.row); st.rerun()

    if "mensaje_copiar" in st.session_state:
        st.code(st.session_state.mensaje_copiar, language="text")
        if st.button("Cerrar Mensaje"): del st.session_state.mensaje_copiar; st.rerun()

st.divider()

# --- 3. FORMULARIO CON GPS ---
st.subheader("📝 Registrar Nuevo Pedido")
# Captura de GPS
loc = streamlit_js_eval(key='loc', function_name='getCurrentPosition', pre_function_call_value=None)

lat_val, lon_val = 0, 0
if loc:
    lat_val = loc['coords']['latitude']
    lon_val = loc['coords']['longitude']
    st.success("📍 Ubicación lista para guardar")

col_izq, col_der = st.columns(2)
with col_izq:
    sec = st.text_input("📍 Sector:", key="sector")
    ubi = st.text_input("🗺️ Link Ubicación:", key="ubica")
    celu = st.text_input("📱 Celular:", key="cel")
with col_der:
    mon = st.text_input("💰 Monto ($):", key="monto")
    pro = st.text_area("📦 Productos:", key="prod")

if st.button("GENERAR Y GUARDAR"):
    if sec and pro:
        fecha_f = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        # Aseguramos que se guarden 9 columnas exactas
        datos_fila = [fecha_f, sec, ubi, celu, mon, pro, "Pendiente", lat_val, lon_val]
        try:
            client = conectar_google(); hoja = client.open("Registro de Pedidos").sheet1
            hoja.append_row(datos_fila)
            st.success("✅ Guardado correctamente")
            st.code(formatear_mensaje({"Productos":pro, "Monto":mon, "Sector":sec, "Celular":celu, "Ubicación":ubi}), language="text")
            st.button("Limpiar formulario", on_click=limpiar_campos)
        except Exception as e: st.error(f"Error al guardar: {e}")
