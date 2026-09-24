// AtmosphereWeather: pestaña propia en el menu Settings del juego (scene "settings").
// Las opciones vienen de opciones.js (cargado antes; ya registro la definicion
// y la traduccion del idioma del jugador).
// settings.js vanilla carga los mods ANTES de ko.applyBindings, asi que el HTML
// que se agrega aqui queda enlazado. El contenido de cada pestaña es HTML fijo
// en settings.html: sin el bloque de abajo la pestaña saldria vacia.
// Estructura calcada de la pestaña Gameplay (settings.html 162-193): UN
// form-group con sub-group-title + sub-group. .option-list es una columna flex
// de alto fijo: con varios hijos directos, Coherent los encoge y se enciman.
// Textos: siempre data-bind "text: loc(...)" (los <loc> del documento ya se
// tradujeron al cargar la scene, antes que este HTML).
(function () {
    try {
        var O = window.AtmosphereWeather.OPCIONES, G = O.GRUPO, S = O.definicion.settings;
        // Las computadas ya se evaluaron al crear el modelo: forzar recalculo.
        model.settingDefinitions(api.settings.definitions);

        var item = function (k) { return '$root.settingsItemMap()[\'' + G + '.' + k + '\']'; };
        var valor = function (k) { return item(k) + '.value()'; };
        var L = function (s) { return 'loc(\'!LOC:' + s + '\')'; };   // claves sin comillas (opciones.js)
        var texto = function (expr, estilo, visible) {
            return '<div ' + estilo + ' data-bind="' + (visible ? 'visible: ' + visible + ', ' : '') + 'text: ' + expr + '"></div>';
        };
        var avanzado = valor('advanced') + ' === \'on\'';
        var extremo = ['quality'].concat(O.POR_EFECTO).map(function (k) { return valor(k) + ' === \'extreme\''; }).join(' || ');
        var AVISO = 'style="color:salmon; margin:0 0 10px;"'; // mismo color que .warning de la pestaña Server
        var NOTA = 'style="opacity:0.7; margin:0 0 10px;"';
        // Nota destacada (pedido de Pablo): invitacion a sugerir valores por defecto.
        var DESTACADA = 'style="font-size:16px; color:#8fd3ff; margin:4px 0 14px;"';
        var FILA = 'class="sub-group top" style="flex-wrap:wrap; min-height:0;"';
        // El nombre del boton sale de la traduccion oficial del juego, en mayusculas como en pantalla.
        var BOTON = '{ button: loc(\'!LOC:Restore Tab Defaults\').toUpperCase() }';
        var aviso = function (s) {
            var t = s.indexOf('__button__') >= 0 ? 'loc(\'!LOC:' + s + '\', ' + BOTON + ')' : L(s);
            return L('Warning:') + ' + \' \' + ' + t;
        };

        // Lectura del deslizador (el vanilla no muestra el numero), con unidad traducida.
        var lectura = function (k) {
            var d = S[k], v = 'Number(' + valor(k) + ')';
            var txt = 'Math.round(' + v + ' / ' + d.divisor + ') + \'' + d.sufijo + '\'' + (d.palabra ? ' + ' + L(d.palabra) : '');
            return texto(txt + ' + (' + v + ' === ' + d.default + ' ? \' (\' + ' + L('normal') + ' + \')\' : \'\')', 'style="margin-top:4px;"');
        };
        var opcion = function (k) {
            var t = '<div data-bind="template: { name: \'setting-template\', data: ' + item(k) + ' }"></div>';
            if (S[k].type === 'slider') { return '<div class="option slider">' + t + lectura(k) + '</div>'; }
            return '<div class="option" data-bind="template: { name: \'setting-template\', data: ' + item(k) + ' }"></div>';
        };

        var html = O.secciones.map(function (s) {
            if (s.avisoExtremo) { return texto(aviso(s.avisoExtremo), AVISO, extremo); }
            var h = '<div data-bind="visible: ' + (s.avanzado ? avanzado : 'true') + '">';
            h += texto(L(s.titulo), 'class="sub-group-title"');
            if (s.aviso) { h += texto(aviso(s.aviso), AVISO); }
            h += '<div ' + FILA + '>' + s.claves.map(opcion).join('') + '</div>';
            if (s.nota) { h += texto(L(s.nota), s.destacada ? DESTACADA : NOTA); }
            return h + '</div>';
        }).join('');

        // Traduccion hecha con IA sin revision nativa: aviso arriba de todo (pedido de Pablo).
        if (O.idiomaSinRevisar) { html = texto(L(O.AVISO_TRADUCCION), AVISO) + html; }

        $('.container_settings').append(
            // Scroll vertical como Gameplay (.option-list.ui, settings.css 265-272).
            '<div class="option-list" style="max-height:100%; overflow-y:auto; overflow-x:hidden;" data-bind="visible: $root.activeSettingsGroup() === \'' + G + '\', deferBindingsUntilVisible: true">' +
            '<div class="form-group" style="flex-shrink:0;">' + html + '</div></div>'
        );

        // "Match game graphics": si el jugador cambia Graphics > Quality Preset
        // (o las sombras) en esta misma pantalla, las calidades por efecto lo siguen.
        ko.computed(function () {
            var m = model.settingsItemMap(), gq = m['graphics.quality'], gs = m['graphics.shadows'], q = m[G + '.quality'];
            if (!gq || !q) { return; }
            gq.value(); if (gs) { gs.value(); } // dependencias
            if (q.value() === 'auto') { ko.ignoreDependencies(function () { O.alCambiarCalidad('auto'); }); }
        });
    } catch (e) {
        console.error('[AtmosphereWeather] settings: ' + (e && e.message || e));
    }
}());
