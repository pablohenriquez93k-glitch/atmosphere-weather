// AtmosphereWeather — arranque, tick global, planetas que mueren.
// Arranca apenas la partida tiene datos de planetas (sin esperar al aterrizaje).
(function () {
    'use strict';
    var AW = window.AtmosphereWeather;
    var cfg = AW.cfg;
    var reg = AW.reg;

    var sims = {};   // planetId -> Agua | Lava | Metal

    function listaPlanetas() {
        try {
            var st = model.planetListState && model.planetListState();
            return (st && st.planets) || [];
        } catch (e) {
            return [];
        }
    }

    // Agua y metal se crean siempre (sus efectos se prenden y apagan en partida);
    // las plumas de lava solo si estan encendidas al empezar (menu: "*").
    function crearSim(perfil) {
        if (perfil.clima === 'agua') { return new AW.Agua(perfil); }
        if (perfil.clima === 'lava' && cfg.EFECTOS.lava) { return new AW.render.Lava(perfil); }
        if (perfil.clima === 'metal') { return new AW.render.Metal(perfil); }
        return null;
    }
    function listaSims() { return Object.keys(sims).map(function (k) { return sims[k]; }); }

    function arrancar(lista) {
        var nuevas = [];
        for (var i = 0; i < lista.length; i++) {
            var perfil = AW.perfil(i, lista[i]);
            if (!perfil) { continue; }
            var sim = crearSim(perfil);
            if (sim) { sims[i] = sim; nuevas.push(sim); }
        }
        reg.repartir(nuevas);
        // Precalentar primero (sin puppets), despues mostrar todo.
        nuevas.forEach(function (s) { if (s.precalentar) { s.precalentar(); } });
        nuevas.forEach(function (s) { s.encender(); });
        AW.log('arrancado', { planetas: lista.length, conClima: nuevas.length });

        setInterval(tick, cfg.TICK_S * 1000);
        setInterval(motor, cfg.MOTOR_MS);
        setInterval(vigilarPlanetas, 5000);
    }

    function tick() {
        for (var k in sims) {
            if (!sims.hasOwnProperty(k)) { continue; }
            try { sims[k].tick(cfg.TICK_S); } catch (e) { AW.log('tick_error', { planetId: k, error: String(e && e.message || e) }); }
        }
    }

    // Motor de movimiento: reloj real, separado del tick del clima. Un solo
    // ciclo global: cada DRIFT_S todas las nubes de todos los planetas se
    // mueven en UNA llamada, con la duracion hasta el ciclo siguiente.
    var proxCiclo = 0;
    function motor() {
        var ahora = Date.now(), D = cfg.DRIFT_S * 1000;
        if (!proxCiclo) { proxCiclo = ahora; }
        if (ahora < proxCiclo) { return; }
        AW.motorStats(ahora - proxCiclo);
        if (ahora - proxCiclo > D / 2) { proxCiclo = ahora; } // atraso grande: se reengancha
        var fin = proxCiclo + D, durS = (fin - ahora) / 1000;
        for (var k in sims) {
            if (!sims.hasOwnProperty(k) || !sims[k].motorCiclo) { continue; }
            try { sims[k].motorCiclo(durS); } catch (e) { AW.log('motor_error', { planetId: k, error: String(e && e.message || e) }); }
        }
        proxCiclo = fin;
        reg.vigiaCiclo();
        // Primero crear (una llamada); con los ids ya asignados, mover TODO junto.
        reg.procesarCola(cfg.CREAR_POR_CICLO, reg.flush);
    }

    // Ragnarok / choque: planeta muerto -> se borra su clima.
    function vigilarPlanetas() {
        var lista = listaPlanetas();
        for (var k in sims) {
            if (!sims.hasOwnProperty(k)) { continue; }
            if (AW.estaMuerto(lista[k])) {
                AW.log('planeta_muerto', { planetId: k });
                sims[k].detener();
                delete sims[k];
            }
        }
    }

    function esperarPlanetas(intento) {
        var lista = listaPlanetas();
        var listos = lista.length > 0 && lista.every(function (p) { return p && (p.isSun || p.radius); });
        if (listos) {
            reg.purgarViejos(function () { arrancar(lista); });
            return;
        }
        if (intento >= 120) { AW.log('sin_planetas', { intento: intento }); return; }
        setTimeout(function () { esperarPlanetas(intento + 1); }, 1000);
    }

    var opciones = reg.leerOpciones(false);
    // Menu Settings abierto en partida: al cerrarlo, releer las opciones. Solo JS:
    // lo que haya que crear, mover o borrar sale en el proximo ciclo.
    if (typeof model !== 'undefined' && model.showSettings && model.showSettings.subscribe) {
        model.showSettings.subscribe(function (abierto) {
            if (abierto) { return; }
            var antes = { efectos: cfg.EFECTOS, nivel: cfg.NIVEL }, previas = opciones;
            var nuevas = reg.leerOpciones(true);
            if (!nuevas || JSON.stringify(nuevas) === JSON.stringify(previas)) { return; }
            opciones = nuevas;
            reg.repartir(listaSims());
            listaSims().forEach(function (s) { if (s.aplicarOpciones) { s.aplicarOpciones(antes); } });
            var cambios = {};
            for (var k in nuevas) { if (!previas || nuevas[k] !== previas[k]) { cambios[k] = nuevas[k]; } }
            AW.log('opciones_cambiadas', cambios);
        });
    }
    AW.log('cargado', { opciones: opciones });
    reg.cargarVariantes(function () { esperarPlanetas(1); });
}());
