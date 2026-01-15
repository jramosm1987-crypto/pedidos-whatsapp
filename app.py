import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Generador de Pedidos", page_icon="🛍️")

# Función para guardar en Google Sheets
def guardar_en_nube(datos):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # En Streamlit, las credenciales se manejan como "Secrets" por seguridad
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        hoja = client.open("Registro de Pedidos").sheet1 
        hoja.append_row(datos)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

st.title("🛍️ Generador de Pedidos")
st.write("Completa los datos y presiona el botón para guardar y copiar.")

# Campos de entrada
sector = st.text_input("Sector")
ubica = st.text_input("Ubicación (Google Maps)")
cel = st.text_input("Celular del Cliente")
monto = st.text_input("Monto Total")
prod = st.text_area("Productos")

if st.button("GENERAR Y GUARDAR"):
    if sector and prod:
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        datos_fila = [fecha_hora, sector, ubica, cel, monto, prod]
        
        if guardar_en_nube(datos_fila):
            st.success("✅ ¡Pedido guardado en Google Sheets!")
            
            # Formato para copiar
            mensaje = f"✅ *NUEVO PEDIDO*\n---\n📦 *Productos:* {prod}\n💰 *Monto:* ${monto}\n📍 *Sector:* {sector}\n📱 *Cel:* {cel}\n🗺️ *Ubicación:* {ubica}"
            st.code(mensaje, language="text")
            st.info("Copia el texto del cuadro de arriba para WhatsApp.")
    else:
        st.warning("Por favor completa Sector y Productos.")

