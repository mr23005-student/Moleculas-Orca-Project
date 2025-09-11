# Manual de Uso - Moleculas ORCA Project

Este proyecto permite analizar moléculas usando cálculos computacionales con ORCA, visualizar espectros IR y estructuras 3D, y generar reportes automáticos.

## 1. Instalación de ORCA

Descarga ORCA desde la página oficial: [https://orcaforum.kofo.mpg.de/app.php/dl
download](https://orcaforum.kofo.mpg.de/app.php/dl
download)

Descomprime el archivo y agrega el ejecutable a tu PATH. Ejemplo:
```bash
export PATH=$PATH:/ruta/a/orca_6_1_0_linux_x86-64_shared_openmpi418/
```

## 2. Configuración del entorno virtual

Recomendamos usar un entorno virtual para instalar las dependencias:
```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Instalación de librerías

Instala las dependencias con:
```bash
pip install -r requirements.txt
```

## 4. Ejecución de la aplicación web

Levanta la interfaz web con:
```bash
streamlit run app.py
```

## 5. Estructura y explicación de archivos principales
 - `app.py`:
 
`app.py`: Interfaz web principal. Permite cargar moléculas, ejecutar cálculos, visualizar espectros y estructuras 3D. Sus funciones principales son:
	- **init_session()**: Inicializa el estado de la sesión de Streamlit, asegurando que variables temporales estén listas para cada usuario.
	- **mostrar_molecula_3d(xyz_file)**: Visualiza la molécula en 3D usando py3Dmol y la muestra de forma interactiva en la web.
	- **cleanup_temp_files()**: Elimina archivos temporales generados durante el procesamiento de moléculas, evitando acumulación de datos innecesarios.
	- **Carga y procesamiento de archivos**: Permite al usuario subir archivos `.xyz`, prepara el archivo y lo almacena temporalmente.
	- **Ejecución de cálculos ORCA**: Llama a `run_orca.py` para realizar los cálculos de química computacional, mostrando el progreso y mensajes en tiempo real.
	- **Procesamiento de resultados**: Una vez finalizados los cálculos, muestra los espectros IR (en diferentes estilos), permite descargar el CSV de frecuencias y el reporte PDF.
	- **Visualización 3D**: Muestra la estructura molecular en 3D de manera interactiva.
	- **Gestión de errores**: Captura y muestra errores durante el procesamiento, asegurando una experiencia robusta para el usuario.

 - `run_orca.py`:
 
`run_orca.py`: Script que automatiza el flujo completo de cálculo y reporte con ORCA. Sus funciones principales son:
	- **generar_inp(xyz_file, job, output_dir)**: Genera un archivo de entrada (.inp) para ORCA a partir de un archivo `.xyz` de coordenadas atómicas.
	- **ejecutar_orca(inpfile, intermediates_dir)**: Ejecuta el software ORCA usando el archivo de entrada y guarda la salida en el directorio especificado.
	- **generar_reporte_pdf(molfile, energia, freqs, intensidades, png_file, mol_png)**: Crea un reporte PDF con la energía total, frecuencias vibracionales, espectro IR y una imagen 3D de la molécula.
	- **Bloque principal (`if __name__ == "__main__"`)**: Permite ejecutar el script desde la terminal con argumentos para controlar el flujo (generar PDF, CSV, visualización 3D, tipo de cálculo, etc.). Organiza los resultados en carpetas, llama a las funciones anteriores y utiliza los módulos auxiliares para procesar datos y generar visualizaciones.

 - `parser_orca.py`:
 
`parser_orca.py`: Módulo encargado de extraer y procesar datos de los archivos de salida de ORCA. Sus funciones principales son:
	- **_float_re**: Expresión regular para detectar números flotantes, incluyendo notación científica (E/D).- **_to_float(x: str) -> float**: Convierte cadenas con notación Fortran (D/E) a float estándar de Python.
	- **parse_ir(outfile)**: Abre el archivo de salida de ORCA, busca la sección "IR SPECTRUM" y extrae frecuencias e intensidades. Si no la encuentra, busca "VIBRATIONAL FREQUENCIES" y asigna intensidad simulada. Devuelve listas de frecuencias e intensidades.
	- **process_ir_data(freqs, intensities, start=400, end=4000, points=1000, sigma=15.0)**: Genera un espectro IR suavizado a partir de las frecuencias e intensidades, normalizando y sumando picos gaussianos. Devuelve los valores del eje x, y y los picos principales.
	- **parse_raman(outfile)**: Busca la sección "RAMAN SPECTRUM" y extrae pares frecuencia/intensidad en un diccionario. Si no la encuentra, busca "RAMAN ACTIVITIES" y extrae frecuencia/actividad. Devuelve un diccionario {frecuencia: intensidad/actividad}.
	- **parse_nmr(outfile)**: Busca la sección "CHEMICAL SHIFTS" y extrae el índice del átomo, el elemento y el desplazamiento químico (ppm) en una lista de tuplas.
	- **parse_energy_total(outfile)**: Busca la energía total en el archivo de salida, probando varias expresiones regulares en orden de prioridad. Devuelve el último valor encontrado o None si no hay coincidencias.

 - `spectra.py`:
 
`spectra.py`: Módulo encargado de generar, graficar y exportar espectros IR a partir de los datos procesados. Sus funciones principales son:
	- **plot_ir_spectrum(molfile, freqs, intensidades)**: Genera un espectro IR profesional y lo guarda como PNG. Procesa los datos, grafica el espectro suavizado, añade picos y etiquetas, configura la apariencia y guarda la imagen.
	- **plot_ir_variants(molfile, freqs, intensidades)**: Genera tres variantes del espectro IR: picos discretos, espectro suavizado invertido y espectro etiquetado. Configura y guarda cada imagen como PNG.
	- **export_csv(molfile, freqs, intensidades)**: Exporta frecuencias e intensidades IR a un archivo CSV. Si todas las intensidades son 0, asigna 1.0 a todas. Usa pandas para crear y guardar el archivo.

 - `visualize.py`:
 
`visualize.py`: Módulo encargado de generar visualizaciones 3D interactivas de moléculas y capturas estáticas en PNG. Sus funciones principales son:
	- **save_molecule_html(xyz_file, outdir="results/moleculas_3d")**: Genera un archivo HTML con la molécula en 3D y una captura PNG. Crea el directorio de salida, lee las coordenadas del archivo `.xyz`, genera la visualización interactiva con py3Dmol, guarda el HTML y usa Selenium para tomar una captura PNG. Si ocurre un error, retorna None para el PNG. Devuelve las rutas de los archivos generados.

- `requirements.txt`: Lista de dependencias necesarias para el proyecto.
- `data/`: Carpeta con archivos `.xyz` de ejemplo para pruebas.
- `results/`: Carpeta donde se guardan reportes, espectros y visualizaciones generadas.

## 6. Flujo de trabajo típico

1. Carga un archivo `.xyz` de molécula en la web.
2. Ejecuta el cálculo con ORCA desde la interfaz.
3. Visualiza el espectro IR y la estructura 3D.
4. Descarga el reporte PDF generado.

## 7. Notas adicionales
- Asegúrate de que ORCA esté correctamente instalado y accesible desde la terminal.
- El proyecto está optimizado para Linux.
- Si tienes problemas con Selenium/Chrome, revisa la instalación de Chrome y el driver correspondiente.

---

Para dudas o sugerencias, consulta el archivo `docs/manual_uso.md` o abre un issue en el repositorio.
