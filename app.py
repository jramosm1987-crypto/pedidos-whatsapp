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
    except Exception as e:
        st.error(f"Error de credenciales: {e}")
        return None

def obtener_datos():
    client = conectar_google()
    if client:
        try:
            hoja = client.open("Registro de Pedidos").sheet1
            return hoja.get_all_records()
        except:
            return []
    return []

# --- INTERFAZ ---
st.title("🚀 Panel de Control y Despacho")

datos = obtener_datos()
fecha_hoy = datetime.now().strftime("%d/%m/%Y")
# Filtrar pedidos de hoy
pedidos_hoy = [fila for fila in datos if fecha_hoy in str(fila.get('Fecha y Hora', ''))]

# --- MÉTRICAS ---
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

# --- HOJA DE RUTA (LINKS) ---
st.subheader("🗺️ Hoja de Ruta (Ubicaciones)")
if pedidos_hoy:
    cols_mapa = st.columns(4)
    for i, p in enumerate(pedidos_hoy):
        with cols_mapa[i % 4]:
            link = p.get('Ubicación (Google Maps)', p.get('Ubicación', ''))
            if "maps" in str(link).lower():
                st.link_button(f"📍 {p.get('Sector')}", str(link))
else:
    st.info("No hay rutas para mostrar.")

st.divider()

# --- GESTIÓN DE ESTADOS Y BORRADO ---
st.subheader("🔄 Gestión de Pedidos de Hoy")
if pedidos_hoy:
    opciones_estado = ["Pendiente", "En Camino", "Entregado"]
    for idx, pedido in enumerate(pedidos_hoy):
        # Usamos 4 columnas para incluir el botón de borrar
        c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
        
        with c1:
            st.write(f"**{pedido.get('Sector')}** - {pedido.get('Productos', '')[:30]}...")
        
        with c2:
            estado_actual = pedido.get('Estado') if pedido.get('Estado') in opciones_estado else "Pendiente"
            nuevo_estado = st.selectbox(
                f"Estado {idx}", opciones_estado, 
                index=opciones_estado.index(estado_actual), 
                key=f"sel_{idx}", label_visibility="collapsed"
            )
        
        with c3:
            if st.button("OK", key=f"btn_upd_{idx}"):
                client = conectar_google()
                hoja = client.open("Registro de Pedidos").sheet1
                celda = hoja.find(pedido['Fecha y Hora'])
                hoja.update_cell(celda.row, 7, nuevo_estado)
                st.rerun()
        
        with c4:
            # BOTÓN PARA BORRAR
            if st.button("🗑️", key=f"btn_del_{idx}", help="Borrar este pedido"):
                try:
                    client = conectar_google()
                    hoja = client.open("Registro de Pedidos").sheet1
                    # Buscar la fila por la estampa de tiempo única
                    celda = hoja.find(pedido['Fecha y Hora'])
                    hoja.delete_rows(celda.row)
                    st.success("Eliminado")
                    st.rerun()
                except Exception as e:
                    st.error("Error al borrar")
else:
    st.write("Sin pedidos hoy.")

st.divider()

# --- FORMULARIO DE REGISTRO ---
st.subheader("📝 Nuevo Pedido")
sector = st.text_input("📍 Sector:")
ubica = st.text_input("🗺️ Link de Ubicación:")
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
            st.success("✅ ¡Guardado!")
            st.code(f"✅ *NUEVO PEDIDO*\n---\n📦 *Prod:* {prod}\n💰 *Monto:* ${monto}\n📍 *Sector:* {sector}\n📱 *Cel:* {cel}\n🗺️ *Ubicación:* {ubica}", language="text")
        except: st.error("Error al conectar")
