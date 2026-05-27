"""
main_desa.py
============
Entry point para el diseñador de desarenadores.
Usa PySide6 en lugar de CustomTkinter.
"""

import sys

from interfaz import VentanaDesarenador
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = VentanaDesarenador()
    win.show()
    sys.exit(app.exec())
