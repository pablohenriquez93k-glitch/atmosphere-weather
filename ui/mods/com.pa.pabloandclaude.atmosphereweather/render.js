// AtmosphereWeather — reserva de relampagos de tormenta, cortocircuitos de
// metal y plumas de lava (LavaTest). Las nubes de agua viven en clima.js.
// Rayos y arcos son HORNEADOS (scripts/generar_pfx.py): cada .pfx trae el
// dibujo y se repite solo en bucle; crear un puppet de rayo en juego da tiron,
// por eso todos se crean al arrancar.
(function () {
    'use strict';
    var AW = window.AtmosphereWeather;
    var cfg = AW.cfg;
    var geo = AW.geo;
    var reg = AW.reg;
    var render = AW.render = {};

    // ---------------- reserva de rayos (sin tiron) ----------------
    // Crear un puppet de rayo (~30 emisores) congela el juego un instante.
    // Por eso se crean TODOS al arrancar y quedan estacionados bajo tierra
    // (invisibles); cada .pfx se repite solo (bucle). Una tormenta toma rayos
    // de la reserva: el ciclo los lleva bajo su nube dentro del lote de
    // movimiento (sin llamadas extra) y al terminar vuelven a estacionarse.
    render.Reserva = function (p, n) {
        this.p = p;
        this.slots = [];
        var fams = ['rayoh_tierra', 'rayoh_nube'];
        for (var f = 0; f < fams.length; f++) {
            for (var i = 0; i < n; i++) { this.slots.push(this.nuevo(fams[f])); }
        }
    };
    render.Reserva.prototype.parque = function () {
        var p = this.p, r = p.radius * cfg.RESERVA_PROFUNDIDAD;
        return reg.location(p.planetId, geo.latUniforme(), geo.rand(0, 360), r, p.scale);
    };
    render.Reserva.prototype.nuevo = function (fam) {
        var slot = { fam: fam, pid: null, libre: true, estacion: this.parque() };
        var pfx = reg.pfxAzar(fam);
        if (pfx) {
            reg.crear({ etiqueta: 'reserva_' + fam, location: slot.estacion, fx: [reg.fx(pfx)],
                alCrear: function (id) { slot.pid = id; } });
        }
        return slot;
    };
    render.Reserva.prototype.tomar = function (fam) {
        for (var i = 0; i < this.slots.length; i++) {
            var s = this.slots[i];
            if (s.libre && s.pid !== null && s.fam === fam) { s.libre = false; return s; }
        }
        return null; // reserva agotada: esa tormenta no lleva ese rayo
    };
    render.Reserva.prototype.devolver = function (s) {
        if (!s) { return; }
        s.libre = true;
        reg.mover(s.pid, s.estacion, 0); // salto directo al estacionamiento, en el lote del ciclo
    };
    render.Reserva.prototype.detener = function () {
        for (var i = 0; i < this.slots.length; i++) { reg.matar(this.slots[i].pid); }
        this.slots = [];
    };

    // ---------------- metal: cortocircuitos ----------------
    // Arcos creados una sola vez al arrancar; cada .pfx chisporrotea solo en
    // bucle. Cada arco salta a otro lugar cada cfg.METAL.reubicar s (en el
    // lote del ciclo), si no siempre salen de los mismos puntos.
    render.Metal = function (perfil) {
        this.p = perfil;
        this.vivo = false;
        this.muerto = false;
        this.arcos = [];
    };
    render.Metal.prototype.locAzar = function () {
        var p = this.p;
        // p.radius es el radio BASE: en metal las placas quedan por encima y el
        // arco salia enterrado. snap:true = pegar al terreno real (Atlas 3.6).
        var loc = reg.location(p.planetId, geo.latUniforme(), geo.rand(0, 360), p.radius, p.scale);
        loc.snap = true;
        loc.enviarSnap = true;
        return loc;
    };
    // Apagado (menu Settings): los arcos se estacionan bajo tierra, sin borrarlos,
    // asi volver a encenderlos no crea puppets (crear = tiron).
    render.Metal.prototype.parque = function () {
        var p = this.p;
        var loc = reg.location(p.planetId, geo.latUniforme(), geo.rand(0, 360), p.radius * cfg.RESERVA_PROFUNDIDAD, p.scale);
        loc.enviarSnap = true; // snap:false explicito: si no, el motor lo vuelve a pegar al terreno
        return loc;
    };
    render.Metal.prototype.encender = function () {
        this.vivo = true;
        var p = this.p, self = this, R = cfg.METAL.reubicar;
        var n = Math.max(1, Math.round(reg.nivel('arcos') * p.scale * p.scale));
        for (var i = 0; i < n; i++) {
            var fam = Math.random() < cfg.METAL.pNaranja ? 'arcoh_naranja' : 'arcoh_cian';
            var pfx = reg.pfxAzar(fam);
            if (!pfx) { continue; }
            var escondido = !cfg.EFECTOS.metal;
            reg.crear({ etiqueta: fam, location: escondido ? this.parque() : this.locAzar(),
                fx: [reg.fx(pfx)], alCrear: function (id) {
                    // Nacio escondido (apagado al empezar): si las chispas se encienden
                    // mientras se creaba, t = 0 -> sube en el proximo tick, no en 20-50 s.
                    self.arcos.push({ pid: id, t: escondido ? 0 : geo.rand(R[0], R[1]) });
                } });
        }
    };
    render.Metal.prototype.aplicarOpciones = function (antes) {
        if (!this.vivo || antes.efectos.metal === cfg.EFECTOS.metal) { return; }
        for (var i = 0; i < this.arcos.length; i++) {
            reg.mover(this.arcos[i].pid, cfg.EFECTOS.metal ? this.locAzar() : this.parque(), 0);
        }
        AW.log(cfg.EFECTOS.metal ? 'metal_encendido' : 'metal_estacionado', { planetId: this.p.planetId, arcos: this.arcos.length });
    };
    render.Metal.prototype.tick = function (dt) {
        if (this.muerto || !this.vivo || !cfg.EFECTOS.metal) { return; }
        var R = cfg.METAL.reubicar;
        for (var i = 0; i < this.arcos.length; i++) {
            var a = this.arcos[i];
            a.t -= dt;
            if (a.t > 0) { continue; }
            a.t = geo.rand(R[0], R[1]);
            reg.mover(a.pid, this.locAzar(), 0); // salto, en el lote del ciclo
        }
    };
    render.Metal.prototype.detener = function () {
        this.muerto = true;
        this.arcos.forEach(function (a) { reg.matar(a.pid); });
    };

    // ---------------- lava: plumas de ceniza (LavaTest) ----------------
    render.Lava = function (perfil) {
        var L = cfg.LAVA;
        this.p = perfil;
        this.vivo = false;
        this.muerto = false;
        this.plumas = [];
        var m = reg.nivel('plumas');
        var n = geo.clamp(Math.round(L.plumasBase * m * perfil.scale), Math.max(1, Math.round(L.plumasMin * m)), Math.round(L.plumasMax * m));
        for (var i = 0; i < n; i++) {
            // Volcanes no siguen bandas: posicion uniforme en la esfera.
            this.plumas.push({
                lat: geo.latUniforme(), lon: geo.rand(0, 360),
                velJ: 1 + geo.rand(-cfg.VIENTO_VEL_JITTER, cfg.VIENTO_VEL_JITTER),
                dirJ: geo.rand(-cfg.VIENTO_DIR_JITTER, cfg.VIENTO_DIR_JITTER),
                brillo: Math.random() < L.pBrillo,
                barro: Math.random() < L.pBarro,
                fuerzaR: Math.random(),
                pid: null, gen: 0,
                caida: { pid: null, gen: 0, clave: '' }   // ceniza/barro cayendo: puppet aparte (cambia con el viento)
            });
        }
    };

    render.Lava.prototype.materializar = function (pl) {
        var self = this, p = this.p, gen = ++pl.gen;
        var fx = [reg.fx(reg.pfxAzar('ceniza'))];
        if (pl.brillo) { fx.push(reg.fx(reg.pfxAzar('brillo_lava'))); }
        if (cfg.EFECTOS.rayosLava) {
            // Rayos volcanicos en bucle DENTRO de la pluma (creados una sola vez).
            // Mayoria dentro de la nube de ceniza, alguno a tierra.
            var R = reg.nivel('rayosLava');
            for (var k = 0; k < R[0]; k++) { fx.push(reg.fx(reg.pfxAzar('rayoh_nube'))); }
            if (Math.random() < R[1]) { fx.push(reg.fx(reg.pfxAzar('rayoh_tierra'))); }
        }
        fx = fx.filter(function (f) { return !!f.filename; });
        reg.crear({
            etiqueta: 'pluma',
            location: reg.location(p.planetId, pl.lat, pl.lon, p.rNube, p.scale),
            fx: fx,
            cancelado: function () { return self.muerto || pl.gen !== gen; },
            alCrear: function (id) {
                pl.pid = id;
                if (self.durCiclo) { reg.mover(id, reg.location(p.planetId, pl.lat, pl.lon, p.rNube, p.scale), self.durCiclo); }
            },
            alPerder: function () { if (!self.muerto && pl.gen === gen) { pl.pid = null; self.materializar(pl); } }
        });
    };

    // Ceniza (y barro) cayendo con viento: variante fuerza x 8 direcciones
    // segun la posicion de la pluma. Si cambia, se recrea SOLO este puppet
    // (la pluma sigue intacta); lo que ya cae termina de caer (killOnDeactivate false).
    render.Lava.prototype.claveCaida = function (pl) {
        var fams = ['caida_ceniza_viento'];
        if (pl.barro) { fams.push('lluvia_barro_viento'); }
        var dir = geo.dirLocal(pl.lat, pl.lon, pl.dirJ, 0, 8), out = [];
        for (var i = 0; i < fams.length; i++) {
            var nf = Math.max(1, Math.floor(reg.cuantas(fams[i]) / 8));
            var f = 1 + Math.min(nf - 1, Math.floor(pl.fuerzaR * nf));
            var pfx = reg.pfx(fams[i], (f - 1) * 8 + dir);
            if (pfx) { out.push(pfx); }
        }
        return out;
    };

    render.Lava.prototype.caer = function (pl) {
        var self = this, p = this.p, s = pl.caida, pfxs = this.claveCaida(pl), clave = pfxs.join('|');
        if (clave === s.clave) { return; }
        s.clave = clave;
        var gen = ++s.gen;
        reg.matar(s.pid); s.pid = null;
        if (!pfxs.length) { return; }
        reg.crear({
            etiqueta: 'caida_lava',
            location: reg.location(p.planetId, pl.lat, pl.lon, p.rNube, p.scale),
            fx: pfxs.map(function (f) { return reg.fx(f); }),
            cancelado: function () { return self.muerto || s.gen !== gen; },
            alCrear: function (id) {
                s.pid = id;
                if (self.durCiclo) { reg.mover(id, reg.location(p.planetId, pl.lat, pl.lon, p.rNube, p.scale), self.durCiclo); }
            },
            alPerder: function () { if (!self.muerto && s.gen === gen) { s.pid = null; s.clave = ''; self.caer(pl); } }
        });
    };

    render.Lava.prototype.encender = function () {
        this.vivo = true;
        for (var i = 0; i < this.plumas.length; i++) { this.materializar(this.plumas[i]); this.caer(this.plumas[i]); }
    };

    render.Lava.prototype.tick = function () {}; // todo pasa en motorCiclo

    // Ciclo de movimiento sincronizado (igual que las nubes de agua).
    render.Lava.prototype.motorCiclo = function (durS) {
        if (!this.vivo || this.muerto) { return; }
        var p = this.p;
        this.durCiclo = durS;
        for (var i = 0; i < this.plumas.length; i++) {
            var pl = this.plumas[i];
            var ll = geo.derivar(pl.lat, pl.lon, p.rNube, pl.velJ, pl.dirJ, p.scale, 1, cfg.DRIFT_S);
            pl.lat = ll.lat; pl.lon = ll.lon;
            var loc = reg.location(p.planetId, pl.lat, pl.lon, p.rNube, p.scale);
            reg.mover(pl.pid, loc, durS);
            this.caer(pl); // cambio de viento -> nueva caida (sale en este mismo ciclo)
            reg.mover(pl.caida.pid, loc, durS);
        }
    };

    render.Lava.prototype.detener = function () {
        this.muerto = true;
        for (var i = 0; i < this.plumas.length; i++) {
            var pl = this.plumas[i];
            reg.matar(pl.pid); pl.pid = null;
            reg.matar(pl.caida.pid); pl.caida.pid = null;
        }
    };
}());
