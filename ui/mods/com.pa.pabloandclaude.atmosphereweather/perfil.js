// AtmosphereWeather — perfil de planeta: sol / gaseoso / rocoso + bioma -> clima.
// Datos reales disponibles en partida (Atlas 1.4): biome, radius, isSun, dead.
// No hay dato de agua/oceanos: la humedad sale solo del bioma.
(function () {
    'use strict';
    var AW = window.AtmosphereWeather;
    var cfg = AW.cfg;

    function val(x) { return typeof x === 'function' ? x() : x; }

    AW.estaMuerto = function (info) { return !!(info && val(info.dead)); };

    // Temperatura del planeta: viene en celestial_data (campo temp) pero el
    // modelo de la UI no la guarda -> se captura envolviendo el handler.
    var temps = {};
    if (typeof handlers !== 'undefined' && handlers.celestial_data) {
        var orig = handlers.celestial_data;
        handlers.celestial_data = function (payload) {
            try {
                (payload && payload.planets || []).forEach(function (pl, i) { temps[i] = pl.temp; });
            } catch (e) { /* nada */ }
            return orig.apply(this, arguments);
        };
    }

    // Latitud hasta la que el terreno es desierto (0 = sin franja seca).
    AW.latSeca = function (temp) {
        if (typeof temp !== 'number' || isNaN(temp)) { return 0; }
        return Math.max(0, cfg.SECA_K * temp - cfg.SECA_OFFSET);
    };

    // Latitud desde la que nieva (cfg.NIEVE_POR_TEMP, interpolada).
    AW.latNieve = function (temp) {
        var T = cfg.NIEVE_POR_TEMP;
        if (typeof temp !== 'number' || isNaN(temp)) { return cfg.NIEVE_LAT_POLOS; }
        if (temp <= T[0][0]) { return T[0][1]; }
        for (var i = 1; i < T.length; i++) {
            if (temp <= T[i][0]) {
                var f = (temp - T[i - 1][0]) / (T[i][0] - T[i - 1][0]);
                return T[i - 1][1] + f * (T[i][1] - T[i - 1][1]);
            }
        }
        return T[T.length - 1][1];
    };

    // Devuelve null si el planeta no lleva clima.
    AW.perfil = function (planetId, info) {
        if (!info) { return null; }
        var biome = val(info.biome);
        var esSol = val(info.isSun) === true;
        var gaseoso = val(info.has_terrain) === false || biome === 'gas';
        var bio = cfg.BIOMAS[biome];
        var motivo = esSol ? 'sol' : gaseoso ? 'gaseoso' : !bio ? 'bioma sin clima' : AW.estaMuerto(info) ? 'muerto' : null;
        if (motivo) {
            AW.log('perfil_sin_clima', { planetId: planetId, biome: biome, motivo: motivo });
            return null;
        }
        var radius = val(info.radius) || cfg.REFERENCE_RADIUS;
        var scale = radius / cfg.REFERENCE_RADIUS;
        var p = {
            planetId: planetId,
            nombre: val(info.name),
            biome: biome,
            clima: bio.clima,
            bio: bio,
            radius: radius,
            // celestial_data.temp NO es la del editor: temp = 0.035 x editor - 1.5
            // (medido con el .pas de Gamma: 0->-1.5, 50->0.25, 100->2). Se pasa a 0-100.
            temp: typeof temps[planetId] === 'number' ? Math.round((temps[planetId] + 1.5) / 0.035) : undefined,
            scale: scale,
            rNube: radius + scale * cfg.ALTURA_BASE
        };
        AW.log('perfil', { planetId: planetId, nombre: p.nombre, biome: biome, clima: p.clima, radius: radius,
            temp: p.temp, latNieve: bio.nieve === 'polos' ? Math.round(AW.latNieve(p.temp)) : bio.nieve,
            latSeca: bio.nieve === 'polos' ? Math.round(AW.latSeca(p.temp)) : 0 });
        return p;
    };
}());
