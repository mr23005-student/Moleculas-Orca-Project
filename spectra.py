# spectra.py
import os
import matplotlib.pyplot as plt
import pandas as pd

def plot_ir_spectrum(molfile, freqs, intensidades):
    """Genera un espectro IR y lo guarda como PNG.
    Si no hay intensidades, usa 1.0 para mostrar picos.
    """
    os.makedirs("results/espectros", exist_ok=True)
    pngfile = os.path.join(
        "results/espectros",
        os.path.basename(molfile).replace(".xyz", "_IR.png")
    )

    # Si todas las intensidades son 0 → asignar 1.0
    if not intensidades or all(i == 0.0 for i in intensidades):
        intensidades = [1.0] * len(freqs)

    plt.figure(figsize=(6, 4))
    plt.plot(freqs, intensidades, color="blue")
    plt.title(f"Espectro IR de {os.path.basename(molfile)}")
    plt.xlabel("Frecuencia (cm⁻¹)")
    plt.ylabel("Intensidad (KM/mol o normalizada)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(pngfile, dpi=300)
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
