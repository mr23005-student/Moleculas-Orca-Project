# parser_orca.py
import re

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
    
    print(f"🔍 Analizando archivo: {outfile}")
    
    # Buscar sección IR SPECTRUM
    in_ir = False
    for i, line in enumerate(lines):
        if "IR SPECTRUM" in line.upper():
            print(f"✅ Encontrado IR SPECTRUM en línea {i+1}")
            in_ir = True
            # Mostrar algunas líneas siguientes para debug
            for j in range(i, min(i+10, len(lines))):
                print(f"Línea {j+1}: {lines[j].strip()}")
            continue
            
        if in_ir:
            # Buscar líneas de datos
            m = re.match(rf"\s*\d+:\s+{_float_re}\s+{_float_re}", line)
            if m:
                print(f"📊 Línea de datos: {line.strip()}")
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
