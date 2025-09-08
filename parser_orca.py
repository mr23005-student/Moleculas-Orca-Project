import re

def parse_ir(outfile):
    """
    Parsea las frecuencias vibracionales y (si existen) intensidades IR desde un .out de ORCA.
    Devuelve dos listas: freqs, intensidades.
    """
    freqs = []
    intensidades = []

    with open(outfile) as f:
        lines = f.readlines()

    inside_block = False
    for line in lines:
        if "VIBRATIONAL FREQUENCIES" in line:
            inside_block = True
            continue

        if inside_block:
            # Caso 1: frecuencia sola → "6:    1637.64 cm**-1"
            match_simple = re.search(r"\s*\d+:\s+([\d\.]+)\s+cm\*\*-1", line)
            if match_simple:
                freqs.append(float(match_simple.group(1)))
                intensidades.append(0.0)
                continue

            # Caso 2: frecuencia + intensidad → "6   1637.64   45.2"
            match_full = re.search(r"\s*\d+\s+([\d\.]+)\s+([\d\.]+)", line)
            if match_full and "cm" not in line:
                freqs.append(float(match_full.group(1)))
                intensidades.append(float(match_full.group(2)))
                continue

            # Fin del bloque
            if "NORMAL MODES" in line:
                break

    return freqs, intensidades


import re

def parse_energy_total(outfile):
    """
    Parsea la energía final de un cálculo ORCA.
    Busca 'FINAL SINGLE POINT ENERGY'. Si no lo encuentra, devuelve el último 'TOTAL SCF ENERGY'.
    """
    energia = None
    with open(outfile) as f:
        for line in f:
            if "FINAL SINGLE POINT ENERGY" in line or "TOTAL SCF ENERGY" in line:
                # Buscar un número decimal en la línea
                match = re.search(r"(-?\d+\.\d+)", line)
                if match:
                    energia = float(match.group(1))
    return energia

