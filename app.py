import streamlit as st

st.set_page_config(page_title="Generador de Pedidos", page_icon="🛍️")

st.title("🛍️ Generador de Pedidos")
st.write("Completa los datos y usa el botón para copiar el mensaje.")

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
    # Mostramos el mensaje para previsualizar
    st.text(mensaje)
    
    # NUEVO: Botón que copia directo al portapapeles
    st.copy_to_clipboard(mensaje, before_copy_label="📋 COPIAR MENSAJE", after_copy_label="✅ ¡COPIADO!")
    
    st.info("Una vez copiado, ve a WhatsApp y dale a 'Pegar'.")
else:
    st.warning("Completa 'Sector' y 'Productos' para generar el botón de copia.")
