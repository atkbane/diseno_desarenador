# Marco Teórico — Diseño de Desarenador

Documentación de las fórmulas y métodos implementados en `desarenador_hydraulics.py`. Cada sección referencia la función que materializa la fórmula.

---

## 1. Definición y clasificación

El desarenador es una estructura hidráulica que reduce la velocidad del flujo para que las partículas sólidas en suspensión decanten al fondo, desde donde son evacuadas periódicamente.

$$
\text{Desarenador} = \text{Transición de entrada} + \text{Cámara de sedimentación} + \text{Vertedero de salida} + \text{Compuerta de lavado}
$$

**Clasificación (ANA, Villón):**
- Por operación: lavado continuo / lavado intermitente
- Por velocidad: baja ($v < 1$ m/s) / alta ($v > 1$ m/s)
- Por disposición: en serie / en paralelo (varias naves)

> Fuentes: ANA §4.2, Villón cap. 6, ESHA §6.2.3

---

## 2. Geometría de la cámara

### 2.1 Bisel dinámico — `calc_bisel_height`

Fórmula empírica derivada de correlación de 8 desarenadores propios:

$$
h_{\text{bisel}} = \max(0,\; 0.32 \cdot H - 0.40) \quad [\text{m}]
$$

Redondeado a múltiplos de 0.05 m. Para tirantes $H < 1.25$ m, el bisel se anula (no se justifica geométricamente).

> Nota: el término "bisel dinámico" no aparece en la literatura clásica; es un concepto de la práctica ingenieril latinoamericana. Las memorias de cálculo (CARHUAC, CHANCAY II, SANTARI) aplican Bernoulli entre secciones para obtener el perfil de la lámina, que es el equivalente funcional.
>
> Fuentes: ANA (2015) p. 78, Villón (2001) p. 101

### 2.2 Sección transversal — `car_sec_des`

Sección rectangular arriba y trapezoidal abajo (bisel con talud 1 : 0.8, horizontal : vertical):

$$
A = b \cdot (h - h_{\text{bisel}}) + \frac{b + b_m}{2} \cdot h_{\text{bisel}}
$$

donde $b_m = b - 2 \cdot h_{\text{bisel}} \cdot \tan\theta$ es la base menor del trapecio y $\tan\theta = 0.8$.

Perímetro mojado:

$$
P = 2 \cdot (h - h_{\text{bisel}}) + b_m + 2 \cdot \sqrt{h_{\text{bisel}}^2 + (h_{\text{bisel}} \cdot 0.8)^2}
$$

Radio hidráulico: $R_h = A / P$.

> Fuentes: ANA p. 78, Villón p. 101

---

## 3. Velocidad real del flujo

Con el caudal total $Q$ repartido entre $N$ naves idénticas de ancho $b$ y tirante $h$:

### 3.1 Caudal por nave

$$
q_{\text{nave}} = \frac{Q}{N} \quad [\text{m}^3/\text{s}]
$$

### 3.2 Velocidad real

$$
v_{\text{real}} = \frac{q_{\text{nave}}}{A} \quad [\text{m/s}]
$$

donde $A$ es el área de la sección transversal de `car_sec_des`.

> Fuentes: ANA p. 79, Villón p. 104

---

## 4. Velocidad límite del flujo

La velocidad real debe ser menor que la velocidad crítica de arrastre para que las partículas no se depositen ni se resuspendan. El programa ofrece dos métodos independientes.

### 4.1 Método de Camp (1946) — `vel_CAMP`

$$
v = a \cdot \sqrt{d} \quad [\text{cm/s}] \;\;\rightarrow\;\; \text{resultado} / 100 \;\;[\text{m/s}]
$$

| Diámetro $d$ [mm] | Coeficiente $a$ |
|--------------------|-----------------|
| $d > 1.0$ mm | 36 |
| $0.1 \leq d \leq 1.0$ mm | 44 |
| $d < 0.1$ mm | 51 |

Estándar para desarenadores (ANA, Villón).

> Fuentes: ANA p. 80, Villón p. 105, Tomas Tirolesas Tabla 15.2

### 4.2 Método de Shields (1936) — `vel_critica_shields`

Velocidad máxima admisible para evitar la resuspensión del sedimento ya depositado:

$$
v_{\text{crítica}} = k_s \cdot R_h^{1/6} \cdot \sqrt{(\rho_s/\rho_w - 1) \cdot d \cdot \theta_{cr}} \quad [\text{m/s}]
$$

Donde:
- $k_s = 1/n$ = coeficiente de Strickler, $n = 0.013$ (concreto)
- $R_h$ = radio hidráulico [m]
- $\rho_s/\rho_w = 2.65$ (cuarzo)
- $\theta_{cr} = 0.03$ (Shields, incipient motion — valor conservador)

