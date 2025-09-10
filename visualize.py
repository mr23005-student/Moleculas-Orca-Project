import os
import py3Dmol
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def save_molecule_html(xyz_file, outdir="results/moleculas_3d"):
    """Genera un archivo HTML con la molécula en 3D y una captura PNG."""
    os.makedirs(outdir, exist_ok=True)
    jobname = os.path.splitext(os.path.basename(xyz_file))[0]

    # Archivos de salida
    html_file = os.path.join(outdir, f"{jobname}_3D.html")
    png_file = os.path.join(outdir, f"{jobname}_3D.png")

    # Leer coordenadas del .xyz
    with open(xyz_file) as f:
        xyz_data = f.read()

    # Generar visualización interactiva con py3Dmol
    view = py3Dmol.view(width=400, height=400)
    view.addModel(xyz_data, "xyz")
    view.setStyle({"stick": {}})
    view.zoomTo()

    # Guardar como HTML interactivo
    with open(html_file, "w") as f:
        f.write(view._make_html())

    # Intentar guardar captura PNG usando selenium
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(600, 600)
        driver.get("file://" + os.path.abspath(html_file))
        driver.save_screenshot(png_file)
        driver.quit()
    except Exception as e:
        print(f"⚠️ No se pudo generar PNG estático de la molécula: {e}")
        png_file = None

    print(f"[OK] Visualización 3D guardada en: {html_file}")
    return html_file, png_file
