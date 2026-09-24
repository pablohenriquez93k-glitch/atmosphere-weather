"""Genera los .pfx de AtmosphereWeather, variantes.json y parametros.json.

Uso: python scripts/generar_pfx.py
- Todo lo ajustable esta en el bloque PARAMETROS de abajo: cambiar ahi y correr.
- Agregar una variante = agregar una entrada a su lista y correr.
- variantes.json (conteos) y parametros.json (altura de nubes y costo real
  en particulas de cada variante) los lee el JS: no hay que tocar config.js.
- Cambios en .pfx = reinicio completo del juego (F5 no recarga specs).

Todo parte de combos YA CONFIRMADOS en juego (ver docs/estado_actual_mod.md):
nubes, lluvia (RainTest), nieve (SnowTest), rayos horneados, lava (LavaTest).
Respaldo previo a la limpieza del 2026-09-23 (mecanismos viejos, pruebas):
respaldos/2026-09-23_antes_limpieza/.
"""
import json
import math
import os

# =============================== PARAMETROS ===============================
# Distancias en yardas a radio de planeta 500 (el puppet escala con el radio).

ALTURA_NUBES = 120        # altura de las nubes sobre el suelo
MARGEN_CANON = 16         # caida extra (15 m) para llegar al fondo de canones
EMISOR_OFFSET_Y = 12      # la precipitacion nace esto por debajo del centro de la nube
EMISOR_RADIO = 30         # radio horizontal del area de precipitacion bajo cada cuerpo (era 18; nube radio 40)
EMISOR_TASA_MULT = 2.0    # tasas de lluvia/nieve x esto: compensa el area x2.8 del radio 30 (algo menos densa)
PRECIP_EXTREMO = 1.5      # calidad Extreme del menu: familias *_x15 con tasas x esto
MARGEN_PARTICULAS = 1.1   # tope de particulas = tasa x vida x esto

# Lluvia aditiva sin dataChannelFormat (precedente vanilla
# default_commander_landing.pfx). La de RainTest (particle_transparent +
# PositionColorAndAlignVector) daba microtiron al crear el puppet.
LLUVIA_COLOR = (0.22, 0.22, 0.25)   # aditivo: suma luz -> color bajo = raya tenue

# Nubes (emision continua: cada bocanada vive NUBE_VIDA s con fundido)
NUBE_VIDA = 30.0
NUBE_VIDA_RNG = 8.0
# Cada puppet de nube emite NUBE_GENERACION s y se detiene solo; el JS crea la
# generacion siguiente y mueve la vieja hasta que sus bocanadas se apagan.
# (Borrar o cambiar fx de un puppet deja sus particulas huerfanas y quietas.)
# Prueba B microtiron: 30 -> 120 (cada relevo crea puppets; crear = tiron).
NUBE_GENERACION = 120.0
# Forma (anti "palomitas", 2026-09-23): cuerpo ancho y chato, bocanadas grandes
# y translucidas que se funden + velo enorme casi transparente para el borde.
# (+Y local = abajo: offsetY > 0 baja la capa.)
# Prueba 1 (30 / 12x34 / alfa x0.7): seguian manchas opacas con borde de
# coliflor (softSmoke). Prueba 2: pocas bocanadas ENORMES y muy translucidas
# que se solapan mucho -> el borde se pierde en la superposicion.
NUBE_ANCHO = 40.0         # radio horizontal (era 18)
NUBE_ALTO = 4.0           # radio vertical (era 6): base mas plana
# Prueba 4 (con 'lit'): 9x90 / 6x55 / velo 160 salia borroso tipo niebla con
# manchas redondas sueltas -> mas bocanadas, mas chicas, algo mas opacas.
NUBE_ALFA_MULT = 0.6      # opacidad de nucleo/relleno
NUBE_NUCLEO = (14, 55, 18)          # bocanadas, tamano, rango (era 8, 26, 9)
NUBE_RELLENO = (8, 35, 12)          # (era 5, 16, 6)
NUBE_VELO = (3, 120, 25, 0.08)      # bocanadas, tamano, rango, alfa
# Volumen: base gris-azulada abajo, cima mas blanca arriba (multiplica el color).
NUBE_TINTE_BASE = (0.85, 0.85, 0.87)   # neutro: con 'lit' el azul (0.95) salia chillon de noche
NUBE_TINTE_CIMA = (1.0, 1.0, 1.0)
# Shader: particle_transparent_lit + simpleSmokeSingle con curva "rgb" +
# dataChannelFormat (calcado de vanilla titan_structure_death.pfx, Atlas 2.1b-d).
NUBE_BASE_Y = 2.0         # nucleo un poco abajo
NUBE_CIMA_Y = -5.0        # relleno arriba

