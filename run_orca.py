import os
import argparse
import subprocess
from parser_orca import parse_ir, parse_energy_total
from spectra import plot_ir_spectrum, export_csv
from visualize import save_molecule_html
from reportlab.pdfgen import canvas

# 🔹 Ruta del ejecutable ORCA (ajústala si está en otro sitio)
ORCA_BIN = "/home/jonathan/orca-6.1.0-f.0_linux_x86-64/bin/orca"


def generar_inp(xyz_file, job="optfreq"):
    """Genera un archivo .inp de ORCA dentro de la carpeta de la molécula."""
    molname = os.path.splitext(os.path.basename(xyz_file))[0]
    mol_dir = os.path.join("runs", molname)
    inputs_dir = os.path.join(mol_dir, "inputs")
    os.makedirs(inputs_dir, exist_ok=True)

    with open(xyz_file) as f:
        lines = f.readlines()

    # Filtrar solo coordenadas válidas (evitar líneas vacías o basura)
    coords = "".join([line for line in lines[2:] if line.strip()])

    inp_text = f"""! B3LYP def2-SVP Opt Freq TightSCF

* xyz 0 1
{coords}*
"""

    inpfile = os.path.join(inputs_dir, f"{molname}.inp")
    with open(inpfile, "w") as f:
        f.write(inp_text)

    return inpfile, molname, mol_dir


def ejecutar_orca(inpfile, mol_dir, molname):
    """Ejecuta ORCA dentro de la carpeta de la molécula."""
    outputs_dir = os.path.join(mol_dir, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    outfile = os.path.join(outputs_dir, f"{molname}.out")

    # Guardar todos los archivos auxiliares que ORCA genere en intermediates/
    intermediates_dir = os.path.join(mol_dir, "intermediates")
    os.makedirs(intermediates_dir, exist_ok=True)

    with open(outfile, "w") as f:
        subprocess.run(
            [ORCA_BIN, os.path.abspath(inpfile)],
            cwd=intermediates_dir,
            stdout=f,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True
        )

    return outfile



def generar_reporte_pdf(molfile, energia, freqs, intensidades):
    """Genera un PDF con energía, frecuencias e imagen del espectro IR."""
    os.makedirs("results/reportes", exist_ok=True)
    pdf_file = os.path.join(
        "results/reportes",
        os.path.basename(molfile).replace(".xyz", "_IR.pdf")
    )

    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm

    c = canvas.Canvas(pdf_file)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 800, f"Reporte de {os.path.basename(molfile)}")
    c.setFont("Helvetica", 12)

    if energia is not None:
        c.drawString(100, 770, f"Energía total (Eh): {energia:.6f}")
    else:
        c.drawString(100, 770, "Energía total: no encontrada")

    c.drawString(100, 750, "Frecuencias IR (cm⁻1) e Intensidades:")
    for i, (frec, inten) in enumerate(zip(freqs[:10], intensidades[:10])):
        c.drawString(120, 730 - i*20, f"{frec:.2f} cm⁻1  ({inten:.2f})")

    # Insertar espectro IR como imagen
    pngfile = os.path.join(
        "results/espectros",
        os.path.basename(molfile).replace(".xyz", "_IR.png")
    )
    if os.path.exists(pngfile):
        c.drawImage(pngfile, 2*cm, 2*cm, width=16*cm, height=8*cm)
    else:
        c.drawString(100, 200, "⚠️ No se encontró la imagen del espectro IR.")

    c.save()
    print(f"✅ Reporte generado: {pdf_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mol", required=True, help="Archivo .xyz de entrada")
    parser.add_argument("--pdf", action="store_true", help="Generar reporte PDF")
    parser.add_argument("--csv", action="store_true", help="Exportar espectro a CSV")
    parser.add_argument("--view", action="store_true", help="Generar visualización 3D")
    parser.add_argument("--job", default="optfreq", help="Tipo de cálculo ORCA")
    args = parser.parse_args()

    molfile = args.mol
    inpfile, molname, mol_dir = generar_inp(molfile, args.job)
    outfile = ejecutar_orca(inpfile, mol_dir, molname)

    freqs, intensidades = parse_ir(outfile)
    energia = parse_energy_total(outfile)

    if energia is not None:
        print(f"✅ Energía total (Eh): {energia:.6f}")
    else:
        print("⚠️ Energía total no encontrada en el archivo de salida")

    print(f"✅ Se encontraron {len(freqs)} frecuencias vibracionales")

    # 🔹 Generar siempre PNG si hay frecuencias
    if freqs and intensidades:
        plot_ir_spectrum(molfile, freqs, intensidades)

    if args.pdf:
        generar_reporte_pdf(molfile, energia, freqs, intensidades)

    if args.csv:
        export_csv(molfile, freqs, intensidades)

    if args.view:
        save_molecule_html(molfile)

    print(f"✅ Resultados guardados en runs/{molname}/ y results/")
    print("¡Proceso completado!")