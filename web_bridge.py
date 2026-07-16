"""
web_bridge.py
=============
Módulo puente entre la interfaz web (JavaScript/Pyodide) y la lógica
de cálculo hidráulico de desarenadores (desarenador_hydraulics).

Expone una única función: ejecutar_diseno(parametros)
que devuelve un dict JSON-serializable.
"""

from desarenador_hydraulics import diseno_desarenador


def _formatear(r: dict, titulo: str, bas: float, alt: float) -> str:
    sep = "\u2500" * 44
    icono = "\u2705" if r["estado"] == "OK" else "\u274c"
    linea_estado = (
        f"{icono} DISEÑO OK  (Margen: {r['margen_pct']}%)"
        if r["estado"] == "OK" else
        f"{icono} FALLA — V. real supera V. límite"
    )

    vel_label = "Camp" if r["vel_limite"] == "camp" else "Shields"
    w_label = "Manual" if r["fuente_w"] == "manual" else "Zanke"

    res = (
        f"Proyecto    : {titulo}\n"
        f"Vel. límite : {vel_label}\n"
        f"Fuente w    : {w_label}\n"
        f"{sep}\n"
        f"{linea_estado}\n"
        f"{sep}\n"
        "\n"
        "VELOCIDADES\n"
        f"  V. real (Q/Área)       : {r['v_real']} m/s\n"
        f"  Límite CAMP            : {r['v_camp']} m/s\n"
        f"  Límite SHIELDS         : {r['v_shields']} m/s\n"
        f"  Factor limitante       : {r['factor_limitante']}\n"
        f"  W caída                : {r['w_caida']} m/s\n"
        f"  W efectiva (Bestelli)  : {r['w_efectiva']} m/s\n"
        f"{sep}\n"
        "\n"
        "DIMENSIONES\n"
        f"  Longitud sedimentación : {r['lon_sed']} m\n"
        f"  Ancho de nave          : {bas} m\n"
        f"  Tirante agua (H)       : {alt} m\n"
        f"  Altura bisel           : {r['alt_bisel']} m\n"
        f"  Área sección           : {r['area']} m²\n"
        f"  Perímetro mojado       : {r['perimetro']} m\n"
        f"  Radio hidráulico       : {r['radio_hid']} m\n"
        f"  Caudal por nave        : {r['q_nave']} m³/s\n"
        f"{sep}\n"
        "\n"
        "VERTEDERO\n"
        f"  Carga sobre cresta (h) : {r['h_vertedero']} m\n"
        f"  Altura cresta (P)      : {r['p_cresta']} m\n"
    )

    if r.get("q_limpia", 0) > 0:
        res += (
            f"{sep}\n"
            "LIMPIEZA (N-1)\n"
            f"  Caudal por nave (q')  : {r['q_limpia']} m³/s\n"
            f"  V. real (N-1)         : {r['v_real_limpia']} m/s\n"
            f"  Carga vertedero (h')  : {r['h_limpia']} m\n"
            f"  Tirante total (H')    : {r['h_total_limpia']} m\n"
        )

    res += sep
    return res


def ejecutar_diseno(parametros: dict) -> dict:
    """
    Ejecuta el diseño completo del desarenador y devuelve resultados
    listos para serializar a JSON.

    Parámetros (dict)
    -----------------
    titulo   : str (opcional) — nombre del proyecto
    q        : float — caudal total [m³/s]
    d_par    : float — diámetro de partícula [mm]
    bas      : float — ancho de nave [m]
    alt      : float — tirante de agua [m]
    n_nav    : int — número de naves
    c_ver    : float — coeficiente C del vertedero
    vel_limite : str — "camp" o "shields"
    fuente_w   : str — "manual" o "zanke"
    v_par    : float — velocidad de caída [cm/s] (solo si fuente_w="manual")

    Retorna
    -------
    dict con: ok, texto, datos, error
    """
    try:
        titulo = parametros.get("titulo", "").strip() or "—"
        q = float(parametros["q"])
        d_par = float(parametros["d_par"])
        bas = float(parametros["bas"])
        alt = float(parametros["alt"])
        n_nav = int(parametros["n_nav"])
        c_ver = float(parametros.get("c_ver", 2.00))
        vel_limite = parametros.get("vel_limite", "camp")
        fuente_w = parametros.get("fuente_w", "manual")
        v_par = float(parametros.get("v_par", 0.0))

        r = diseno_desarenador(
            q=q, d_par=d_par, bas=bas, alt=alt,
            c_ver=c_ver, n_nav=n_nav,
            vel_limite=vel_limite, fuente_w=fuente_w,
            v_par=v_par,
        )

        texto = _formatear(r, titulo, bas, alt)

        return {
            "ok": True,
            "texto": texto,
            "datos": r,
        }

    except ValueError as ex:
        return {"ok": False, "error": str(ex)}
    except Exception as ex:
        return {"ok": False, "error": f"Error inesperado: {ex}"}