# Lluvia
LLUVIA_VEL = 86           # yd/s de caida
LLUVIA_VEL_RNG = 8
LLUVIA_VIENTO_TASA = 90   # gotas/s por cuerpo (x EMISOR_TASA_MULT)
VENTARRON_TASA = 110
VIRGA_TASA = 60
VIRGA_FRAC = 0.45         # fraccion de la caida antes de evaporarse

# Nieve
NIEVE_VEL = 14            # yd/s de caida
NIEVE_VEL_RNG = 4
NIEVE_TASAS = [20, 40, 70]         # copos/s por cuerpo: fina -> intensa

# Viento (desplazamiento de gotas y copos al caer, accelX/accelZ)
# Se generan NIVELES_VIENTO fuerzas en [base - rango, base + rango]; el JS
# elige una al azar por cuerpo de nube.
VIENTO_LLUVIA = 18.0      # 6 original (RainTest) x3
VIENTO_LLUVIA_RANGO = 6.0 # x1 -> 12 / 18 / 24
VIENTO_VENTARRON_MULT = 2.0   # desierto lloviendo: aire caliente + frio
VIENTO_NIEVE = 0.48
VIENTO_NIEVE_RANGO = 0.16
NIVELES_VIENTO = 3
# ==========================================================================

# Rutas relativas al repo: este script vive en <repo>/scripts (excluido del zip).
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD_ID = "com.pa.pabloandclaude.atmosphereweather"
MOD_DIR = REPO
SPEC_DIR = os.path.join(MOD_DIR, "pa", "effects", "specs", "atmosphereweather")
UI_DIR = os.path.join(MOD_DIR, "ui", "mods", MOD_ID)
# Fuentes de lava: copia de los .pfx del mod de prueba LavaTest (cerrado).
LAVA_SRC = os.path.join(REPO, "scripts", "fuentes_lava")

TEX = "/pa/effects/textures/particles/"

# Caida completa: desde donde nace la precipitacion hasta el fondo de un canon.
CAIDA = ALTURA_NUBES - EMISOR_OFFSET_Y + MARGEN_CANON


def vida_caida(vel, frac=1.0):
    return round(CAIDA * frac / vel, 3)


def tope(tasa, vida, vida_rng):
    return int(math.ceil(tasa * (vida + vida_rng) * MARGEN_PARTICULAS))


# ---------------- nubes ----------------
def nube(rgb, a1, a2):
    r, g, b = rgb
    def capa(label, rx, ry, oy, size, size_rng, n, alpha, tint):
        tr, tg, tb = tint
        c = [min(255, int(round(v * 255))) for v in (r * tr, g * tg, b * tb)]
        a = int(round(alpha * 255))
        spec = {"shader": "particle_transparent_lit", "facing": "Camera",
                "rgb": [[0.0, 1, c + [0]], [0.2, 1, c + [a]], [0.8, 1, c + [a]], [1.0, 1, c + [0]]],
                "baseTexture": TEX + "simpleSmokeSingle.papa",
                "dataChannelFormat": "PositionAndColor"}
        return {
            "label": label,
            "spec": spec,
            "useWorldSpace": False,
            "type": "SHELL",
            "offsetY": oy,
            "offsetRangeX": rx, "offsetRangeY": ry, "offsetRangeZ": rx,
            "velocityRangeX": 0.05, "velocityRangeY": 0.05, "velocityRangeZ": 0.05,
            "velocity": 1e-05,
            "sizeX": size, "sizeRangeX": size_rng,
            "rotationRange": 3.1415, "rotationRateRange": 0.0,
            "emissionRate": round(n / NUBE_VIDA, 4), "maxParticles": n + 3,
            "lifetime": NUBE_VIDA, "lifetimeRange": NUBE_VIDA_RNG, "endDistance": -1,
            "emitterLifetime": NUBE_GENERACION,
            # True: si el planeta muere (o purga tras F5) la nube se va de golpe.
            # En el relevo normal no se nota: el fantasma se borra con sus
            # particulas ya muertas (clima.js retirarNube).
            "killOnDeactivate": True, "bLoop": False,
        }
    nn, ns, nr = NUBE_NUCLEO
    rn, rs, rr = NUBE_RELLENO
    vn, vs, vr, va = NUBE_VELO
    m = NUBE_ALFA_MULT
    return {"emitters": [
        capa("velo", NUBE_ANCHO * 1.2, NUBE_ALTO, 0.0, vs, vr, vn, va, NUBE_TINTE_BASE),
        capa("nucleo", NUBE_ANCHO, NUBE_ALTO, NUBE_BASE_Y, ns, nr, nn, round(a1 * m, 3), NUBE_TINTE_BASE),
        capa("relleno", NUBE_ANCHO * 0.65, NUBE_ALTO * 1.5, NUBE_CIMA_Y, rs, rr, rn, round(a2 * m, 3), NUBE_TINTE_CIMA),
    ]}

