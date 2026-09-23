// AtmosphereWeather — perfil de planeta: sol / gaseoso / rocoso + bioma -> clima.
// Datos reales disponibles en partida (Atlas 1.4): biome, radius, isSun, dead.
// No hay dato de agua/oceanos: la humedad sale solo del bioma.
(function () {
    'use strict';
    var AW = window.AtmosphereWeather;
    var cfg = AW.cfg;

    function val(x) { return typeof x === 'function' ? x() : x; }

    AW.estaMuerto = function (info) { return !!(info && val(info.dead)); };

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
            scale: scale,
            rNube: radius + scale * cfg.ALTURA_BASE
        };
        AW.log('perfil', { planetId: planetId, nombre: p.nombre, biome: biome, clima: p.clima, radius: radius });
        return p;
    };
}());
