// AtmosphereWeather — opciones del menu Settings (pestaña "Atmosphere Weather").
// Se carga en DOS scenes: "settings" (arma la pestaña, settings.js) y
// "live_game" (lee los valores, registro.js). Una sola definicion para ambas.
// El juego guarda los valores en localStorage (<uberName>.paSettings);
// local_only = no se sube a PlayFab. Textos en ingles (publico del mod).
(function () {
    'use strict';
    var AW = window.AtmosphereWeather = window.AtmosphereWeather || {};
    var GRUPO = 'atmosphere_weather';
    var ID = 'com.pa.pabloandclaude.atmosphereweather';

    // ---------------- traducciones (Atlas 4b) ----------------
    // Todo texto visible pasa por loc('!LOC:<ingles>'): la clave es el texto en
    // ingles. Las traducciones viven en translations/<idioma>.json (las genera
    // scripts/generar_traducciones.py) y se suman al diccionario del juego con
    // i18n.addResourceBundle (i18next 1.7.1 del juego; mismo mecanismo que el
    // mod "Mod Translations" de Quitch, sin depender de el). Solo hace falta en
    // la scene settings: nuestros scripts corren antes de ko.applyBindings.
    var L = function (s) { return '!LOC:' + s; };
    // Idiomas revisados por un hablante nativo (el resto muestra el aviso).
    var VERIFICADOS = ['es-ES'];   // revisado por Pablo en juego (2026-09-23)
    var ALIAS = { 'zh-HK': 'zh-TW' };   // chino tradicional
    function cargarTraduccion() {
        try {
            if (!window.i18n || !i18n.addResourceBundle || !i18n.lng) { return null; }
            var lng = i18n.lng();
            if (!lng || /^en/.test(lng)) { return null; }
            var candidatos = [lng, ALIAS[lng], lng.split('-')[0]];
            for (var i = 0; i < candidatos.length; i++) {
                var c = candidatos[i];
                if (!c) { continue; }
                var xhr = new XMLHttpRequest();
                xhr.open('GET', 'coui://ui/mods/' + ID + '/translations/' + c.toLowerCase() + '.json', false);
                try { xhr.send(); } catch (e0) { continue; }
                if (!xhr.responseText) { continue; }
                var datos = JSON.parse(xhr.responseText), plano = {};
                for (var k in datos) {
                    if (datos.hasOwnProperty(k) && datos[k] && datos[k].message) { plano[k] = datos[k].message; }
                }
                i18n.addResourceBundle(lng, 'translation', plano);
                return c;
            }
        } catch (e) {
            if (window.console) { console.error('[AtmosphereWeather] traduccion: ' + (e && e.message || e)); }
        }
        return null;
    }

    var NIVELES = ['low', 'medium', 'high', 'extreme'];
    var NIVELES_TXT = [L('Low'), L('Medium'), L('High'), L('Extreme')];
    // Calidades por efecto: la calidad general las fija todas juntas.
    var POR_EFECTO = ['q_clouds', 'q_precipitation', 'q_storm_lightning',
        'q_volcanic_plumes', 'q_volcanic_lightning', 'q_short_circuits'];

    // La plantilla vanilla aplica loc() a title y optionsText (settings.html 52-58).
    function sel(title, options, optionsText, def, callback) {
        var d = { title: L(title), type: 'select', options: options, optionsText: optionsText, default: def };
        if (callback) { d.callback = callback; }
        return d;
    }
    function onOff(title) { return sel(title, ['on', 'off'], [L('On'), L('Off')], 'on'); }
    // Deslizador (como "Icon display distance" de Gameplay). El vanilla no
    // muestra el numero: settings.js agrega la lectura "valor/divisor + sufijo
    // + palabra traducida". Toda lectura lleva unidad legible (pedido de Pablo).
    function desliz(title, min, max, step, def, sufijo, divisor, palabra) {
        return { title: L(title), type: 'slider', options: { min: min, max: max, step: step }, default: def,
            sufijo: sufijo, divisor: divisor || 1, palabra: palabra || '' };
    }
    function valor(k) { return api.settings.value(GRUPO, k); }

    // 'auto' = seguir el preset de Graphics del jugador (Atlas 4b). CUSTOM se
    // decide por las sombras, la opcion grafica que mas pesa.
    function nivelAuto() {
        var q = String(api.settings.value('graphics', 'quality') || '').toUpperCase();
        if (q === 'CUSTOM') { q = String(api.settings.value('graphics', 'shadows') || '').toUpperCase(); }
        return q === 'OFF' || q === 'LOW' ? 'low' : q === 'MEDIUM' ? 'medium' : 'high';
    }
    function nivelGeneral(g) { return g === 'auto' ? nivelAuto() : g; }

    // Calidad general -> fija las de cada efecto (patron vanilla "Quality Preset").
    var aplicando = false;
    function alCambiarCalidad(v) {
        var n = nivelGeneral(v);
        if (NIVELES.indexOf(n) < 0) { return; } // 'custom': no toca nada
        aplicando = true;
        try { POR_EFECTO.forEach(function (k) { api.settings.set(GRUPO, k, n); }); } finally { aplicando = false; }
    }
    // Una calidad por efecto distinta de la general -> general = Custom.
    function alCambiarEfecto(v) {
        if (aplicando) { return; }
        var g = valor('quality');
        if (g !== 'custom' && v !== nivelGeneral(g)) { api.settings.set(GRUPO, 'quality', 'custom'); }
    }
    function nivel(title) {
        return sel(title, NIVELES, NIVELES_TXT, 'high', alCambiarEfecto);
    }

    // Nombres para jugadores sin conocimiento tecnico: cada titulo dice que hace.
    var S = {
        quality: sel('Weather detail (all effects)', ['auto'].concat(NIVELES, ['custom']),
            [L('Match game graphics')].concat(NIVELES_TXT, [L('Custom')]), 'high', alCambiarCalidad),

        clouds: onOff('Show clouds'),
        rain: onOff('Show rain'),
        snow: onOff('Show snow'),
        virga: onOff('Show rain that dries up before landing'),
        storm_lightning: onOff('Show lightning in storms *'),
        volcanic_plumes: onOff('Show volcano ash clouds *'),
        volcanic_lightning: onOff('Show lightning in volcano ash *'),
        short_circuits: onOff('Show electric sparks on metal planets'),

        q_clouds: nivel('How many clouds'),
        q_precipitation: nivel('How much rain and snow'),
        q_storm_lightning: nivel('How many storms have lightning *'),
        q_volcanic_plumes: nivel('How many volcano ash clouds *'),
        q_volcanic_lightning: nivel('How much lightning in volcano ash *'),
        q_short_circuits: nivel('How many sparks on metal planets *'),

        advanced: sel('Show advanced options', ['off', 'on'], [L('No'), L('Yes')], 'off'),

        // Clima (seguro: solo cambia como se ve).
        wind_speed: desliz('How fast clouds drift', 25, 300, 25, 100, '%'),
        rain_chance: desliz('How often clouds turn into rain', 25, 150, 25, 100, '%'),
        storm_chance: desliz('How often rain turns into a storm', 0, 300, 25, 100, '%'),
        rain_duration: desliz('How long rain lasts', 50, 200, 10, 100, '%'),
        cloud_lifetime: desliz('How long clouds last', 50, 200, 10, 100, '%'),

        // Rendimiento (riesgoso: puede dar tirones).
        particle_budget: desliz('Effect limit per planet', 15000, 60000, 1000, 29000, 'k ', 1000, 'particles'),
        particle_cap: desliz('Effect limit for the whole system', 250000, 1000000, 50000, 500000, 'k ', 1000, 'particles'),
        spawn_per_cycle: desliz('How fast new clouds and rain appear', 20, 160, 10, 40, ' ', 1, 'per update'),
        cycle_length: desliz('Seconds between cloud movement updates (lower may stutter)', 6, 12, 1, 8, ' s'),

        // Default No: el log del jugador queda limpio (arranque y errores se escriben igual).
        debug_log: sel('Write troubleshooting info to the game log', ['on', 'off'], [L('Yes'), L('No')], 'off')
    };

    AW.OPCIONES = {
        GRUPO: GRUPO,
        NIVELES: NIVELES,
        nivelAuto: nivelAuto,
        alCambiarCalidad: alCambiarCalidad,
        POR_EFECTO: POR_EFECTO,
        AVANZADAS: ['wind_speed', 'rain_chance', 'storm_chance', 'rain_duration', 'cloud_lifetime',
            'particle_budget', 'particle_cap', 'spawn_per_cycle', 'cycle_length', 'debug_log'],
        definicion: { title: 'Atmosphere Weather', local_only: true, settings: S },
        // Idioma cargado (null = ingles o sin archivo) y si falta revision nativa.
        idioma: null,
        idiomaSinRevisar: false,
        // Pedido de Pablo: avisar en un lugar visible que las traducciones no
        // revisadas por hablantes nativos pueden tener errores (arriba de la pestaña).
        AVISO_TRADUCCION: 'This translation was made with AI and has not been reviewed by a native speaker, so it may contain translation errors. Please report them on the mod page.',
        // Estructura de la pestaña (settings.js). Textos = claves en ingles (loc).
        // Sin comillas simples ni dobles: van dentro de data-bind.
        secciones: [
            { titulo: 'Detail', claves: ['quality'],
              nota: 'Lower detail shows fewer weather effects and runs better on slower computers. Match game graphics uses the level of your Graphics quality preset.' },
            { titulo: 'Turn effects on or off',
              aviso: 'Turning an effect off does not remove it at once: what is already in the sky fades out on its own (up to 2 minutes).',
              claves: ['clouds', 'rain', 'snow', 'virga', 'storm_lightning', 'volcanic_plumes', 'volcanic_lightning', 'short_circuits'] },
            { titulo: 'Detail per effect', claves: POR_EFECTO,
              nota: '* Takes effect in your next match.' },
            { avisoExtremo: 'Extreme shows 50% more than High. If the game stutters, lower the detail.' },
            { titulo: 'Advanced', claves: ['advanced'] },
            { titulo: 'Weather behavior', avanzado: true, claves: ['wind_speed', 'rain_chance', 'storm_chance', 'rain_duration', 'cloud_lifetime'],
              // __button__ = nombre del boton traducido por el juego (settings.js).
              aviso: 'Changing these options can break the mod. If that happens, press __button__.' },
            { titulo: 'Performance', avanzado: true, claves: ['particle_budget', 'particle_cap', 'spawn_per_cycle', 'cycle_length'],
              aviso: 'Risky: higher values can make the game stutter.' },
            { titulo: 'Troubleshooting', avanzado: true, claves: ['debug_log'] }
        ]
    };

    // Registrar la definicion tambien en live_game: api.settings.value()
    // devuelve el default cuando el jugador nunca guardo nada.
    try { if (window.api && api.settings && api.settings.definitions) { api.settings.definitions[GRUPO] = AW.OPCIONES.definicion; } } catch (e) { /* nada */ }

    // Traduccion: solo en la scene settings (ahi existe model.settingDefinitions).
    if (typeof model !== 'undefined' && model && model.settingDefinitions) {
        AW.OPCIONES.idioma = cargarTraduccion();
        AW.OPCIONES.idiomaSinRevisar = !!AW.OPCIONES.idioma && VERIFICADOS.indexOf(AW.OPCIONES.idioma) < 0;
    }
}());