# var01 blanca fina -> var05 gris oscura de tormenta
NUBES = [
    nube((1.0, 1.0, 1.05), 0.45, 0.32),
    nube((1.0, 1.0, 1.05), 0.55, 0.40),
    nube((0.80, 0.80, 0.85), 0.60, 0.45),
    nube((0.60, 0.60, 0.64), 0.66, 0.50),
    nube((0.40, 0.40, 0.44), 0.72, 0.56),
]


# ---------------- viento ----------------
def fuerzas(base, rango):
    if NIVELES_VIENTO == 1:
        return [base]
    return [base - rango + 2 * rango * i / (NIVELES_VIENTO - 1) for i in range(NIVELES_VIENTO)]

def rosa(fn, a):
    """8 direcciones locales (0, 45, ... 315 grados desde +X hacia +Z)."""
    return [fn((a * math.cos(math.radians(45 * k)), a * math.sin(math.radians(45 * k)))) for k in range(8)]

def con_viento(pfx, accel):
    if accel != (0.0, 0.0):
        # Ejes LOCALES del puppet (Atlas 3.6: rumbo de +X = 270 - lon, +Z = +X + 90).
        pfx["emitters"][0]["accelX"] = round(accel[0], 3)
        pfx["emitters"][0]["accelZ"] = round(accel[1], 3)
    return pfx


# ---------------- lluvia (tearDrop, aditiva) ----------------
LLUVIA_VIDA = vida_caida(LLUVIA_VEL)
LLUVIA_VIDA_RNG = 0.15

def lluvia(tasa, accel, vida=LLUVIA_VIDA, mult=1.0):
    tasa = max(1, round(tasa * EMISOR_TASA_MULT * mult, 2))
    # Aditivo: el fundido va en el color (color 0 = invisible).
    c = LLUVIA_COLOR
    f = [[0.0, 0.0], [0.15, 1.0], [0.85, 1.0], [1.0, 0.0]]
    spec = {"shader": "particle_add", "facing": "velocity",
            "red": [[t, round(v * c[0], 3)] for t, v in f],
            "green": [[t, round(v * c[1], 3)] for t, v in f],
            "blue": [[t, round(v * c[2], 3)] for t, v in f],
            "baseTexture": TEX + "tearDrop.papa"}
    return con_viento({"emitters": [{
        "label": "lluvia",
        "spec": spec,
        "useWorldSpace": False,
        "type": "CYLINDER_Y",
        "offsetRangeX": EMISOR_RADIO, "offsetRangeZ": EMISOR_RADIO,
        "offsetY": EMISOR_OFFSET_Y, "offsetRangeY": 8,
        "velocityY": 1, "velocity": LLUVIA_VEL, "velocityRange": LLUVIA_VEL_RNG,
        "gravity": 0, "drag": 1,
        "sizeX": 0.18, "sizeRangeX": 0.06, "sizeY": 3.2, "sizeRangeY": 0.8,
        "lifetime": vida, "lifetimeRange": LLUVIA_VIDA_RNG,
        "emissionRate": tasa, "maxParticles": tope(tasa, vida, LLUVIA_VIDA_RNG),
        # False: al borrar el puppet las gotas ya en el aire terminan de caer.
        "bLoop": True, "killOnDeactivate": False, "endDistance": 3000,
    }]}, accel)

VENTARRON = (VIENTO_LLUVIA * VIENTO_VENTARRON_MULT, VIENTO_LLUVIA_RANGO * VIENTO_VENTARRON_MULT)

def familias_lluvia(m):
    """Orden: fuerza-mayor (var01-08 fuerza 1, 09-16 fuerza 2, ...)."""
    return {
        "lluvia_viento": [v for f in fuerzas(VIENTO_LLUVIA, VIENTO_LLUVIA_RANGO)
                          for v in rosa(lambda ac: lluvia(LLUVIA_VIENTO_TASA, ac, mult=m), f)],
        "lluvia_ventarron": [v for f in fuerzas(*VENTARRON)
                             for v in rosa(lambda ac: lluvia(VENTARRON_TASA, ac, mult=m), f)],
        # Virga: se evapora antes de tocar el suelo (fuerza de desierto = ventarron).
        "virga_viento": [v for f in fuerzas(*VENTARRON)
                         for v in rosa(lambda ac: lluvia(VIRGA_TASA, ac, vida=vida_caida(LLUVIA_VEL, VIRGA_FRAC), mult=m), f)],
    }


# ---------------- nieve (SnowTest: particle_transparent_lit + dot) ----------------
NIEVE_VIDA = vida_caida(NIEVE_VEL)
NIEVE_VIDA_RNG = 1.5

