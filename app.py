import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Gestión Comonli", page_icon="📈")

# --- CONEXIÓN ---
def conectar_google():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    return gspread.authorize(creds)

def obtener_datos():
    try:
        client = conectar_google()
        hoja = client.open("Registro de Pedidos").sheet1
        return hoja.get_all_records()
    except:
        return []

# --- LÓGICA DE FILTROS ---
datos = obtener_datos()
fecha_hoy = datetime.now().strftime("%d/%m/%Y")

# Filtrar pedidos de hoy
pedidos_hoy = [fila for fila in datos if fecha_hoy in str(fila.get('Fecha y Hora', ''))]
total_hoy = len(pedidos_hoy)

# --- INTERFAZ ---
st.title("🚀 Panel de Pedidos")

# Fila de métricas
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Pedidos de Hoy", value=total_hoy)

# Buscador por Sector
st.subheader("🔍 Filtro por Sector")
sector_buscar = st.text_input("Escribe el nombre del sector para consultar:")

if sector_buscar:
    # Contar coincidencias (sin importar mayúsculas/minúsculas)
    coincidencias = [p for p in pedidos_hoy if sector_buscar.lower() in str(p.get('Sector', '')).lower()]
    st.info(f"Hay **{len(coincidencias)}** pedidos para '{sector_buscar}' el día de hoy.")

st.divider()

# --- FORMULARIO DE REGISTRO ---
st.subheader("📝 Registrar Nuevo Pedido")

sector = st.text_input("📍 Sector:")
ubica = st.text_input("🗺️ Ubicación (Maps):")
cel = st.text_input("📱 Celular:")
monto = st.text_input("💰 Monto ($):")
prod = st.text_area("📦 Productos:")

if st.button("GENERAR Y GUARDAR"):
    if sector and prod:
        fecha_full = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        datos_fila = [fecha_full, sector, ubica, cel, monto, prod]
        
        # Guardar en nube
        try:
            client = conectar_google()
            hoja = client.open("Registro de Pedidos").sheet1
            hoja.append_row(datos_fila)
            st.success("✅ ¡Guardado! Refresca la página para actualizar el contador.")
            
            # Formato WhatsApp
            mensaje_wa = f"✅ *NUEVO PEDIDO*\n---\n📦 *Prod:* {prod}\n💰 *Monto:* ${monto}\n📍 *Sector:* {sector}\n📱 *Cel:* {cel}\n🗺️ *Ubicación:* {ubica}"
            st.code(mensaje_wa, language="text")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
    else:
        st.warning("Completa los campos obligatorios.")
