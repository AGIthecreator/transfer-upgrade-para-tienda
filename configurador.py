import os, subprocess, tkinter as tk, sys
from tkinter import messagebox, scrolledtext, simpledialog

# --- CONFIGURACIÓN DE RUTAS PARA EL EXE ---
if getattr(sys, 'frozen', False):
    ruta_base = os.path.dirname(sys.executable)
else:
    ruta_base = os.path.dirname(os.path.abspath(__file__))
os.chdir(ruta_base)

def run_adb(command):
    try:
        # Busca el adb.exe que empaquetamos o que está en la carpeta
        adb_exe = os.path.join(ruta_base, "adb.exe")
        process = subprocess.run(f'"{adb_exe}" {command}', shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return process.stdout.strip()
    except Exception as e: return f"Error: {str(e)}"

def log_msg(mensaje):
    log.insert(tk.END, f"{mensaje}\n"); log.see(tk.END); root.update_idletasks()

# --- FILTRO ANTIBASURA (Marcas, Operadoras y Juegos) ---
BASURA_KEYWORDS = [
    "facebook", "instagram", "tiktok", "booking", "netflix", "ebay", "linkedin",
    "samsung.android.bixby", "miui.analytics", "miui.msa", "motorola.moto",
    "vodafone", "orange", "movistar", "telefonica", "tmobile",
    "king.candycrush", "playtika", "gameloft", "zynga", "rovio", "playrix", "minigame"
]

def elegir_audio_remoto(titulo):
    log_msg(f"🔎 Buscando audios en el móvil para {titulo}...")
    res = run_adb("shell \"find /sdcard/ -type f \( -name '*.mp3' -o -name '*.m4a' \) 2>/dev/null\"")
    lista_audios = [line.strip() for line in res.split('\n') if line.strip()]
    
    if not lista_audios:
        log_msg("❌ No se encontraron audios clonados.")
        return None

    win = tk.Toplevel(root); win.title(titulo); win.geometry("500x450"); win.grab_set()
    tk.Label(win, text=f"Selecciona audio para {titulo}:", font=("Arial", 10, "bold")).pack(pady=10)
    
    # Scrollbar para la lista
    frame = tk.Frame(win); frame.pack(pady=5, padx=10, fill="both", expand=True)
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    lb = tk.Listbox(frame, width=70, yscrollcommand=scrollbar.set); lb.pack(side=tk.LEFT, fill="both", expand=True)
    scrollbar.config(command=lb.yview)
    
    for a in lista_audios: lb.insert(tk.END, a)
    
    seleccion = {"path": None}
    def confirmar():
        if lb.curselection():
            seleccion["path"] = lb.get(lb.curselection())
            win.destroy()

    tk.Button(win, text="CONFIRMAR SELECCIÓN", command=confirmar, bg="#27ae60", fg="white", height=2).pack(pady=10)
    win.wait_window()
    return seleccion["path"]

def puesta_a_punto():
    log.delete(1.0, tk.END)
    dispositivos = run_adb("devices")
    if "device" not in dispositivos or dispositivos.strip() == "List of devices attached":
        messagebox.showerror("Error", "Móvil no detectado. Revisa la Depuración USB."); return

    # 1. LIMPIEZA DE BASURA
    log_msg("🧹 Iniciando limpieza de Bloatware y Juegos...")
    apps = run_adb("shell pm list packages").replace("package:", "").split()
    for app in apps:
        if any(key in app.lower() for key in BASURA_KEYWORDS):
            run_adb(f"shell pm uninstall -k --user 0 {app}")
            log_msg(f"   🗑️ Eliminado: {app}")

    # 2. RENDIMIENTO
    run_adb("shell settings put global window_animation_scale 0.5")
    run_adb("shell settings put global transition_animation_scale 0.5")
    run_adb("shell settings put global animator_duration_scale 0.5")
    log_msg("⚡ Interfaz acelerada (0.5x).")

    # 3. AJUSTES DE PANTALLA
    seg = simpledialog.askinteger("Ajustes", "¿Segundos para apagado de pantalla?", initialvalue=120)
    if seg: run_adb(f"shell settings put system screen_off_timeout {seg * 1000}")

    # 4. CONFIGURACIÓN DE AUDIOS
    if messagebox.askyesno("Sonidos", "¿Configurar Tonos desde los archivos clonados?"):
        path_llamada = elegir_audio_remoto("LLAMADA")
        if path_llamada:
            run_adb(f'shell settings put system ringtone "file://{path_llamada}"')
            log_msg(f"✅ Tono de llamada fijado.")
        
        path_alarma = elegir_audio_remoto("ALARMA")
        if path_alarma:
            run_adb(f'shell settings put system alarm_alert "file://{path_alarma}"')
            log_msg(f"✅ Tono de alarma fijado.")

    log_msg("\n✨ CONFIGURACIÓN FINALIZADA CON ÉXITO.")
    messagebox.showinfo("Listo", "El móvil ha sido optimizado.")

# --- INTERFAZ PRINCIPAL ---
root = tk.Tk(); root.title("Configurador Premium v3.1"); root.geometry("550x650")
tk.Label(root, text="WORKSTATION DE OPTIMIZACIÓN", font=("Arial", 14, "bold")).pack(pady=20)

btn = tk.Button(root, text="🚀 INICIAR PUESTA A PUNTO", bg="#2980b9", fg="white", font=("Arial", 11, "bold"), height=3, width=35, command=puesta_a_punto)
btn.pack(pady=10)

log = scrolledtext.ScrolledText(root, width=60, height=20, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
log.pack(pady=20)

root.mainloop()