def nieve(tasa, accel, mult=1.0):
    tasa = max(1, round(tasa * EMISOR_TASA_MULT * mult, 2))
    return con_viento({"emitters": [{
        "label": "nieve",
        "spec": {"shader": "particle_transparent_lit", "facing": "Camera",
                 "red": 0.95, "green": 0.95, "blue": 0.97,
                 "alpha": [[0.0, 0.0], [0.1, 0.65], [0.85, 0.65], [1.0, 0.0]],
                 "baseTexture": TEX + "dot.papa"},
        "useWorldSpace": False,
        "type": "CYLINDER_Y",
        "offsetRangeX": EMISOR_RADIO, "offsetRangeZ": EMISOR_RADIO,
        "offsetY": EMISOR_OFFSET_Y, "offsetRangeY": 8,
        "velocityY": 1, "velocity": NIEVE_VEL, "velocityRange": NIEVE_VEL_RNG,
        "gravity": 0, "drag": 1,
        "sizeX": 0.5, "sizeRangeX": 0.15, "sizeY": 0.5, "sizeRangeY": 0.15,
        "rotationRange": 3.4, "rotationRateRange": 1,
        "lifetime": NIEVE_VIDA, "lifetimeRange": NIEVE_VIDA_RNG,
        "emissionRate": tasa, "maxParticles": tope(tasa, NIEVE_VIDA, NIEVE_VIDA_RNG),
        "bLoop": True, "killOnDeactivate": False, "endDistance": 3000,
    }]}, accel)

def familia_nieve(m):
    """Orden: intensidad-mayor, luego fuerza, luego 8 direcciones."""
    return [v for t in NIEVE_TASAS
            for f in fuerzas(VIENTO_NIEVE, VIENTO_NIEVE_RANGO)
            for v in rosa(lambda ac, t=t: nieve(t, ac, m), f)]

PRECIP = dict(familias_lluvia(1.0), nieve_viento=familia_nieve(1.0))
PRECIP_X15 = {k + "_x15": v for k, v in
              dict(familias_lluvia(PRECIP_EXTREMO), nieve_viento=familia_nieve(PRECIP_EXTREMO)).items()}


# ---------------- rayos HORNEADOS (sin movePuppet) ----------------
# Cada .pfx es un rayo completo ya dibujado: cada tramo es un emisor fijo
# (particle_add + facing velocity + dot.papa, patron vanilla de
# default_commander_landing / meteor_impact_explosion) en el centro del tramo,
# orientado por velocityX/Y/Z y con largo = sizeY. Todo el rayo aparece a la
# vez tras un "delay" horneado al azar (el JS lo crea en el ciclo y el delay
# reparte los rayos en el tiempo). Ejes locales del puppet: +Y = abajo.
# Origen del puppet: base de la nube (tierra) o centro de la nube (nube).
import random

RAYOH_VARIANTES = 20            # por familia (tierra / nube)
RAYOH_DELAY = (0.0, 3.6)        # s: momento del rayo dentro del ciclo de 4 s
# s que dura visible cada tramo: el canal titila (3 golpes); ramas y ramitas
# solo brillan en el primer golpe, como en un rayo real.
RAYOH_VIDA = {"canal": 0.7, "rama": 0.3, "ramita": 0.25, "cian": 0.5, "naranja": 0.6}
RAYOH_SOLAPE = 1.03             # largo extra del tramo (aditivo: mas solape = uniones brillantes)
RAYOH_ESPESOR_NUBE = 6          # = base del nucleo de nubes (NUBE_BASE_Y + NUBE_ALTO)
RAYOH_SEMILLA = 1234

RAYOH_ESTILO = {  # grosor, curvas de color (HDR), del LightningTest aprobado
    # Canal: 3 golpes de retorno DENTRO de la curva (vida 0.7 s: golpes en
    # 0 / 0.14 / 0.31 s), como el titileo real (3-4 golpes, 40-150 ms entre
    # ellos). En la curva y no duplicando tramos: menos emisores = menos tiron
    # al crear el puppet (probado: 4 rayos x ~45 emisores congelan).
    "canal":  (0.6, [[0, 3], [0.1, 0.9], [0.2, 2.6], [0.33, 0.8], [0.45, 2.0], [0.6, 0.7], [1, 0]],
                    [[0, 3], [0.1, 1.0], [0.2, 2.7], [0.33, 0.9], [0.45, 2.1], [0.6, 0.8], [1, 0]],
                    [[0, 4], [0.1, 1.4], [0.2, 3.4], [0.33, 1.3], [0.45, 2.8], [0.6, 1.1], [1, 0.4]]),
    # Cortocircuitos de metal: chisporroteo (varios pulsos rapidos).
    "cian":    (0.25, [[0, 0.5], [0.2, 0.15], [0.35, 0.5], [0.55, 0.1], [0.7, 0.4], [1, 0]],
                      [[0, 2.4], [0.2, 0.7], [0.35, 2.4], [0.55, 0.5], [0.7, 1.9], [1, 0]],
                      [[0, 3.2], [0.2, 1.0], [0.35, 3.2], [0.55, 0.7], [0.7, 2.6], [1, 0.3]]),
    "naranja": (0.4,  [[0, 3.4], [0.2, 1.0], [0.35, 3.4], [0.55, 0.8], [0.7, 2.7], [1, 0.2]],
                      [[0, 1.8], [0.2, 0.5], [0.35, 1.8], [0.55, 0.4], [0.7, 1.4], [1, 0]],
                      [[0, 0.4], [0.2, 0.1], [0.35, 0.4], [0.55, 0.1], [0.7, 0.3], [1, 0]]),
    "rama":   (0.35, [[0, 1.8], [0.15, 1.0], [1, 0]], [[0, 1.9], [0.15, 1.1], [1, 0]], [[0, 2.6], [0.15, 1.6], [1, 0.3]]),
    "ramita": (0.2, [[0, 1.2], [0.15, 0.7], [1, 0]], [[0, 1.3], [0.15, 0.75], [1, 0]], [[0, 1.9], [0.15, 1.1], [1, 0.2]]),
}

