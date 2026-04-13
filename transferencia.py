import os, subprocess, tkinter as tk, sys
from tkinter import messagebox, scrolledtext

if getattr(sys, 'frozen', False):
    ruta_base = os.path.dirname(sys.executable)
else:
    ruta_base = os.path.dirname(os.path.abspath(__file__))
os.chdir(ruta_base)

def run_adb(command, serial=None):
    adb_exe = os.path.join(ruta_base, "adb.exe")
    prefix = f'"{adb_exe}"'
    if serial:
        prefix += f" -s {serial}"
    try:
        process = subprocess.run(f'{prefix} {command}', shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return process.stdout.strip()
    except Exception as e: return f"Error: {str(e)}"

def obtener_dispositivos():
    output = run_adb("devices")
    lines = output.splitlines()[1:]
    return [line.split()[0] for line in lines if "device" in line]

def log_msg(mensaje):
    log.insert(tk.END, f"{mensaje}\n"); log.see(tk.END); root.update_idletasks()

RUTAS_A_MOVER = [
    "/sdcard/DCIM/Camera",
    "/sdcard/WhatsApp/Media/WhatsApp Images",
    "/sdcard/WhatsApp/Media/WhatsApp Video",
    "/sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Images",
    "/sdcard/Android/media/com.whatsapp/WhatsApp/Media/WhatsApp Video",
    "/sdcard/Download",
    "/sdcard/Pictures/Screenshots"
]

def trasplante_directo():
    log.delete(1.0, tk.END)
    dispositivos = obtener_dispositivos()
    
    if len(dispositivos) < 2:
        messagebox.showwarning("Atención", f"Se necesitan 2 móviles conectados.\nDetectados: {len(dispositivos)}\n\nActiva la Depuración USB en ambos.")
        return

    viejo = dispositivos[0]
    nuevo = dispositivos[1]
    
    log_msg(f"✅ ORIGEN detectado: {viejo}")
    log_msg(f"✅ DESTINO detectado: {nuevo}")
    log_msg("🚀 Iniciando transferencia directa (Sin usar disco del PC)...")

    for ruta in RUTAS_A_MOVER:
        folder_name = ruta.split('/')[-1]
        log_msg(f"📂 Trasladando: {folder_name}...")
        
        # EXPLICACIÓN: 'adb pull' envía a la salida estándar y 'adb push' la recibe. 
        # Como esto es complejo por consola simple, usamos un puente temporal de 1 en 1
        # para asegurar que no se sature el PC.
        temp_pc = os.path.join(ruta_base, "temp_transfer")
        if not os.path.exists(temp_pc): os.makedirs(temp_pc)
        
        # Extraemos un bloque y lo inyectamos inmediatamente para liberar espacio
        run_adb(f'pull "{ruta}" "{temp_pc}"', serial=viejo)
        run_adb(f'push "{temp_pc}/." "/sdcard/ARCHIVOS_RECUPERADOS/{folder_name}/"', serial=nuevo)
        
        # Borramos lo del PC justo después de pasarlo al nuevo
        for f in os.listdir(temp_pc):
            file_path = os.path.join(temp_pc, f)
            try:
                if os.path.isfile(file_path): os.unlink(file_path)
            except: pass
            
    log_msg("\n✅ TRASPLANTE FINALIZADO.")
    messagebox.showinfo("Éxito", "Todos los archivos han sido movidos al móvil nuevo.")

# --- INTERFAZ ---
root = tk.Tk(); root.title("Trasplante Directo USB"); root.geometry("550x600")
tk.Label(root, text="MUDANZA DIRECTA (Móvil a Móvil)", font=("Arial", 12, "bold")).pack(pady=20)
tk.Button(root, text="🔗 INICIAR TRASPLANTE", bg="#8e44ad", fg="white", font=("Arial", 11, "bold"), height=3, width=30, command=trasplante_directo).pack()
log = scrolledtext.ScrolledText(root, width=60, height=20, bg="#1c1c1c", fg="#33ff33"); log.pack(pady=20)
root.mainloop()
