import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Gestión de Pedidos Comonli", page_icon="📦", layout="wide")

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

# --- INTERFAZ ---
st.title("🚀 Panel de Control de Pedidos")

datos = obtener_datos()
fecha_hoy = datetime.now().strftime("%d/%m/%Y")
pedidos_hoy = [fila for fila in datos if fecha_hoy in str(fila.get('Fecha y Hora', ''))]

# --- SECCIÓN DE MÉTRICAS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Hoy", len(pedidos_hoy))
with col2:
    pendientes = len([p for p in pedidos_hoy if p.get('Estado') != 'Entregado'])
    st.metric("Por Entregar", pendientes)
with col3:
    entregados = len([p for p in pedidos_hoy if p.get('Estado') == 'Entregado'])
    st.metric("Entregados", entregados)

st.divider()

# --- GESTIÓN DE ESTADOS ---
st.subheader("🔄 Actualizar Estado de Pedidos (Hoy)")
if pedidos_hoy:
    opciones_estado = ["Pendiente", "En Camino", "Entregado"]
    for idx, pedido in enumerate(pedidos_hoy):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.write(f"**{pedido.get('Sector')}** - {pedido.get('Productos', '')[:30]}...")
        with c2:
            # FIX: Validamos que el estado exista en nuestras opciones, si no, usamos "Pendiente"
            estado_actual = pedido.get('Estado')
            if estado_actual not in opciones_estado:
                estado_actual = "Pendiente"
                
            nuevo_estado = st.selectbox(
                f"Estado pedido {idx}", 
                opciones_estado, 
                index=opciones_estado.index(estado_actual),
                key=f"sel_{idx}",
                label_visibility="collapsed"
            )
        with c3:
            if st.button("Actualizar", key=f"btn_{idx}"):
                try:
                    client = conectar_google()
                    hoja = client.open("Registro de Pedidos").sheet1
                    celda = hoja.find(pedido['Fecha y Hora'])
                    hoja.update_cell(celda.row, 7, nuevo_estado)
                    st.success("¡Listo!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
else:
    st.write("Aún no hay pedidos registrados para hoy.")

st.divider()

# --- FORMULARIO DE REGISTRO ---
st.subheader("📝 Registrar Nuevo Pedido")
sector = st.text_input("📍 Sector:")
ubica = st.text_input("🗺️ Ubicación:")
cel = st.text_input("📱 Celular:")
monto = st.text_input("💰 Monto ($):")
prod = st.text_area("📦 Productos:")

if st.button("GENERAR Y GUARDAR"):
    if sector and prod:
        fecha_full = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        datos_fila = [fecha_full, sector, ubica, cel, monto, prod, "Pendiente"]
        
        try:
            client = conectar_google()
            hoja = client.open("Registro de Pedidos").sheet1
            hoja.append_row(datos_fila)
            st.success("✅ Pedido guardado.")
            st.code(f"✅ *NUEVO PEDIDO*\n---\n📦 *Prod:* {prod}\n💰 *Monto:* ${monto}\n📍 *Sector:* {sector}\n📱 *Cel:* {cel}\n🗺️ *Ubicación:* {ubica}", language="text")
        except Exception as e:
            st.error(f"Error: {e}")