def _escala_curva(c, k):
    return [[t, round(v * k, 3)] for t, v in c]

RAYOH_TEXTURA = "flat.papa"     # textura de cada tramo (Pablo: flat se ve mejor; dot es un huso)

# BUCLE: crear un puppet de rayo (~30 emisores) congela el juego un instante
# (probado: "no tolerable"). Por eso los rayos se crean UNA vez (reserva al
# arrancar) y cada .pfx se repite solo: dispara cada PERIODO s (emissionRate =
# 1/periodo, bLoop). El delay horneado es la fase dentro del periodo.
RAYOH_PERIODO = (6.0, 14.0)     # s entre descargas de un mismo rayo de tormenta
ARCOH_FRECUENCIA = 3.0          # chispas x3 sobre el original (15-45 s). Aprobado por Pablo 2026-09-23 (x11 era prueba)
ARCOH_PERIODO = (15.0 / ARCOH_FRECUENCIA, 45.0 / ARCOH_FRECUENCIA)    # s entre chispazos de un cortocircuito

def en_bucle(e, periodo):
    """Convierte un emisor de rafaga unica en uno que se repite cada periodo s."""
    e.pop("emissionBursts", None)
    e["emissionRate"] = round(1.0 / periodo, 5)
    e["bLoop"] = True
    return e

def tramo(a, b, nivel, delay, brillo=1.0):
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    largo = math.sqrt(dx * dx + dy * dy + dz * dz) or 0.01
    ancho, r, g, bl = RAYOH_ESTILO[nivel]
    return {
        "label": "rayo " + nivel,
        "spec": {"shader": "particle_add", "facing": "velocity",
                 "red": _escala_curva(r, brillo), "green": _escala_curva(g, brillo), "blue": _escala_curva(bl, brillo),
                 "baseTexture": TEX + RAYOH_TEXTURA,
                 "dataChannelFormat": "PositionColorAndAlignVector"},
        "useWorldSpace": False,
        "offsetX": round((a[0] + b[0]) / 2, 3), "offsetY": round((a[1] + b[1]) / 2, 3), "offsetZ": round((a[2] + b[2]) / 2, 3),
        "velocityX": round(dx / largo, 4), "velocityY": round(dy / largo, 4), "velocityZ": round(dz / largo, 4),
        "velocity": 0.01,
        "sizeX": ancho, "sizeY": round(largo * RAYOH_SOLAPE, 3),
        "lifetime": RAYOH_VIDA[nivel],
        # delay SIN emitterLifetime (probado en juego: delay + emitterLifetime no
        # se dibuja en un puppet; delay solo si, como el destello de LightningTest).
        "emissionBursts": 1, "maxParticles": 1,
        "delay": round(delay, 3),
        "bLoop": False, "killOnDeactivate": True, "endDistance": 3000, "sort": "NoSort",
    }

DESTELLO_ALZA = 6   # yd sobre el suelo (+Y local = abajo): si nace en el suelo, el terreno lo corta
# El canal (tramos "facing velocity") se ve ~0.5 s despues que el destello con el
# mismo delay (Pablo, lava, 2026-09-24): el destello se atrasa para coincidir.
DESTELLO_RETRASO = 0.5

def destello_en(p, delay, rgb=(2.2, 2.4, 3.2), tam=40):
    """Destello de impacto (de LightningTest) en el punto p del puppet."""
    return {
        "label": "destello de impacto",
        # cameraPush: acerca el sprite a la camara para que el terreno no lo corte
        # (precedente vanilla: "BIG WHITE BALL" de default_building_explosion.pfx).
        "spec": {"shader": "particle_add_soft", "red": rgb[0], "green": rgb[1], "blue": rgb[2],
                 "alpha": [[0, 1], [0.7, 0.6], [1, 0]], "cameraPush": 1,
                 "baseTexture": TEX + "softdot.papa", "dataChannelFormat": "PositionAndColor"},
        "useWorldSpace": False,
        "offsetX": round(p[0], 3), "offsetY": round(p[1] - DESTELLO_ALZA, 3), "offsetZ": round(p[2], 3),
        "sizeX": tam, "sizeRangeX": tam / 4, "velocity": 0, "delay": round(delay, 3),
        "emissionBursts": 1, "maxParticles": 1, "lifetime": 0.25,
        "killOnDeactivate": True, "bLoop": False, "endDistance": 3000, "sort": "NoSort",
    }

