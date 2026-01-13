import streamlit as st
import urllib.parse

st.set_page_config(page_title="Generador de Pedidos", page_icon="🛍️")

st.title("🛍️ Generador de Pedidos")
st.write("Completa los datos y copia el mensaje para WhatsApp.")

# Campos de entrada en la web
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

if st.button("Generar Mensaje"):
    if sector and productos:
        # Mostrar el mensaje en un cuadro para copiar
        st.text_area("Copia el texto de abajo:", mensaje, height=200)
        st.success("¡Mensaje generado! Selecciónalo y cópialo.")
    else:
        st.error("Por favor llena los campos obligatorios (Sector y Productos).")