**Valores típicos de $\theta_{cr}$:**

| Régimen | $\theta_{cr}$ |
|---------|---------------|
| Turbulento liso | $> 0.035$ |
| Transición | $0.030 - 0.04$ |
| Plenamente rugoso ($R_* > 75$) | $\approx 0.06$ |

El programa usa $\theta_{cr} = 0.03$ (ver código para justificación). Extensión técnica; no es el método estándar de desarenadores.

> Fuentes: Mery §2.8, Mays cap. 6, FHWA HDS-7, Chanson cap. 7

### 4.3 Verificación

$$
\text{Si } v_{\text{real}} > v_{\text{límite}} \Rightarrow \text{FALLA}
$$

$$
\text{Margen} = \left(1 - \frac{v_{\text{real}}}{v_{\text{límite}}}\right) \cdot 100 \quad [\%]
$$

---

## 5. Velocidad de caída de la partícula ($w$)

Velocidad terminal en agua quieta. El programa ofrece dos fuentes independientes.

### 5.1 Manual (tablas) — ingreso directo

El usuario ingresa $w$ en cm/s (de tablas como Arkhangelski, Sudry, Bouvard) y el programa convierte a m/s.

**Tabla de Arkhangelski (referencia):**

| $d$ [mm] | $w$ [cm/s] |
|----------|------------|
| 0.05 | 0.178 |
| 0.10 | 0.692 |
| 0.25 | 2.700 |
| 0.50 | 5.400 |
| 1.00 | 9.44 |
| 3.00 | 19.25 |

> Fuentes: ANA Tabla 4, Villón Tabla 6.3, Tomas Tirolesas (citando Krochin 1978)

### 5.2 Fórmula de Zanke (1977) — `vel_caida_particula`

Fórmula unificada válida para régimen laminar, de transición y turbulento:

$$
D_* = d \cdot \left[ \frac{(\rho_s/\rho_w - 1) \cdot g}{\nu^2} \right]^{1/3}
$$

$$
w_o = \frac{11 \cdot \nu}{d} \cdot \left( \sqrt{1 + 0.01 \cdot D_*^3} - 1 \right) \quad [\text{m/s}]
$$

Donde $d$ está en [m] y $\nu = 1.0 \times 10^{-6}$ m²/s (agua a 20 °C).

> Fuentes: ESHA §6.2.3 (fórmula empírica de Zanke). Técnicamente válida aunque no aparece en ANA/Villón.

### 5.3 Otros métodos (referencia, no implementados)

| Método | Fórmula | Rango válido |
|--------|---------|--------------|
| Stokes | $w_s = (s-1) \cdot g \cdot d^2 / (18\nu)$ | $d \leq 0.1$ mm |
| Owens | $w = k \cdot \sqrt{d \cdot (\rho_s - 1)}$ | Variable |
| Scotti-Foglieni | $w = 3.8\sqrt{d} + 8.3d$ | General |
| Sudry | Nomograma $w = f(d, \rho_s)$ | General |
| Sellerio | Nomograma | General |

> Fuentes: Depeweg §5.3, Chanson §7.3, Villón Fig. 6.3-6.4

---

## 6. Corrección por turbulencia (Bestelli / Levin) — `w_en_agua_fluyendo`

En agua fluyendo, la velocidad de caída efectiva es menor que en agua quieta por la turbulencia:

$$
w_f = w - \alpha \cdot v \quad [\text{m/s}]
$$

$$
\alpha = \frac{0.132}{\sqrt{h}}
$$

Donde $h$ es el tirante [m] y $v$ la velocidad horizontal del flujo [m/s].

Forma explícita usada por el programa:

$$
w_f = w - \frac{0.132}{\sqrt{h}} \cdot v \quad [\text{m/s}]
$$

Las 9 memorias de cálculo consultadas (CARHUAC, CHANCAY II, H-1, MARAÑÓN, RUNATULLO I, RUNATULLO III, SANTARI, ZANA, HUASCOY) usan exactamente esta expresión.

> Fuentes: ANA p. 83 (citando Levin + Bestelli), Villón p. 111, ESHA §6.2.3

---

## 7. Longitud de sedimentación — `lon_sed`

A partir de la velocidad de caída efectiva $w_f$ (calculada en §6):

$$
L = \frac{v_{\text{real}} \cdot h}{w_f} \quad [\text{m}]
$$

Esta es la forma implementada en el código (corrección de turbulencia explícita vía $w_f$). La forma histórica equivalente con corrección implícita es:

$$
L = \frac{h^{3/2} \cdot v_{\text{real}}}{\sqrt{h} \cdot w - 0.132 \cdot v_{\text{real}}}
$$