def caminata(rng, p0, pasos, largo, giro, y_fin):
    """Caminata aleatoria horizontal (X/Z) bajando linealmente de p0.y a y_fin."""
    pts = [p0]
    ang = rng.uniform(0, 360)
    for i in range(1, pasos):
        ang += rng.uniform(-giro, giro)
        l = rng.uniform(*largo)
        prev = pts[-1]
        y = p0[1] + (y_fin - p0[1]) * i / (pasos - 1)
        pts.append((prev[0] + l * math.cos(math.radians(ang)), y, prev[2] + l * math.sin(math.radians(ang))))
    return pts

def rayo_horneado(rng, a_tierra):
    delay = rng.uniform(*RAYOH_DELAY)
    # Ancla sin delay: sin un emisor activo al nacer, el motor descarta el
    # efecto y los emisores con delay nunca salen (probado en juego).
    em = [ancla()]
    def cadena(pts, nivel, d=delay, brillo=1.0):
        for i in range(len(pts) - 1):
            em.append(tramo(pts[i], pts[i + 1], nivel, d, brillo))
    if a_tierra:
        suelo = ALTURA_NUBES - RAYOH_ESPESOR_NUBE   # desde la base de la nube al suelo
        canal = caminata(rng, (0, 0, 0), rng.randint(12, 16), (2, 5), 45, suelo)  # tramos cortos, quiebres bruscos
        cadena(canal, "canal")   # el segundo golpe de retorno va en su curva de color
        em.append(destello_en(canal[-1], delay + DESTELLO_RETRASO))
        pool = canal[1:-1]
        for _ in range(rng.randint(1, 3)):
            o = rng.choice(canal[1:-1])
            fin = o[1] + (suelo - o[1]) * rng.uniform(0.3, 0.6)
            rama = caminata(rng, o, rng.randint(4, 6), (3, 6), 40, fin)
            cadena(rama, "rama")
            pool += rama[1:]
        n_ramitas = rng.randint(4, 8)
    else:
        # Dentro de la nube: casi horizontal, dentro del espesor, no toca suelo.
        y0 = rng.uniform(-RAYOH_ESPESOR_NUBE, RAYOH_ESPESOR_NUBE)
        y1 = max(-RAYOH_ESPESOR_NUBE, min(RAYOH_ESPESOR_NUBE, y0 + rng.uniform(-4, 4)))
        canal = caminata(rng, (rng.uniform(-10, 10), y0, rng.uniform(-10, 10)), rng.randint(4, 6), (3, 6), 35, y1)
        cadena(canal, "rama")
        pool = canal
        n_ramitas = rng.randint(2, 5)
    for _ in range(n_ramitas):
        o = rng.choice(pool)
        ramita = caminata(rng, o, rng.randint(2, 3), (1.5, 4), 40, o[1] + rng.uniform(0.5, 3))
        cadena(ramita, "ramita")
    return bucle_pfx({"emitters": em}, rng.uniform(*RAYOH_PERIODO), delay)

def bucle_pfx(pfx, periodo, fase):
    """Todo emisor con delay (tramos y destello) se repite cada periodo s, en fase.
    Conserva el desfase de cada emisor respecto del mas temprano (el destello va
    DESTELLO_RETRASO despues del canal)."""
    base = min([e["delay"] for e in pfx["emitters"] if "delay" in e] or [0])
    for e in pfx["emitters"]:
        if "delay" in e:
            desfase = e["delay"] - base
            en_bucle(e, periodo)
            e["delay"] = round((fase + desfase) % periodo, 3)
    return pfx

# Un efecto sin ningun emisor activo al nacer se descarta y los emisores con
# delay nunca salen (Atlas 3.6): ANCLA invisible sin delay que lo mantiene vivo.
def ancla():
    """Emision CONTINUA invisible (aditivo negro) sin delay, como la cuerda de
    LightningTest que mantenia vivo al destello retrasado."""
    return {"label": "ancla invisible",
            "spec": {"shader": "particle_add", "red": 0, "green": 0, "blue": 0,
                     "baseTexture": TEX + "dot.papa"},
            "useWorldSpace": False, "velocity": 0, "sizeX": 0.01,
            "lifetime": 0.5, "emissionRate": 2, "maxParticles": 2,
            "endDistance": -1, "sort": "NoSort"}

