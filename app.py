import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Generador de Pedidos Comonli", page_icon="📦")

# Función para conectar con Google Sheets
def conectar_google():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_info = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
    return gspread.authorize(creds)

def obtener_total_pedidos():
    try:
        client = conectar_google()
        hoja = client.open("Registro de Pedidos").sheet1
        # Cuenta filas y resta el encabezado
        return len(hoja.get_all_values()) - 1
    except:
        return 0

def guardar_en_nube(datos):
    try:
        client = conectar_google()
        hoja = client.open("Registro de Pedidos").sheet1 
        hoja.append_row(datos)
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# --- INTERFAZ ---
st.title("📋 Gestión de Pedidos")

# Mostrar Contador
total = obtener_total_pedidos()
st.metric(label="Pedidos Totales Registrados", value=total)
st.divider()

# Formulario
sector = st.text_input("📍 Sector:")
ubica = st.text_input("🗺️ Ubicación (Google Maps):")
cel = st.text_input("📱 Celular Cliente:")
monto = st.text_input("💰 Monto Total ($):")
prod = st.text_area("📦 Productos:")

if st.button("GENERAR Y GUARDAR"):
    if sector and prod:
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        datos_fila = [fecha_hora, sector, ubica, cel, monto, prod]
        
        if guardar_en_nube(datos_fila):
            st.success("✅ Pedido guardado. ¡El contador se actualizará al recargar!")
            mensaje_wa = f"✅ *NUEVO PEDIDO*\n---\n📦 *Prod:* {prod}\n💰 *Monto:* ${monto}\n📍 *Sector:* {sector}\n📱 *Cel:* {cel}\n🗺️ *Ubicación:* {ubica}"
            st.code(mensaje_wa, language="text")
            # Botón para refrescar y ver el nuevo número
            if st.button("Actualizar Contador"):
                st.rerun()
    else:
        st.warning("Completa los campos obligatorios.")


