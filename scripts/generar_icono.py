# Genera icon.gif (300x300, en bucle) para Community Mods: 4 planetas (Earth,
# Ice, Lava, Metal) con sus efectos, como se ven en juego (captura 763, Gamma
# System): nubes altas en bocanadas (blancas de dia, azul-violeta de noche),
# lluvia entre nube y suelo, tormentas con rayos, nieve, plumas de ceniza con
# rayos volcanicos, ceniza que cae y lluvia acida, y chispas en metal.
# Tambien deja icon.png (un cuadro fijo). Se dibuja a 2x y se reduce.
# Requiere numpy y Pillow.
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import os
MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # raiz del repo
W = 600                     # lienzo de trabajo (2x)
N = 64                      # cuadros (1 vuelta completa = bucle perfecto)
MS = 70                     # ms por cuadro
ALT = 1.17                  # altura de las nubes (radios): lejos del suelo
LUZ = np.array([-0.62, -0.42, 0.66]); LUZ /= np.linalg.norm(LUZ)
rng = np.random.default_rng(11)
yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)


def ruido(w, h, octavas, semilla):
    r = np.random.default_rng(semilla)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in octavas:
        base = r.random((max(2, h * o // w), o)).astype(np.float32)
        # repetir columnas para que la textura cierre sin costura al girar
        base = np.concatenate([base[:, -2:], base, base[:, :2]], 1)
        ancho = w * (o + 4) // o
        img = Image.fromarray((base * 255).astype(np.uint8)).resize((ancho, h), Image.BICUBIC)
        c0 = 2 * w // o
        out += amp * np.asarray(img, np.float32)[:, c0:c0 + w] / 255.0
        tot += amp
        amp *= 0.5
    return out / tot


TW, TH = 512, 256


def textura(bioma, semilla):
    """(color, emision) equirectangulares."""
    a = ruido(TW, TH, [6, 12, 24, 48, 96], semilla)
    d = ruido(TW, TH, [128, 256], semilla + 1)[..., None]
    emis = np.zeros((TH, TW, 3), np.float32)
    if bioma == 'earth':
        tex = np.zeros((TH, TW, 3), np.float32) + [22, 32, 62]
        cl = np.clip((a - 0.5) * 6, 0, 1)[..., None]
        v = (np.array([58, 66, 34]) * (1 - cl) + np.array([92, 88, 52]) * cl) * (0.75 + 0.5 * d)
        tex[a > 0.5] = v[a > 0.5]
    elif bioma == 'ice':
        cl = np.clip((a - 0.35) * 3, 0, 1)[..., None]
        tex = (np.array([196, 204, 218]) * (1 - cl) + np.array([236, 240, 247]) * cl) * (0.9 + 0.12 * d)   # todo nieve
    elif bioma == 'lava':   # captura 757: roca marron rojiza + campos de lava
        tex = (np.array([92, 58, 48]) + np.array([60, 40, 30]) * a[..., None]) * (0.8 + 0.4 * d)
        campo = np.clip((a - 0.57) / 0.06, 0, 1)[..., None]
        tex = tex * (1 - campo)
        emis = campo * (np.array([255, 95, 25]) * (0.75 + 0.35 * d))
    else:  # metal, captura 758: placas gris-azul, franjas-trinchera con luces azules
        tex = (np.array([112, 122, 142]) * (0.85 + 0.3 * d)) * np.ones((TH, TW, 1))
        tex[:, np.arange(TW) % 32 < 1] *= 0.7                        # juntas de placas
        tex[np.arange(TH) % 20 < 1, :] *= 0.8
        lat = (0.5 - np.arange(TH) / (TH - 1)) * 180
        for centro in (-38, 0, 38):                                  # franjas-trinchera
            fr = np.abs(lat - centro) < 5
            tex[fr] = [28, 36, 54]
            luces = fr[:, None] & (np.arange(TW)[None, :] % 12 < 5) & (np.abs(lat - centro) < 2)[:, None]
            emis[luces] = [30, 85, 160]
            tex[np.abs(np.abs(lat - centro) - 5.5) < 0.8] *= 1.25       # bordes claros
    return tex.astype(np.float32), emis.astype(np.float32)


# ---- fondo: azul verdoso de PA, nebulosa suave y estrellas ----
g = yy / W
fondo = np.array([12, 44, 64]) * (1 - g)[..., None] + np.array([10, 58, 76]) * g[..., None]
neb = np.exp(-(((xx - 420) ** 2) / 2 / 170 ** 2 + ((yy - 470) ** 2) / 2 / 130 ** 2))
fondo = (fondo + neb[..., None] * np.array([10, 40, 30])).astype(np.float32)
for _ in range(120):
    x, y = rng.integers(0, W, 2)
    b = rng.uniform(0.3, 1.0)
    fondo[y, x] = fondo[y, x] * (1 - b) + np.array([200, 225, 235]) * b


class Planeta:
    def __init__(self, bioma, cx, cy, R, tilt, semilla, halo_color, halo_ancho=0.09):
        self.bioma, self.cx, self.cy, self.R = bioma, cx, cy, R
        self.ct, self.st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        self.s = R / 178.0                                   # escala de tamanos
        self.tex, self.emis = textura(bioma, semilla)
        self.halo_color = np.array(halo_color, np.float32)
        dx, dy = (xx - cx) / R, (yy - cy) / R
        d2 = dx * dx + dy * dy
        self.disco = d2 <= 1.0
        nz = np.sqrt(np.clip(1 - d2, 0, 1))
        lamb = dx * LUZ[0] + dy * LUZ[1] + nz * LUZ[2]
        self.sombra = np.clip(0.04 + 1.15 * lamb, 0.03, 1.0)[self.disco][:, None]
        by = dy * self.ct + nz * self.st
        bz = -dy * self.st + nz * self.ct
        lat = np.arcsin(np.clip(-by, -1, 1))
        self.lon0 = np.arctan2(dx, bz)[self.disco]
        self.filas = ((0.5 - lat / math.pi) * (TH - 1)).astype(np.int32)[self.disco]
        rr = np.sqrt(d2)
        self.halo = (np.exp(-((rr - 1.0) / halo_ancho) ** 2) * np.clip((rr - (0.85 if halo_ancho < 0.15 else 0.97)) / 0.05, 0, 1)
                     * np.clip(0.35 + 0.9 * (dx * LUZ[0] + dy * LUZ[1] + 0.3), 0.25, 1.0))[..., None]
        self.cumulos, self.golpes, self.plumas, self.chispas = [], [], [], []

    def dir(self, la, lo):
        x = math.cos(la) * math.sin(lo)
        y = -math.sin(la)
        z = math.cos(la) * math.cos(lo)
        return x, y * self.ct - z * self.st, y * self.st + z * self.ct

    def proy(self, la, lo, h):
        x, y, z = self.dir(la, lo)
        vis = z >= 0 or (x * x + y * y) * h * h >= 1.0
        return self.cx + x * self.R * h, self.cy + y * self.R * h, z, vis

    def luz(self, la, lo):
        x, y, z = self.dir(la, lo)
        return x * LUZ[0] + y * LUZ[1] + z * LUZ[2]

    def visibles(self, la, lo, zmin=-0.1):
        return [f for f in range(N) if self.dir(la, lo - 2 * math.pi * f / N)[2] > zmin]


# ---- nubes ----
def cumulo(P, la, lo, n, tam, dis, tipo, gotas):
    c = dict(la=la, lo=lo, tipo=tipo, flash={}, puffs=[
        dict(la=la + rng.normal(0, dis), lo=lo + rng.normal(0, dis * 1.4),
             r=rng.uniform(*tam) * P.s, fase=rng.uniform(0, 2 * math.pi), k=int(rng.integers(1, 3)))
        for _ in range(n)], gotas=[])
    for _ in range(gotas):
        p = c['puffs'][int(rng.integers(n))]
        c['gotas'].append(dict(la=p['la'] + rng.normal(0, 0.04), lo=p['lo'] + rng.normal(0, 0.06),
                               fase=rng.random(), k=1 if tipo == 'nieve' else int(rng.integers(3, 5)),
                               bam=rng.uniform(0, 2 * math.pi)))
    P.cumulos.append(c)
    return c


PATRON = ((0, 1.0), (1, 0.35), (2, 0.9), (3, 0.25), (5, 0.6))   # el canal titila (3 golpes)


def programar(P, la, lo, veces, separacion, zmin=-0.15):
    """Elige cuadros de inicio donde el punto se ve."""
    vis = P.visibles(la, lo, zmin)
    usados = []
    for _ in range(veces * 4):
        if len(usados) >= veces or not vis:
            break
        f0 = int(rng.choice(vis))
        if all(abs(f0 - u) >= separacion for u in usados):
            usados.append(f0)
    return usados


def tormentas(P, cant, veces):
    for i in range(cant):
        la = math.radians(rng.choice([-1, 1]) * rng.uniform(10, 35))
        c = cumulo(P, la, 2 * math.pi * i / cant + rng.normal(0, 0.2), 14, (20, 32), 0.07, 'tormenta', 90)
        for f0 in programar(P, la, c['lo'], veces, 6):
            se, tierra = int(rng.integers(1 << 30)), rng.random() < 0.8
            for df, fu in PATRON:
                P.golpes.append(dict(f=(f0 + df) % N, c=c, fu=fu, se=se, tierra=tierra, tipo='tormenta'))


# ---- planetas ----
PL = []
earth = Planeta('earth', 150, 150, 92, 18, 3, (175, 205, 228)); PL.append(earth)
for banda, cant in ((62, 3), (38, 5), (-36, 5), (-62, 3)):
    for _ in range(cant):
        tipo = 'nieve' if abs(banda) >= 55 else ('lluvia' if rng.random() < 0.6 else 'nube')
        cumulo(earth, math.radians(banda + rng.normal(0, 6)), rng.uniform(0, 2 * math.pi),
               int(rng.integers(5, 9)), (15, 26), 0.08, tipo, 0 if tipo == 'nube' else 50)
tormentas(earth, 6, 6)

ice = Planeta('ice', 450, 150, 88, -12, 21, (205, 225, 245)); PL.append(ice)
for banda in (60, 40, 20, 0, -20, -40, -60):
    for _ in range(3):
        cumulo(ice, math.radians(banda + rng.normal(0, 6)), rng.uniform(0, 2 * math.pi),
               int(rng.integers(4, 8)), (14, 24), 0.08, 'nieve', 110)

lava = Planeta('lava', 150, 450, 84, 10, 37, (225, 95, 70), 0.2); PL.append(lava)
for i in range(4):
    la = math.radians(rng.uniform(-40, 40))
    lo = 2 * math.pi * i / 4 + rng.normal(0, 0.3)
    pl = dict(la=la, lo=lo, puffs=[], gotas=[])
    for j in range(26):                         # columna que sube y se abre
        pl['puffs'].append(dict(fase=j / 26 + rng.normal(0, 0.02), dla=rng.normal(0, 1), dlo=rng.normal(0, 1),
                                r=rng.uniform(30, 46) * lava.s))
    for _ in range(60):                         # ceniza que cae y lluvia acida
        pl['gotas'].append(dict(la=la + rng.normal(0, 0.12), lo=lo + rng.normal(0, 0.16), fase=rng.random(),
                                acida=rng.random() < 0.45, k=int(rng.integers(1, 3))))
    lava.plumas.append(pl)
    for f0 in programar(lava, la, lo, 6, 5):    # rayos volcanicos: muchos, cortos
        se = int(rng.integers(1 << 30))
        for df, fu in PATRON[:4]:
            lava.golpes.append(dict(f=(f0 + df) % N, c=pl, fu=fu, se=se, tierra=False, tipo='volcan'))

metal = Planeta('metal', 450, 450, 90, -20, 55, (150, 170, 190)); PL.append(metal)
for i in range(34):                              # arcos que saltan de lugar
    la, lo = math.radians(rng.uniform(-60, 60)), rng.uniform(0, 2 * math.pi)
    naranja = rng.random() < 0.25
    for f0 in programar(metal, la, lo, 3, 8, zmin=0.0):
        se = int(rng.integers(1 << 30))
        la2, lo2 = la + rng.normal(0, 0.08), lo + rng.normal(0, 0.1)
        for df, fu in PATRON:
            metal.chispas.append(dict(f=(f0 + df) % N, la=la2, lo=lo2, fu=fu, se=se, naranja=naranja))

# ---- dibujo ----
_sprites = {}


def sprite(r):
    r = max(2, int(r))
    if r not in _sprites:
        y, x = np.mgrid[0:2 * r + 1, 0:2 * r + 1] - r
        _sprites[r] = np.clip(1 - np.sqrt(x * x + y * y) / r, 0, 1) ** 0.9 * 0.9
    return _sprites[r]


def pegar(img, x, y, r, color, alfa):
    sp = sprite(r) * alfa
    r = sp.shape[0] // 2
    x0, y0 = int(x) - r, int(y) - r
    sx0, sy0 = max(0, -x0), max(0, -y0)
    x0c, y0c = max(0, x0), max(0, y0)
    x1c, y1c = min(W, x0 + sp.shape[0]), min(W, y0 + sp.shape[0])
    if x0c >= x1c or y0c >= y1c:
        return
    a = sp[sy0:sy0 + (y1c - y0c), sx0:sx0 + (x1c - x0c)][..., None]
    reg = img[y0c:y1c, x0c:x1c]
    reg[:] = reg * (1 - a) + np.asarray(color, np.float32) * a


def mezclar(img, capa_l, color, fuerza):
    a = np.asarray(capa_l, np.float32)[..., None] / 255.0 * fuerza
    return img * (1 - a) + np.asarray(color, np.float32) * a


def resplandor(img, x, y, sigma, fu, color):
    x0, x1 = int(max(0, x - 3 * sigma)), int(min(W, x + 3 * sigma))
    y0, y1 = int(max(0, y - 3 * sigma)), int(min(W, y + 3 * sigma))
    if x0 >= x1 or y0 >= y1:
        return
    a = np.exp(-(((xx[y0:y1, x0:x1] - x) ** 2 + (yy[y0:y1, x0:x1] - y) ** 2) / (2 * sigma ** 2)))[..., None] * fu
    reg = img[y0:y1, x0:x1]
    reg[:] = reg * (1 - a) + np.asarray(color, np.float32) * a


BLANCO = np.array([236, 236, 244], np.float32)
NOCHE = np.array([78, 74, 150], np.float32)      # azul-violeta del lado noche
BASE = np.array([150, 150, 170], np.float32)
CENIZA = np.array([185, 118, 80], np.float32)    # ceniza marron-naranja (captura 757)
ACIDA = (190, 225, 70)                            # LAVA_LLUVIA_ACIDA_COLOR (verde-amarillo)


def mix_luz(luz, oscuro, claro):
    t = min(1.0, max(0.0, (luz + 0.15) / 0.6))
    t = t * t * (3 - 2 * t)
    return oscuro * (1 - t) + claro * t


def quebrada(P, puntos3d, r, jit):
    """Hace zigzag una linea 3D (lista de (la, lo, h))."""
    out = []
    for i, (a, b, h) in enumerate(puntos3d):
        if 0 < i < len(puntos3d) - 1:
            a, b = a + r.normal(0, jit), b + r.normal(0, jit * 1.3)
        out.append((a, b, h))
    return out


cuadros = []
for f in range(N):
    giro = 2 * math.pi * f / N
    t = f / N
    img = fondo.copy()
    capa_ll = Image.new("L", (W, W), 0); dl = ImageDraw.Draw(capa_ll)     # lluvia
    capa_ac = Image.new("L", (W, W), 0); da = ImageDraw.Draw(capa_ac)     # lluvia acida
    capa_nv = Image.new("L", (W, W), 0); dn = ImageDraw.Draw(capa_nv)     # nieve
    capa_cz = Image.new("L", (W, W), 0); dz = ImageDraw.Draw(capa_cz)     # ceniza
    rayos = {k: (Image.new("L", (W, W), 0), Image.new("L", (W, W), 0))
             for k in ('blanco', 'violeta', 'cian', 'naranja')}
    brillos = []
    puffs = []

    for P in PL:
        # superficie + halo
        col = ((((P.lon0 + giro) / (2 * math.pi)) % 1.0) * (TW - 1)).astype(np.int32)
        sup = P.tex[P.filas, col] * P.sombra + np.array([6, 10, 26]) * (1 - P.sombra) * 0.6 + P.emis[P.filas, col]
        img[P.disco] = np.minimum(sup, 255)
        img = img * (1 - P.halo * 0.55) + P.halo_color * P.halo * 0.55

        # golpes activos -> destello de su nube
        for gp in P.golpes:
            if gp['f'] == f:
                gp['c'].setdefault('flash', {})
        activos = [gp for gp in P.golpes if gp['f'] == f]
        fl_de = {}
        for gp in activos:
            fl_de[id(gp['c'])] = max(fl_de.get(id(gp['c']), 0), gp['fu'])

        # nubes: bocanadas + lluvia/nieve debajo
        for c in P.cumulos:
            fl = fl_de.get(id(c), 0.0)
            torm = c['tipo'] == 'tormenta'
            for p in c['puffs']:
                lo = p['lo'] - giro + 0.04 * math.sin(2 * math.pi * t + p['fase'])
                px, py, z, vis = P.proy(p['la'], lo, ALT)
                if z < -0.45 or not vis:
                    continue
                r = p['r'] * (1 + 0.18 * math.sin(2 * math.pi * p['k'] * t + p['fase']))
                if z < 0.25:
                    r *= max(0.35, 0.75 + z)
                luz = P.luz(p['la'], lo)
                cima = mix_luz(luz, NOCHE, BLANCO) * (0.8 if torm else 1.0)
                if fl:
                    cima = cima * (1 - fl) + np.array([228, 236, 255]) * fl
                base = BASE * (0.4 + 0.6 * max(0.0, min(1.0, luz + 0.3))) * (0.65 if torm else 0.9)
                puffs.append((P.cy * 0 + z, px, py, max(3, r), base, cima))
            for gt in c['gotas']:
                lo = gt['lo'] - giro
                caida = (gt['fase'] + t * gt['k']) % 1.0
                h = ALT - 0.03 - (ALT - 1.0 - 0.03) * caida
                lz = max(0.3, min(1.0, P.luz(gt['la'], lo) + 0.55))
                if c['tipo'] == 'nieve':
                    px, py, z, vis = P.proy(gt['la'], lo + 0.015 * math.sin(2 * math.pi * 3 * t + gt['bam']), h)
                    if vis:
                        dn.ellipse((px - 2.8, py - 2.8, px + 2.8, py + 2.8), fill=int(240 * lz))
                else:
                    x1, y1, _, v1 = P.proy(gt['la'], lo, h)
                    x2, y2, _, v2 = P.proy(gt['la'] + 0.006, lo + 0.009, h - 0.07)   # veta con viento
                    if v1 and v2:
                        dl.line((x1, y1, x2, y2), fill=int(235 * lz), width=2)

        # plumas de lava: columna que sube, ceniza y lluvia acida alrededor
        for pl in P.plumas:
            lo0 = pl['lo'] - giro
            gx, gy, gz, gv = P.proy(pl['la'], lo0, 1.0)
            if gv and gz > -0.1:
                brillos.append((gx, gy, 10 * P.s * 2, 0.8, (255, 120, 40)))
            for p in pl['puffs']:
                sube = (p['fase'] + t) % 1.0
                h = 1.0 + (ALT + 0.2 - 1.0) * sube
                ab = 0.02 + 0.2 * sube                      # se abre al subir
                la, lo = pl['la'] + p['dla'] * ab, lo0 + p['dlo'] * ab * 1.3
                px, py, z, vis = P.proy(la, lo, h)
                if z < -0.45 or not vis:
                    continue
                luz = P.luz(la, lo)
                c = mix_luz(luz, np.array([80, 48, 40]), CENIZA)
                k_ = min(1.0, sube * 2.5)
                c = c * k_ + np.array([235, 115, 40]) * (1 - k_)   # abajo brilla la lava
                r = p['r'] * (0.35 + 0.8 * sube)
                if z < 0.25:
                    r *= max(0.35, 0.75 + z)
                puffs.append((z + 0.001 * h, px, py, max(3, r), c * 0.7, c))
            for gt in pl['gotas']:
                caida = (gt['fase'] + t * gt['k']) % 1.0
                h = ALT - (ALT - 1.0) * caida
                lo = gt['lo'] - giro
                if gt['acida']:
                    x1, y1, _, v1 = P.proy(gt['la'], lo, h)
                    x2, y2, _, v2 = P.proy(gt['la'], lo + 0.008, h - 0.06)
                    if v1 and v2:
                        da.line((x1, y1, x2, y2), fill=220, width=2)
                else:
                    px, py, _, vis = P.proy(gt['la'], lo, h)
                    if vis:
                        dz.ellipse((px - 2, py - 2, px + 2, py + 2), fill=200)

        # rayos (tormenta: a tierra o en la nube; volcan: dentro de la pluma)
        for gp in activos:
            c, fu = gp['c'], gp['fu']
            r = np.random.default_rng(gp['se'])
            lo = c['lo'] - giro
            if gp['tipo'] == 'tormenta':
                tx, ty, tz, _ = P.proy(c['la'], lo, ALT)
                if tz < -0.3:
                    continue
                brillos.append((tx, ty, 24 * P.s * 2, 0.65 * fu, (215, 225, 255)))
                la0, lo_0 = c['la'] + r.normal(0, 0.04), lo + r.normal(0, 0.05)
                if gp['tierra']:
                    canal = [(la0, lo_0, ALT - (ALT - 1.0) * i / 8) for i in range(9)]
                    canal = quebrada(P, canal, r, 0.018)
                    i0 = int(r.integers(2, 5))
                    a, b, h = canal[i0]
                    rama = quebrada(P, [(a, b, h)] + [(a + 0.03 * k * r.choice([-1, 1]), b + 0.04 * k, h - 0.02 * k)
                                                       for k in (1, 2, 3)], r, 0.012)
                    gx, gy, _, gv = P.proy(*canal[-1])
                    if gv:
                        brillos.append((gx, gy, 9, 0.9 * fu, (230, 240, 255)))
                else:  # arana dentro de la nube
                    ang = r.uniform(0, 2 * math.pi)
                    canal = quebrada(P, [(la0 + 0.03 * i * math.sin(ang), lo_0 + 0.04 * i * math.cos(ang), ALT + 0.01)
                                         for i in range(7)], r, 0.02)
                    rama = []
                lineas, color = [(canal, 5), (rama, 3)], 'blanco'
            else:
                tx, ty, tz, _ = P.proy(c['la'], lo, ALT - 0.05)
                if tz < -0.2:
                    continue
                brillos.append((tx, ty, 18 * P.s * 2, 0.5 * fu, (200, 170, 255)))
                la0 = c['la'] + r.normal(0, 0.03)
                canal = quebrada(P, [(la0, lo + r.normal(0, 0.04), ALT - 0.02 - 0.03 * i) for i in range(6)], r, 0.03)
                lineas, color = [(canal, 4)], 'violeta'
            cg, cc = rayos[color]
            dg, dc = ImageDraw.Draw(cg), ImageDraw.Draw(cc)
            for linea, ancho in lineas:
                pts = [P.proy(*q) for q in linea]
                for (x1, y1, _, v1), (x2, y2, _, v2) in zip(pts, pts[1:]):
                    if v1 and v2:
                        dg.line((x1, y1, x2, y2), fill=int(255 * fu), width=ancho + 12)
                        dc.line((x1, y1, x2, y2), fill=int(255 * fu), width=ancho)

        # chispas de metal: arco quebrado pegado al suelo
        for ch in P.chispas:
            if ch['f'] != f:
                continue
            r = np.random.default_rng(ch['se'])
            lo = ch['lo'] - giro
            ang = r.uniform(0, 2 * math.pi)
            largo = r.uniform(0.07, 0.13)
            arco = [(ch['la'] + largo * i / 6 * math.sin(ang), lo + largo * i / 6 * math.cos(ang) * 1.3,
                     1.0 + 0.05 * math.sin(math.pi * i / 6)) for i in range(7)]
            arco = quebrada(P, arco, r, 0.012)
            color = 'naranja' if ch['naranja'] else 'cian'
            cg, cc = rayos[color]
            dg, dc = ImageDraw.Draw(cg), ImageDraw.Draw(cc)
            pts = [P.proy(*q) for q in arco]
            if not all(v for *_, v in pts):
                continue
            for (x1, y1, _, _), (x2, y2, _, _) in zip(pts, pts[1:]):
                dg.line((x1, y1, x2, y2), fill=int(255 * ch['fu']), width=14)
                dc.line((x1, y1, x2, y2), fill=int(255 * ch['fu']), width=4)
            mx, my = pts[3][0], pts[3][1]
            brillos.append((mx, my, 14, 0.5 * ch['fu'], (255, 170, 80) if ch['naranja'] else (120, 220, 255)))

    # capas en orden: precipitacion -> nubes/plumas -> rayos y brillos
    img = mezclar(img, capa_ll, (170, 192, 225), 0.9)
    img = mezclar(img, capa_ac, ACIDA, 0.85)
    img = mezclar(img, capa_cz, (115, 72, 52), 0.9)
    img = mezclar(img, capa_nv, (246, 249, 255), 1.0)
    puffs.sort(key=lambda q: q[0])
    for z, px, py, r, base, cima in puffs:
        ox, oy = -LUZ[0] * r * 0.25, -LUZ[1] * r * 0.25
        pegar(img, px + ox, py + oy, r, base, 0.8)
        pegar(img, px - ox * 0.6, py - oy * 0.6, r * 0.85, cima, 0.85)
    for x, y, sg, fu, colr in brillos:
        resplandor(img, x, y, sg, fu, colr)
    COLORES = {'blanco': ((150, 190, 255), (242, 248, 255)), 'violeta': ((170, 130, 255), (240, 230, 255)),
               'cian': ((80, 200, 255), (225, 250, 255)), 'naranja': ((255, 130, 40), (255, 235, 200))}
    for k, (cg, cc) in rayos.items():
        img = mezclar(img, cg.filter(ImageFilter.GaussianBlur(4)), COLORES[k][0], 0.85)
        img = mezclar(img, cc, COLORES[k][1], 1.0)

    cuadros.append(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((300, 300), Image.LANCZOS))

# paleta comun (evita parpadeo de colores entre cuadros)
muestras = list(range(0, N, N // 8))
muestra = Image.new("RGB", (300, 300 * len(muestras)))
for i, f in enumerate(muestras):
    muestra.paste(cuadros[f], (0, 300 * i))
pal = muestra.quantize(colors=255, method=Image.MEDIANCUT)
gif = [c.quantize(palette=pal, dither=Image.FLOYDSTEINBERG) for c in cuadros]
gif[0].save(MOD + r"\icon.gif", save_all=True, append_images=gif[1:], duration=MS, loop=0, optimize=True, disposal=1)
cuadros[0].save(MOD + r"\icon.png", optimize=True)   # imagen fija (README, anuncio)
print("ok")
