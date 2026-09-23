// AtmosphereWeather — geometria y azar. Funciones cerradas copiadas tal cual
// de los mods de prueba (Atlas 3.2 y 3.4): NO modificar sin reabrir la
// investigacion de orientacion.
(function () {
    'use strict';
    var AW = window.AtmosphereWeather;
    var cfg = AW.cfg;
    var geo = AW.geo = {};

    geo.rand = function (min, max) { return min + Math.random() * (max - min); };
    geo.randInt = function (min, max) { return min + Math.floor(Math.random() * (max - min + 1)); };
    geo.pick = function (arr) { return arr[Math.floor(Math.random() * arr.length)]; };
    geo.clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };

    // Umbral con rango doble: base +- rango, y el rango varia +-UMBRAL_JITTER.
    geo.umbral = function (par) {
        var rango = par[1] * (1 + geo.rand(-cfg.UMBRAL_JITTER, cfg.UMBRAL_JITTER));
        return par[0] + geo.rand(-rango, rango);
    };

    geo.cicloS = function () {
        return cfg.CYCLE_BASE_S + geo.rand(-cfg.CYCLE_RANGE_S, cfg.CYCLE_RANGE_S);
    };

    // ---- arquitectura CERRADA ----
    geo.latLonToPos = function (latDeg, lonDeg, r) {
        var lat = latDeg * Math.PI / 180, lon = lonDeg * Math.PI / 180;
        return [r * Math.cos(lat) * Math.cos(lon), r * Math.cos(lat) * Math.sin(lon), r * Math.sin(lat)];
    };

    function quatFromToRotation(f, t) {
        var dot = f[0] * t[0] + f[1] * t[1] + f[2] * t[2];
        if (dot > 0.999999) { return [0, 0, 0, 1]; }
        if (dot < -0.999999) {
            var a = Math.abs(f[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0];
            var x0 = f[1] * a[2] - f[2] * a[1], y0 = f[2] * a[0] - f[0] * a[2], z0 = f[0] * a[1] - f[1] * a[0];
            var l0 = Math.sqrt(x0 * x0 + y0 * y0 + z0 * z0);
            return [x0 / l0, y0 / l0, z0 / l0, 0];
        }
        var cx = f[1] * t[2] - f[2] * t[1], cy = f[2] * t[0] - f[0] * t[2], cz = f[0] * t[1] - f[1] * t[0];
        var w = 1 + dot;
        var len = Math.sqrt(cx * cx + cy * cy + cz * cz + w * w);
        return [cx / len, cy / len, cz / len, w / len];
    }

    function latLonToOrientQuatBlend(latDeg, lonDeg) {
        var lat = latDeg * Math.PI / 180, lon = lonDeg * Math.PI / 180;
        var o = [Math.cos(lat) * Math.cos(lon), Math.cos(lat) * Math.sin(lon), Math.sin(lat)];
        var q = quatFromToRotation([0, 1, 0], [-o[0], -o[1], -o[2]]);
        var cx = q[0], cz = q[2], w = q[3];
        var m = Math.sqrt(cx * cx + cz * cz);
        if (m < 1e-9) { return q; }
        var thN = Math.atan2(-cx, cz) * 180 / Math.PI;
        var thU = thN < 0 ? (180 + thN) : thN;
        var thS = 90 + thN;
        var t = Math.min(1, Math.abs(thN) / 90);
        var th = (thU * t + thS * (1 - t)) * Math.PI / 180;
        return [-m * Math.sin(th), 0, m * Math.cos(th), w];
    }

    geo.orient = function (latDeg) { return latLonToOrientQuatBlend(latDeg, 0); };
    // ---- fin arquitectura cerrada ----

    // Offset (dx este, dy norte) en el plano tangente a (latC, lonC) -> lat/lon (LavaTest).
    geo.offset = function (latC, lonC, dx, dy, r) {
        var lat = latC * Math.PI / 180, lon = lonC * Math.PI / 180;
        var c = [Math.cos(lat) * Math.cos(lon), Math.cos(lat) * Math.sin(lon), Math.sin(lat)];
        var e = [-Math.sin(lon), Math.cos(lon), 0];
        var n = [-Math.sin(lat) * Math.cos(lon), -Math.sin(lat) * Math.sin(lon), Math.cos(lat)];
        var p = [c[0] * r + e[0] * dx + n[0] * dy, c[1] * r + e[1] * dx + n[1] * dy, c[2] * r + e[2] * dx + n[2] * dy];
        var len = Math.sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2]);
        var lonDeg = Math.atan2(p[1], p[0]) * 180 / Math.PI;
        if (lonDeg < 0) { lonDeg += 360; }
        return { lat: Math.asin(geo.clamp(p[2] / len, -1, 1)) * 180 / Math.PI, lon: lonDeg };
    };

    geo.latUniforme = function () { return Math.asin(2 * Math.random() - 1) * 180 / Math.PI; };

    geo.latMult = function (lat) {
        var a = Math.abs(lat);
        for (var i = 0; i < cfg.LAT_MULT.length; i++) {
            if (a <= cfg.LAT_MULT[i].hasta) { return cfg.LAT_MULT[i].mult; }
        }
        return 1;
    };

    geo.bandaViento = function (lat) {
        var a = Math.abs(lat);
        for (var i = 0; i < cfg.BANDAS_VIENTO.length; i++) {
            if (a <= cfg.BANDAS_VIENTO[i].hasta) { return cfg.BANDAS_VIENTO[i]; }
        }
        return cfg.BANDAS_VIENTO[cfg.BANDAS_VIENTO.length - 1];
    };

    // Direccion del viento (grados desde el este, antihorario) en una latitud,
    // con la desviacion propia de la nube. Oestes se abren hacia el polo,
    // alisios/polares hacia el ecuador (efecto Coriolis, como en la Tierra).
    geo.dirViento = function (lat, dirJ) {
        var b = geo.bandaViento(lat);
        var h = lat >= 0 ? 1 : -1;
        return b.dir + h * 15 + dirJ;
    };

    // Viento en (lat, lon) + rafaga -> variante de direccion (1..nDir) en ejes
    // locales del puppet (Atlas 3.6: +X sur, +Z este; el eje gira con la longitud).
    geo.dirLocal = function (lat, lon, dirJ, rafaga, nDir) {
        var dirMundo = geo.dirViento(lat, dirJ) + (rafaga || 0);
        var giro = cfg.VIENTO_LOCAL_OFFSET_DEG + cfg.VIENTO_LOCAL_LON_SIGNO * lon;
        var local = (((dirMundo - giro) * cfg.VIENTO_LOCAL_SIGNO) % 360 + 360) % 360;
        return 1 + Math.round(local / (360 / nDir)) % nDir;
    };

    // Un paso de deriva: nueva lat/lon tras durS segundos de viento.
    geo.derivar = function (lat, lon, r, velJ, dirJ, scale, mult, durS) {
        var b = geo.bandaViento(lat);
        var d = cfg.VIENTO_BASE * b.vel * velJ * scale * (mult || 1) * durS;
        var ang = geo.dirViento(lat, dirJ) * Math.PI / 180;
        return geo.offset(lat, lon, d * Math.cos(ang), d * Math.sin(ang), r);
    };
}());
