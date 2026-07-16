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

G               = 9.81    # m/s² — gravedad
PS_SEDIMENTO    = 2.650   # g/cm³ — densidad del sedimento (cuarzo)
PW_AGUA         = 1.000   # g/cm³ — densidad del agua
VISCO_20C       = 1.0e-6  # m²/s — viscosidad cinemática del agua a 20°C
N_MANNING       = 0.013   # s/m^(1/3) — rugosidad de Manning (concreto)
K_STRICKLER     = 1.0 / N_MANNING  # ≈ 76.92
TALUD_H         = 0.8     # relación horizontal del talud (1 : 0.8)


# ─────────────────────────────────────────────────────────────────────────────
#  BISEL DINÁMICO
# ─────────────────────────────────────────────────────────────────────────────

def calc_bisel_height(H: float) -> float:
    """
    Altura del bisel en función de la altura total H.

    Fórmula empírica: alto_bisel = max(0, 0.32 * H - 0.40)
    Redondeado a múltiplos de 0.05 m.

    Origen: Correlación de 8 desarenadores propios.
    Referencia: ANA (2015) p. 78, Villon (2001) p. 101.
    """
    if H <= 0:
        return 0.0
    raw = max(0.0, 0.32 * H - 0.40)
    rounded = round(raw / 0.05) * 0.05
    return round(rounded, 2)


# ─────────────────────────────────────────────────────────────────────────────
#  GEOMETRÍA DE LA SECCIÓN
# ─────────────────────────────────────────────────────────────────────────────

def car_sec_des(b: float, h: float):
    """
    Área, perímetro mojado y radio hidráulico de una sección tipo desarenador.

        ┌─────────────────── b ─────────────────────────┐
        │                                               │
        │                                               │  h - alt_bisel
        │                                               │
        ├─── proy_bisel ──┤             ├── proy_bisel ─┤
         ╲                │             │              ╱│  alt_bisel
          ╲               │             │             ╱ │
           ╲──────────────── b ──────────────────────╱  │

    Retorna: (area, perimetro, radio_hidraulico, alt_bisel)
    """
    alt_bisel = calc_bisel_height(h)
    proy_bisel = alt_bisel * TALUD_H

    area_sup = b * (h - alt_bisel)
    base_menor = b - 2 * proy_bisel
    area_inf = (b + base_menor) / 2 * alt_bisel
    area = round(area_sup + area_inf, 2)

    long_talud = math.sqrt(proy_bisel ** 2 + alt_bisel ** 2)
    peri = round(
        2 * (h - alt_bisel) +
        (b - 2 * proy_bisel) +
        2 * long_talud,
        2
    )

    rh = round(area / peri, 2) if peri > 0 else 0.0
    return area, peri, rh, alt_bisel


# ─────────────────────────────────────────────────────────────────────────────
#  VELOCIDAD LÍMITE — CAMP (1946)
# ─────────────────────────────────────────────────────────────────────────────

def vel_CAMP(d: float) -> float:
    """
    Velocidad máxima del flujo para sedimentación (Camp, 1946).

        v = a · √d  [cm/s]   →   resultado dividido por 100 → m/s

    where a depends on particle diameter (d en mm):
      d > 1.0 mm  →  a = 36
      d ≥ 0.1 mm  →  a = 44
      d < 0.1 mm  →  a = 51

    Reference: Camp (1946). ANA p. 80, Villón p. 105.
    """
    if d <= 0:
        return 0.0
    if d > 1.0:
        a = 36
    elif d >= 0.1:
        a = 44
    else:
        a = 51
    return round(math.sqrt(d) * a / 100, 3)


# ─────────────────────────────────────────────────────────────────────────────
#  VELOCIDAD LÍMITE — SHIELDS (1936)
# ─────────────────────────────────────────────────────────────────────────────

def vel_critica_shields(b: float, h: float, d: float) -> float:
    """
    Velocidad máxima admisible para evitar resuspensión.

        v_crítica = ks · R^(1/6) · √( (ρs/ρw - 1) · d · 0.03 )

    where ks = 1/n (Strickler), R = radio hidráulico.
    Not standard for desarenador design — extension only.
    """
    if d <= 0 or b <= 0 or h <= 0:
        return 0.0
    area, peri, rh, _ = car_sec_des(b, h)
    if rh <= 0:
        return 0.0
    d_m = d / 1000
    # θ_cr = 0.03 (Shields, incipient motion — valor conservador).
    # Ver marco_teorico.md §3.2 para justificación y rangos típicos.
    raiz = math.sqrt((PS_SEDIMENTO / PW_AGUA - 1) * d_m * 0.03)
    return round(K_STRICKLER * rh ** (1 / 6) * raiz, 3)


# ─────────────────────────────────────────────────────────────────────────────
#  VELOCIDAD DE CAÍDA — ZANKE (1977)
# ─────────────────────────────────────────────────────────────────────────────

def vel_caida_particula(d: float) -> float:
    """
    Velocidad de caída en agua quieta (Zanke, 1977).

        D = d · [ (ρs/ρw - 1) · g / ν² ]^(1/3)
        wo = 11 · ν / d · ( √(1 + 0.01 · D³) - 1 )

    Unified formula for laminar, transitional and turbulent regimes.
    Not in ANA/Villon but technically valid.
    """
    if d <= 0:
        return 0.0
    d_m = d / 1000
    D = d_m * ((PS_SEDIMENTO / PW_AGUA - 1) * G / VISCO_20C ** 2) ** (1 / 3)
    wo = 11 * VISCO_20C / d_m * (math.sqrt(1 + 0.01 * D ** 3) - 1)
    return round(wo, 4)


