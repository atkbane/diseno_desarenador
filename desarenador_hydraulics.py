"""
desarenador_hydraulics.py
=========================
Funciones de cálculo hidráulico para el diseño de desarenadores
en centrales hidroeléctricas.

Unidades del Sistema Internacional (SI) salvo indicación explícita.
"""

import math

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTES FÍSICAS
# ─────────────────────────────────────────────────────────────────────────────

# Gravedad
G               = 9.81    # m/s²

# Densidades
PS_SEDIMENTO    = 2.650   # g/cm³ — densidad del sedimento
PW_AGUA         = 1.000   # g/cm³ — densidad del agua

# Viscosidad cinemática del agua a 20 °C
VISCO_20C       = 1.3e-6  # m²/s

# Rugosidad de Manning (concreto)
N_MANNING       = 0.013   # s/m^(1/3)
K_STRICKLER     = 1.0 / N_MANNING  # ≈ 76.92

# Talud del bisel (relación horizontal : vertical)
TALUD_H         = 0.8     # —   relación horizontal del talud (1 : 0.8)


# ─────────────────────────────────────────────────────────────────────────────
#  BISEL DINÁMICO
# ─────────────────────────────────────────────────────────────────────────────

def calc_bisel_height(H: float) -> float:
    """
    Calcula la altura del bisel en función de la altura total H.

    Fórmula:
        alto_bisel = 0.32 * H - 0.40

    El resultado se redondea al múltiplo de 0.05 m más cercano
    (es decir, a múltiplos de 5 cm).

    Regla de redondeo:
        - Si el valor cae exactamente a la mitad entre dos múltiplos
          (p.ej. 0.825), se redondea hacia arriba (0.85).
        - 0.82 → 0.80 ; 0.83 → 0.85

    Parámetros
    ----------
    H : float — altura total desde la base del bisel hasta la superficie
                del agua [m]

    Retorna
    -------
    float — altura del bisel redondeada a múltiplos de 0.05 m
    """
    if H <= 0:
        return 0.0

    raw = 0.32 * H - 0.40
    # Redondeo al múltiplo de 0.05 más cercano
    # round() en Python usa "bankers rounding" para .5, pero para este
    # caso usamos la lógica: round(valor / 0.05) * 0.05
    # que redondea .5 hacia arriba (al entero más cercano).
    rounded = round(raw / 0.05) * 0.05
    return round(rounded, 2)


# ─────────────────────────────────────────────────────────────────────────────
#  GEOMETRÍA DE LA SECCIÓN
# ─────────────────────────────────────────────────────────────────────────────

def car_sec_des(b: float, h: float):
    """
    Área, perímetro mojado y radio hidráulico de una sección tipo desarenador.

    La sección tiene un bisel inferior con talud 1:0.8 y altura variable
    calculada con calc_bisel_height(h):
 
        ┌─────────────────── b ─────────────────────────┐
        │                                               │
        │                                               │  h - alt_bisel
        │                                               │
        ├─── proy_bisel ──┤             ├── proy_bisel ─┤
         ╲                │             │              ╱│  alt_bisel
          ╲               │             │             ╱ │
           ╲──────────────── b ──────────────────────╱  │

    Los biseles inferiores son inclinados hacia el centro, formando una
    especie de embudo que dirige las partículas sedimentadas al centro
    del desarenador.

    Parámetros
    ----------
    b : float — ancho total de la nave [m]
    h : float — tirante de agua total (desde fondo hasta superficie) [m]

    Retorna
    -------
    tuple (area, perimetro, radio_hidraulico, alt_bisel)
    """
    # Altura del bisel calculada dinámicamente
    alt_bisel = calc_bisel_height(h)

    # Proyección horizontal del talud (cada lado)
    proy_bisel = alt_bisel * TALUD_H

    # ── Área ──────────────────────────────────
    # Área de la parte superior (rectangular)
    area_sup = b * (h - alt_bisel)

    # Área de la parte inferior (trapecio con biseles)
    #   base mayor = b, base menor = b - 2 * proy_bisel
    base_menor = b - 2 * proy_bisel
    area_inf = (b + base_menor) / 2 * alt_bisel

    area = round(area_sup + area_inf, 2)

    # ── Perímetro mojado ──────────────────────
    #   laterales rectos: 2 * (h - alt_bisel)
    #   base inferior plana: b - 2 * proy_bisel
    #   taludes: 2 * sqrt(proy_bisel² + alt_bisel²)
    long_talud = math.sqrt(proy_bisel ** 2 + alt_bisel ** 2)
    peri = round(
        2 * (h - alt_bisel) +
        (b - 2 * proy_bisel) +
        2 * long_talud,
        2
    )

    # ── Radio hidráulico ──────────────────────
    rh = round(area / peri, 2) if peri > 0 else 0.0

    return area, peri, rh, alt_bisel


