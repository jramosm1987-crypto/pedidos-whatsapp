import streamlit as st

st.set_page_config(page_title="Generador de Pedidos", page_icon="🛍️")

st.title("🛍️ Generador de Pedidos")
st.write("Completa los datos y presiona el botón para copiar.")

# Campos de entrada
sector = st.text_input("Sector")
ubicacion = st.text_input("Ubicación (Google Maps)")
celular = st.text_input("Celular del Cliente")
monto = st.text_input("Monto Total")
productos = st.text_area("Productos")

# Formato del mensaje
mensaje = (
    f"✅ *NUEVO PEDIDO*\n"
    f"--------------------------\n"
    f"📦 *Productos:* {productos}\n"
    f"💰 *Monto:* ${monto}\n"
    f"📍 *Sector:* {sector}\n"
    f"📱 *Celular:* {celular}\n"
    f"🗺️ *Ubicación:* {ubicacion}\n"
    f"--------------------------"
)

st.divider()

if sector and productos:
    st.subheader("Mensaje Generado:")
    # Usamos st.code porque incluye un botón de "copiar" automático en la esquina superior derecha
    st.code(mensaje, language="markdown")
    
    st.success("Haz clic en el icono de las hojitas (arriba a la derecha del cuadro negro) para COPIAR.")
else:
    st.warning("Completa 'Sector' y 'Productos' para ver el mensaje.")
