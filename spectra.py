import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def plot_ir_spectrum(molfile, freqs, intensidades, ancho=20.0):
    """
    Genera un espectro IR simulado con picos gaussianos.
    - freqs: lista de frecuencias (cm-1)
    - intensidades: lista de intensidades relativas
    - ancho: FWHM (ancho a media altura) en cm-1 para las gaussianas
    """
    if not freqs or not intensidades:
        print("⚠️ No hay frecuencias para graficar.")
        return None

    os.makedirs("results/espectros", exist_ok=True)
    pngfile = os.path.join("results/espectros", os.path.basename(molfile).replace(".xyz", "_IR.png"))

    # Crear eje de frecuencias (x)
    x = np.linspace(400, 4000, 5000)  # rango típico IR

    # Convertir ancho FWHM a sigma
    sigma = ancho / (2 * np.sqrt(2 * np.log(2)))

    # Construir espectro con gaussianas
    y = np.zeros_like(x)
    for f, inten in zip(freqs, intensidades):
        if inten <= 0:   # ⚠️ asegurar que siempre haya algo
            inten = 1.0
        y += inten * np.exp(-(x - f)**2 / (2 * sigma**2))

    # Normalizar
    if y.max() > 0:
        y /= y.max()

    # Graficar
    plt.figure(figsize=(8, 4))
    plt.plot(x, y, color="blue")
    plt.title(f"Espectro IR simulado de {os.path.basename(molfile)}")
    plt.xlabel("Número de onda (cm⁻¹)")
    plt.ylabel("Absorbancia (a.u.)")
    plt.xlim(4000, 400)  # Escala inversa típica IR
    plt.tight_layout()
    plt.savefig(pngfile, dpi=300)
    plt.close()

    print(f"✅ Espectro IR guardado en: {pngfile}")
    return pngfile


def export_csv(molfile, freqs, intensidades):
    """Exporta frecuencias e intensidades IR a CSV."""
    os.makedirs("results/espectros", exist_ok=True)
    csvfile = os.path.join("results/espectros", os.path.basename(molfile).replace(".xyz", "_IR.csv"))

    df = pd.DataFrame({"Frecuencia (cm-1)": freqs, "Intensidad": intensidades})
    df.to_csv(csvfile, index=False)

    print(f"✅ Datos exportados a: {csvfile}")
    return csvfile