# ─────────────────────────────────────────────────────────────────────────────
#  VELOCIDAD DE SEDIMENTACIÓN — CAMP
# ─────────────────────────────────────────────────────────────────────────────

def vel_CAMP(d: float) -> float:
    """
    Velocidad máxima del flujo para sedimentación (fórmula de Camp).

    v = a · √d

    donde a depende del diámetro de la partícula:
      d ≥ 1.0 mm  →  a = 36
      d ≥ 0.2 mm  →  a = 44
      d < 0.2 mm  →  a = 51

    Parámetros
    ----------
    d : float — diámetro de la partícula [mm]

    Retorna
    -------
    Velocidad máxima [m/s]
    """
    if d <= 0:
        return 0.0

    if d >= 1.0:
        a = 36
    elif d >= 0.2:
        a = 44
    else:
        a = 51

    return round(math.sqrt(d) * a / 100, 3)


# ─────────────────────────────────────────────────────────────────────────────
#  VELOCIDAD MÁXIMA ADMISIBLE — SHIELDS (1936)
# ─────────────────────────────────────────────────────────────────────────────

def vel_critica_shields(b: float, h: float, d: float) -> float:
    """
    Velocidad máxima admisible del flujo para evitar la resuspensión
    del sedimento (fórmula de Shields, 1936).

    Esta función se usa como velocidad límite en el método complejo.
    Representa la velocidad a la que el sedimento comienza a moverse
    (transporte incipiente / inicio de arrastre).

    Fórmula original de Shields adaptada con Manning-Strickler:

        v_crítica = ks · R^(1/6) · √( (ρs/ρw - 1) · d · 0.03 )

    donde:
        ks = 1/n  → coeficiente de Strickler [—]
        n         → coeficiente de Manning (concreto) [s/m^(1/3)]
        R         → radio hidráulico de la sección [m]
        ρs        → densidad del sedimento [g/cm³]
        ρw        → densidad del agua [g/cm³]
        d         → diámetro de la partícula [m]
        0.03      → coeficiente adimensional de Shields para
                    condiciones típicas de desarenadores

    Referencia:
        Shields, A. (1936). "Anwendung der Ähnlichkeitsmechanik und der
        Turbulenzforschung auf die Geschiebebewegung".
        Mitteilungen der Preußischen Versuchsanstalt für Wasserbau und
        Schiffbau, Heft 26, Berlin.

    Parámetros
    ----------
    b : float — ancho de la nave [m]
    h : float — tirante de agua [m]
    d : float — diámetro de la partícula [mm]

    Retorna
    -------
    float — velocidad máxima admisible (crítica) [m/s]
    """
    if d <= 0 or b <= 0 or h <= 0:
        return 0.0

    area, peri, rh, _ = car_sec_des(b, h)

    if rh <= 0:
        return 0.0

    d_m = d / 1000  # mm → m
    raiz = math.sqrt((PS_SEDIMENTO / PW_AGUA - 1) * d_m * 0.03)
    rh_6 = rh ** (1 / 6)

    return round(K_STRICKLER * rh_6 * raiz, 3)



# ─────────────────────────────────────────────────────────────────────────────
#  VELOCIDAD DE CAÍDA DE LA PARTÍCULA  (STUB)
# ─────────────────────────────────────────────────────────────────────────────

