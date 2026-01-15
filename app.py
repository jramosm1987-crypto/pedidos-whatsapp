import tkinter as tk
from tkinter import messagebox
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURACIÓN DE GOOGLE SHEETS ---
def guardar_en_nube(datos):
    try:
        # 1. Define el alcance y carga las credenciales
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Asegúrate de que el archivo 'credenciales.json' esté en la misma carpeta
        creds = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope)
        client = gspread.authorize(creds)
        
        # 2. Abre la hoja (Asegúrate de que el nombre coincida exactamente)
        hoja = client.open("Registro de Pedidos").sheet1 
        
        # 3. Inserta la fila
        hoja.append_row(datos)
        return True
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False

# --- FUNCIONES DEL FORMULARIO ---
def copiar_al_portapapeles():
    s = entry_sector.get()
    u = entry_ubica.get()
    c = entry_cel.get()
    m = entry_monto.get()
    p = entry_prod.get("1.0", "end-1c")
    
    if not s or not p.strip():
        messagebox.showwarning("Atención", "Por favor completa al menos Sector y Productos")
        return

    # Formato para WhatsApp
    mensaje = (
        f"✅ *NUEVO PEDIDO*\n"
        f"--------------------------\n"
        f"📦 *Productos:* {p}\n"
        f"💰 *Monto:* ${m}\n"
        f"📍 *Sector:* {s}\n"
        f"📱 *Celular:* {c}\n"
        f"🗺️ *Ubicación:* {u}\n"
        f"--------------------------"
    )
    
    root.clipboard_clear()
    root.clipboard_append(mensaje)
    root.update() 

    # --- NUEVO: GUARDAR EN LA NUBE ---
    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    datos_fila = [fecha_hora, s, u, c, m, p]
    
    exito_nube = guardar_en_nube(datos_fila)
    
    if exito_nube:
        messagebox.showinfo("¡Listo!", "Mensaje copiado y guardado en Google Sheets.")
    else:
        messagebox.showwarning("Aviso", "Mensaje copiado, pero falló el guardado en la nube.")

def limpiar_campos():
    entry_sector.delete(0, tk.END)
    entry_ubica.delete(0, tk.END)
    entry_cel.delete(0, tk.END)
    entry_monto.delete(0, tk.END)
    entry_prod.delete("1.0", tk.END)
    entry_sector.focus()

# --- INTERFAZ (Tu código original) ---
root = tk.Tk()
root.title("Generador de Pedidos Nube")
root.geometry("380x550")
root.configure(padx=20, pady=10)

lbl_style = {"font": ("Arial", 10, "bold")}

tk.Label(root, text="Sector:", **lbl_style).pack(anchor="w")
entry_sector = tk.Entry(root, width=45)
entry_sector.pack(pady=5)

tk.Label(root, text="Ubicación (Google Maps):", **lbl_style).pack(anchor="w")
entry_ubica = tk.Entry(root, width=45)
entry_ubica.pack(pady=5)

tk.Label(root, text="Celular Cliente:", **lbl_style).pack(anchor="w")
entry_cel = tk.Entry(root, width=45)
entry_cel.pack(pady=5)

tk.Label(root, text="Monto Total:", **lbl_style).pack(anchor="w")
entry_monto = tk.Entry(root, width=45)
entry_monto.pack(pady=5)

tk.Label(root, text="Productos:", **lbl_style).pack(anchor="w")
entry_prod = tk.Text(root, width=34, height=5)
entry_prod.pack(pady=5)

frame_botones = tk.Frame(root)
frame_botones.pack(pady=20)

btn_copiar = tk.Button(frame_botones, text="GENERAR Y COPIAR", 
                       command=copiar_al_portapapeles, 
                       bg="#25D366", fg="white", font=("Arial", 10, "bold"), 
                       padx=10, pady=10)
btn_copiar.pack(side="left", padx=5)

btn_limpiar = tk.Button(frame_botones, text="LIMPIAR", 
                        command=limpiar_campos, 
                        bg="#f44336", fg="white", font=("Arial", 10, "bold"), 
                        padx=10, pady=10)
btn_limpiar.pack(side="left", padx=5)

root.mainloop()
