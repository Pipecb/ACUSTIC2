import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

fs = 44100
t = np.linspace(0, 1, fs, endpoint=False)

# ------------------ CONTROL ------------------
def control(frame, text, frm, to, val):
    var = tk.DoubleVar(value=val)

    container = ttk.Frame(frame)
    container.pack(fill="x", pady=5)

    ttk.Label(container, text=text).pack(anchor="w")

    ttk.Scale(container, from_=frm, to=to, variable=var, orient="horizontal").pack(fill="x")

    ttk.Entry(container, textvariable=var).pack(fill="x")

    return var

# ------------------ SEÑAL ------------------
def señal():
    f1, f2 = freq1.get(), freq2.get()
    p1, p2 = np.deg2rad(fase1.get()), np.deg2rad(fase2.get())

    x1 = np.sin(2*np.pi*f1*t + p1)
    x2 = np.sin(2*np.pi*f2*t + p2)

    return x1, x2, x1 + x2

# ------------------ GRAFICAR ------------------
def graficar():
    x1, x2, x = señal()

    ax1.clear()
    ax2.clear()

    N = 1000
    max_val = np.max(np.abs(x))

    ax1.plot(t[:N], x[:N])

    if max_val < 1e-6:
        ax1.set_ylim(-1, 1)
        ax1.set_title("Señal (Cancelación perfecta)")
    else:
        ax1.set_ylim(-max_val*1.2, max_val*1.2)
        ax1.set_title("Señal")

    ax1.set_xlabel("Tiempo (s)")
    ax1.set_ylabel("Amplitud")
    ax1.grid()

    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1/fs)
    mag = np.abs(X)/len(x)

    ax2.plot(f, mag)
    ax2.set_xlim(0, 2000)

    if np.max(mag) > 0:
        ax2.set_ylim(0, np.max(mag)*1.2)

    ax2.set_title("FFT (Espectro de frecuencia)")
    ax2.set_xlabel("Frecuencia (Hz)")
    ax2.set_ylabel("Magnitud")
    ax2.grid()

    res = np.max(np.abs(x))
    estado.set(f"Residual: {res:.2e}")

    canvas.draw()

# ------------------ AUDIO ------------------
def play():
    _, _, x = señal()

    max_val = np.max(np.abs(x))

    if max_val < 1e-6:
        estado.set("Silencio (cancelación perfecta)")
        sd.stop()
        return

    x = x / max_val
    sd.play(x, fs)

# ------------------ CALCULOS ------------------
def calcular():
    try:
        I = float(intensidad.get())
        p = float(presion.get())
        L1 = float(n1.get())
        L2 = float(n2.get())

        LI = 10*np.log10(I/1e-12)
        Lp = 20*np.log10(p/20e-6)
        L = 10*np.log10(10**(L1/10)+10**(L2/10))

        resultado.set(f"LI: {LI:.1f} dB | Lp: {Lp:.1f} dB | LΣ: {L:.1f} dB")
    except:
        resultado.set("Error en datos")

# ------------------ PRESETS ------------------
def cancelacion():
    freq1.set(500); freq2.set(500)
    fase1.set(0); fase2.set(180)
    graficar()

def constructiva():
    freq1.set(500); freq2.set(500)
    fase1.set(0); fase2.set(0)
    graficar()

# ------------------ UI ------------------
root = tk.Tk()
root.title("Simulador de Ondas y Acústica")

main = ttk.Frame(root)
main.pack(padx=15, pady=15)

# -------- ONDAS --------
frame_ondas = ttk.LabelFrame(main, text="Parámetros de las ondas")
frame_ondas.pack(fill="x", pady=10)

freq1 = control(frame_ondas, "Frecuencia 1 (Hz)", 0, 1000, 440)
freq2 = control(frame_ondas, "Frecuencia 2 (Hz)", 0, 1000, 450)
fase1 = control(frame_ondas, "Fase 1 (°)", 0, 360, 0)
fase2 = control(frame_ondas, "Fase 2 (°)", 0, 360, 0)

frame_btns = ttk.Frame(frame_ondas)
frame_btns.pack(pady=10, fill="x")

ttk.Button(frame_btns, text="Graficar", command=graficar).pack(fill="x", pady=2)
ttk.Button(frame_btns, text="Reproducir", command=play).pack(fill="x", pady=2)
ttk.Button(frame_btns, text="Cancelación destructiva", command=cancelacion).pack(fill="x", pady=2)
ttk.Button(frame_btns, text="Interferencia constructiva", command=constructiva).pack(fill="x", pady=2)

# -------- ACÚSTICA --------
frame_acustica = ttk.LabelFrame(main, text="Cálculos acústicos")
frame_acustica.pack(fill="x", pady=10)

ttk.Label(frame_acustica, text="Intensidad (W/m²)").pack()
intensidad = ttk.Entry(frame_acustica)
intensidad.pack(pady=2)

ttk.Label(frame_acustica, text="Presión sonora (Pa)").pack()
presion = ttk.Entry(frame_acustica)
presion.pack(pady=2)

ttk.Label(frame_acustica, text="Nivel 1 (dB)").pack()
n1 = ttk.Entry(frame_acustica)
n1.pack(pady=2)

ttk.Label(frame_acustica, text="Nivel 2 (dB)").pack()
n2 = ttk.Entry(frame_acustica)
n2.pack(pady=2)

ttk.Button(frame_acustica, text="Calcular parámetros acústicos", command=calcular).pack(pady=8)

resultado = tk.StringVar()
ttk.Label(frame_acustica, textvariable=resultado, foreground="blue").pack()

# -------- ESTADO --------
estado = tk.StringVar()
ttk.Label(main, textvariable=estado).pack(pady=5)

# -------- GRÁFICAS --------
frame_graf = ttk.LabelFrame(main, text="Visualización de señales")
frame_graf.pack(fill="both", expand=True, pady=10)

fig, (ax1, ax2) = plt.subplots(2,1, figsize=(6,5))
canvas = FigureCanvasTkAgg(fig, master=frame_graf)
canvas.get_tk_widget().pack(fill="both", expand=True)

root.mainloop()