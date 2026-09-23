// AtmosphereWeather — registro de puppets propios, cola de creacion, vigia,
// variantes y presupuesto. NUNCA usa clearPuppets() (global: mata puppets de
// otros mods). Solo unPuppet() sobre ids propios.
(function () {
    'use strict';
    var AW = window.AtmosphereWeather;
    var cfg = AW.cfg;
    var geo = AW.geo;
    var reg = AW.reg = {};

    var runId = Date.now().toString(36);
    var PROPIO_RE = /\/atmosphereweather\//;

    // Con el log de diagnostico apagado (default para jugadores) igual se
    // escriben el arranque y los errores: sirven para dar soporte.
    var SIEMPRE = /cargado|error|excepcion|rechazado|sin_id|sin_planetas/;
    AW.log = function (evento, data) {
        if (!cfg.LOG && !SIEMPRE.test(evento)) { return; }
        try {
            console.log('[AtmosphereWeather v' + AW.VERSION + '] ' + evento + ' ' + JSON.stringify({ run: runId, data: data }));
        } catch (e) {
            console.log('[AtmosphereWeather] ' + evento + ' (stringify fallo)');
        }
    };
    function errStr(e) { return String(e && e.message || e); }

    // ---------------- variantes ----------------
    reg.variantes = cfg.VARIANTES_DEFAULT;

    reg.costos = null; // de parametros.json: particulas reales por variante

    // Carga variantes.json y parametros.json (los escribe scripts/generar_pfx.py).
    reg.cargarVariantes = function (listo) {
        var pendientes = 2, hecho = false, origen = [];
        function fin() {
            if (hecho) { return; }
            hecho = true;
            AW.log('variantes', { origen: origen, altura: cfg.ALTURA_BASE, conteos: reg.variantes });
            listo();
        }
        function uno(nombre) { origen.push(nombre); if (--pendientes === 0) { fin(); } }
        function cargar(url, nombre, aplicar) {
            try {
                $.getJSON(url).then(function (data) {
                    if (data && typeof data === 'object') { aplicar(data); uno(nombre); } else { uno(nombre + ' vacio'); }
                }, function () { uno(nombre + ' no cargo (default)'); });
            } catch (e) {
                uno(nombre + ' excepcion (default)');
            }
        }
        cargar(cfg.VARIANTES_URL, 'variantes.json', function (d) { reg.variantes = d; });
        cargar(cfg.PARAMETROS_URL, 'parametros.json', function (d) {
            if (d.altura_nubes) { cfg.ALTURA_BASE = d.altura_nubes; }
            if (d.nube_generacion_s) { cfg.NUBE_GEN_S = d.nube_generacion_s; }
            if (d.nube_vida_max_s) { cfg.NUBE_VIDA_MAX_S = d.nube_vida_max_s; }
            if (d.costos) { reg.costos = d.costos; }
        });
        setTimeout(function () { origen.push('timeout'); fin(); }, 3000);
    };

    reg.cuantas = function (efecto) { return reg.variantes[efecto] || 0; };

    // idx 1-based; si pide mas de las que hay, se ajusta a la ultima.
    reg.pfx = function (efecto, idx) {
        var n = reg.cuantas(efecto);
        if (!n) { return null; }
        var i = geo.clamp(Math.round(idx), 1, n);
        return cfg.SPEC_DIR + efecto + '_var' + (i < 10 ? '0' : '') + i + '.pfx';
    };
    // nivel 0..1 -> una de TODAS las variantes disponibles.
    reg.pfxNivel = function (efecto, nivel) {
        var n = reg.cuantas(efecto);
        return reg.pfx(efecto, 1 + Math.round(geo.clamp(nivel, 0, 1) * (n - 1)));
    };
    reg.pfxAzar = function (efecto) {
        var n = reg.cuantas(efecto);
        return n ? reg.pfx(efecto, geo.randInt(1, n)) : null;
    };

    reg.fx = function (pfx) {
        return { type: 'idle', filename: pfx, bone: 'bone_root', offset: [0, 0, 0], orientation: [0, 0, 0] };
    };

    reg.location = function (planetId, lat, lon, r, scale) {
        return { planet: planetId, pos: geo.latLonToPos(lat, lon, r), orient: geo.orient(lat), scale: scale, snap: false };
    };

    // Version LIVIANA para movePuppet: el lote del ciclo lleva ~1.300 entradas;
    // con 15 decimales y campos fijos eran ~200 KB de JSON por ciclo. Todo
    // campo de location es opcional en movePuppet (worldview.js): solo
    // posicion (0.1 yd) y orientacion.
    function red(v, k) { return Math.round(v * k) / k; }
    reg.locMover = function (loc) {
        var l = {
            planet: loc.planet,
            pos: [red(loc.pos[0], 10), red(loc.pos[1], 10), red(loc.pos[2], 10)],
            orient: [red(loc.orient[0], 1e4), red(loc.orient[1], 1e4), red(loc.orient[2], 1e4), red(loc.orient[3], 1e4)]
        };
        // snap solo viaja si hace falta (lote liviano). Los arcos de metal lo
        // mandan SIEMPRE (enviarSnap): el motor parece recordar el snap del
        // puppet, y al estacionarlos bajo tierra sin snap:false explicito
        // volvian a pegarse a la superficie (chispas apagadas que seguian).
        if (loc.snap || loc.enviarSnap) { l.snap = !!loc.snap; }
        return l;
    };

    // ---------------- registro ----------------
    // id -> { etiqueta, creado, alPerder }
    var propios = {};
    reg.cantidad = function () { return Object.keys(propios).length; };

    // Cola: se vacia en el ciclo de movimiento (main.js), nunca entre medio.
    var cola = [];
    // Vacia la cola en UNA llamada (worldview.puppet acepta arrays) y llama
    // listo() cuando el motor devolvio los ids: asi el ciclo puede mover
    // tambien a las recien creadas (si no, quedaban quietas un ciclo).
    reg.procesarCola = function (max, listo) {
        var tareas = [];
        while (cola.length && tareas.length < max) {
            var t = cola.shift();
            if (!(t.cancelado && t.cancelado())) { tareas.push(t); }
        }
        var hecho = false;
        function fin() { if (!hecho) { hecho = true; if (listo) { listo(); } } }
        if (!tareas.length) { fin(); return; }
        try {
            api.getWorldView(0).puppet(tareas.map(function (t) { return { location: t.location, fx_offsets: t.fx }; }), true).then(function (res) {
                res = Array.isArray(res) ? res : [res];
                for (var i = 0; i < tareas.length; i++) { registrarCreado(tareas[i], res[i] && res[i].id); }
                fin();
            }, function (err) {
                AW.log('crear_lote_rechazado', { n: tareas.length, error: errStr(err) });
                fin();
            });
        } catch (e) {
            AW.log('crear_lote_excepcion', { n: tareas.length, error: errStr(e) });
            fin();
        }
        setTimeout(fin, 1000); // no trabar el ciclo si la promesa no vuelve
    };

    function registrarCreado(t, id) {
        if (id === undefined || id === null) { AW.log(t.etiqueta + '_sin_id', {}); return; }
        if (t.cancelado && t.cancelado()) { reg.matar(id); return; }
        propios[id] = { etiqueta: t.etiqueta, creado: Date.now(), alPerder: t.alPerder };
        if (t.alCrear) { t.alCrear(id); }
    }

    // t = { location, fx:[...], etiqueta, alCrear(id), alPerder(), cancelado() }
    // Se crea en el proximo ciclo (reg.procesarCola, main.js).
    reg.crear = function (t) { cola.push(t); };

    // Confirmado en juego (2026-09-22): toda llamada al motor entre ciclos
    // interrumpe los movimientos de los demas puppets. Borrados y movimientos
    // se acumulan y salen en el ciclo (reg.flush).
    var aMatar = [];
    reg.matar = function (id) {
        if (id === null || id === undefined) { return; }
        delete propios[id];
        aMatar.push(id);
    };

    // worldview.movePuppet acepta arrays (worldview.js): todos los movimientos
    // pendientes viajan en UNA llamada por ciclo (reg.flush, lo llama main.js).
    var movs = {};
    reg.mover = function (id, location, durS) {
        if (id === null || id === undefined) { return; }
        movs[id] = { loc: reg.locMover(location), dur: Math.round(durS * 1000) / 1000 };
    };
    var movidos = 0, lotes = 0, atrasoMax = 0, atrasoSum = 0, atrasoN = 0;
    // Atraso del motor de movimiento respecto al reloj (ms): diagnostico.
    AW.motorStats = function (ms) {
        atrasoMax = Math.max(atrasoMax, ms); atrasoSum += ms; atrasoN++;
    };
    reg.flush = function () {
        var wv = api.getWorldView(0);
        if (aMatar.length) {
            var am = aMatar; aMatar = [];
            try { wv.unPuppet(am, true); } catch (e1) { AW.log('matar_lote_excepcion', { n: am.length, error: errStr(e1) }); }
        }
        var ids = [], locs = [], durs = [];
        for (var k in movs) {
            if (!movs.hasOwnProperty(k) || !propios[k]) { continue; }
            ids.push(Number(k)); locs.push(movs[k].loc); durs.push(movs[k].dur);
        }
        movs = {};
        if (!ids.length) { return; }
        movidos += ids.length; lotes++;
        try {
            api.getWorldView(0).movePuppet(ids, locs, durs).then(function () {}, function (err) {
                AW.log('mover_lote_rechazado', { n: ids.length, error: errStr(err) });
            });
        } catch (e) {
            AW.log('mover_lote_excepcion', { n: ids.length, error: errStr(e) });
        }
    };
    setInterval(function () {
        AW.log('estado', { puppets: reg.cantidad(), movidosPorMin: movidos, lotesPorMin: lotes,
            atrasoMotorMs: { max: Math.round(atrasoMax), medio: atrasoN ? Math.round(atrasoSum / atrasoN) : 0 } });
        movidos = 0; lotes = 0; atrasoMax = 0; atrasoSum = 0; atrasoN = 0;
    }, 60000);

    // ---------------- getAllPuppets ----------------
    // Estructura del resultado no documentada: se busca el id en cada item y
    // se identifica lo propio por la ruta de nuestros .pfx.
    function listarTodos(cb) {
        try {
            api.getWorldView(0).getAllPuppets(true).then(function (all) {
                var lista = Array.isArray(all) ? all : (all && all.puppets) || [];
                cb(lista);
            }, function (err) { AW.log('get_all_rechazado', { error: errStr(err) }); cb(null); });
        } catch (e) {
            AW.log('get_all_excepcion', { error: errStr(e) });
            cb(null);
        }
    }
    function idDe(item) {
        var id = item && item.id !== undefined ? item.id : item;
        return typeof id === 'number' ? id : null;
    }

    // Tras F5 el JS nuevo no conoce los ids del anterior: purga por ruta.
    reg.purgarViejos = function (listo) {
        var hecho = false;
        function fin() { if (!hecho) { hecho = true; listo(); } }
        listarTodos(function (lista) {
            if (lista) {
                var viejos = [];
                for (var i = 0; i < lista.length; i++) {
                    var s = '';
                    try { s = JSON.stringify(lista[i]); } catch (e) { continue; }
                    var id = idDe(lista[i]);
                    if (id !== null && PROPIO_RE.test(s) && !propios[id]) { viejos.push(id); }
                }
                if (viejos.length) {
                    try { api.getWorldView(0).unPuppet(viejos, true); } catch (e2) { AW.log('purga_excepcion', { error: errStr(e2) }); }
                }
                var muestra = '';
                try { muestra = JSON.stringify(lista[0]).slice(0, 400); } catch (e3) { muestra = 'n/a'; }
                AW.log('purga', { total: lista.length, purgados: viejos.length, muestra: muestra });
            }
            fin();
        });
        setTimeout(fin, 3000);
    };

    // Vigia: si otro mod borro puppets nuestros (clearPuppets), se recrean.
    var avisoEstructura = false;
    function vigia() {
        var n = reg.cantidad();
        if (!n) { return; }
        listarTodos(function (lista) {
            if (!lista) { return; }
            var vivos = {}, encontrados = 0;
            for (var i = 0; i < lista.length; i++) {
                var id = idDe(lista[i]);
                if (id !== null) { vivos[id] = true; encontrados++; }
            }
            if (!encontrados) {
                if (!avisoEstructura) { avisoEstructura = true; AW.log('vigia_sin_ids', { nota: 'estructura de getAllPuppets desconocida, vigia inactivo' }); }
                return;
            }
            var ahora = Date.now(), perdidos = 0;
            for (var k in propios) {
                if (!propios.hasOwnProperty(k)) { continue; }
                var p = propios[k];
                if (!vivos[k] && ahora - p.creado > 5000) {
                    delete propios[k];
                    perdidos++;
                    if (p.alPerder) { try { p.alPerder(); } catch (e) { AW.log('vigia_recrear_error', { error: errStr(e) }); } }
                }
            }
            if (perdidos) { AW.log('vigia_recreados', { perdidos: perdidos }); }
        });
    }
    // Lo llama el ciclo global (main.js) antes del lote: getAllPuppets es una
    // llamada al motor y cada 10 s daba picos de frametime (PresentMon).
    var proxVigia = Date.now() + cfg.VIGIA_S * 1000;
    reg.vigiaCiclo = function () {
        if (!(cfg.VIGIA_S > 0) || Date.now() < proxVigia) { return; }
        proxVigia = Date.now() + cfg.VIGIA_S * 1000;
        vigia();
    };

    // ---------------- presupuesto ----------------
    reg.costo = function (efecto, idx) {
        var real = reg.costos && reg.costos[efecto];
        if (real && real.length) { return real[geo.clamp(Math.round(idx || 1) - 1, 0, real.length - 1)]; }
        var c = cfg.COSTO[efecto];
        if (c === undefined) { return 0; }
        if (Array.isArray(c)) { return c[geo.clamp(Math.round(idx) - 1, 0, c.length - 1)]; }
        return c;
    };

    // Reparte: PART_POR_PLANETA_REF escalado por area y por la calidad de nubes;
    // si pasa el global, todos bajan parejo. Se puede volver a llamar en partida.
    // planetas: simuladores (cada uno con .p = perfil); se les fija .presupuesto.
    reg.repartir = function (planetas) {
        var total = 0, i;
        for (i = 0; i < planetas.length; i++) {
            var s = planetas[i].p.scale;
            planetas[i].presupuesto = cfg.PART_POR_PLANETA_REF * s * s * reg.nivel('nubes');
            total += planetas[i].presupuesto;
        }
        if (total > cfg.PART_GLOBAL) {
            var f = cfg.PART_GLOBAL / total;
            for (i = 0; i < planetas.length; i++) { planetas[i].presupuesto *= f; }
        }
        AW.log('presupuesto', { planetas: planetas.length, total: Math.round(Math.min(total, cfg.PART_GLOBAL)) });
    };

    // Valor del nivel de calidad elegido para un efecto (cfg.NIVELES).
    reg.nivel = function (efecto) {
        var t = cfg.NIVELES[efecto];
        var v = t[cfg.NIVEL[efecto]];
        return v === undefined ? t.high : v;
    };

    // ---------------- opciones del menu Settings (opciones.js) ----------------
    // live_game carga los settings UNA vez al arrancar: al cerrar el menu en
    // partida se relee localStorage (recargar). Devuelve las opciones leidas.
    reg.leerOpciones = function (recargar) {
        var O = AW.OPCIONES, o = {};
        try {
            if (recargar) { api.settings.loadLocalData(); }
            var S = O.definicion.settings;
            for (var k in S) {
                if (!S.hasOwnProperty(k)) { continue; }
                var v = api.settings.value(O.GRUPO, k);
                o[k] = v === undefined || v === null ? S[k].default : v;
            }
            // Avanzado apagado = valores por defecto (lo guardado no se usa).
            if (o.advanced !== 'on') { O.AVANZADAS.forEach(function (a) { o[a] = S[a].default; }); }
        } catch (e) {
            AW.log('opciones_error', { error: errStr(e) });
            return null;
        }
        aplicar(o);
        return o;
    };

    function aplicar(o) {
        var B = AW.cfgBase, on = function (k) { return o[k] !== 'off'; };
        cfg.EFECTOS = {
            nubes: on('clouds'), lluvia: on('rain'), nieve: on('snow'), virga: on('virga'),
            rayos: on('storm_lightning'), lava: on('volcanic_plumes'),
            rayosLava: on('volcanic_lightning'), metal: on('short_circuits')
        };
        cfg.NIVEL = {
            nubes: o.q_clouds, precip: o.q_precipitation, rayos: o.q_storm_lightning,
            plumas: o.q_volcanic_plumes, rayosLava: o.q_volcanic_lightning, arcos: o.q_short_circuits
        };
        // "Match game graphics": todo sigue al preset de Graphics del jugador.
        if (o.quality === 'auto') {
            var n = AW.OPCIONES.nivelAuto();
            for (var e in cfg.NIVEL) { if (cfg.NIVEL.hasOwnProperty(e)) { cfg.NIVEL[e] = n; } }
        }
        // Los deslizadores pueden guardar el numero como texto: Number() siempre.
        cfg.VIENTO_BASE = B.VIENTO_BASE * Number(o.wind_speed) / 100;
        cfg.MULT_LLUVIA = Number(o.rain_chance) / 100;
        cfg.MULT_TORMENTA = Number(o.storm_chance) / 100;
        cfg.LLUVIA_DURACION_S = B.LLUVIA_DURACION_S.map(function (s) { return s * Number(o.rain_duration) / 100; });
        cfg.CYCLE_BASE_S = B.CYCLE_BASE_S * Number(o.cloud_lifetime) / 100;
        cfg.CYCLE_RANGE_S = B.CYCLE_RANGE_S * Number(o.cloud_lifetime) / 100;
        cfg.PART_POR_PLANETA_REF = Number(o.particle_budget);
        cfg.PART_GLOBAL = Number(o.particle_cap);
        cfg.CREAR_POR_CICLO = Number(o.spawn_per_cycle);
        cfg.DRIFT_S = Number(o.cycle_length);
        // El relevo de generacion se revisa por ciclo: anticipo >= ciclo + 2 s.
        cfg.GEN_ANTICIPO_S = Math.max(B.GEN_ANTICIPO_S, cfg.DRIFT_S + 2);
        cfg.LOG = o.debug_log !== 'off';
    }
}());