def vel_caida_particula(d: float) -> float:
    """
    Velocidad de caída de la partícula en agua quieta (fórmula de Zanke, 1977).

    La fórmula de Zanke es una expresión unificada válida para regímenes
    laminar, transicional y turbulento, basada en el diámetro adimensional D:

        D = d · [ (ρs/ρw - 1) · g / ν² ]^(1/3)

        wo = 11 · ν / d · ( √(1 + 0.01 · D³) - 1 )

    donde:
        wo : velocidad de caída [m/s]
        d  : diámetro de la partícula [m]
        ν  : viscosidad cinemática del agua [m²/s]
        ρs : densidad del sedimento [g/cm³]
        ρw : densidad del agua [g/cm³]
        g  : aceleración de la gravedad [m/s²]

    Referencia: Zanke, U. (1977). "Berechnung der Sinkgeschwindigkeiten
                von Sedimenten". Mitteilungen des Franzius-Instituts, Heft 46.

    Parámetros
    ----------
    d : float — diámetro de la partícula [mm]

    Retorna
    -------
    float — velocidad de caída [m/s]
    """
    if d <= 0:
        return 0.0

    d_m = d / 1000  # mm → m  (la fórmula requiere d en metros)

    # Diámetro adimensional D (Zanke)
    # D = d * [ (ρs/ρw - 1) * g / ν² ]^(1/3)
    D = d_m * ((PS_SEDIMENTO / PW_AGUA - 1) * G / VISCO_20C ** 2) ** (1 / 3)

    # Velocidad de caída (Zanke)
    # wo = 11 * ν / d * ( sqrt(1 + 0.01 * D³) - 1 )
    wo = 11 * VISCO_20C / d_m * (math.sqrt(1 + 0.01 * D ** 3) - 1)

    return round(wo, 4)



# ─────────────────────────────────────────────────────────────────────────────
#  VELOCIDAD DE CAÍDA EN AGUA FLUYENDO
# ─────────────────────────────────────────────────────────────────────────────

def w_en_agua_fluyendo(w: float, v: float, h: float) -> float:
    """
    Velocidad de caída de la partícula en agua fluyendo.

    Corrige la velocidad de caída en agua quieta (w) por efectos
    de turbulencia del flujo (ecuación de Sokolov).

        wf = w - 0.132 / √h · v

    donde:
        wf : velocidad de caída efectiva en agua fluyendo [m/s]
        w  : velocidad de caída en agua quieta [m/s]
        v  : velocidad del flujo [m/s]
        h  : tirante de agua [m]

    Esta corrección se aplica en el método complejo. Luego la longitud
    se calcula con lon_sed_complejo() que usa wf directamente.

    Parámetros
    ----------
    w : float — velocidad de caída en agua quieta [m/s]
    v : float — velocidad del flujo [m/s]
    h : float — tirante de agua [m]

    Retorna
    -------
    float — velocidad de caída efectiva en agua fluyendo [m/s]
    """
    Wf = w - (0.132 / math.sqrt(h)) * v
    return round(Wf, 4)



# ─────────────────────────────────────────────────────────────────────────────
#  LONGITUD DE SEDIMENTACIÓN — MÉTODO SIMPLE (Bestelli / Sokolov / Velikanov)
# ─────────────────────────────────────────────────────────────────────────────

def lon_sed_simple(h: float, v: float, w: float) -> float:
    """
    Longitud de sedimentación para el método simple.

    Fórmula de Bestelli / Sokolov / Velikanov, que incluye la corrección
    por turbulencia en el denominador:

        L = h^(3/2) · v / ( √h · w - 0.132 · v )

    donde:
        h : tirante de agua [m]
        v : velocidad del flujo [m/s]
        w : velocidad de caída de la partícula [m/s]
            (ingresada directamente por el usuario)

    Condición de validez: √h · w > 0.132 · v

    Parámetros
    ----------
    h : float — tirante de agua [m]
    v : float — velocidad del flujo [m/s]
    w : float — velocidad de caída de la partícula [m/s]

    Retorna
    -------
    float — longitud de sedimentación [m]
    """
    if h <= 0 or v <= 0 or w <= 0:
        return 0.0

    denom = math.sqrt(h) * w - 0.132 * v
    if denom <= 0:
        return float('inf')

    return round(h ** 1.5 * v / denom, 2)


