# Diseño de Desarenador — Web

Calcula las dimensiones principales de un desarenador para centrales hidroeléctricas usando dos métodos hidráulicos: **Simple** (Camp) y **Complejo** (Zanke + Shields).  
Pensado para ingenieros civiles, estudiantes o profesionales que necesiten dimensionar naves de sedimentación con bisel dinámico.

---

## 🌐 Acceso web

Abre la aplicación directamente desde el navegador, sin instalación:  
👉 [https://atkbane.github.io/diseno_desarenador](https://atkbane.github.io/diseno_desarenador)

> Funciona completamente en el navegador. No envía datos a ningún servidor.

---

## 📐 Base teórica

### Fórmulas principales

| Concepto / Método | Expresión | Parámetros clave |
|-------------------|-----------|------------------|
| Velocidad límite (Camp) | `v = a · √d`  (a = 36, 44 ó 51 según d) | d: diámetro partícula [mm] |
| Velocidad crítica (Shields) | `v_crítica = ks · R^(1/6) · √((ρs/ρw − 1) · d · 0.03)` | ks = 1/n, R: radio hidráulico |
| Velocidad caída (Zanke) | `w_o = 11 · ν/d · (√(1 + 0.01·D³) − 1)` | D: diámetro adimensional |
| Corrección por turbulencia (Sokolov) | `w_f = w − 0.132/√h · v` | h: tirante, v: velocidad flujo |
| Longitud simple (Bestelli/Sokolov/Velikanov) | `L = h^(3/2) · v / (√h·w − 0.132·v)` | v, h, w |
| Longitud compleja | `L = V · h / w_f` | v, h, w_f (ya corregida) |
| Vertedero cresta redondeada | `h = (Q / (C·L))^(2/3)` | C ≈ 2.10 |
| Bisel dinámico | `alt_bisel = redondeo(0.32·H − 0.40)` | H: tirante total |

### Supuestos del modelo

- Sección transversal con bisel inferior de talud 1:0.8 (horizontal:vertical).
- Coeficiente de Manning para concreto: n = 0.013 s/m^(1/3).
- Densidad del sedimento: 2.65 g/cm³ (cuarzo).
- Densidad del agua: 1.00 g/cm³.
- Viscosidad cinemática del agua a 20 °C: 1.3×10⁻⁶ m²/s.
- Coeficiente de Shields: 0.03 (condiciones típicas de desarenador).
- Flujo en régimen uniforme dentro de cada nave.

---

## ✨ Características

- **Dos métodos de cálculo** — Simple (Camp + Bestelli) o Complejo (Zanke + Shields + Sokolov), seleccionables con radio buttons.
- **Velocidad de caída condicional** — campo visible solo en método Simple; en método Complejo se calcula automáticamente.
- **Validación en tiempo real** — campos resaltados en rojo si los valores no son válidos.
- **Resultados formateados** — misma presentación que la versión de escritorio (separadores, íconos ✅/❌, secciones VELOCIDADES, DIMENSIONES, VERTEDERO, LIMPIEZA N-1).
- **Limpieza (N-1)** — si hay más de 1 nave, se calcula la condición de limpieza (una nave fuera de servicio).
- **Interfaz responsiva** — dos columnas en escritorio, apilada en móviles.
- **Sin instalación** — todo corre en el navegador con Pyodide. No requiere servidor.

---

## 🧪 Cómo usar

1. **Selecciona el método** — Simple (ingresas velocidad de caída) o Complejo (se calcula todo).
2. **Ingresa los datos** — Caudal, diámetro de partícula, dimensiones de la nave, coeficiente C del vertedero y número de naves.
3. **Presiona "Calcular"** — Pyodide se carga automáticamente la primera vez (~5–10 s). Los resultados aparecen en la columna derecha.

Para empezar de nuevo, presiona **"Limpiar"**.

---

## 🛠️ Tecnologías

- [Python](https://python.org) — Lógica de cálculo hidráulico (numpy no requerido, solo math).
- [Pyodide v0.26.4](https://pyodide.org) — Python en el navegador (via CDN).
- HTML5 / CSS3 / JavaScript (vanilla) — Interfaz de usuario.
- [GitHub Pages](https://pages.github.com) — Hosting gratuito.

---

## 📁 Estructura del proyecto

```
diseno-desarenador-web/
├── desarenador_hydraulics.py   # Lógica del modelo (fórmulas, validación)
├── web_main.py                 # Puente Python/Pyodide (formatea resultados)
├── index.html                  # Interfaz web
├── README.md
└── LICENSE
```

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

Creado por [Aldo Tapia](https://github.com/atkbane) – ingeniero civil hidráulico.