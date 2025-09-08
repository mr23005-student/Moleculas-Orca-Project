import os
import py3Dmol

def save_molecule_html(xyz_file):
    """Genera una visualización 3D de la molécula en formato HTML."""
    os.makedirs("results/moleculas_3d", exist_ok=True)
    htmlfile = os.path.join("results/moleculas_3d", os.path.basename(xyz_file).replace(".xyz", "_3D.html"))

    with open(xyz_file) as f:
        xyz_data = f.read()

    view = py3Dmol.view(width=400, height=400)
    view.addModel(xyz_data, "xyz")
    view.setStyle({"stick": {}})
    view.zoomTo()
    view.render()
    with open(htmlfile, "w") as f:
        f.write(view._make_html())

    print(f"✅ Visualización 3D guardada en: {htmlfile}")
    return htmlfile

