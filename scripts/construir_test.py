"""Construye la copia de PRUEBA de Atmosphere Weather en la carpeta de mods del juego.

El repo (esta carpeta) no vive en mods\\: ahi esta instalada la version publicada de
Community Mods y dos mods con el mismo identifier chocan. La copia de prueba lleva:
  - identifier  com.pa.pabloandclaude.atmosphereweathertest
  - display_name "Atmosphere Weather (TEST)"
  - carpetas propias: ui/mods/<id test>/ y pa/effects/specs/atmosphereweathertest/
    (si compartiera la de efectos, pisaria los .pfx de la publicada).
Activar solo UNA de las dos a la vez: ambas crean la misma pestaña y el mismo clima.

Uso: python scripts/construir_test.py   (despues: reinicio completo si cambiaron .pfx,
F5 si solo cambio JS).
"""
import json
import os
import shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODS = os.path.join(os.environ["LOCALAPPDATA"], "Uber Entertainment", "Planetary Annihilation", "mods")

ID = "com.pa.pabloandclaude.atmosphereweather"
ID_TEST = ID + "test"
FX, FX_TEST = "specs/atmosphereweather/", "specs/atmosphereweathertest/"
DESTINO = os.path.join(MODS, ID_TEST)
TEXTO = (".js", ".json", ".html", ".css")


def cambiar(texto):
    return texto.replace(ID, ID_TEST).replace(FX, FX_TEST)


def main():
    if os.path.exists(DESTINO):
        shutil.rmtree(DESTINO)
    for base in ("pa", "ui"):
        for raiz, _, archivos in os.walk(os.path.join(REPO, base)):
            rel = os.path.relpath(raiz, REPO).replace("\\", "/") + "/"
            rel_test = cambiar(rel)
            os.makedirs(os.path.join(DESTINO, rel_test), exist_ok=True)
            for a in archivos:
                src = os.path.join(raiz, a)
                dst = os.path.join(DESTINO, rel_test, a)
                if a.endswith(TEXTO):
                    with open(src, encoding="utf-8") as f:
                        t = f.read()
                    with open(dst, "w", encoding="utf-8", newline="") as f:
                        f.write(cambiar(t))
                else:
                    shutil.copy2(src, dst)
    with open(os.path.join(REPO, "modinfo.json"), encoding="utf-8") as f:
        info = json.loads(cambiar(f.read()))
    info["display_name"] += " (TEST)"
    info["description"] = "TEST BUILD - do not publish. " + info["description"]
    with open(os.path.join(DESTINO, "modinfo.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    # Ninguna referencia a la version publicada debe quedar en la copia.
    for raiz, _, archivos in os.walk(DESTINO):
        for a in archivos:
            if a.endswith(TEXTO):
                with open(os.path.join(raiz, a), encoding="utf-8") as f:
                    t = f.read()
                assert (ID + "/") not in t and ('"' + ID + '"') not in t and FX not in t, a
    print("TEST ->", DESTINO)


if __name__ == "__main__":
    main()