Ambas son matemáticamente idénticas; el programa usa la primera por claridad (se ve la corrección de turbulencia como un paso separado).

> Nota: la longitud teórica se mayoraba tradicionalmente con un factor de seguridad $K$ (ANA Tabla 6: 1.25 a $v=0.20$ m/s, 1.50 a $v=0.30$ m/s, 2.00 a $v=0.50$ m/s). El programa **no aplica** este factor — usa la longitud directa de Bestelli.
>
> Fuentes: ANA p. 82-83, Villón p. 109-111

---

## 8. Vertedero de salida (Creager) — `des_cre`

### 8.1 Ecuación de descarga

$$
Q = C \cdot L \cdot h^{3/2}
$$

Despejando la carga sobre la cresta:

$$
h = \left( \frac{Q}{C \cdot L} \right)^{2/3} \quad [\text{m}]
$$

Donde $L$ es la longitud del vertedero (= ancho de la nave, $b$) y $C$ el coeficiente de descarga.

### 8.2 Coeficientes de descarga

| Perfil | $C$ |
|--------|-----|
| Creager (cresta redondeada, programa) | 2.00 |
| Creager (WES standard) | 1.84 – 2.20 |
| Cresta aguda (Francis) | 1.84 |

### 8.3 Altura de la cresta

$$
P_{\text{cresta}} = h - h_{\text{vertedero}}
$$

> Fuentes: ANA p. 77, Villón p. 102, Mery §2.16, Chow cap. 7, Krochin §5.3

---

## 9. Condición operativa (limpieza de una nave, N-1)

Cuando una nave está fuera de servicio por mantenimiento, el caudal se reparte entre las $N-1$ naves restantes. Esta verificación es **informativa**: no altera las dimensiones de diseño ($b$, $h$, $L$).

$$
Q_{\text{limpia}} = \frac{Q}{N - 1}
$$

Con la misma $b$ y $h$ del diseño, se recalcula:

- **Carga sobre el vertedero** (mayor, porque $Q_{\text{limpia}} > Q/N$):

$$
h_{\text{limpia}} = \left( \frac{Q_{\text{limpia}}}{C \cdot b} \right)^{2/3}
$$

- **Nivel de superficie libre** en las naves activas:

$$
H_{\text{total, limpia}} = P_{\text{cresta}} + h_{\text{limpia}}
$$

- **Velocidad real operativa** con la sobrecarga:

$$
v_{\text{real, limpia}} = \frac{Q_{\text{limpia}}}{A}
$$

Estos resultados permiten identificar la altura mínima de las paredes del desarenador para que la condición N-1 no genere rebalse. La limpieza de una nave es un evento breve (~1 h), por lo que **no se recalcula la longitud de sedimentación** para esta condición.

---

## 10. Supuestos y constantes

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| $n$ Manning | 0.013 | Concreto (ANA estándar) |
| $\rho_s$ | 2.65 g/cm³ | Cuarzo (sedimento típico) |
| $\rho_w$ | 1.00 g/cm³ | Agua dulce |
| $\nu$ | $1.0 \times 10^{-6}$ m²/s | Agua a 20 °C |
| $\theta_{cr}$ (Shields) | 0.03 | Incipient motion (conservador) |
| Talud bisel | 1 : 0.8 (H : V) | Geométrico estándar |
| $C$ vertedero | 2.00 | Perfil Creager |
| Flujo | Uniforme | Dentro de cada nave |

---

## 11. Referencias

**Fuentes bibliográficas** (consultadas en biblioteca personal):

1. ANA (2015). *Criterios de Diseño de Obras Hidráulicas.*
2. Villón, M. (2001). *Diseño de Estructuras Hidráulicas.*
3. Krochin, S. *Diseño Hidráulico.*
4. Mery, H. *Hidráulica Aplicada al Diseño de Obras.*
5. Novak, P. et al. *Hydraulic Structures.*
6. ESHA. *Guía para el Desarrollo de una Pequeña Central Hidroeléctrica.*
7. Chanson, H. *Hydraulics of Open Channel Flow.*
8. Chow, V.T. *Hidráulica de Canales Abiertos.*
9. Liria, J. *Hydraulic Canals.*
10. Depeweg, H. et al. *Sediment Transport in Irrigation Canals.*
11. Mays, L. *Hydraulic Design Handbook.*
12. Tomas Tirolesas. *Tomas Tirolesas.*
13. FHWA. *Sizing Riprap (SPR-260).*

**Memorias de cálculo consultadas (9 proyectos):** CARHUAC, CHANCAY II, H-1, MARAÑÓN, RUNATULLO I, RUNATULLO III, SANTARI, ZANA, HUASCOY.
