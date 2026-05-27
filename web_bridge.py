"""
web_main.py
===========
Módulo puente entre la interfaz web (JavaScript/Pyodide) y la lógica
de cálculo hidráulico de desarenadores (desarenador_hydraulics).

Expone una única función: ejecutar_diseno(parametros)
que devuelve un dict JSON-serializable.
"""

from desarenador_hydraulics import diseno_desarenador

# ─────────────────────────────────────────────────────────────────────────────
#  FORMATEO DE RESULTADOS (mismo formato que interfaz_desa._formatear)
# ─────────────────────────────────────────────────────────────────────────────

def _formatear(r: dict, titulo: str, bas: float, alt: float) -> str:
    sep = "\u2500" * 42
    icono = "\u2705" if r["estado"] == "OK" else "\u274c"
    linea_estado = (
        f"{icono} DISEÑO OK  (Margen: {r['margen_pct']}%)"
        if r["estado"] == "OK" else
        f"{icono} FALLA — V. real supera V. límite"
    )

    metodo_label = "Simple" if r["metodo_usado"] == "simple" else "Compleja"

    res = (
        f"Proyecto : {titulo}\n"
        f"Método   : {metodo_label}\n"
        f"{sep}\n"
        f"{linea_estado}\n"
        f"{sep}\n"
        "\n"
        "VELOCIDADES\n"
        f"  V. real (Q/Área)       : {r['v_real']} m/s\n"
        f"  Límite CAMP            : {r['v_camp']} m/s\n"
        f"  Límite SHIELDS         : {r['v_shields']} m/s\n"
    )

    if r["metodo_usado"] == "complejo":
        res += (
            f"  W caída (Zanke)        : {r['w_caida']} m/s\n"
            f"  W efectiva (fluyendo)  : {r['w_efectiva']} m/s\n"
        )

    res += (
        f"  Factor limitante       : {r['factor_limitante']}\n"
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
            f"  Caudal por nave (h')  : {r['q_limpia']} m³/s\n"
            f"  Carga vertedero (h')  : {r['h_limpia']} m\n"
            f"  Tirante total (H')    : {r['h_total_limpia']} m\n"
        )

    res += sep
    return res


# ─────────────────────────────────────────────────────────────────────────────
#  FUNCIÓN PRINCIPAL (llamada desde JavaScript)
# ─────────────────────────────────────────────────────────────────────────────

def ejecutar_diseno(parametros: dict) -> dict:
    """
    Ejecuta el diseño completo del desarenador y devuelve resultados
    listos para serializar a JSON.

    Parámetros (dict)
    -----------------
    titulo : str (opcional) — nombre del proyecto
    q : float — caudal total [m³/s]
    d_par : float — diámetro de partícula [mm]
    bas : float — ancho de nave [m]
    alt : float — tirante de agua [m]
    n_nav : int — número de naves
    c_ver : float — coeficiente C del vertedero
    v_par : float — velocidad de caída [cm/s] (solo método simple)
    metodo : str — "simple" o "complejo"

    Retorna
    -------
    dict con:
        ok : bool
        texto : str (resultado formateado) — solo si ok=True
        datos : dict (resultados crudos) — solo si ok=True
        error : str — solo si ok=False
    """
    try:
        titulo = parametros.get("titulo", "").strip() or "—"
        q = float(parametros["q"])
        d_par = float(parametros["d_par"])
        bas = float(parametros["bas"])
        alt = float(parametros["alt"])
        n_nav = int(parametros["n_nav"])
        c_ver = float(parametros.get("c_ver", 2.10))
        metodo = parametros.get("metodo", "simple")

        if metodo == "simple":
            v_par = float(parametros["v_par"])
        else:
            v_par = 0.0

        r = diseno_desarenador(
            q=q, d_par=d_par, bas=bas, alt=alt,
            v_par=v_par, c_ver=c_ver, n_nav=n_nav,
            metodo=metodo,
        )

        texto = _formatear(r, titulo, bas, alt)

        return {
            "ok": True,
            "texto": texto,
            "datos": {
                "q_nave": r["q_nave"],
                "area": r["area"],
                "perimetro": r["perimetro"],
                "radio_hid": r["radio_hid"],
                "alt_bisel": r["alt_bisel"],
                "v_real": r["v_real"],
                "v_camp": r["v_camp"],
                "v_shields": r["v_shields"],
                "v_limite": r["v_limite"],
                "factor_limitante": r["factor_limitante"],
                "w_caida": r["w_caida"],
                "w_efectiva": r["w_efectiva"],
                "estado": r["estado"],
                "margen_pct": r["margen_pct"],
                "lon_sed": r["lon_sed"],
                "h_vertedero": r["h_vertedero"],
                "p_cresta": r["p_cresta"],
                "q_limpia": r["q_limpia"],
                "h_limpia": r["h_limpia"],
                "h_total_limpia": r["h_total_limpia"],
                "metodo_usado": r["metodo_usado"],
            },
        }

    except ValueError as ex:
        return {"ok": False, "error": str(ex)}
    except Exception as ex:
        return {"ok": False, "error": f"Error inesperado: {ex}"}