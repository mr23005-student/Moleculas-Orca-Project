import os
import argparse
import subprocess
from parser_orca import parse_ir, parse_energy_total
from spectra import plot_ir_spectrum, export_csv
from visualize import save_molecule_html
from reportlab.pdfgen import canvas

# Ruta del ejecutable de ORCA
ORCA_BIN = r"C:\Orca\orca.exe"

def generar_inp(xyz_file, job="optfreq", output_dir="inputs"):
    """Genera un archivo .inp de ORCA a partir de un .xyz."""
    with open(xyz_file) as f:
        lines = f.readlines()
    coords = "".join(lines[2:])

    inp_text = f"""! B3LYP def2-SVP Opt Freq TightSCF

* xyz 0 1
{coords}*
"""
    os.makedirs(output_dir, exist_ok=True)
    inpfile = os.path.join(output_dir, os.path.basename(xyz_file).replace(".xyz", ".inp"))
    with open(inpfile, "w") as f:
        f.write(inp_text)
    return inpfile


def ejecutar_orca(inpfile, intermediates_dir="outputs"):
    """Ejecuta ORCA con un .inp y guarda la salida en outputs/."""
    os.makedirs(intermediates_dir, exist_ok=True)
    outfile = os.path.join(intermediates_dir, os.path.basename(inpfile).replace(".inp", ".out"))
    with open(outfile, "w") as f:
        subprocess.run([ORCA_BIN, inpfile], stdout=f, stderr=subprocess.STDOUT)
    return outfile


def generar_reporte_pdf(molfile, energia, freqs, intensidades, png_file=None, mol_png=None):
    """Genera un PDF con energía, frecuencias IR, espectro y molécula 3D."""
    os.makedirs("results/reportes", exist_ok=True)
    pdf_file = os.path.join(
        "results/reportes", os.path.basename(molfile).replace(".xyz", "_IR.pdf")
    )

    c = canvas.Canvas(pdf_file)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 800, f"Reporte ORCA: {os.path.basename(molfile)}")

    c.setFont("Helvetica", 12)
    if energia:
        c.drawString(100, 770, f"Energía total: {energia:.6f} Eh")
    else:
        c.drawString(100, 770, "[ADVERTENCIA] Energía no encontrada")

    c.drawString(100, 750, f"Número de frecuencias vibracionales: {len(freqs)}")

    # Listar primeras frecuencias
    for i, (frec, inten) in enumerate(zip(freqs[:10], intensidades[:10])):
        c.drawString(120, 730 - i * 20, f"{frec:.2f} cm-1 (Intensidad: {inten:.2f})")

    # 🔹 Insertar espectro IR
    if png_file and os.path.exists(png_file):
        c.drawImage(png_file, 100, 400, width=400, height=300)

    # 🔹 Insertar molécula 3D (captura PNG generada en visualize.py)
    if mol_png and os.path.exists(mol_png):
        c.drawImage(mol_png, 100, 100, width=300, height=250)

    c.save()
    print(f"[OK] Reporte generado: {pdf_file}")
    return pdf_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mol", required=True, help="Archivo .xyz de entrada")
    parser.add_argument("--pdf", action="store_true", help="Generar reporte PDF")
    parser.add_argument("--csv", action="store_true", help="Exportar espectro a CSV")
    parser.add_argument("--view", action="store_true", help="Generar visualización 3D")
    parser.add_argument("--job", default="optfreq", help="Tipo de cálculo ORCA")
    parser.add_argument("--outdir", default="runs", help="Directorio base para resultados")
    args = parser.parse_args()

    molfile = args.mol
    jobname = os.path.splitext(os.path.basename(molfile))[0]

    # Crear carpetas organizadas
    base_dir = os.path.join(args.outdir, jobname)
    inputs_dir = os.path.join(base_dir, "inputs")
    outputs_dir = os.path.join(base_dir, "outputs")

    inpfile = generar_inp(molfile, args.job, inputs_dir)
    outfile = ejecutar_orca(inpfile, outputs_dir)

    freqs, intensidades = parse_ir(outfile)
    energia = parse_energy_total(outfile)

    print(f"[OK] Energía total: {energia if energia else 'No encontrada'}")
    print(f"[OK] Se encontraron {len(freqs)} frecuencias vibracionales")


    png_file = plot_ir_spectrum(molfile, freqs, intensidades) if args.csv or args.pdf else None
    csv_file = export_csv(molfile, freqs, intensidades) if args.csv else None
    html_file, mol_png = save_molecule_html(molfile) if args.view else (None, None)

    if args.pdf:
        generar_reporte_pdf(molfile, energia, freqs, intensidades, png_file, mol_png)

    print(f"[OK] Resultados guardados en {base_dir} y results/")

