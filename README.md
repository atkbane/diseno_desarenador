# Diseño de Desarenador

Calcula las dimensiones principales de un desarenador para centrales hidroeléctricas con dos opciones independientes: **velocidad límite** (Camp/Shields) y **fuente de w** (Manual/Zanke).  
Pensado para ingenieros civiles, estudiantes o profesionales que necesiten dimensionar naves de sedimentación con bisel dinámico.

---

## 🌐 Acceso web

Abre la aplicación directamente desde el navegador, sin instalación:  
👉 [https://atkbane.github.io/vaciado_desarenador/](https://atkbane.github.io/vaciado_desarenador/)

> Funciona completamente en el navegador. No envía datos a ningún servidor.

---

## 📐 Base teórica

### Opciones de cálculo

El programa ofrece dos opciones independientes:

**1. Velocidad límite del flujo:**
| Opción | Fórmula | Fuente |
|--------|---------|--------|
| **Camp** (estándar) | `v = a·√d` (a = 36, 44 ó 51 según d) | ANA p. 80, Villon p. 105 |
| **Shields** (alternativo) | `v_crítica = ks·R^(1/6)·√((ρs/ρw−1)·d·0.03)` | Shields (1936) |

**2. Velocidad de caída de la partícula (w):**
| Opción | Método | Fuente |
|--------|--------|--------|
| **Manual** | Usuario ingresa w de tablas/nomogramas | Arkhangelski, Sudry, Bouvard |
| **Zanke** | Cálculo automático desde d | Zanke (1977) |

**Corrección por turbulencia:** Siempre se aplica Bestelli/Levin (`wf = w − 0.132/√h · v`).

### Fórmulas principales

| Concepto / Método | Expresión | Parámetros clave |
|-------------------|-----------|------------------|
| Velocidad límite (Camp) | `v = a · √d`  (a = 36, 44 ó 51 según d) | d: diámetro partícula [mm]; rangos: <0.1, 0.1-1, >1 |
| Velocidad crítica (Shields) | `v_crítica = ks · R^(1/6) · √((ρs/ρw − 1) · d · 0.03)` | ks = 1/n, R: radio hidráulico |
| Velocidad caída (Zanke) | `w_o = 11 · ν/d · (√(1 + 0.01·D³) − 1)` | D: diámetro adimensional |
| Corrección por turbulencia (Sokolov) | `w_f = w − 0.132/√h · v` | h: tirante, v: velocidad flujo |
| Longitud simple (Bestelli/Sokolov/Velikanov) | `L = h^(3/2) · v / (√h·w − 0.132·v)` | v, h, w |
| Longitud compleja | `L = V · h / w_f` | v, h, w_f (ya corregida) |
| Vertedero cresta redondeada | `h = (Q / (C·L))^(2/3)` | C = 2.00 (Creager) |
| Bisel dinámico | `alt_bisel = redondeo(0.32·H − 0.40)` | H: tirante total |

### Supuestos del modelo

- Sección transversal con bisel inferior de talud 1:0.8 (horizontal:vertical).
- Coeficiente de Manning para concreto: n = 0.013 s/m^(1/3).
- Densidad del sedimento: 2.65 g/cm³ (cuarzo).
- Densidad del agua: 1.00 g/cm³.
- Viscosidad cinemática del agua a 20 °C: 1.0×10⁻⁶ m²/s.
- Coeficiente de Shields: 0.03 (condiciones típicas de desarenador).
- Flujo en régimen uniforme dentro de cada nave.

> 📖 Detalle completo de fórmulas, derivaciones, referencias bibliográficas y mapeo a funciones del código: ver [`marco_teorico.md`](./marco_teorico.md).

---

## ✨ Características

- **Dos opciones independientes** — Velocidad límite (Camp/Shields) y Fuente de w (Manual/Zanke).
- **4 combinaciones posibles** — Camp+Manual, Camp+Zanke, Shields+Manual, Shields+Zanke.
- **Velocidad de caída condicional** — campo visible solo cuando se selecciona "Manual".
- **Validación en tiempo real** — campos resaltados en rojo si los valores no son válidos.
- **Resultados formateados** — secciones VELOCIDADES, DIMENSIONES, VERTEDERO, LIMPIEZA N-1.
- **Limpieza (N-1)** — si hay más de 1 nave, se calcula la condición de limpieza.
- **Interfaz responsiva** — dos columnas en escritorio, apilada en móviles.

---

## 🧪 Cómo usar

1. **Selecciona la velocidad límite** — Camp (estándar) o Shields (alternativo).
2. **Selecciona la fuente de w** — Manual (ingresas w de tablas) o Zanke (se calcula automáticamente).
3. **Ingresa los datos** — Caudal, diámetro de partícula, dimensiones de la nave, coeficiente C del vertedero y número de naves.
4. **Presiona "Calcular"** — Los resultados aparecen en la columna derecha.

Para empezar de nuevo, presiona **"Limpiar"**.

---

## 🛠️ Tecnologías

- [Python](https://python.org) — Lógica de cálculo hidráulico (solo `math`, sin numpy).
- [Pyodide](https://pyodide.org/) — Ejecución de Python en el navegador.
- [Plotly](https://plotly.com/) — Gráficos interactivos (si aplica).

---

## 📁 Estructura del proyecto

```
diseno_desarenador/
├── desarenador_hydraulics.py   # Lógica de cálculo (constantes, fórmulas)
├── web_bridge.py               # Puente Python/Pyodide (entry point web)
├── index.html                  # Interfaz web
├── marco_teorico.md            # Documentación teórica completa
├── .old/                       # Código descartado (no se mantiene)
└── README.md
```

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

Creado por [Aldo Tapia](https://github.com/atkbane) – ingeniero civil hidráulico.