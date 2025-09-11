import os
import streamlit as st
import subprocess
import tempfile
import py3Dmol
import streamlit.components.v1 as components
import shutil
import time
from subprocess import Popen, PIPE

# -----------------------
# Session state
# -----------------------
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.temp_dir = None
    st.session_state.previous_upload = None

st.config.set_option("browser.gatherUsageStats", False)
st.set_page_config(
    page_title="Moleculas ORCA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure directories exist
for dir_path in ["results/reportes", "results/espectros", "results/moleculas_3d"]:
    os.makedirs(dir_path, exist_ok=True)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RUN_ORCA = os.path.join(PROJECT_DIR, "run_orca.py")

@st.cache_resource
def init_session():
    if not st.session_state.initialized:
        st.session_state.initialized = True
    return True

init_session()

# -----------------------
# UI
# -----------------------
st.title("🔬 Generador de cálculos ORCA")
st.markdown("Sube una molécula `.xyz` y genera automáticamente:")
st.markdown("- ✅ Energía total")
st.markdown("- ✅ Espectro IR (PNG + CSV)")
st.markdown("- ✅ Visualización 3D interactiva")
st.markdown("- ✅ Reporte en PDF")

# -----------------------
# Función 3D
# -----------------------
@st.cache_resource
def mostrar_molecula_3d(xyz_file):
    try:
        with open(xyz_file, encoding="utf-8") as f:
            xyz_data = f.read()
        view = py3Dmol.view(width=500, height=400)
        view.addModel(xyz_data, "xyz")
        view.setStyle({"stick": {}})
        view.zoomTo()
        html = view._make_html()
        components.html(html, height=500, width=600)
    except Exception as e:
        st.error(f"Error al visualizar molécula: {str(e)}")

# -----------------------
# Limpieza
# -----------------------
def cleanup_temp_files():
    if st.session_state.temp_dir and os.path.exists(st.session_state.temp_dir):
        shutil.rmtree(st.session_state.temp_dir)
        st.session_state.temp_dir = None

# -----------------------
# Subida y procesamiento
# -----------------------
try:
    molfile = st.file_uploader("Sube un archivo .xyz de la molécula", type=["xyz"],
                               key="mol_upload", on_change=cleanup_temp_files)

    if molfile is not None and molfile != st.session_state.previous_upload:
        st.session_state.previous_upload = molfile
        
        progress_placeholder = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Preparando archivo...")
            progress_bar.progress(10)
            
            cleanup_temp_files()
            st.session_state.temp_dir = tempfile.mkdtemp()
            mol_path = os.path.join(st.session_state.temp_dir, molfile.name)
            
            with open(mol_path, "wb") as f:
                f.write(molfile.getbuffer())

            jobname = os.path.splitext(os.path.basename(mol_path))[0]
            progress_placeholder.info(f"📂 Procesando molécula: **{jobname}**")
            
            # -----------------------
            # Ejecutar ORCA
            # -----------------------
            status_text.text("Iniciando cálculos ORCA...")
            progress_bar.progress(30)
            
            process = Popen(
                ["python", RUN_ORCA, "--mol", mol_path, "--pdf", "--csv", "--view"],
                cwd=PROJECT_DIR,
                stdout=PIPE,
                stderr=PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    status_text.text(f"ORCA: {output.strip()}")
            
            _, stderr = process.communicate()
            if process.returncode != 0:
                raise Exception(f"ORCA failed: {stderr}")
            
            progress_bar.progress(50)
            status_text.text("Cálculos ORCA completados...")
            
            # -----------------------
            # Resultados
            # -----------------------
            status_text.text("Procesando resultados...")
            progress_bar.progress(70)

            pdf_path = f"results/reportes/{jobname}_IR.pdf"
            csv_path = f"results/espectros/{jobname}_IR.csv"
            png_path = f"results/espectros/{jobname}_IR.png"

            status_text.text("Generando visualizaciones...")
            progress_bar.progress(90)

            col1, col2 = st.columns(2)
            with col1:
<<<<<<< HEAD
                if os.path.exists(png_path):
                    st.subheader("📊 Espectro IR")
                    st.image(png_path, caption=f"Espectro IR de {jobname}")

=======
                # Espectros IR
                st.subheader("📊 Espectros IR")
                
                # Rutas de los tres tipos de espectros
                png_discrete = f"results/espectros/{jobname}_IR_discrete.png"
                png_smooth = f"results/espectros/{jobname}_IR_smooth.png"
                png_labeled = f"results/espectros/{jobname}_IR_labeled.png"
                
                # Mostrar los tres espectros
                if os.path.exists(png_discrete):
                    st.markdown("### Espectro de Picos Discretos")
                    st.image(png_discrete, caption="Picos IR individuales")
                
                if os.path.exists(png_smooth):
                    st.markdown("### Espectro Suavizado")
                    st.image(png_smooth, caption="Espectro IR suavizado")
                
                if os.path.exists(png_labeled):
                    st.markdown("### Espectro con Etiquetas")
                    st.image(png_labeled, caption="Espectro IR con frecuencias etiquetadas")

                # CSV (mantener la funcionalidad existente)
>>>>>>> origin/main
                if os.path.exists(csv_path):
                    st.subheader("📑 Frecuencias (CSV)")
                    with open(csv_path, encoding="utf-8") as f:
                        st.download_button(
                            label="⬇️ Descargar CSV",
                            data=f,
                            file_name=f"{jobname}_IR.csv",
                            mime="text/csv",
                        )

            with col2:
                st.subheader("🧩 Visualización 3D interactiva")
                mostrar_molecula_3d(mol_path)

                if os.path.exists(pdf_path):
                    st.subheader("📄 Reporte en PDF")
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Descargar PDF",
                            data=f,
                            file_name=f"{jobname}_IR.pdf",
                            mime="application/pdf",
                        )

            progress_bar.progress(100)
            status_text.text("¡Proceso completado!")
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()
            progress_placeholder.empty()

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            cleanup_temp_files()
            st.error(f"Error procesando el archivo: {str(e)}")
            
except Exception as e:
    cleanup_temp_files()
    st.error(f"Error en la aplicación: {str(e)}")