_rng = random.Random(RAYOH_SEMILLA)
RAYOH_TIERRA = [rayo_horneado(_rng, True) for _ in range(RAYOH_VARIANTES)]
RAYOH_NUBE = [rayo_horneado(_rng, False) for _ in range(RAYOH_VARIANTES)]
# Lava: los rayos volcanicos de LavaTest eran copia exacta de los de tormenta
# -> se reusan rayoh_tierra / rayoh_nube (proporcion volcanica en el JS).


# ---------------- metal: cortocircuitos HORNEADOS ----------------
# Origen del puppet = SUELO (+Y local = abajo, asi que "arriba" es -Y).
# Cian: arco rasante que chisporrotea. Naranja (raro): descarga a tierra con
# destello, falla de alta potencia.
ARCOH_VARIANTES = 10

def arco_horneado(rng, naranja):
    delay = rng.uniform(*RAYOH_DELAY)
    em = [ancla()]
    nivel = "naranja" if naranja else "cian"
    if naranja:
        pts = caminata(rng, (0, -rng.uniform(5, 8), 0), rng.randint(4, 7), (2, 5), 40, 0)
    else:
        pts = caminata(rng, (0, -rng.uniform(1, 4), 0), rng.randint(3, 6), (1.5, 4), 50, -rng.uniform(1, 4))
    for i in range(len(pts) - 1):
        em.append(tramo(pts[i], pts[i + 1], nivel, delay))
    if naranja:
        em.append(destello_en(pts[-1], delay, (3.0, 1.6, 0.4), 18))
    periodo = rng.uniform(*ARCOH_PERIODO) * (2.5 if naranja else 1)  # naranja: mas raro
    return bucle_pfx({"emitters": em}, periodo, rng.uniform(0, periodo))

_rng_arco = random.Random(RAYOH_SEMILLA + 1)
ARCOH_CIAN = [arco_horneado(_rng_arco, False) for _ in range(ARCOH_VARIANTES)]
ARCOH_NARANJA = [arco_horneado(_rng_arco, True) for _ in range(ARCOH_VARIANTES)]


EFECTOS = dict(PRECIP, **PRECIP_X15)
EFECTOS.update({
    "nubes": NUBES,
    "rayoh_tierra": RAYOH_TIERRA,
    "rayoh_nube": RAYOH_NUBE,
    "arcoh_cian": ARCOH_CIAN,
    "arcoh_naranja": ARCOH_NARANJA,
})

# Lava: se copian los .pfx de LavaTest (su ventana los ajusta y valida).
# OJO: su caida (barro, ceniza) esta calibrada a la altura de LavaTest (172).
# Sus rayos volcanicos eran copia de los de tormenta: se usan los horneados.
# caida_ceniza / lluvia_barro solo sirven de base para sus variantes *_viento.
LAVA = ["ceniza", "brillo_lava", "caida_ceniza", "lluvia_barro"]
LAVA_SOLO_BASE = ("caida_ceniza", "lluvia_barro")
# Ajustes al copiar (sin tocar los archivos de LavaTest):
# - ceniza: particle_wake + softSmoke -> mismo look aprobado de las nubes
#   (NUBE_MODO 'lit', tamano x LAVA_CENIZA_TAMANO).
# - caida_ceniza / lluvia_barro: vida recalculada a ALTURA_NUBES y variantes
#   con viento (3 fuerzas x 8 direcciones, mismo orden que la lluvia).
# Prueba 1 (tamano x2): pocas plumas y chicas para el planeta. Pablo: pocos
# montones pero GRANDES -> mas ancha, mas bocanadas y mas grandes.
LAVA_CENIZA_TAMANO = 3.5      # tamano de bocanada
LAVA_CENIZA_ANCHO = 3.0       # offsetRange de la pluma (y ancho de su caida)
LAVA_CENIZA_BOCANADAS = 2.5   # cantidad de bocanadas
LAVA_CAIDA_TASA = 3.0         # tasa de ceniza/barro cayendo (area ~x5.8 -> algo menos densa)
# Lluvia de lava = lluvia ACIDA (plan de Pablo): verde-amarillo azufre, no pardo.
LAVA_LLUVIA_ACIDA_COLOR = (0.66, 0.74, 0.28)
VIENTO_CENIZA = VIENTO_NIEVE * 0.8        # Pablo: un poco menos que la nieve
VIENTO_CENIZA_RANGO = VIENTO_NIEVE_RANGO * 0.8


