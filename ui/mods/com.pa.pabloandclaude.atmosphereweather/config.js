// AtmosphereWeather — constantes. Todo lo ajustable vive aqui.
// Los .pfx, variantes.json y parametros.json salen de scripts/generar_pfx.py (repo).
var AW = window.AtmosphereWeather = window.AtmosphereWeather || {};

AW.VERSION = '1.0.1';   // = "version" de modinfo.json

AW.cfg = {
    SPEC_DIR: '/pa/effects/specs/atmosphereweather/',
    VARIANTES_URL: 'coui://ui/mods/com.pa.pabloandclaude.atmosphereweather/variantes.json',
    // Respaldo si variantes.json no carga (debe coincidir con scripts/generar_pfx.py).
    VARIANTES_DEFAULT: {
        nubes: 5, lluvia_viento: 24, lluvia_ventarron: 24, virga_viento: 24, nieve_viento: 72,
        rayoh_tierra: 20, rayoh_nube: 20, arcoh_cian: 10, arcoh_naranja: 10,
        ceniza: 1, brillo_lava: 1, caida_ceniza_viento: 24, lluvia_barro_viento: 24
    },

    // Altura y costos reales vienen de parametros.json (scripts/generar_pfx.py,
    // bloque PARAMETROS). Estos valores son solo respaldo.
    PARAMETROS_URL: 'coui://ui/mods/com.pa.pabloandclaude.atmosphereweather/parametros.json',
    // Interruptores por efecto (true = activo). Los pisa el menu Settings.
    EFECTOS: {
        nubes: true,
        lluvia: true,
        nieve: true,
        virga: true,
        rayos: true,     // relampagos de tormenta (horneados, reserva + bucle)
        lava: true,
        rayosLava: true, // relampagos volcanicos (horneados, dentro de la pluma)
        metal: true
    },

    REFERENCE_RADIUS: 500,
    ALTURA_BASE: 120,          // se multiplica por radius/500
    TICK_S: 0.5,

    // ---- ciclo de vida de una nube ----
    CYCLE_BASE_S: 240,
    CYCLE_RANGE_S: 60,         // vida maxima = 180-300 s
    UMBRAL_JITTER: 0.3,        // el rango de cada umbral varia +-30% por ciclo

    // ---- grilla ----
    GRID_BANDS: 12,            // 15 grados cada una
    GRID_SECTORS: 24,
    NUBES_POR_CELDA: 3,

    // ---- biomas ----
    // tasa: unidades de evaporacion/s. nube/lluvia: [base, rango].
    // pConv/multConv: nubes convectivas crecen mas rapido (tormentas).
    // cobertura: fraccion del planeta cubierta de nubes (tope de puppets).
    // nieve: 'siempre' | 'polos' | 'nunca'.
    BIOMAS: {
        earth:    { clima: 'agua', tasa: 1.0, nube: [100, 15], lluvia: [200, 30],  pLluvia: 0.70, pTormenta: 0.15, pConv: 0.25, multConv: 2, cobertura: 0.55, nieve: 'polos', pEstrato: 0.4 },
        tropical: { clima: 'agua', tasa: 0.9, nube: [45, 7],   lluvia: [70, 10],   pLluvia: 0.85, pTormenta: 0.35, pConv: 0.40, multConv: 2, cobertura: 0.70, nieve: 'nunca', pEstrato: 0.1 },
        desert:   { clima: 'agua', tasa: 1.0, nube: [500, 75], lluvia: [2500, 375], pLluvia: 0.15, pTormenta: 0.30, pConv: 0.20, multConv: 8, cobertura: 0.05, nieve: 'nunca', pEstrato: 0.0, pVirga: 0.6, vientoLluviaMult: 2.5 },
        ice_boss: { clima: 'agua', tasa: 0.6, nube: [80, 12],  lluvia: [160, 24],  pLluvia: 0.75, pTormenta: 0.03, pConv: 0.10, multConv: 1.5, cobertura: 0.40, nieve: 'siempre', pEstrato: 0.5 },
        lava:       { clima: 'lava' },
        metal:      { clima: 'metal' },
        metal_boss: { clima: 'metal' }
        // moon, asteroid, gas, sol: sin clima
    },
    NIEVE_LAT_POLOS: 60,       // respaldo si el planeta no trae temperatura
    // Linea de nieve segun la temperatura del planeta (editor 0-100). El terreno
    // Earth pone hielo donde la temperatura local es baja (pa/terrain/earth.json,
    // sub-bioma ice); el motor la calcula en C++. Calibrado a ojo con el editor
    // (Pablo, 2026-09-24): [temperatura, latitud desde la que nieva].
    NIEVE_POR_TEMP: [[0, 0], [15, 19], [32, 37], [45, 60], [61, 88], [65, 91]],
    // Franja SECA (sub-bioma desert de earth.json, temperatura local alta): con
    // los mismos datos la nieve empieza a ~1.3 x temp grados; el desierto cubre
    // |lat| < 1.3 x temp - 44 (HSO 50 -> 21, Augur 61 -> 35, 32 -> nada). Ahi
    // se usa el clima de BIOMAS.desert: casi no llueve y mucho es virga (Pablo).
    SECA_K: 1.3,
    SECA_OFFSET: 44,
    ESTRATO_LAT: [40, 65],

    // Multiplicador de evaporacion por latitud (circulacion real).
    LAT_MULT: [
        { hasta: 10, mult: 1.5 },  // ZCIT
        { hasta: 20, mult: 1.0 },
        { hasta: 35, mult: 0.4 },  // franja seca subtropical
        { hasta: 40, mult: 0.8 },
        { hasta: 65, mult: 1.1 },  // frentes de latitud media
        { hasta: 90, mult: 0.5 }   // polos
    ],

    LLUVIA_DURACION_S: [60, 150], // cuanto dura una lluvia (x1.5 tormenta)
    RAMPA_S: 15,               // llovizna al empezar y al terminar (cambio gradual)
    NUBE_LLENA_S: 20,          // la lluvia/nieve espera a que su nube lleve esto formandose
    RETORNO_DISIPA: 0.5,       // nube que no llueve devuelve esto a la celda
    FACTOR_TORMENTA: 1.5,      // potencial >= umbral lluvia x esto = tormenta
    CRECER_CADA_S: 4,
    DISIPAR_CADA_S: 6,

    // ---- tipos de nube ----
    TIPOS: {
        cumulo:      { maxCuerpos: 4, radio: 25 },
        estrato:     { maxCuerpos: 8, paso: 38 },   // era 45: banda continua (cuerpo ~60 de ancho)
        cumulonimbo: { maxCuerpos: 6, radio: 22, alturas: [0, 30, 60] }
    },
    // Area que tapa un cuerpo (tope de cobertura = area planeta x cobertura / esto).
    // 3300 era para cuerpos chicos (radio ~31). Con bocanadas grandes (radio ~85,
    // solapadas dentro de la nube) 3300 tapaba casi todo el planeta en 1 min.
    CUERPO_AREA: 12000,
    CUERPO_DIST: [0.3, 0.75],  // distancia de cada cuerpo al centro (x radio). Era 0.4-1: huecos

    // ---- viento ----
    // dir en grados desde el este, antihorario (0 = hacia el este, 180 = hacia el oeste).
    // Mueve nubes y plumas; la lluvia/nieve se inclina con accelX/Z en el .pfx.
    BANDAS_VIENTO: [
        { hasta: 30, dir: 180, vel: 1.0 },  // alisios
        { hasta: 60, dir: 0,   vel: 1.6 },  // oestes
        { hasta: 90, dir: 180, vel: 0.5 }   // polares
    ],
    VIENTO_BASE: 0.5,          // yardas/s a radio 500 (medio planeta en ~30-60 min)
    VIENTO_VEL_JITTER: 0.3,
    VIENTO_DIR_JITTER: 20,
    // Ciclo global (Atlas 3.6): toda llamada al motor interrumpe los movimientos
    // de los demas puppets -> cada DRIFT_S se crea, borra y mueve TODO en lote,
    // nada entre medio. Un motor con reloj real encadena los pasos.
    DRIFT_S: 8,                // duracion de cada paso de movimiento. Con 4 habia picos de frametime cada ciclo (PresentMon); con 8 plano
    MOTOR_MS: 100,             // cada cuanto revisa el motor si toca mover

    // Ejes locales del puppet (calibrado en juego 2026-09-22, Atlas 3.6):
    // en lon 0 +X local = SUR, +Z = ESTE; el eje gira con la longitud.
    // Angulo local = (dirMundo - OFFSET - LON_SIGNO x lon) x SIGNO.
    VIENTO_LOCAL_OFFSET_DEG: -90,
    VIENTO_LOCAL_SIGNO: 1,
    VIENTO_LOCAL_LON_SIGNO: -1, // lon 0 sur, lon 90 oeste, lon 180 norte: rumbo de +X = 270 - lon

    // ---- presupuesto de particulas ----
    PART_POR_PLANETA_REF: 29000,  // planeta radio 500; escala por area y por NIVELES.nubes
    PART_GLOBAL: 500000,
    COSTO: {  // RESPALDO: los costos reales por variante vienen de parametros.json
        nubes: 17, lluvia_viento: 220, lluvia_ventarron: 300, virga_viento: 70, nieve_viento: 600
    },

    // ---- creacion de puppets ----
    // Generaciones de nube (respaldo; valores reales en parametros.json).
    NUBE_GEN_S: 30,            // cada puppet de nube emite esto y se detiene solo (emitterLifetime)
    NUBE_VIDA_MAX_S: 38,       // vida maxima de una bocanada
    GEN_ANTICIPO_S: 10,        // la generacion nueva nace esto antes de que la vieja deje de emitir (>= DRIFT_S + 2: el relevo se revisa por ciclo)
    CREAR_POR_CICLO: 40,       // pocas creaciones por ciclo, repartidas (400 daba tirones)
    // Planeta destruido: la atmosfera se va en MUERTE_S como maximo (registro.js
    // ejecutarDespedida). Nubes y plumas se estiran (escala local x,y,z) y se
    // alejan (radio x EMPUJE); la lluvia pasa a virga; lo demas se apaga.
    // Fraccion de la capacidad de la cola que pueden usar los relevos de nubes;
    // el resto queda para lluvia/nieve, nubes nuevas y demas (reg.repartir).
    CAPACIDAD_USO: 0.7,
    MUERTE_S: 10,
    MUERTE_TANDAS: 5,          // borrado en tandas al azar (se va por partes, no de golpe)
    MUERTE_ESTIRA: [3.0, 0.4, 1.6],   // aprobado por Pablo (2026-09-24)
    MUERTE_EMPUJE: 1.09,              // Pablo: 1.35 alejaba demasiado -> alejamiento / 4
    VIGIA_S: 600,              // 0 = apagado. Cada 10 s daba picos de frametime (getAllPuppets); va dentro del ciclo

    // Precalentamiento: el clima corre en silencio antes de mostrar nada.
    PRECALENTAMIENTO_S: 2400,
    PRECALENTAMIENTO_DT: 5,

    // ---- calidad por efecto (menu Settings, opciones.js) ----
    // high = valores aprobados en juego; extreme = 150 % de high.
    NIVEL: { nubes: 'high', precip: 'high', rayos: 'high', plumas: 'high', rayosLava: 'high', arcos: 'high' },
    NIVELES: {
        nubes:     { low: 0.5, medium: 0.75, high: 1.0, extreme: 1.5 },   // tope de nubes y presupuesto de particulas
        precip:    { low: 'centro', medium: 'mitad', high: 'todos', extreme: 'denso' }, // cuerpos que llueven; denso = variantes _x15
        rayos:     { low: 3, medium: 6, high: 10, extreme: 15 },           // reserva de rayos por familia (tormentas con rayos a la vez)
        plumas:    { low: 0.6, medium: 0.8, high: 1.0, extreme: 1.5 },     // x plumasBase / plumasMax
        rayosLava: { low: [1, 0], medium: [1, 0.2], high: [2, 0.4], extreme: [3, 0.6] }, // [rayos de nube, prob. rayo a tierra] por pluma
        arcos:     { low: 4, medium: 8, high: 12, extreme: 18 }            // arcos por planeta r500
    },
    // Multiplicadores de Avanzado (1 = normal).
    MULT_LLUVIA: 1,
    MULT_TORMENTA: 1,

    // ---- relampagos de tormenta ----
    // Horneados (scripts/generar_pfx.py, rayoh_tierra / rayoh_nube), en bucle.
    // Reserva: creados al arrancar, estacionados bajo tierra; cada tormenta
    // toma 1 a tierra + 1 de nube. Crear rayos en juego = tiron.
    RESERVA_PROFUNDIDAD: 0.3,  // radio del estacionamiento (fraccion del radio: bajo tierra)
    RAYO_ESPESOR: 6,           // = base del nucleo de nubes (RAYOH_ESPESOR_NUBE en generar_pfx.py)

    // ---- metal: cortocircuitos horneados en bucle ----
    // Cantidad de arcos: NIVELES.arcos (escala por area).
    METAL: {
        pNaranja: 0.1,
        reubicar: [20, 50]      // s: cada arco salta a otro lugar (si no, chispas siempre en los mismos puntos)
    },

    // ---- lava (de LavaTest; su ventana ajusta y valida) ----
    // Rayos volcanicos en bucle dentro de cada pluma: NIVELES.rayosLava.
    LAVA: {
        plumasBase: 5, plumasMin: 3, plumasMax: 8,   // x NIVELES.plumas
        pBrillo: 0.6, pBarro: 0.35
    },

    LOG: true
};
// Valores base de lo que Avanzado multiplica o reemplaza (registro.js aplica las opciones).
AW.cfgBase = JSON.parse(JSON.stringify(AW.cfg));
