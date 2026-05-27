"""
interfaz_desa.py
================
Interfaz gráfica con PySide6 para diseño de desarenadores.
Layout de 2 columnas: datos | resultados.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QRadioButton,
    QButtonGroup, QTextEdit, QFrame, QMessageBox, QVBoxLayout,
)
from typing import List

from desarenador_hydraulics import diseno_desarenador

# ── Constantes de UI ──────────────────────────────
WIDTH  = 645
HEIGHT = 540


class VentanaDesarenador(QWidget):
    """Ventana principal con layout de 2 columnas."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diseño de Desarenador - PySide6")
        self.resize(WIDTH, HEIGHT)

        self.metodo = "simple"  # por defecto

        # ── layout principal horizontal ──
        lm = QHBoxLayout(self)
        lm.setContentsMargins(8, 8, 8, 8)
        lm.setSpacing(8)

        # col 0: datos (fijo 320px)
        col0 = self._build_col_datos()
        col0.setFixedWidth(260)
        lm.addWidget(col0)

        # col 1: resultados (stretch)
        lm.addWidget(self._build_col_resultados(), stretch=1)

    # ─────────────────────────────────────────────────────────────────────────
    #  COLUMNA IZQUIERDA
    # ─────────────────────────────────────────────────────────────────────────

    def _build_col_datos(self) -> QFrame:
        panel = QFrame()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # ── Proyecto ──
        gb_proy = QGroupBox("Proyecto")
        form_proy = QVBoxLayout(gb_proy)
        self.e_titulo = QLineEdit()
        self.e_titulo.setPlaceholderText("Nombre del proyecto…")
        form_proy.addWidget(self.e_titulo)
        layout.addWidget(gb_proy)

        # ── Método de Cálculo ──
        gb_met = QGroupBox("Método de Cálculo")
        form_met = QVBoxLayout(gb_met)
        self._btn_group = QButtonGroup(self)
        rb_simple = QRadioButton("Simple  —  ingresas la velocidad de caída")
        rb_simple.setChecked(True)
        self._btn_group.addButton(rb_simple, 0)
        form_met.addWidget(rb_simple)

        rb_complejo = QRadioButton("Compleja  —  se calcula todo\n(Zanke + Shields)")
        self._btn_group.addButton(rb_complejo, 1)
        form_met.addWidget(rb_complejo)

        self._btn_group.idToggled.connect(self._on_metodo_toggle)
        layout.addWidget(gb_met)

        # ── Datos de Entrada ──
        gb_ent = QGroupBox("Datos de Entrada")
        form_ent = QFormLayout(gb_ent)

        self.e_q = QLineEdit()
        self.e_q.setToolTip("Caudal total de diseño")
        form_ent.addRow("Caudal (m³/s):", self.e_q)

        self.e_n_nav = QLineEdit("3")
        self.e_n_nav.setToolTip("Número de naves del desarenador")
        form_ent.addRow("N° Naves:", self.e_n_nav)

        self.e_d_par = QLineEdit()
        self.e_d_par.setToolTip("Diámetro de la partícula a sedimentar")
        form_ent.addRow("Diámetro (mm):", self.e_d_par)

        self.e_c_ver = QLineEdit("2.10")
        self.e_c_ver.setToolTip("Coeficiente de descarga del vertedero (cresta redondeada)")
        form_ent.addRow("Coef. C:", self.e_c_ver)

        self.e_bas = QLineEdit()
        self.e_bas.setToolTip("Ancho de cada nave")
        form_ent.addRow("Ancho nave (m):", self.e_bas)

        self.e_alt = QLineEdit()
        self.e_alt.setToolTip("Tirante de agua total (fondo → superficie)")
        form_ent.addRow("Tirante agua (m):", self.e_alt)

        self.e_v_par = QLineEdit()
        self.e_v_par.setToolTip("Velocidad de caída de la partícula (solo método Simple)")
        self.lbl_v_par = QLabel("Vel. caída (cm/s):")
        form_ent.addRow(self.lbl_v_par, self.e_v_par)

        layout.addWidget(gb_ent)

        # ── Botones ──
        hb_btns = QHBoxLayout()
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.clicked.connect(self._on_limpiar)
        hb_btns.addWidget(btn_limpiar)

        btn_calcular = QPushButton("Calcular")
        btn_calcular.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                padding: 6px 16px;
                background-color: #2a7;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #1a6; }
        """)
        btn_calcular.clicked.connect(self._on_calcular)
        hb_btns.addWidget(btn_calcular)

        layout.addLayout(hb_btns)
        layout.addStretch()
        return panel

    # ─────────────────────────────────────────────────────────────────────────
    #  COLUMNA DERECHA — RESULTADOS
    # ─────────────────────────────────────────────────────────────────────────

    def _build_col_resultados(self) -> QFrame:
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.Box)
        layout = QVBoxLayout(panel)

        gb_res = QGroupBox("Resultados")
        layout_res = QVBoxLayout(gb_res)

        self.txt_res = QTextEdit()
        self.txt_res.setReadOnly(True)
        self.txt_res.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 11px;
            }
        """)
        layout_res.addWidget(self.txt_res, stretch=1)

        layout.addWidget(gb_res)
        return panel

    # ─────────────────────────────────────────────────────────────────────────
    #  EVENTOS
    # ─────────────────────────────────────────────────────────────────────────

    def _on_metodo_toggle(self, btn_id: int):
        """Muestra/oculta el campo de velocidad de caída según el método."""
        self.metodo = "simple" if btn_id == 0 else "complejo"
        visible = self.metodo == "simple"
        self.e_v_par.setVisible(visible)
        self.lbl_v_par.setVisible(visible)
        if not visible:
            self.e_v_par.clear()

    def _on_calcular(self):
        try:
            titulo = self.e_titulo.text().strip() or "—"
            q = float(self.e_q.text())
            d_par = float(self.e_d_par.text())
            bas = float(self.e_bas.text())
            alt = float(self.e_alt.text())
            n_nav = int(self.e_n_nav.text())
            c_ver = float(self.e_c_ver.text())

            if self.metodo == "simple":
                v_par = float(self.e_v_par.text())
            else:
                v_par = 0.0

            r = diseno_desarenador(
                q=q, d_par=d_par, bas=bas, alt=alt,
                v_par=v_par, c_ver=c_ver, n_nav=n_nav,
                metodo=self.metodo,
            )

            self.txt_res.setPlainText(self._formatear(r, titulo, bas, alt))

        except ValueError as ex:
            QMessageBox.critical(self, "Error de entrada", str(ex))
        except Exception as ex:
            QMessageBox.critical(self, "Error inesperado", f"{ex}")

    def _on_limpiar(self):
        self.e_titulo.clear()
        for field in (self.e_q, self.e_d_par, self.e_bas,
                      self.e_alt, self.e_v_par):
            field.clear()
        self.e_n_nav.setText("3")
        self.e_c_ver.setText("2.10")
        self.txt_res.clear()

    # ─────────────────────────────────────────────────────────────────────────
    #  FORMATEO DE RESULTADOS
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _formatear(r: dict, titulo: str, bas: float, alt: float) -> str:
        sep = "─" * 42
        icono = "✅" if r["estado"] == "OK" else "❌"
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
                f"LIMPIEZA (N-1)\n"
                f"  Caudal por nave (h')  : {r['q_limpia']} m³/s\n"
                f"  Carga vertedero (h')  : {r['h_limpia']} m\n"
                f"  Tirante total (H')    : {r['h_total_limpia']} m\n"
            )

        res += sep
        return res