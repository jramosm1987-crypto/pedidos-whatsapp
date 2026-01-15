import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Gestión de Pedidos Comonli", page_icon="📦", layout="wide")

# --- CONEXIÓN ---
def conectar_google():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        return gspread.authorize(creds)
    except:
        return None

def obtener_datos():
    client = conectar_google()
    if client:
        try:
            hoja = client.open("Registro de Pedidos").sheet1
            return hoja.get_all_records()
        except: return []
    return []

# --- LÓGICA DE LIMPIEZA ---
def limpiar_campos():
    st.session_state.sector = ""
    st.session_state.ubica = ""
    st.session_state.cel = ""
    st.session_state.monto = ""
    st.session_state.prod = ""

# --- INTERFAZ ---
st.title("🚀 Panel de Control Comonli")

datos = obtener_datos()
fecha_hoy = datetime.now().strftime("%d/%m/%Y")
pedidos_hoy = [fila for fila in datos if fecha_hoy in str(fila.get('Fecha y Hora', ''))]

# MÉTRICAS
c1, c2, c3 = st.columns(3)
with c1: st.metric("Total Hoy", len(pedidos_hoy))
with c2: st.metric("Pendientes", len([p for p in pedidos_hoy if p.get('Estado') != 'Entregado']))
with c3: st.metric("Entregados", len([p for p in pedidos_hoy if p.get('Estado') == 'Entregado']))

st.divider()

# GESTIÓN DE PEDIDOS (Actualizar/Borrar)
st.subheader("🔄 Pedidos de Hoy")
if pedidos_hoy:
    opciones = ["Pendiente", "En Camino", "Entregado"]
    for idx, p in enumerate(pedidos_hoy):
        col_a, col_b, col_c, col_d = st.columns([3, 2, 1, 1])
        with col_a: st.write(f"📍 **{p.get('Sector')}** - {p.get('Productos')[:20]}...")
        with col_b:
            estado_actual = p.get('Estado') if p.get('Estado') in opciones else "Pendiente"
            nuevo_e = st.selectbox(f"e{idx}", opciones, index=opciones.index(estado_actual), key=f"s{idx}", label_visibility="collapsed")
        with col_c:
            if st.button("OK", key=f"ok{idx}"):
                client = conectar_google(); hoja = client.open("Registro de Pedidos").sheet1
                celda = hoja.find(p['Fecha y Hora']); hoja.update_cell(celda.row, 7, nuevo_e); st.rerun()
        with col_d:
            if st.button("🗑️", key=f"del{idx}"):
                client = conectar_google(); hoja = client.open("Registro de Pedidos").sheet1
                celda = hoja.find(p['Fecha y Hora']); hoja.delete_rows(celda.row); st.rerun()
else: st.write("No hay pedidos.")

st.divider()

# --- FORMULARIO CON LIMPIEZA AUTOMÁTICA ---
st.subheader("📝 Nuevo Pedido")

# Usamos 'key' para poder limpiar los campos desde el código
sector = st.text_input("📍 Sector:", key="sector")
ubica = st.text_input("🗺️ Link Ubicación:", key="ubica")
cel = st.text_input("📱 Celular:", key="cel")
monto = st.text_input("💰 Monto ($):", key="monto")
prod = st.text_area("📦 Productos:", key="prod")

if st.button("GENERAR Y GUARDAR"):
    if sector and prod:
        fecha_f = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        datos_fila = [fecha_f, sector, ubica, cel, monto, prod, "Pendiente"]
        
        try:
            client = conectar_google()
            hoja = client.open("Registro de Pedidos").sheet1
            hoja.append_row(datos_fila)
            
            # Mostramos el mensaje para copiar
            st.success("✅ ¡Guardado en Google Sheets!")
            mensaje_wa = f"✅ *NUEVO PEDIDO*\n---\n📦 *Prod:* {prod}\n💰 *Monto:* ${monto}\n📍 *Sector:* {sector}\n📱 *Cel:* {cel}\n🗺️ *Ubicación:* {ubica}"
            st.code(mensaje_wa, language="text")
            
            # Botón para limpiar y seguir con otro
            st.button("Limpiar formulario para nuevo pedido", on_click=limpiar_campos)
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Completa Sector y Productos.")