# ─────────────────────────────────────────────────────────────────────────────
#  LONGITUD DE SEDIMENTACIÓN — MÉTODO COMPLEJO
# ─────────────────────────────────────────────────────────────────────────────

def lon_sed_complejo(h: float, v: float, wf: float) -> float:
    """
    Longitud de sedimentación para el método complejo.

    Fórmula simplificada que usa la velocidad de caída efectiva wf
    (ya corregida por turbulencia en w_en_agua_fluyendo):

        L = V · h / wf

    donde:
        h  : tirante de agua [m]
        v  : velocidad del flujo [m/s]
        wf : velocidad de caída efectiva en agua fluyendo [m/s]
             (calculada con w_en_agua_fluyendo)

    NOTA: A diferencia de lon_sed_simple(), esta fórmula NO incluye
    el término -0.132·v en el denominador, porque esa corrección ya
    se aplicó al calcular wf.

    Parámetros
    ----------
    h  : float — tirante de agua [m]
    v  : float — velocidad del flujo [m/s]
    wf : float — velocidad de caída efectiva en agua fluyendo [m/s]

    Retorna
    -------
    float — longitud de sedimentación [m]
    """
    if h <= 0 or v <= 0 or wf <= 0:
        return 0.0

    return round(v * h / wf, 2)



# ─────────────────────────────────────────────────────────────────────────────
#  VERTEDERO DE CRESTA REDONDEADA
# ─────────────────────────────────────────────────────────────────────────────

def des_cre(Q: float, L: float, C: float = 2.10) -> float:
    """
    Carga sobre un vertedero de cresta redondeada (ecuación de descarga).

    h = ( Q / (C · L) )^(2/3)

    donde:
        Q : caudal [m³/s]
        L : longitud de la cresta [m]
        C : coeficiente de descarga (default 2.10)

    Parámetros
    ----------
    Q : float — caudal [m³/s]
    L : float — longitud de la cresta [m]
    C : float — coeficiente de descarga (default 2.10)

    Retorna
    -------
    float — carga sobre la cresta [m]
    """
    if Q <= 0 or L <= 0 or C <= 0:
        return 0.0

    return round((Q / (C * L)) ** (2 / 3), 2)


# ─────────────────────────────────────────────────────────────────────────────
#  FUNCIÓN PRINCIPAL DE DISEÑO
# ─────────────────────────────────────────────────────────────────────────────

