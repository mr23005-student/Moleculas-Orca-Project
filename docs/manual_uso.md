# Instalación de dependencias

Antes de ejecutar el proyecto, asegúrate de instalar las dependencias necesarias. Ejecuta los siguientes comandos en la terminal desde la raíz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install reportlab py3Dmol numpy matplotlib
```

Esto instalará las librerías requeridas:

Si ves advertencias amarillas sobre importaciones, asegúrate de que el entorno virtual esté activado y que las dependencias estén instaladas correctamente.
## 1. Requisitos previos

- Tener Python 3 instalado.
- Tener acceso a internet para instalar dependencias.
- Tener una cuenta de correo para descargar ORCA.

## 2. Instalación de dependencias Python

Desde la raíz del proyecto, ejecuta:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Esto instalará todas las librerías necesarias:
- streamlit
- pandas
- reportlab
- py3Dmol
- numpy
- matplotlib
- selenium
- scipy
- rdkit

## 3. Descarga e instalación de ORCA

1. Ve a https://orcaforum.kofo.mpg.de/app.php/dlext/
2. Regístrate con tu correo institucional o personal (es obligatorio para descargar ORCA).
3. Descarga la versión de ORCA para Linux.
4. Descomprime el archivo descargado, por ejemplo en `/home/usuario/orca`.
5. Agrega la carpeta `bin` de ORCA al PATH. En la terminal ejecuta:
	```bash
	export PATH=$PATH:/home/usuario/orca/bin
	```
	(Puedes agregar esta línea a tu `~/.bashrc` para que sea permanente).
6. Verifica la instalación con:
	```bash
	orca --version
	```
	Si ves la versión, ORCA está listo para usarse.

## 4. Estructura del proyecto

- `data/`: Archivos `.xyz` de moléculas de ejemplo.
- `inputs/`: Aquí se generan los archivos de entrada para ORCA.
- `outputs/`: Aquí se guardan las salidas de ORCA.
- `results/`: Reportes PDF, espectros y visualizaciones generadas.
- `run_orca.py`: Script principal para procesar una molécula.
- `app.py`: Interfaz web para uso interactivo.

## 5. Ejecución desde terminal

Para procesar una molécula y generar todos los resultados:

```bash
source .venv/bin/activate
python run_orca.py --mol data/water.xyz --pdf --csv --view
```

Esto generará:
- Reporte PDF en `results/reportes/`
- Espectro IR (PNG y CSV) en `results/espectros/`
- Visualización 3D en `results/moleculas_3d/`

## 6. Uso de la interfaz web

Puedes usar la interfaz web ejecutando:

```bash
streamlit run app.py
```

Desde el navegador podrás subir archivos `.xyz`, ver resultados, descargar reportes y espectros.

## 7. Explicación de los procesos

- **Generación de archivo .inp**: El script toma el archivo `.xyz` y genera el archivo de entrada para ORCA en `inputs/`.
- **Ejecución de ORCA**: ORCA realiza el cálculo cuántico y guarda la salida en `outputs/`.
- **Procesamiento de resultados**: Se extraen frecuencias IR, energía total y se generan gráficos y reportes.
- **Visualización 3D**: Se crea una visualización interactiva de la molécula usando py3Dmol.
- **Interfaz web**: Permite realizar todo el flujo de trabajo de forma sencilla y visual.

## 8. Notas importantes

- Si ORCA no está en el PATH, puedes editar el script para poner la ruta completa al ejecutable.
- Si tienes problemas con dependencias, revisa que el entorno virtual esté activado.
- Para cualquier duda, consulta la documentación oficial de ORCA y las librerías usadas.

---

¡Listo! Siguiendo este manual cualquier usuario podrá instalar, configurar y ejecutar el proyecto sin problemas.
