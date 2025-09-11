# parser_orca.py
import re
import numpy as np

# --------- Utilidades ---------
_float_re = r"(-?\d+(?:\.\d+)?(?:[EeDd][\+\-]?\d+)?)"

def _to_float(x: str) -> float:
    # Convierte notación Fortran D/E a float
    return float(x.replace("D", "E").replace("d", "E"))

# --------- IR (frecuencias + intensidades) ---------
def parse_ir(outfile):
    """Versión con debug"""
    with open(outfile, "r") as f:
        lines = f.readlines()

    freqs = []
    intens = []
    
    print(f"[INFO] Analizando archivo: {outfile}")

    
    # Buscar sección IR SPECTRUM
    in_ir = False
    for i, line in enumerate(lines):
        if "IR SPECTRUM" in line.upper():
            print(f"[OK] Encontrado IR SPECTRUM en línea {i+1}")
            in_ir = True
            # Mostrar algunas líneas siguientes para debug
            for j in range(i, min(i+10, len(lines))):
                print(f"Línea {j+1}: {lines[j].strip()}")
            continue
            
        if in_ir:
            # Buscar líneas de datos
            m = re.match(rf"\s*\d+:\s+{_float_re}\s+{_float_re}", line)
            if m:
                print(f"[DATA] Línea de datos: {line.strip()}")
                fcm, inten = _to_float(m.group(1)), _to_float(m.group(2))
                freqs.append(fcm)
                intens.append(inten)

    if freqs:
        return freqs, intens

    # 2) VIBRATIONAL FREQUENCIES (solo frecuencias → intensidades simuladas)
    in_vib = False
    for line in lines:
        if "VIBRATIONAL FREQUENCIES" in line.upper():
            in_vib = True
            continue
        if in_vib:
            if "NORMAL MODES" in line.upper():
                break
            m = re.search(rf"\s*\d+:\s+{_float_re}\s+cm\*\*-1", line)
            if m:
                freqs.append(_to_float(m.group(1)))
                intens.append(1.0)  # asigna intensidad simulada para graficar

    return freqs, intens

def process_ir_data(freqs, intensities, start=400, end=4000, points=1000, sigma=15.0):
    """Procesa datos para generar un espectro IR suavizado.
    
    Args:
        freqs: Lista de frecuencias
        intensities: Lista de intensidades
        start, end: Rango de frecuencias (cm-1)
        points: Número de puntos para el espectro
        sigma: Ancho de los picos gaussianos
    """
    x = np.linspace(start, end, points)
    y = np.zeros_like(x)
    
    # Normalizar intensidades
    max_intensity = max(intensities)
    if max_intensity > 0:
        intensities = [i/max_intensity for i in intensities]
    
    # Generar curva suavizada
    for freq, inten in zip(freqs, intensities):
        y += inten * np.exp(-(x - freq)**2 / (2 * sigma**2))
    
    # Normalizar resultado final
    if np.max(y) > 0:
        y = y / np.max(y)
    
    return x, y, list(zip(freqs, intensities))

# --------- Raman ---------
def parse_raman(outfile):
    """
    Devuelve dict {freq_cm-1: intensidad}.
    """
    with open(outfile, "r") as f:
        lines = f.readlines()

    data = {}
    in_raman = False
    for line in lines:
        if "RAMAN SPECTRUM" in line.upper():
            in_raman = True
            continue
        if in_raman:
            if line.strip() == "" or "IR SPECTRUM" in line.upper():
                break
            m = re.match(rf"\s*\d+\s+{_float_re}\s+{_float_re}", line)
            if m:
                freq = _to_float(m.group(1))
                inten = _to_float(m.group(2))
                data[freq] = inten

    if data:
        return data

    # fallback: "RAMAN ACTIVITIES"
    in_act = False
    for line in lines:
        if "RAMAN ACTIVITIES" in line.upper():
            in_act = True
            continue
        if in_act:
            if line.strip() == "":
                break
            m = re.match(rf"\s*\d+\s+{_float_re}\s+{_float_re}", line)
            if m:
                freq = _to_float(m.group(1))
                act = _to_float(m.group(2))
                data[freq] = act
    return data

# --------- NMR ---------
def parse_nmr(outfile):
    """
    Devuelve lista [(atom_index, element, shift_ppm), ...].
    """
    with open(outfile, "r") as f:
        lines = f.readlines()

    shifts = []
    in_block = False
    for line in lines:
        if "CHEMICAL SHIFTS" in line.upper():
            in_block = True
            continue
        if in_block:
            if line.strip() == "":
                if shifts:
                    break
            m = re.match(rf"\s*(\d+)\s+([A-Za-z]{{1,2}})\s+{_float_re}\s+ppm", line)
            if m:
                idx = int(m.group(1))
                elem = m.group(2)
                shift = _to_float(m.group(3))
                shifts.append((idx, elem, shift))
    return shifts

# --------- Energía ---------
def parse_energy_total(outfile):
    """
    Busca energía en este orden:
    - FINAL SINGLE POINT ENERGY
    - Total Energy :
    - SCF total energy:
    - TOTAL SCF ENERGY
    Devuelve float o None.
    """
    with open(outfile, "r") as f:
        text = f.read()

    candidates = []
    for m in re.finditer(rf"FINAL SINGLE POINT ENERGY\s+{_float_re}", text, flags=re.IGNORECASE):
        candidates.append(_to_float(m.group(1)))
    for m in re.finditer(rf"Total Energy\s*[:=]\s*{_float_re}", text, flags=re.IGNORECASE):
        candidates.append(_to_float(m.group(1)))
    for m in re.finditer(rf"SCF\s+total\s+energy\s*[:=]\s*{_float_re}", text, flags=re.IGNORECASE):
        candidates.append(_to_float(m.group(1)))
    for m in re.finditer(rf"TOTAL\s+SCF\s+ENERGY\s*[:=]?\s*{_float_re}", text, flags=re.IGNORECASE):
        candidates.append(_to_float(m.group(1)))

    return candidates[-1] if candidates else None