def diseno_desarenador(
    q: float,
    d_par: float,
    bas: float,
    alt: float,
    v_par: float,
    c_ver: float = 2.10,
    n_nav: int = 3,
    metodo: str = "simple",
) -> dict:
    """
    Diseño completo de un desarenador.

    Ofrece dos métodos de cálculo para la longitud de sedimentación:

    **Método "simple"** (por defecto):
        - El usuario ingresa directamente la velocidad de caída (v_par)
        - Se usa vel_CAMP() como velocidad límite
        - Se usa lon_sed() con v_par para la longitud

    **Método "complejo"**:
        - Se calcula la velocidad de caída de la partícula (vel_caida_particula)
        - Se usa vel_critica_shields() como velocidad límite (v. máxima admisible)
        - Se calcula la velocidad de caída en agua fluyendo (w_en_agua_fluyendo)
        - Se usa lon_sed() con la velocidad de caída efectiva


    Parámetros
    ----------
    q      : float — caudal total de diseño [m³/s]
    d_par  : float — diámetro de la partícula a sedimentar [mm]
    bas    : float — ancho de cada nave [m]
    alt    : float — tirante de agua total (desde fondo hasta superficie) [m]
    v_par  : float — velocidad de caída de la partícula [cm/s]
                     (solo usado en método "simple")
    c_ver  : float — coeficiente de descarga del vertedero (default 0.76)
    n_nav  : int   — número de naves (default 3)
    metodo : str   — método de cálculo: "simple" o "complejo" (default "simple")

    Retorna
    -------
    dict con los siguientes campos:
        q_nave, area, peri, rh, alt_bisel,
        v_real, v_camp, v_shields, v_limite,
        w_caida, w_efectiva,
        factor_limitante, estado, margen_pct,
        lon_sed, h_vertedero, p_cresta,
        h_limpia, h_total_limpia,
        metodo_usado

    """
    # ── Validaciones ────────────────────────
    if q <= 0:
        raise ValueError("El caudal debe ser > 0.")
    if d_par <= 0:
        raise ValueError("El diámetro de partícula debe ser > 0.")
    if bas <= 0:
        raise ValueError("El ancho de nave debe ser > 0.")
    if alt <= 0:
        raise ValueError("El tirante de agua debe ser > 0.")
    if n_nav < 1:
        raise ValueError("El número de naves debe ser ≥ 1.")
    if metodo not in ("simple", "complejo"):
        raise ValueError("El método debe ser 'simple' o 'complejo'.")
    if metodo == "simple" and v_par <= 0:
        raise ValueError(
            "En método 'simple' la velocidad de caída debe ser > 0."
        )

    # ── Caudal por nave ────────────────────
    q_nave = round(q / n_nav, 2)

    # ── Geometría (incluye bisel dinámico) ──
    area, peri, rh, alt_bisel = car_sec_des(bas, alt)

    # ── Velocidades ─────────────────────────
    v_real = round(q_nave / area, 3) if area > 0 else 0.0
    v_camp = vel_CAMP(d_par)
    v_shields = vel_critica_shields(bas, alt, d_par)

    # ── Velocidad límite según método ───────
    if metodo == "simple":
        # Método simple: usa Camp como velocidad límite
        v_limite = v_camp
        factor_limitante = "CAMP (Sedimentación)"
    else:
        # Método complejo: usa Shields (velocidad máxima admisible)
        v_limite = v_shields if v_shields > 0 else v_camp
        if v_shields > 0:
            factor_limitante = "SHIELDS (V. Máx. Admisible)"
        else:
            factor_limitante = "CAMP (fallback)"


    # ── Verificación de velocidad ───────────
    if v_real > v_limite:
        estado = "FALLA"
        margen_pct = 0.0
    else:
        margen_pct = round((1 - v_real / v_limite) * 100, 1)
        estado = "OK"

    # ── Velocidad de caída y longitud ───────
    if metodo == "simple":
        # Método simple: el usuario ingresa v_par directamente
        w_ms = v_par / 100  # cm/s → m/s
        w_caida = w_ms
        w_efectiva = w_ms
    else:
        # Método complejo: se calcula todo
        w_caida = vel_caida_particula(d_par)       # m/s
        w_efectiva = w_en_agua_fluyendo(w_caida, v_real, alt)  # m/s

    if metodo == "simple":
        l_sed = lon_sed_simple(alt, v_real, w_efectiva)
    else:
        l_sed = lon_sed_complejo(alt, v_real, w_efectiva)


    # ── Vertedero ───────────────────────────
    h_ver = des_cre(q_nave, bas, c_ver)
    p_cresta = round(alt - h_ver, 2)

    # ── Condición de limpieza (N-1) ─────────
    if n_nav > 1:
        q_limpia = round(q / (n_nav - 1), 2)
        h_limpia = des_cre(q_limpia, bas, c_ver)
        h_total_limpia = round(p_cresta + h_limpia, 2)
    else:
        q_limpia = 0.0
        h_limpia = 0.0
        h_total_limpia = 0.0

    return {
        "q_nave": q_nave,
        "area": area,
        "perimetro": peri,
        "radio_hid": rh,
        "alt_bisel": alt_bisel,
        "v_real": v_real,
        "v_camp": v_camp,
        "v_shields": v_shields,
        "v_limite": v_limite,

        "factor_limitante": factor_limitante,
        "w_caida": w_caida,
        "w_efectiva": w_efectiva,
        "estado": estado,
        "margen_pct": margen_pct,
        "lon_sed": l_sed,
        "h_vertedero": h_ver,
        "p_cresta": p_cresta,
        "q_limpia": q_limpia,
        "h_limpia": h_limpia,
        "h_total_limpia": h_total_limpia,
        "metodo_usado": metodo,
    }
