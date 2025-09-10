import os
import streamlit as st
import subprocess
import tempfile
import py3Dmol
import streamlit.components.v1 as components

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

# Disable usage stats and set up configuration
st.config.set_option("browser.gatherUsageStats", False)
st.set_page_config(
    page_title="Moleculas ORCA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure directories exist
for dir_path in ["results/reportes", "results/espectros", "results/moleculas_3d"]:
    os.makedirs(dir_path, exist_ok=True)

# Directorio base del proyecto
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RUN_ORCA = os.path.join(PROJECT_DIR, "run_orca.py")

@st.cache_resource
def init_session():
    if not st.session_state.initialized:
        st.session_state.initialized = True
    return True

# Initialize session
init_session()

st.title("🔬 Generador de cálculos ORCA")
st.markdown("Sube una molécula `.xyz` y genera automáticamente:")
st.markdown("- ✅ Energía total")
st.markdown("- ✅ Espectro IR (PNG + CSV)")
st.markdown("- ✅ Visualización 3D interactiva")
st.markdown("- ✅ Reporte en PDF")

# Función para mostrar molécula en 3D
@st.cache_resource
def mostrar_molecula_3d(xyz_file):
    try:
        with open(xyz_file) as f:
            xyz_data = f.read()

        view = py3Dmol.view(width=500, height=400)
        view.addModel(xyz_data, "xyz")
        view.setStyle({"stick": {}})
        view.zoomTo()

        html = view._make_html()
        components.html(html, height=500, width=600)
    except Exception as e:
        st.error(f"Error al visualizar molécula: {str(e)}")

# Subir molécula con manejo de errores
try:
    molfile = st.file_uploader("Sube un archivo .xyz de la molécula", type=["xyz"], key="mol_upload")

    if molfile is not None:
        # Guardar archivo temporalmente
        temp_dir = tempfile.mkdtemp()
        mol_path = os.path.join(temp_dir, molfile.name)
        
        try:
            with open(mol_path, "wb") as f:
                f.write(molfile.getbuffer())

            jobname = os.path.splitext(os.path.basename(mol_path))[0]
            st.info(f"📂 Procesando molécula: **{jobname}**")

            # Ejecutar flujo completo
            with st.spinner("Ejecutando ORCA, esto puede tardar unos minutos..."):
                process = subprocess.run(
                    ["python", RUN_ORCA, "--mol", mol_path, "--pdf", "--csv", "--view"],
                    cwd=PROJECT_DIR,
                    capture_output=True,
                    text=True,
                )

            # Mostrar log
            st.subheader("📜 Log de ejecución")
            if process.stdout:
                st.text(process.stdout)
            if process.stderr:
                st.error(process.stderr)

            # Rutas de salida
            pdf_path = f"results/reportes/{jobname}_IR.pdf"
            csv_path = f"results/espectros/{jobname}_IR.csv"
            png_path = f"results/espectros/{jobname}_IR.png"

            col1, col2 = st.columns(2)

            with col1:
                # Espectro IR
                if os.path.exists(png_path):
                    st.subheader("📊 Espectro IR")
                    st.image(png_path, caption=f"Espectro IR de {jobname}")

                # CSV
                if os.path.exists(csv_path):
                    st.subheader("📑 Frecuencias (CSV)")
                    with open(csv_path) as f:
                        st.download_button(
                            label="⬇️ Descargar CSV",
                            data=f,
                            file_name=f"{jobname}_IR.csv",
                            mime="text/csv",
                        )

            with col2:
                # Molécula en 3D
                st.subheader("🧩 Visualización 3D interactiva")
                mostrar_molecula_3d(mol_path)

                # PDF
                if os.path.exists(pdf_path):
                    st.subheader("📄 Reporte en PDF")
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Descargar PDF",
                            data=f,
                            file_name=f"{jobname}_IR.pdf",
                            mime="application/pdf",
                        )

        except Exception as e:
            st.error(f"Error procesando el archivo: {str(e)}")
            
except Exception as e:
    st.error(f"Error en la aplicación: {str(e)}")
