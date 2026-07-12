"""
run_desktop.py
=============
Interfaz gráfica PySide6 para diseño de desarenadores.
Un solo archivo: interfaz + entry point.

Layout: 2 columnas (datos | resultados)
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QGroupBox, QLabel, QLineEdit, QPushButton,
    QRadioButton, QButtonGroup, QTextEdit, QFrame, QMessageBox,
)
from desarenador_hydraulics import diseno_desarenador

# ── Constantes de UI ──────────────────────────────
WIDTH  = 660
HEIGHT = 560


class VentanaDesarenador(QWidget):
    """Ventana principal con layout de 2 columnas."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diseño de Desarenador")
        self.resize(WIDTH, HEIGHT)

        # ── layout principal horizontal ──
        lm = QHBoxLayout(self)
        lm.setContentsMargins(8, 8, 8, 8)
        lm.setSpacing(8)

        # col 0: datos (fijo)
        col0 = self._build_col_datos()
        col0.setFixedWidth(280)
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

        # ── Proyecto ──────────────────────
        gb_proy = QGroupBox("Proyecto")
        form_proy = QVBoxLayout(gb_proy)
        self.e_titulo = QLineEdit()
        self.e_titulo.setPlaceholderText("Nombre del proyecto…")
        form_proy.addWidget(self.e_titulo)
        layout.addWidget(gb_proy)

        # ── Opciones de Cálculo ───────────
        gb_opc = QGroupBox("Opciones de Cálculo")
        lay_opc = QVBoxLayout(gb_opc)
        lay_opc.setSpacing(8)

        # — Velocidad límite —
        lay_opc.addWidget(QLabel("Velocidad límite del flujo:"))
        self._bg_vel = QButtonGroup(self)
        self.rb_camp = QRadioButton("Camp (estándar)")
        self.rb_camp.setChecked(True)
        self.rb_shields = QRadioButton("Shields (alternativo)")
        self._bg_vel.addButton(self.rb_camp, 0)
        self._bg_vel.addButton(self.rb_shields, 1)
        lay_opc.addWidget(self.rb_camp)
        lay_opc.addWidget(self.rb_shields)

        # separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        lay_opc.addWidget(sep)

        # — Fuente de velocidad de caída —
        lay_opc.addWidget(QLabel("Velocidad de caída (w):"))
        self._bg_w = QButtonGroup(self)
        self.rb_w_manual = QRadioButton("Manual (tablas/nomogramas)")
        self.rb_w_manual.setChecked(True)
        self.rb_w_zanke = QRadioButton("Zanke (automático)")
        self._bg_w.addButton(self.rb_w_manual, 0)
        self._bg_w.addButton(self.rb_w_zanke, 1)
        lay_opc.addWidget(self.rb_w_manual)
        lay_opc.addWidget(self.rb_w_zanke)

        # campo w manual
        self.lbl_v_par = QLabel("Vel. caída (cm/s):")
        self.e_v_par = QLineEdit()
        self.e_v_par.setToolTip("Velocidad de caída de la partícula en agua quieta\n(de tablas: Arkhangelski, Sudry, Bouvard, etc.)")
        lay_opc.addWidget(self.lbl_v_par)
        lay_opc.addWidget(self.e_v_par)

        layout.addWidget(gb_opc)

        # ── Datos de Entrada ──────────────
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

        self.e_c_ver = QLineEdit("2.00")
        self.e_c_ver.setToolTip("Coeficiente de descarga del vertedero (perfil Creager)")
        form_ent.addRow("Coef. C:", self.e_c_ver)

        self.e_bas = QLineEdit()
        self.e_bas.setToolTip("Ancho de cada nave")
        form_ent.addRow("Ancho nave (m):", self.e_bas)

        self.e_alt = QLineEdit()
        self.e_alt.setToolTip("Tirante de agua total (fondo → superficie)")
        form_ent.addRow("Tirante agua (m):", self.e_alt)

        layout.addWidget(gb_ent)

        # ── Botones ───────────────────────
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

        # ── Eventos de opciones ───────────
        self._bg_w.idToggled.connect(self._on_fuente_w_toggle)

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

    def _on_fuente_w_toggle(self, btn_id: int):
        """Muestra/oculta el campo de velocidad de caída según la fuente."""
        es_manual = btn_id == 0
        self.e_v_par.setVisible(es_manual)
        self.lbl_v_par.setVisible(es_manual)
        if not es_manual:
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

            vel_limite = "camp" if self.rb_camp.isChecked() else "shields"
            fuente_w = "manual" if self.rb_w_manual.isChecked() else "zanke"
            v_par = float(self.e_v_par.text()) if fuente_w == "manual" else 0.0

            r = diseno_desarenador(
                q=q, d_par=d_par, bas=bas, alt=alt,
                c_ver=c_ver, n_nav=n_nav,
                vel_limite=vel_limite, fuente_w=fuente_w,
                v_par=v_par,
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
        self.e_c_ver.setText("2.00")
        self.txt_res.clear()

    # ─────────────────────────────────────────────────────────────────────────
    #  FORMATEO DE RESULTADOS
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _formatear(r: dict, titulo: str, bas: float, alt: float) -> str:
        sep = "─" * 44
        icono = "✅" if r["estado"] == "OK" else "❌"
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
                f"LIMPIEZA (N-1)\n"
                f"  Caudal por nave (h')  : {r['q_limpia']} m³/s\n"
                f"  Carga vertedero (h')  : {r['h_limpia']} m\n"
                f"  Tirante total (H')    : {r['h_total_limpia']} m\n"
            )

        res += sep
        return res


# ── Entry point ────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = VentanaDesarenador()
    win.show()
    sys.exit(app.exec())
