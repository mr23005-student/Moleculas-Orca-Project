# spectra.py
import os
import matplotlib.pyplot as plt
import numpy as np
from parser_orca import process_ir_data
import pandas as pd

def plot_ir_spectrum(molfile, freqs, intensidades):
    """Genera un espectro IR profesional y lo guarda como PNG."""
    os.makedirs("results/espectros", exist_ok=True)
    pngfile = os.path.join(
        "results/espectros",
        os.path.basename(molfile).replace(".xyz", "_IR.png")
    )

    # Procesar datos
    x_values, y_values, peaks = process_ir_data(freqs, intensidades)
    
    # Crear figura con estilo profesional
    plt.figure(figsize=(12, 6))
    
    # Graficar espectro principal
    plt.plot(x_values, y_values, color='darkblue', linewidth=1.5)
    
    # Añadir líneas verticales para los picos principales
    for freq, inten in peaks:
        if inten > 0.1:  # Solo mostrar picos significativos
            plt.vlines(freq, 0, inten, colors='gray', linestyles=':', alpha=0.5)
            # Añadir etiqueta de frecuencia
            plt.text(freq, inten+0.02, f'{int(freq)}', 
                    rotation=90, ha='center', va='bottom', fontsize=8)
    
    # Configurar apariencia
    plt.title(f"Espectro IR - {os.path.basename(molfile)}", pad=20)
    plt.xlabel("Número de onda (cm⁻¹)")
    plt.ylabel("Transmitancia")
    
    # Ajustar ejes y grid
    plt.grid(True, linestyle=':', alpha=0.3)
    plt.xlim(4000, 400)  # Invertir eje x (convención IR)
    plt.ylim(-0.05, 1.1)
    
    # Invertir eje y para mostrar picos hacia abajo
    plt.gca().invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(pngfile, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✅ Espectro IR guardado en: {pngfile}")
    return pngfile


def export_csv(molfile, freqs, intensidades):
    """Exporta frecuencias e intensidades IR a CSV."""
    os.makedirs("results/espectros", exist_ok=True)
    csvfile = os.path.join(
        "results/espectros",
        os.path.basename(molfile).replace(".xyz", "_IR.csv")
    )

    # Si todas las intensidades son 0 → asignar 1.0
    if not intensidades or all(i == 0.0 for i in intensidades):
        intensidades = [1.0] * len(freqs)

    df = pd.DataFrame({"Frecuencia (cm-1)": freqs, "Intensidad": intensidades})
    df.to_csv(csvfile, index=False)

    print(f"✅ Datos exportados a: {csvfile}")
    return csvfile
