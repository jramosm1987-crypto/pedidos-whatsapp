import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="Generador de Pedidos Comonli", page_icon="📦")

# Estilos CSS para mejorar la apariencia
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #25D366;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Función para conectar y guardar en Google Sheets
def guardar_en_nube(datos):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Obtiene credenciales desde Secrets de Streamlit
        creds_info = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        client = gspread.authorize(creds)
        
        # Abre la hoja por nombre
        hoja = client.open("Registro de Pedidos").sheet1 
        hoja.append_row(datos)
        return True
    except Exception as e:
        st.error(f"Error de conexión con Google Sheets: {e}")
        return False

# Título de la App
st.title("📋 Nuevo Pedido")

# Formulario
with st.container():
    sector = st.text_input("📍 Sector:")
    ubica = st.text_input("🗺️ Ubicación (Google Maps):")
    cel = st.text_input("📱 Celular Cliente:")
    monto = st.text_input("💰 Monto Total ($):")
    prod = st.text_area("📦 Productos:", height=150)

# Botón de acción
if st.button("GENERAR Y GUARDAR"):
    if not sector or not prod.strip():
        st.warning("⚠️ Por favor completa al menos Sector y Productos.")
    else:
        # Preparar datos para la nube
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        datos_fila = [fecha_hora, sector, ubica, cel, monto, prod]
        
        # Intentar guardar
        exito = guardar_en_nube(datos_fila)
        
        if exito:
            st.success("✅ Pedido registrado en la nube correctamente.")
            
            # Crear formato para WhatsApp
            mensaje_wa = (
                f"✅ *NUEVO PEDIDO*\n"
                f"--------------------------\n"
                f"📦 *Productos:* {prod}\n"
                f"💰 *Monto:* ${monto}\n"
                f"📍 *Sector:* {sector}\n"
                f"📱 *Celular:* {cel}\n"
                f"🗺️ *Ubicación:* {ubica}\n"
                f"--------------------------"
            )
            
            st.write("### Copia el mensaje para WhatsApp:")
            st.code(mensaje_wa, language="text")
        else:
            st.error("❌ El pedido no se pudo guardar en la nube. Revisa los Secrets.")

# Instrucciones al final
st.info("Recuerda que para guardar, la hoja de Google debe estar compartida con el email del robot.")
