import os
import argparse
import subprocess
from parser_orca import parse_ir, parse_energy_total
from spectra import plot_ir_spectrum, export_csv, plot_ir_variants
from visualize import save_molecule_html
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import datetime
#esta es la rama raman jaja
# Ruta del ejecutable de ORCA
ORCA_BIN = "/usr/bin/orca"


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
    """
    Genera un PDF con energía, lista de frecuencias (multipágina si es necesario),
    espectro IR y captura de la molécula 3D.
    Devuelve la ruta al PDF generado.
    """
    os.makedirs("results/reportes", exist_ok=True)
    jobname = os.path.basename(molfile).replace(".xyz", "")
    pdf_file = os.path.join("results/reportes", f"{jobname}_IR.pdf")

    width, height = letter
    c = canvas.Canvas(pdf_file, pagesize=letter)

    def draw_header():
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, height - 2*cm, f"Reporte ORCA: {jobname}")
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, height - 2.6*cm,
                     f"Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.setFont("Helvetica", 12)

    # Página inicial y encabezado
    draw_header()
    y = height - 4*cm

    # Energía
    if energia is not None:
        try:
            c.drawString(2*cm, y, f"Energía total: {energia:.6f} Eh")
        except Exception:
            c.drawString(2*cm, y, f"Energía total: {energia}")
    else:
        c.drawString(2*cm, y, "[ADVERTENCIA] Energía no encontrada")
    y -= 0.8*cm

    # Número de frecuencias
    total_freqs = len(freqs) if freqs else 0
    c.drawString(2*cm, y, f"Número de frecuencias vibracionales: {total_freqs}")
    y -= 0.6*cm

    # Listado de frecuencias (toda la lista, multipágina)
    c.setFont("Helvetica", 10)
    if freqs:
        for i, (f, inten) in enumerate(zip(freqs, intensidades), start=1):
            line = f"{i:03d}. {f:.2f} cm-1    Intensidad: {inten:.2f}"
            c.drawString(2*cm, y, line)
            y -= 0.5*cm
            # Si nos acercamos al pie de página, crear nueva página y repetir encabezado
            if y < 4*cm:
                c.showPage()
                draw_header()
                y = height - 4*cm
    else:
        c.drawString(2*cm, y, "No se encontraron frecuencias")
        y -= 0.5*cm

    # Insertar espectro IR (en página propia para mejor layout)
    if png_file and os.path.exists(png_file):
        try:
            c.showPage()
            draw_header()
            # Ajustar imagen al ancho con márgenes
            img_w = width - 4*cm
            # altura proporcional (ajusta factor si quieres otra relación)
            img_h = img_w * 0.6
            img_x = 2*cm
            img_y = (height - img_h) / 2
            c.drawImage(png_file, img_x, img_y, width=img_w, height=img_h, preserveAspectRatio=True)
        except Exception as e:
            print(f"[WARN] No se pudo insertar espectro en PDF: {e}")

    # Insertar imagen de la molécula (en página propia)
    if mol_png and os.path.exists(mol_png):
        try:
            c.showPage()
            draw_header()
            img_w = width - 4*cm
            img_h = img_w * 0.75
            img_x = 2*cm
            img_y = (height - img_h) / 2
            c.drawImage(mol_png, img_x, img_y, width=img_w, height=img_h, preserveAspectRatio=True)
        except Exception as e:
            print(f"[WARN] No se pudo insertar imagen de la molécula en PDF: {e}")

    # Guardar y reportar ruta
    c.save()
    print(f"[OK] Reporte generado: {pdf_file}")
    # Imprimimos una línea con etiqueta para que app.py pueda capturarla fácilmente
    print(f"[PDF] {pdf_file}")
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


    png_files = plot_ir_variants(molfile, freqs, intensidades) if args.csv or args.pdf else None
    png_file = png_files[2] if png_files else None  # Usar el espectro etiquetado para el PDF

    csv_file = export_csv(molfile, freqs, intensidades) if args.csv else None
    html_file, mol_png = save_molecule_html(molfile) if args.view else (None, None)

    if args.pdf:
        generar_reporte_pdf(molfile, energia, freqs, intensidades, png_file, mol_png)

    print(f"[OK] Resultados guardados en {base_dir} y results/")

