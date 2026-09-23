// AtmosphereWeather — ciclo del agua por planeta (earth, tropical, desert, ice_boss).
//
// Celdas acumulan evaporacion -> nace nube -> crece (suma cuerpos) -> al pasar
// el umbral de lluvia, randomizer: llueve (o tormenta) / se disipa. La lluvia
// gasta agua; sin agua para y la nube muere. Cuerpo = 1 puppet de nube + 1
// puppet de precipitacion debajo (separados: cambiar la lluvia no reinicia la nube).
(function () {
    'use strict';
    var AW = window.AtmosphereWeather;
    var cfg = AW.cfg;
    var geo = AW.geo;
    var reg = AW.reg;
    var AREA_REF = 4 * Math.PI * cfg.REFERENCE_RADIUS * cfg.REFERENCE_RADIUS;

    // Tope de cobertura segun calidad de nubes. Al bajarla en partida, las nubes
    // de mas no se borran: se disipan solas y no nacen nuevas hasta quedar bajo el tope.
    function aplicarCalidad() {
        this.maxCuerpos = Math.round(this.bio.cobertura * reg.nivel('nubes') * AREA_REF / cfg.CUERPO_AREA);
    }
    var Agua = AW.Agua = function (perfil) {
        this.p = perfil;
        this.bio = perfil.bio;
        this.vivo = false;
        this.muerto = false;
        this.nubes = [];
        this.fantasmas = [];
        this.celdas = [];
        this.nCuerpos = 0;
        this.gasto = 0;
        this.presupuesto = Infinity;
        this.aplicarCalidad();

        var nb = cfg.GRID_BANDS, ns = cfg.GRID_SECTORS;
        for (var b = 0; b < nb; b++) {
            for (var s = 0; s < ns; s++) {
                var c = {
                    lat: -90 + (b + 0.5) * 180 / nb,
                    lon: (s + 0.5) * 360 / ns,
                    uN: geo.umbral(this.bio.nube),
                    nubes: 0
                };
                c.hum = geo.rand(0, c.uN);
                this.celdas.push(c);
            }
        }
        AW.log('agua_init', { planetId: perfil.planetId, biome: perfil.biome, maxCuerpos: this.maxCuerpos });
    };

    Agua.prototype.aplicarCalidad = aplicarCalidad;

    // Opciones cambiadas en partida (menu Settings). antes = cfg.EFECTOS/NIVEL previos.
    // Nada se borra de golpe: lo que se apaga se disipa o termina de caer solo.
    Agua.prototype.aplicarOpciones = function (antes) {
        var E = cfg.EFECTOS, i, n;
        this.aplicarCalidad();
        if (!this.vivo) { return; }
        if (antes.efectos.rayos && !E.rayos && this.reserva) {
            for (i = 0; i < this.nubes.length; i++) { this.soltarRayos(this.nubes[i]); this.nubes[i].rayos = null; }
        }
        if (antes.efectos.nubes && !E.nubes) {
            for (i = 0; i < this.nubes.length; i++) {
                n = this.nubes[i];
                if (n.fase === 'disipando') { continue; }
                if (this.reserva) { this.soltarRayos(n); }
                this.fin(n); // deja de llover y se disipa por cuerpos
            }
            return;
        }
        var precip = ['lluvia', 'nieve', 'virga'].some(function (k) { return antes.efectos[k] !== E[k]; }) ||
            antes.nivel.precip !== cfg.NIVEL.precip;
        if (precip) {
            for (i = 0; i < this.nubes.length; i++) { if (this.nubes[i].lloviendo) { this.aplicarTodos(this.nubes[i]); } }
        }
    };

    Agua.prototype.celdaEn = function (lat, lon) {
        var b = geo.clamp(Math.floor((lat + 90) / 180 * cfg.GRID_BANDS), 0, cfg.GRID_BANDS - 1);
        var s = Math.floor(((lon % 360) + 360) % 360 / 360 * cfg.GRID_SECTORS) % cfg.GRID_SECTORS;
        return this.celdas[b * cfg.GRID_SECTORS + s];
    };

    // ---------------- tick ----------------
    Agua.prototype.tick = function (dt) {
        if (this.muerto) { return; }
        var bio = this.bio, n = this.celdas.length, ini = Math.floor(Math.random() * n);
        for (var k = 0; k < n; k++) {
            var c = this.celdas[(ini + k) % n];
            c.hum += bio.tasa * geo.latMult(c.lat) * dt;
            if (cfg.EFECTOS.nubes && c.hum >= c.uN && c.nubes < cfg.NUBES_POR_CELDA && this.nCuerpos < this.maxCuerpos &&
                this.gasto + reg.costo('nubes', 5) <= this.presupuesto) {
                this.nacer(c);
            }
        }
        var vivas = [];
        for (var i = 0; i < this.nubes.length; i++) {
            var nube = this.nubes[i];
            this.tickNube(nube, dt);
            if (!nube.muerta) { vivas.push(nube); }
        }
        this.nubes = vivas;
    };

    Agua.prototype.nacer = function (c) {
        var bio = this.bio;
        c.hum = 0;
        c.uN = geo.umbral(bio.nube);
        c.nubes++;
        var lat = geo.clamp(c.lat + geo.rand(-0.5, 0.5) * 180 / cfg.GRID_BANDS, -89, 89);
        var lon = c.lon + geo.rand(-0.5, 0.5) * 360 / cfg.GRID_SECTORS;
        var a = Math.abs(lat);
        var nube = {
            celda: c,
            lat: lat, lon: (lon + 360) % 360,
            tipo: (a >= cfg.ESTRATO_LAT[0] && a <= cfg.ESTRATO_LAT[1] && Math.random() < bio.pEstrato) ? 'estrato' : 'cumulo',
            fase: 'creciendo',
            uN: geo.umbral(bio.nube),
            uL: geo.umbral(bio.lluvia),
            conv: Math.random() < bio.pConv,
            vida: 0,
            vidaMax: geo.cicloS(),
            velJ: 1 + geo.rand(-cfg.VIENTO_VEL_JITTER, cfg.VIENTO_VEL_JITTER),
            dirJ: geo.rand(-cfg.VIENTO_DIR_JITTER, cfg.VIENTO_DIR_JITTER),
            driftT: geo.rand(0, cfg.DRIFT_S),
            crecerT: cfg.CRECER_CADA_S,
            faseT: 0,
            rampaT: 0,
            tormenta: false,
            virga: false,
            lloviendo: false,
            cuerpos: [],
            muerta: false
        };
        if (nube.uL <= nube.uN) { nube.uL = nube.uN * 1.5; }
        nube.agua = nube.uN;
        nube.dirEstrato = geo.dirViento(lat, nube.dirJ);
        this.nubes.push(nube);
        this.agregarCuerpo(nube, 0);
    };

    Agua.prototype.tickNube = function (n, dt) {
        var bio = this.bio;
        n.vida += dt;
        if (this.vivo && n.lloviendo) { this.soltarEspera(n); }

        // Precalentamiento: deriva por tick. En vivo la mueve el motor (reloj real).
        if (!this.vivo) {
            n.driftT -= dt;
            n.driftAcum = (n.driftAcum || 0) + dt;
            if (n.driftT <= 0) { n.driftT = cfg.DRIFT_S; this.derivar(n, n.driftAcum); n.driftAcum = 0; }
        }

        var tasa = bio.tasa * geo.latMult(n.lat) * (n.conv ? bio.multConv : 1);

        if (n.fase === 'creciendo') {
            n.agua += tasa * dt;
            n.crecerT -= dt;
            if (n.crecerT <= 0) {
                n.crecerT = cfg.CRECER_CADA_S;
                var frac = geo.clamp((n.agua - n.uN) / (n.uL - n.uN), 0, 1);
                var max = cfg.TIPOS[n.tipo].maxCuerpos;
                if (n.cuerpos.length < 1 + Math.round(frac * (max - 1))) { this.agregarCuerpo(n, 0); }
            }
            if (n.agua >= n.uL) { this.decidir(n); }
            else if (n.vida >= n.vidaMax) { this.disipar(n, true); }
        } else if (n.fase === 'esperando') {
            // Decidio llover pero el planeta esta en su tope de particulas.
            n.faseT -= dt;
            if (n.faseT <= 0) {
                if (n.vida >= n.vidaMax) { this.disipar(n, true); } else { this.empezarLluvia(n); }
            }
        } else if (n.fase === 'lluvia' || n.fase === 'amainando') {
            n.agua -= n.consumo * dt;
            var cayendo = n.cuerpos.some(function (c) { return c.precip.pid !== null; });
            // Rayos de la reserva (en bucle): se asignan una vez, cuando ya llueve.
            if (this.reserva && cfg.EFECTOS.rayos && n.tormenta && n.fase === 'lluvia' && cayendo && !n.rayos) { this.tomarRayos(n); }
            if (n.rampaT > 0) {
                // Rampa: llovizna al empezar y al terminar.
                n.rampaT -= dt;
                if (n.rampaT <= 0) {
                    if (n.fase === 'amainando') { this.fin(n); } else { this.aplicarTodos(n); }
                }
            } else if (n.fase === 'lluvia' && (n.agua < n.uN || n.vida >= n.vidaMax * 1.5)) {
                this.terminarLluvia(n);
            }
        } else if (n.fase === 'disipando') {
            n.faseT -= dt;
            if (n.faseT <= 0) {
                n.faseT = cfg.DISIPAR_CADA_S;
                var c = n.cuerpos.pop();
                if (c) { this.quitarCuerpo(c); }
                if (!n.cuerpos.length) { n.muerta = true; n.celda.nubes--; }
            }
        }
    };

    // Randomizer al saturar: llueve (o tormenta) o se disipa.
    Agua.prototype.decidir = function (n) {
        var bio = this.bio;
        if (Math.random() >= geo.clamp(bio.pLluvia * cfg.MULT_LLUVIA, 0, 1)) { this.disipar(n, true); return; }
        n.tormenta = Math.random() < geo.clamp(bio.pTormenta * cfg.MULT_TORMENTA * (n.conv ? 2 : 0.67), 0, 1);
        n.virga = !n.tormenta && !!bio.pVirga && Math.random() < bio.pVirga;
        if (n.tormenta) {
            n.tipo = 'cumulonimbo';
            n.agua = Math.max(n.agua, n.uL * cfg.FACTOR_TORMENTA);
            var T = cfg.TIPOS.cumulonimbo;
            for (var k = 1; k < T.alturas.length && n.cuerpos.length < T.maxCuerpos; k++) {
                this.agregarCuerpo(n, T.alturas[k]);
            }
        }
        this.empezarLluvia(n);
    };

    Agua.prototype.empezarLluvia = function (n) {
        var extra = 0, i;
        n.lloviendo = true;
        n.rampaT = 0; // costo con la intensidad final
        for (i = 0; i < n.cuerpos.length; i++) {
            var pr = this.precip(n, n.cuerpos[i]);
            if (pr) { extra += pr.costo; }
        }
        if (this.gasto + extra > this.presupuesto) {
            n.lloviendo = false;
            n.fase = 'esperando';
            n.faseT = 5;
            return;
        }
        n.fase = 'lluvia';
        // La lluvia gasta el agua sobre el umbral de nube en una duracion sorteada.
        var dur = geo.rand(cfg.LLUVIA_DURACION_S[0], cfg.LLUVIA_DURACION_S[1]) * (n.tormenta ? 1.5 : 1);
        n.consumo = Math.max(0.01, (n.agua - n.uN) / dur);
        // La rampa cuenta tambien la espera a que la nube oscurecida se forme.
        n.rampaT = cfg.RAMPA_S + (this.vivo ? cfg.NUBE_LLENA_S : 0);
        this.aplicarTodos(n);
    };

    // ---------------- rayos de la reserva ----------------
    Agua.prototype.tomarRayos = function (n) {
        var base = n.cuerpos.filter(function (c) { return c.dh === 0; });
        if (!base.length) { return; }
        n.rayos = [];
        var fams = ['rayoh_tierra', 'rayoh_nube'];
        for (var i = 0; i < fams.length; i++) {
            var s = this.reserva.tomar(fams[i]);
            if (s) { n.rayos.push({ slot: s, c: geo.pick(base), aTierra: i === 0, nuevo: true }); }
        }
    };

    Agua.prototype.soltarRayos = function (n) {
        if (!n.rayos) { return; }
        for (var i = 0; i < n.rayos.length; i++) { this.reserva.devolver(n.rayos[i].slot); }
        n.rayos = [];   // vacio (no null): esta tormenta ya no vuelve a tomar
    };

    // Mueve los rayos de la tormenta con su nube (dentro del lote del ciclo).
    Agua.prototype.moverRayos = function (n, durMov) {
        if (!n.rayos || !n.rayos.length) { return; }
        var p = this.p, s = p.scale;
        for (var i = 0; i < n.rayos.length; i++) {
            var r = n.rayos[i], c = r.c;
            var r0 = r.aTierra ? p.rNube - cfg.RAYO_ESPESOR * s : p.rNube;
            var ll = geo.offset(n.lat, n.lon, c.dx * s, c.dy * s, r0);
            // Primera vez: salto directo desde el estacionamiento bajo tierra.
            reg.mover(r.slot.pid, reg.location(p.planetId, ll.lat, ll.lon, r0, s), r.nuevo ? 0 : durMov);
            r.nuevo = false;
        }
    };

    // Amaina: vuelve a llovizna RAMPA_S segundos y recien ahi para.
    Agua.prototype.terminarLluvia = function (n) {
        if (this.reserva) { this.soltarRayos(n); }
        n.fase = 'amainando';
        n.rampaT = cfg.RAMPA_S;
        this.aplicarTodos(n);
    };

    Agua.prototype.fin = function (n) {
        n.lloviendo = false;
        n.fase = 'disipando';
        n.faseT = cfg.DISIPAR_CADA_S;
        this.aplicarTodos(n);
    };

    Agua.prototype.aplicarTodos = function (n) {
        for (var i = 0; i < n.cuerpos.length; i++) { this.aplicar(n, n.cuerpos[i]); }
    };

    Agua.prototype.disipar = function (n, devolver) {
        if (devolver) { this.celdaEn(n.lat, n.lon).hum += n.agua * cfg.RETORNO_DISIPA; }
        n.fase = 'disipando';
        n.faseT = cfg.DISIPAR_CADA_S;
    };

    // ---------------- cuerpos ----------------
    Agua.prototype.agregarCuerpo = function (n, dh) {
        if (this.gasto + reg.costo('nubes', 5) > this.presupuesto) { return; }
        if (n.cuerpos.length && this.nCuerpos >= this.maxCuerpos) { return; } // tope de cobertura
        var T = cfg.TIPOS[n.tipo], k = n.cuerpos.length, dx = 0, dy = 0;
        if (k > 0) {
            if (n.tipo === 'estrato') {
                // En fila a lo largo del viento, alternando adelante/atras.
                var paso = T.paso * Math.ceil(k / 2) * (k % 2 ? 1 : -1);
                var a = n.dirEstrato * Math.PI / 180;
                dx = paso * Math.cos(a) + geo.rand(-8, 8);
                dy = paso * Math.sin(a) + geo.rand(-8, 8);
            } else {
                var rad = T.radio * (dh ? 0.5 : 1);
                // Cerca del centro: los cuerpos se solapan -> una masa, no bolitas sueltas.
                var ang = geo.rand(0, 2 * Math.PI), d = geo.rand(cfg.CUERPO_DIST[0], cfg.CUERPO_DIST[1]) * rad;
                dx = d * Math.cos(ang);
                dy = d * Math.sin(ang);
            }
        }
        var c = {
            dx: dx, dy: dy, dh: dh || 0,
            rafaga: geo.rand(-cfg.VIENTO_DIR_JITTER, cfg.VIENTO_DIR_JITTER), // su propia rafaga
            // Nube y precipitacion en puppets separados: cambiar la lluvia no reinicia la nube.
            nube: { pid: null, gen: 0, clave: '', fx: null },
            precip: { pid: null, gen: 0, clave: '', fx: null },
            costo: 0, muerto: false,
            nubeRef: n
        };
        n.cuerpos.push(c);
        this.nCuerpos++;
        this.aplicar(n, c);
    };

    Agua.prototype.quitarCuerpo = function (c) {
        c.muerto = true;
        this.nCuerpos--;
        this.gasto -= c.costo;
        c.costo = 0;
        // La nube se apaga viajando (fantasma); las gotas terminan de caer solas.
        this.retirarNube(c.nubeRef, c);
        reg.matar(c.precip.pid); c.precip.pid = null;
    };

    // Variante de nube segun fase: blanca fina al nacer -> gris de tormenta.
    Agua.prototype.nivelNube = function (n) {
        if (n.tormenta && n.lloviendo) { return 1; }
        if (n.lloviendo) { return 0.75; }
        if (n.fase === 'disipando') { return 0.25; }
        return 0.5 * geo.clamp((n.agua - n.uN) / (n.uL - n.uN), 0, 1);
    };

    Agua.prototype.esNieve = function (n) {
        var modo = this.bio.nieve;
        return modo === 'siempre' || (modo === 'polos' && Math.abs(n.lat) >= cfg.NIEVE_LAT_POLOS);
    };

    // Precipitacion bajo un cuerpo -> { pfx, costo } o null. Siempre con viento
    // (variantes fuerza x 8 direcciones, generar_pfx.py).
    Agua.prototype.precip = function (n, c) {
        if (!n.lloviendo || c.dh > 0) { return null; }
        // Calidad: centro = solo el cuerpo central, mitad = uno de cada dos,
        // todos, denso = todos con variantes x1.5 (_x15, generar_pfx.py).
        var modo = reg.nivel('precip'), i = n.cuerpos.indexOf(c);
        if ((modo === 'centro' && i !== 0) || (modo === 'mitad' && i % 2 !== 0)) { return null; }
        var E = cfg.EFECTOS, nieve = this.esNieve(n);
        if (nieve ? !E.nieve : (n.virga ? !E.virga : !E.lluvia)) { return null; } // efecto apagado
        var fam = nieve ? 'nieve_viento' : n.virga ? 'virga_viento' : this.bio.vientoLluviaMult ? 'lluvia_ventarron' : 'lluvia_viento';
        if (modo === 'denso' && reg.cuantas(fam + '_x15')) { fam += '_x15'; }
        if (nieve) {
            // Intensidad por tipo (rampa = la mas fina); orden: intensidad-mayor, fuerza, 8 direcciones.
            var idx = n.rampaT > 0 || n.tipo === 'estrato' ? 1 : n.tipo === 'cumulonimbo' ? 3 : 2;
            var fz = Math.max(1, Math.floor(reg.cuantas(fam) / 24));
            return this.variante(fam, ((idx - 1) * fz + this.fuerza(c, fz) - 1) * 8 + this.dirLocal(n, c, 8));
        }
        var nf = Math.max(1, Math.floor(reg.cuantas(fam) / 8)); // fuerza-mayor, luego 8 direcciones
        return this.variante(fam, (this.fuerza(c, nf) - 1) * 8 + this.dirLocal(n, c, 8));
    };

    Agua.prototype.variante = function (efecto, idx) {
        return { pfx: reg.pfx(efecto, idx), costo: reg.costo(efecto, idx) };
    };

    // Viento de la nube + rafaga propia del cuerpo -> variante de direccion
    // (1..nDir) en ejes locales (Atlas 3.6: +X sur, +Z este).
    Agua.prototype.dirLocal = function (n, c, nDir) {
        return geo.dirLocal(n.lat, n.lon, n.dirJ, c.rafaga, nDir);
    };

    // Fuerza de viento propia del cuerpo (1..n), fija durante su vida.
    Agua.prototype.fuerza = function (c, n) {
        if (!c.fuerzaR) { c.fuerzaR = Math.random(); }
        return 1 + Math.min(n - 1, Math.floor(c.fuerzaR * n));
    };

    // Calcula que debe mostrar el cuerpo; recrea solo la parte que cambio.
    Agua.prototype.aplicar = function (n, c) {
        if (c.muerto) { return; }
        var costo = reg.costo('nubes', 5);
        var pr = this.precip(n, c);
        if (pr && pr.pfx) { costo += pr.costo; }
        this.gasto += costo - c.costo;
        c.costo = costo;
        this.fijar(n, c, 'nube', reg.pfxNivel('nubes', this.nivelNube(n)));
        this.fijar(n, c, 'precip', pr && pr.pfx);
    };

    Agua.prototype.fijar = function (n, c, parte, pfx) {
        var slot = c[parte], clave = pfx || '';
        if (clave === slot.clave) { return; }
        slot.clave = clave;
        slot.fx = pfx ? [reg.fx(pfx)] : null;
        if (!this.vivo) { return; }
        // Nube viva: el cambio de variante entra en la PROXIMA generacion
        // (transicion gradual; nunca se cortan bocanadas vivas).
        if (parte === 'nube' && slot.pid !== null) { return; }
        // La precipitacion no empieza hasta que su nube este formada.
        if (parte === 'precip' && pfx && !this.nubeLista(c)) {
            reg.matar(slot.pid); slot.pid = null; slot.gen++;
            slot.espera = true;
            return;
        }
        slot.espera = false;
        this.materializar(n, c, parte);
    };

    Agua.prototype.nubeLista = function (c) {
        return c.nube.pid !== null && Date.now() - c.nube.creado >= cfg.NUBE_LLENA_S * 1000;
    };

    // Suelta la precipitacion que esperaba a su nube.
    Agua.prototype.soltarEspera = function (n) {
        for (var i = 0; i < n.cuerpos.length; i++) {
            var c = n.cuerpos[i];
            if (c.precip.espera && this.nubeLista(c)) {
                c.precip.espera = false;
                if (c.precip.fx) { this.materializar(n, c, 'precip'); }
            }
        }
    };

    Agua.prototype.locCuerpo = function (n, c) {
        var p = this.p, s = p.scale, r = p.rNube + c.dh * s;
        var ll = geo.offset(n.lat, n.lon, c.dx * s, c.dy * s, r);
        return reg.location(p.planetId, ll.lat, ll.lon, r, s);
    };

    // Cruce: el puppet nuevo nace vacio y se llena de a poco; el viejo se
    // borra ya y sus particulas se apagan solas -> transicion gradual.
    Agua.prototype.materializar = function (n, c, parte) {
        var self = this, slot = c[parte], gen = ++slot.gen;
        if (parte === 'nube') { this.retirarNube(n, c); } else { reg.matar(slot.pid); }
        slot.pid = null;
        if (!slot.fx) { return; }
        reg.crear({
            etiqueta: parte,
            location: this.locCuerpo(n, c),
            fx: slot.fx,
            cancelado: function () { return self.muerto || c.muerto || slot.gen !== gen; },
            alCrear: function (id) {
                var ahora = Date.now();
                slot.pid = id;
                slot.inicio = ahora; // inicio de esta generacion
                // "creado" = desde cuando se ve ESTA variante (para esperar la lluvia);
                // una generacion nueva de la misma variante no lo reinicia.
                if (slot.claveCreada !== slot.clave) { slot.claveCreada = slot.clave; slot.creado = ahora; }
                // Se suma al movimiento del ciclo en curso (sale en el mismo flush).
                if (self.durCiclo) { reg.mover(id, self.locCuerpo(n, c), self.durCiclo); }
            },
            alPerder: function () { if (!self.muerto && !c.muerto && slot.gen === gen) { self.materializar(n, c, parte); } }
        });
    };

    // ---------------- viento ----------------
    // Ciclo de movimiento SINCRONIZADO (lo llama el motor de main.js): todas
    // las nubes avanzan un paso de viento y se mueven en durS segundos; los
    // movimientos salen juntos en una sola llamada (reg.flush).
    Agua.prototype.motorCiclo = function (durS) {
        if (!this.vivo || this.muerto) { return; }
        this.durCiclo = durS;
        var relevo = (cfg.NUBE_GEN_S - cfg.GEN_ANTICIPO_S) * 1000, ahora = Date.now();
        for (var i = 0; i < this.nubes.length; i++) {
            var n = this.nubes[i];
            this.derivar(n, cfg.DRIFT_S, durS);
            // Relevo de generacion: la actual esta por dejar de emitir -> nace la siguiente.
            for (var j = 0; j < n.cuerpos.length; j++) {
                var s = n.cuerpos[j].nube;
                if (s.pid !== null && s.fx && ahora - s.inicio >= relevo) { this.materializar(n, n.cuerpos[j], 'nube'); }
            }
        }
        this.moverFantasmas(durS);
    };

    // ---------------- fantasmas ----------------
    // Un puppet de nube que se retira NO se borra ni se le cambian los fx
    // (ambas cosas dejan sus bocanadas huerfanas y quietas: visto en juego).
    // Sigue viajando con su viento: termina su generacion (emitterLifetime
    // del .pfx), sus bocanadas se apagan, y recien ahi se borra, ya vacio.
    Agua.prototype.retirarNube = function (n, c) {
        var pid = c.nube.pid, inicio = c.nube.inicio || Date.now();
        c.nube.pid = null;
        if (pid === null || pid === undefined) { return; }
        if (!n || !this.vivo) { reg.matar(pid); return; }
        this.fantasmas.push({
            pid: pid, lat: n.lat, lon: n.lon, dx: c.dx, dy: c.dy, dh: c.dh,
            velJ: n.velJ, dirJ: n.dirJ,
            mult: (n.lloviendo && this.bio.vientoLluviaMult) ? this.bio.vientoLluviaMult : 1,
            hasta: inicio + (cfg.NUBE_GEN_S + cfg.NUBE_VIDA_MAX_S + 2) * 1000
        });
    };

    Agua.prototype.moverFantasmas = function (durS) {
        var p = this.p, s = p.scale, ahora = Date.now(), vivos = [];
        for (var i = 0; i < this.fantasmas.length; i++) {
            var f = this.fantasmas[i];
            if (ahora >= f.hasta) { reg.matar(f.pid); continue; }
            var ll = geo.derivar(f.lat, f.lon, p.rNube, f.velJ, f.dirJ, s, f.mult, cfg.DRIFT_S);
            f.lat = ll.lat; f.lon = ll.lon;
            var r = p.rNube + f.dh * s;
            var pos = geo.offset(f.lat, f.lon, f.dx * s, f.dy * s, r);
            reg.mover(f.pid, reg.location(p.planetId, pos.lat, pos.lon, r, s), durS);
            vivos.push(f);
        }
        this.fantasmas = vivos;
    };

    // Avanza la nube avanceS segundos de viento y mueve sus puppets en durMov s.
    Agua.prototype.derivar = function (n, avanceS, durMov) {
        var p = this.p;
        var mult = (n.lloviendo && this.bio.vientoLluviaMult) ? this.bio.vientoLluviaMult : 1;
        var nieveAntes = this.esNieve(n);
        var ll = geo.derivar(n.lat, n.lon, p.rNube, n.velJ, n.dirJ, p.scale, mult, avanceS);
        n.lat = ll.lat;
        n.lon = ll.lon;
        if (!this.vivo) { return; }
        var cambiaPrecip = n.lloviendo && nieveAntes !== this.esNieve(n);
        for (var i = 0; i < n.cuerpos.length; i++) {
            var c = n.cuerpos[i];
            if (cambiaPrecip || n.lloviendo) { this.aplicar(n, c); } // el viento cambia la variante
            var loc = this.locCuerpo(n, c), dur = durMov;
            reg.mover(c.nube.pid, loc, dur);
            reg.mover(c.precip.pid, loc, dur);
        }
        this.moverRayos(n, durMov);
    };

    // ---------------- ciclo de vida del planeta ----------------
    // Precalentamiento: corre el clima en silencio para arrancar con clima formado.
    Agua.prototype.precalentar = function () {
        var pasos = Math.round(cfg.PRECALENTAMIENTO_S / cfg.PRECALENTAMIENTO_DT);
        for (var i = 0; i < pasos; i++) { this.tick(cfg.PRECALENTAMIENTO_DT); }
        var lloviendo = this.nubes.filter(function (n) { return n.lloviendo; }).length;
        AW.log('precalentado', { planetId: this.p.planetId, nubes: this.nubes.length, cuerpos: this.nCuerpos, lloviendo: lloviendo, particulas: Math.round(this.gasto) });
    };

    Agua.prototype.encender = function () {
        this.vivo = true;
        // Reserva de rayos creada ahora, junto con las nubes (el tiron de crear
        // puppets de rayo pasa en la carga, no en medio del juego).
        if (cfg.EFECTOS.rayos && this.bio.pTormenta > 0) {
            this.reserva = new AW.render.Reserva(this.p, reg.nivel('rayos'));
        }
        for (var i = 0; i < this.nubes.length; i++) {
            var n = this.nubes[i];
            for (var j = 0; j < n.cuerpos.length; j++) {
                this.materializar(n, n.cuerpos[j], 'nube');
                n.cuerpos[j].precip.espera = !!n.cuerpos[j].precip.fx; // llueve cuando la nube se forme
            }
        }
    };

    Agua.prototype.detener = function () {
        this.muerto = true;
        for (var i = 0; i < this.nubes.length; i++) {
            for (var j = 0; j < this.nubes[i].cuerpos.length; j++) { this.quitarCuerpo(this.nubes[i].cuerpos[j]); }
        }
        this.nubes = [];
        for (var k = 0; k < this.fantasmas.length; k++) { reg.matar(this.fantasmas[k].pid); }
        this.fantasmas = [];
        if (this.reserva) { this.reserva.detener(); this.reserva = null; }
    };
}());