# ─────────────────────────────────────────────────────────────────────────────
#  CORRECCIÓN POR TURBULENCIA — BESTELLI / LEVIN
# ─────────────────────────────────────────────────────────────────────────────

def w_en_agua_fluyendo(w: float, v: float, h: float) -> float:
    """
    Velocidad de caída efectiva en agua fluyendo.

        wf = w - 0.132 / √h · v

    Reference: Bestelli et al., Levin. ANA p. 83, Villon p. 111.
    """
    return round(w - (0.132 / math.sqrt(h)) * v, 4)


# ─────────────────────────────────────────────────────────────────────────────
#  LONGITUD DE SEDIMENTACIÓN (Bestelli / Sokolov / Velikanov)
# ─────────────────────────────────────────────────────────────────────────────

def lon_sed(h: float, v: float, wf: float) -> float:
    """
    Longitud de sedimentación a partir de la velocidad de caída efectiva.

        L = v · h / wf

    donde wf = w - (0.132/√h)·v incluye la corrección por turbulencia
    de Bestelli/Levin (ver `w_en_agua_fluyendo`).

    Reference: Bestelli/Levin. ANA p. 82-83, Villón p. 109-111.
    """
    if h <= 0 or v <= 0 or wf <= 0:
        return 0.0
    return round(v * h / wf, 2)


# ─────────────────────────────────────────────────────────────────────────────
#  VERTEDERO DE CRESTA REDONDEADA
# ─────────────────────────────────────────────────────────────────────────────

def des_cre(Q: float, L: float, C: float = 2.00) -> float:
    """
    Carga sobre vertedero de cresta redondeada.

        h = ( Q / (C · L) )^(2/3)

    Reference: ANA p. 77, Villon p. 102. C = 2.0 (Creager).
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
    c_ver: float = 2.00,
    n_nav: int = 3,
    vel_limite: str = "camp",
    fuente_w: str = "manual",
    v_par: float = 0.0,
) -> dict:
    """
    Diseño completo de un desarenador.

    Two independent options:

    1. Velocidad límite del flujo:
       - "camp"   → v = a·√d (estándar para desarenadores, ANA/Villon)
       - "shields" → v = ks·R^(1/6)·√((ρs/ρw-1)·d·0.03) (extensión)

    2. Velocidad de caída de la partícula (w):
       - "manual" → usuario ingresa w en cm/s (de tablas: Arkhangelski, Sudry, etc.)
       - "zanke"  → cálculo automático desde d (Zanke 1977)

    La corrección por turbulencia (Bestelli/Levin) siempre se aplica.
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
    if vel_limite not in ("camp", "shields"):
        raise ValueError("vel_limite debe ser 'camp' o 'shields'.")
    if fuente_w not in ("manual", "zanke"):
        raise ValueError("fuente_w debe ser 'manual' o 'zanke'.")
    if fuente_w == "manual" and v_par <= 0:
        raise ValueError("Velocidad de caída (v_par) debe ser > 0 cuando fuente_w='manual'.")

    # ── Caudal por nave ────────────────────
    q_nave = round(q / n_nav, 2)

    # ── Geometría ──────────────────────────
    area, peri, rh, alt_bisel = car_sec_des(bas, alt)

    # ── Velocidades ────────────────────────
    v_real = round(q_nave / area, 3) if area > 0 else 0.0
    v_camp = vel_CAMP(d_par)
    v_shields = vel_critica_shields(bas, alt, d_par)

    # ── Velocidad límite ───────────────────
    if vel_limite == "camp":
        v_limite = v_camp
        factor_limitante = "CAMP (Sedimentación)"
    else:
        v_limite = v_shields if v_shields > 0 else v_camp
        factor_limitante = "SHIELDS (V. Máx. Admisible)" if v_shields > 0 else "CAMP (fallback)"

    # ── Verificación de velocidad ──────────
    if v_real > v_limite:
        estado = "FALLA"
        margen_pct = 0.0
    else:
        margen_pct = round((1 - v_real / v_limite) * 100, 1)
        estado = "OK"

    # ── Velocidad de caída ─────────────────
    w_caida = (
        round(v_par / 100, 4)            # manual: cm/s → m/s
        if fuente_w == "manual"
        else vel_caida_particula(d_par)  # zanke: desde d
    )
    w_efectiva = w_en_agua_fluyendo(w_caida, v_real, alt)
    l_sed = lon_sed(alt, v_real, w_efectiva)

    # ── Vertedero ──────────────────────────
    h_ver = des_cre(q_nave, bas, c_ver)
    p_cresta = round(alt - h_ver, 2)

    # ── Condición de limpieza (N-1) ────────
    # Informativo: con la misma b y h del diseño, se recalcula
    # el nivel sobre el vertedero y la velocidad real con el
    # caudal sobrecargado Q/(N-1). No altera el diseño.
    if n_nav > 1:
        q_limpia = round(q / (n_nav - 1), 2)
        v_real_limpia = round(q_limpia / area, 3) if area > 0 else 0.0
        h_limpia = des_cre(q_limpia, bas, c_ver)
        h_total_limpia = round(p_cresta + h_limpia, 2)
    else:
        q_limpia = 0.0
        v_real_limpia = 0.0
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
        "v_real_limpia": v_real_limpia,
        "h_limpia": h_limpia,
        "h_total_limpia": h_total_limpia,
        "vel_limite": vel_limite,
        "fuente_w": fuente_w,
    }