def a_lit(data, escala):
    """particle_wake + softSmoke (red/green/blue/alpha fijos) -> transparent_lit."""
    for e in data["emitters"]:
        s = e["spec"]
        if s.get("shader") != "particle_wake":
            continue
        c = [min(255, int(round(s.get(k, 1.0) * 255))) for k in ("red", "green", "blue")]
        a = s.get("alpha", 1.0)
        a = int(round((a if not isinstance(a, list) else max(v for _, v in a)) * 255))
        e["spec"] = {"shader": "particle_transparent_lit", "facing": s.get("facing", "Camera"),
                     "rgb": [[0.0, 1, c + [a]], [1.0, 1, c + [a]]],
                     "baseTexture": TEX + "simpleSmokeSingle.papa",
                     "dataChannelFormat": "PositionAndColor"}
        for k in ("sizeX", "sizeRangeX"):
            if k in e:
                e[k] = round(e[k] * escala, 2)
        for k in ("offsetRangeX", "offsetRangeZ"):
            if k in e:
                e[k] = round(e[k] * LAVA_CENIZA_ANCHO, 2)
        if isinstance(e.get("emissionBursts"), (int, float)):
            n = int(round(e["emissionBursts"] * LAVA_CENIZA_BOCANADAS))
            e["emissionBursts"] = n
            e["maxParticles"] = n
    return data


def recaer(data):
    """Vida de caida a la altura actual (LavaTest estaba calibrado a 172)."""
    e = data["emitters"][0]
    # Pluma mas ancha -> su caida tambien (80 % del ancho de la ceniza).
    for k in ("offsetRangeX", "offsetRangeZ"):
        if k in e:
            e[k] = round(e[k] * LAVA_CENIZA_ANCHO * 0.8, 2)
    e["emissionRate"] = round(e["emissionRate"] * LAVA_CAIDA_TASA, 2)
    vida = round((ALTURA_NUBES - e.get("offsetY", 0) + MARGEN_CANON) / e["velocity"], 2)
    e["lifetime"] = vida
    e["maxParticles"] = tope(e["emissionRate"], vida, e.get("lifetimeRange", 0))
    # Al borrar el puppet (cambio de viento) lo que ya cae termina de caer.
    e["killOnDeactivate"] = False
    return data


def rosa_de(base, f_base, f_rango):
    return [v for f in fuerzas(f_base, f_rango)
            for v in rosa(lambda ac: con_viento(json.loads(json.dumps(base)), ac), f)]

def write(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def costo(pfx):
    return sum(e.get("maxParticles", 0) for e in pfx["emitters"])


def main():
    os.makedirs(SPEC_DIR, exist_ok=True)
    os.makedirs(UI_DIR, exist_ok=True)
    for f in os.listdir(SPEC_DIR):
        if f.endswith(".pfx"):
            os.remove(os.path.join(SPEC_DIR, f))

    conteos, costos = {}, {}
    for nombre, variantes in EFECTOS.items():
        for i, data in enumerate(variantes, 1):
            write(os.path.join(SPEC_DIR, "%s_var%02d.pfx" % (nombre, i)), data)
        conteos[nombre] = len(variantes)
        costos[nombre] = [costo(v) for v in variantes]

    for nombre in LAVA:
        n = 0
        costos[nombre] = []
        while True:
            src = os.path.join(LAVA_SRC, "%s_var%02d.pfx" % (nombre, n + 1))
            if not os.path.exists(src):
                break
            with open(src, encoding="utf-8") as f:
                data = json.load(f)
            if nombre == "ceniza":
                data = a_lit(data, LAVA_CENIZA_TAMANO)
            if nombre in ("caida_ceniza", "lluvia_barro"):
                data = recaer(data)
                if nombre == "lluvia_barro":
                    sp = data["emitters"][0]["spec"]
                    sp["red"], sp["green"], sp["blue"] = LAVA_LLUVIA_ACIDA_COLOR
                if n == 0:
                    fam = nombre + "_viento"
                    fb, fr = ((VIENTO_CENIZA, VIENTO_CENIZA_RANGO) if nombre == "caida_ceniza"
                              else (VIENTO_LLUVIA, VIENTO_LLUVIA_RANGO))
                    vs = rosa_de(data, fb, fr)
                    for i, v in enumerate(vs, 1):
                        write(os.path.join(SPEC_DIR, "%s_var%02d.pfx" % (fam, i)), v)
                    conteos[fam] = len(vs)
                    costos[fam] = [costo(v) for v in vs]
            if nombre not in LAVA_SOLO_BASE:
                write(os.path.join(SPEC_DIR, os.path.basename(src)), data)
                costos[nombre].append(costo(data))
            n += 1
        if nombre in LAVA_SOLO_BASE:
            del costos[nombre]
        else:
            conteos[nombre] = n
        if n == 0:
            print("AVISO: sin .pfx de lava para", nombre)

    write(os.path.join(UI_DIR, "variantes.json"), conteos)
    write(os.path.join(UI_DIR, "parametros.json"), {
        "altura_nubes": ALTURA_NUBES,
        "nube_generacion_s": NUBE_GENERACION,
        "nube_vida_max_s": NUBE_VIDA + NUBE_VIDA_RNG,
        "costos": costos})
    print("altura %d yd, caida %d yd, vida lluvia %.2f s, vida nieve %.2f s"
          % (ALTURA_NUBES, CAIDA, LLUVIA_VIDA, NIEVE_VIDA))
    print(json.dumps(conteos))


if __name__ == "__main__":
    main()
