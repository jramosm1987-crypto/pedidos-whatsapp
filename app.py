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

# --- CONEXIÓN A GOOGLE SHEETS ---
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

# --- FUNCIONES DE APOYO ---
def limpiar_campos():
    for k in ["sector", "ubica", "cel", "monto", "prod", "lat_manual", "lon_manual"]:
        if k in st.session_state: st.session_state[k] = ""

def formatear_mensaje(p):
    return (f"✅ *NUEVO PEDIDO*\n--------------------------\n"
            f"📦 *Prod:* {p.get('Productos')}\n💰 *Monto:* ${p.get('Monto')}\n"
            f"📍 *Sector:* {p.get('Sector')}\n📱 *Cel:* {p.get('Celular')}\n"
            f"🗺️ *Ubicación:* {p.get('Ubicación')}\n--------------------------")

# --- INTERFAZ PRINCIPAL ---
st.title("🚀 Gestión de Entregas Comonli")

datos = obtener_datos()
fecha_hoy = datetime.now().strftime("%d/%m/%Y")
pedidos_hoy = [fila for fila in datos if fecha_hoy in str(fila.get('Fecha y Hora', ''))]

# --- 1. MAPA DE ENTREGAS ---
st.subheader("🗺️ Mapa de Entregas del Día")
if pedidos_hoy:
    df = pd.DataFrame(pedidos_hoy)
    df['Latitud'] = pd.to_numeric(df['Latitud'], errors='coerce')
    df['Longitud'] = pd.to_numeric(df['Longitud'], errors='coerce')
    df_mapa = df[(df['Latitud'].notnull()) & (df['Latitud'] != 0)].copy()

    if not df_mapa.empty:
        centro = [df_mapa['Latitud'].iloc[0], df_mapa['Longitud'].iloc[0]]
        m = folium.Map(location=centro, zoom_start=13)
        for _, row in df_mapa.iterrows():
            est = str(row.get('Estado', 'Pendiente'))
            color = 'red' if est == 'Pendiente' else 'orange' if est == 'En Camino' else 'green'
            folium.Marker([row['Latitud'], row['Longitud']], popup=f"<b>{row['Sector']}</b>", icon=folium.Icon(color=color)).add_to(m)
        st_folium(m, width=1200, height=400)
    else: st.info("ℹ️ Esperando GPS para activar mapa.")

st.divider()

# --- 2. GESTIÓN DE PEDIDOS ---
st.subheader("🔄 Pedidos de Hoy")
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
                st.session_state.mensaje_copiar = formatear_mensaje(p)
        with c5:
            if st.button("🗑️", key=f"del{idx}"):
                client = conectar_google(); hoja = client.open("Registro de Pedidos").sheet1
                celda = hoja.find(p['Fecha y Hora']); hoja.delete_rows(celda.row); st.rerun()

    if "mensaje_copiar" in st.session_state:
        st.code(st.session_state.mensaje_copiar, language="text"); st.button("Cerrar", on_click=lambda: st.session_state.pop("mensaje_copiar"))

st.divider()

# --- 3. FORMULARIO CON GPS O MANUAL ---
st.subheader("📝 Nuevo Pedido")

# Captura automática de GPS
loc = streamlit_js_eval(key='loc', function_name='getCurrentPosition', pre_function_call_value=None)
lat_val, lon_val = 0, 0

if loc:
    lat_val, lon_val = loc['coords']['latitude'], loc['coords']['longitude']
    st.success(f"📍 GPS Detectado: {lat_val}, {lon_val}")
else:
    st.warning("📡 Buscando GPS... (Revisa el candado del navegador)")

# OPCIÓN MANUAL
manual = st.checkbox("Ingresar ubicación manualmente (Si el GPS de la PC falla)")
if manual:
    col_m1, col_m2 = st.columns(2)
    with col_m1: lat_val = st.number_input("Latitud:", format="%.6f", key="lat_manual")
    with col_m2: lon_val = st.number_input("Longitud:", format="%.6f", key="lon_manual")

col_izq, col_der = st.columns(2)
with col_izq:
    sec = st.text_input("📍 Sector:", key="sector")
    ubi = st.text_input("🗺️ Link Ubicación:", key="ubica")
    celu = st.text_input("📱 Celular:", key="cel")
with col_der:
    mon = st.text_input("💰 Monto ($):", key="monto")
    pro = st.text_area("📦 Productos:", key="prod")

if st.button("GENERAR Y GUARDAR"):
    if not sec or not pro:
        st.error("⚠️ Sector y Productos son obligatorios.")
    elif lat_val == 0:
        st.error("❌ No se puede guardar sin ubicación. Activa el GPS o marca la casilla 'Ingresar manualmente'.")
    else:
        fecha_f = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        datos_fila = [fecha_f, sec, ubi, celu, mon, pro, "Pendiente", lat_val, lon_val]
        try:
            client = conectar_google(); hoja = client.open("Registro de Pedidos").sheet1
            hoja.append_row(datos_fila)
            st.success("✅ ¡Guardado con éxito!")
            st.code(formatear_mensaje({"Productos":pro, "Monto":mon, "Sector":sec, "Celular":celu, "Ubicación":ubi}), language="text")
            st.button("Registrar otro", on_click=limpiar_campos)
        except Exception as e: st.error(f"Error: {e}")
