"""Genera ui/mods/<id>/translations/<idioma>.json de AtmosphereWeather.

Uso: python scripts/generar_traducciones.py
- CLAVES = textos en ingles EXACTOS de opciones.js (la clave de loc()).
- Cada idioma = un bloque de lineas en el MISMO orden que CLAVES.
- Formato de salida = el del juego: { "<ingles>": { "message": "<traduccion>" } }.
- Traducciones hechas con IA (2026-09-23). Vocabulario alineado con las
  traducciones oficiales del juego (settings.json de cada idioma: Low/High,
  On/Off, Graphics, Quality Preset). Sin revision de hablantes nativos:
  opciones.js (VERIFICADOS) decide que idiomas muestran el aviso.
- Mantener __button__ (lo reemplaza el nombre del boton) y los asteriscos.
- de-AT y nl-BE usan de / nl; zh-HK usa zh-TW (alias en opciones.js).
"""
import json
import os

MOD_ID = "com.pa.pabloandclaude.atmosphereweather"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(REPO, "ui", "mods", MOD_ID, "translations")

CLAVES = """Weather detail (all effects)
Show clouds
Show rain
Show snow
Show rain that dries up before landing
Show lightning in storms *
Show volcano ash clouds *
Show lightning in volcano ash *
Show electric sparks on metal planets
How many clouds
How much rain and snow
How many storms have lightning *
How many volcano ash clouds *
How much lightning in volcano ash *
How many sparks on metal planets *
Show advanced options
How fast clouds drift
How often clouds turn into rain
How often rain turns into a storm
How long rain lasts
How long clouds last
Effect limit per planet
Effect limit for the whole system
How fast new clouds and rain appear
Seconds between cloud movement updates (lower may stutter)
Write troubleshooting info to the game log
Match game graphics
Low
Medium
High
Extreme
Custom
On
Off
Yes
No
Detail
Turn effects on or off
Detail per effect
Advanced
Weather behavior
Performance
Troubleshooting
Lower detail shows fewer weather effects and runs better on slower computers. Match game graphics uses the level of your Graphics quality preset.
Turning an effect off does not remove it at once: what is already in the sky fades out on its own (up to 2 minutes).
* Takes effect in your next match.
Extreme shows 50% more than High. If the game stutters, lower the detail.
Changing these options can break the mod. If that happens, press __button__.
Risky: higher values can make the game stutter.
Warning:
normal
particles
per update
This translation was made with AI and has not been reviewed by a native speaker, so it may contain translation errors. Please report them on the mod page.
Default values are open to suggestions: tell us on the mod page."""

IDIOMAS = {}

IDIOMAS["es-ES"] = """Detalle del clima (todos los efectos)
Mostrar nubes
Mostrar lluvia
Mostrar nieve
Mostrar lluvia que se evapora antes de tocar el suelo
Mostrar rayos en las tormentas *
Mostrar nubes de ceniza volcánica *
Mostrar rayos en la ceniza volcánica *
Mostrar chispas eléctricas en planetas de metal
Cantidad de nubes
Cantidad de lluvia y nieve
Cuántas tormentas tienen rayos *
Cantidad de nubes de ceniza volcánica *
Cantidad de rayos en la ceniza volcánica *
Cantidad de chispas en planetas de metal *
Mostrar opciones avanzadas
Velocidad de las nubes
Frecuencia con que las nubes dan lluvia
Frecuencia con que la lluvia se vuelve tormenta
Duración de la lluvia
Duración de las nubes
Límite de efectos por planeta
Límite de efectos de todo el sistema
Rapidez con que aparecen nubes y lluvia nuevas
Segundos entre actualizaciones del movimiento de las nubes (menos puede causar tirones)
Escribir información de diagnóstico en el registro del juego
Igual que los gráficos del juego
Bajo
Medio
Alto
Extremo
Personalizado
Activado
Desactivado
Sí
No
Detalle
Activar o desactivar efectos
Detalle por efecto
Avanzado
Comportamiento del clima
Rendimiento
Diagnóstico
Menos detalle muestra menos efectos del clima y funciona mejor en ordenadores lentos. «Igual que los gráficos del juego» usa el nivel de tu preconfiguración de calidad de Gráficos.
Desactivar un efecto no lo quita de inmediato: lo que ya está en el cielo se desvanece solo (hasta 2 minutos).
* Se aplica en tu próxima partida.
Extremo muestra un 50 % más que Alto. Si el juego da tirones, baja el detalle.
Cambiar estas opciones puede romper el mod. Si pasa, pulsa __button__.
Riesgo: valores más altos pueden hacer que el juego dé tirones.
Aviso:
normal
partículas
por actualización
Esta traducción se hizo con IA y no ha sido revisada por un hablante nativo, así que puede contener errores de traducción. Infórmalos en la página del mod.
Los valores predeterminados están abiertos a sugerencias: cuéntanos en la página del mod."""

IDIOMAS["de"] = """Wetterdetails (alle Effekte)
Wolken anzeigen
Regen anzeigen
Schnee anzeigen
Regen anzeigen, der vor dem Boden verdunstet
Blitze in Gewittern anzeigen *
Vulkanische Aschewolken anzeigen *
Blitze in Vulkanasche anzeigen *
Elektrische Funken auf Metallplaneten anzeigen
Anzahl der Wolken
Menge an Regen und Schnee
Wie viele Gewitter Blitze haben *
Anzahl der vulkanischen Aschewolken *
Menge an Blitzen in Vulkanasche *
Anzahl der Funken auf Metallplaneten *
Erweiterte Optionen anzeigen
Wie schnell Wolken ziehen
Wie oft Wolken zu Regen werden
Wie oft Regen zu einem Gewitter wird
Wie lange Regen dauert
Wie lange Wolken bestehen
Effektlimit pro Planet
Effektlimit für das ganze System
Wie schnell neue Wolken und Regen erscheinen
Sekunden zwischen Aktualisierungen der Wolkenbewegung (weniger kann ruckeln)
Diagnoseinformationen ins Spielprotokoll schreiben
Wie die Spielgrafik
Niedrig
Mittel
Hoch
Extrem
Benutzerdefiniert
An
Aus
Ja
Nein
Details
Effekte ein- oder ausschalten
Details pro Effekt
Erweitert
Wetterverhalten
Leistung
Fehlerbehebung
Weniger Details zeigen weniger Wettereffekte und laufen auf langsameren Computern besser. „Wie die Spielgrafik“ verwendet die Stufe deiner Grafik-Qualitätsvoreinstellung.
Das Ausschalten eines Effekts entfernt ihn nicht sofort: Was schon am Himmel ist, verblasst von selbst (bis zu 2 Minuten).
* Gilt ab deinem nächsten Match.
Extrem zeigt 50 % mehr als Hoch. Wenn das Spiel ruckelt, verringere die Details.
Das Ändern dieser Optionen kann den Mod beschädigen. Falls das passiert, klicke auf __button__.
Riskant: Höhere Werte können das Spiel ruckeln lassen.
Warnung:
normal
Partikel
pro Aktualisierung
Diese Übersetzung wurde mit KI erstellt und nicht von einem Muttersprachler geprüft, daher kann sie Übersetzungsfehler enthalten. Bitte melde sie auf der Seite des Mods.
Vorschläge zu den Standardwerten sind willkommen: schreib uns auf der Mod-Seite."""

IDIOMAS["fr"] = """Détail météo (tous les effets)
Afficher les nuages
Afficher la pluie
Afficher la neige
Afficher la pluie qui s'évapore avant de toucher le sol
Afficher les éclairs des orages *
Afficher les nuages de cendres volcaniques *
Afficher les éclairs dans les cendres volcaniques *
Afficher les étincelles électriques sur les planètes métalliques
Nombre de nuages
Quantité de pluie et de neige
Nombre d'orages avec éclairs *
Nombre de nuages de cendres volcaniques *
Quantité d'éclairs dans les cendres volcaniques *
Nombre d'étincelles sur les planètes métalliques *
Afficher les options avancées
Vitesse de déplacement des nuages
Fréquence à laquelle les nuages donnent de la pluie
Fréquence à laquelle la pluie devient un orage
Durée de la pluie
Durée de vie des nuages
Limite d'effets par planète
Limite d'effets pour tout le système
Vitesse d'apparition des nouveaux nuages et de la pluie
Secondes entre les mises à jour du mouvement des nuages (moins peut provoquer des saccades)
Écrire les informations de diagnostic dans le journal du jeu
Comme les graphismes du jeu
Bas
Moyen
Élevé
Extrême
Personnalisé
Activé
Désactivé
Oui
Non
Détail
Activer ou désactiver les effets
Détail par effet
Avancé
Comportement de la météo
Performances
Dépannage
Moins de détail affiche moins d'effets météo et fonctionne mieux sur les ordinateurs lents. « Comme les graphismes du jeu » utilise le niveau de vos paramètres graphiques prédéfinis.
Désactiver un effet ne le retire pas tout de suite : ce qui est déjà dans le ciel disparaît de lui-même (jusqu'à 2 minutes).
* Prend effet à votre prochaine partie.
Extrême affiche 50 % de plus qu'Élevé. Si le jeu saccade, baissez le détail.
Modifier ces options peut casser le mod. Si cela arrive, cliquez sur __button__.
Risqué : des valeurs plus élevées peuvent faire saccader le jeu.
Attention :
normal
particules
par mise à jour
Cette traduction a été réalisée par IA et n'a pas été relue par un locuteur natif : elle peut donc contenir des erreurs de traduction. Merci de les signaler sur la page du mod.
Les valeurs par défaut sont ouvertes aux suggestions : dites-le-nous sur la page du mod."""

IDIOMAS["it"] = """Dettaglio meteo (tutti gli effetti)
Mostra nuvole
Mostra pioggia
Mostra neve
Mostra pioggia che evapora prima di toccare terra
Mostra fulmini nei temporali *
Mostra nubi di cenere vulcanica *
Mostra fulmini nella cenere vulcanica *
Mostra scintille elettriche sui pianeti metallici
Quante nuvole
Quanta pioggia e neve
Quanti temporali hanno fulmini *
Quante nubi di cenere vulcanica *
Quanti fulmini nella cenere vulcanica *
Quante scintille sui pianeti metallici *
Mostra opzioni avanzate
Velocità delle nuvole
Frequenza con cui le nuvole portano pioggia
Frequenza con cui la pioggia diventa temporale
Durata della pioggia
Durata delle nuvole
Limite di effetti per pianeta
Limite di effetti per l'intero sistema
Velocità di comparsa di nuove nuvole e pioggia
Secondi tra gli aggiornamenti del movimento delle nuvole (meno può causare scatti)
Scrivi informazioni diagnostiche nel registro del gioco
Come la grafica del gioco
Bassa
Media
Alta
Estrema
Personalizzata
Attivo
Disattivo
Sì
No
Dettaglio
Attiva o disattiva effetti
Dettaglio per effetto
Avanzate
Comportamento del meteo
Prestazioni
Risoluzione problemi
Meno dettaglio mostra meno effetti meteo e funziona meglio sui computer lenti. «Come la grafica del gioco» usa il livello del tuo preset qualità della grafica.
Disattivare un effetto non lo rimuove subito: ciò che è già nel cielo svanisce da solo (fino a 2 minuti).
* Ha effetto dalla prossima partita.
Estrema mostra il 50% in più di Alta. Se il gioco va a scatti, riduci il dettaglio.
Modificare queste opzioni può rompere la mod. Se succede, premi __button__.
Rischioso: valori più alti possono far andare il gioco a scatti.
Attenzione:
normale
particelle
per aggiornamento
Questa traduzione è stata fatta con l'IA e non è stata revisionata da un madrelingua, quindi può contenere errori di traduzione. Segnalali nella pagina della mod.
I valori predefiniti sono aperti a suggerimenti: scrivici sulla pagina della mod."""

IDIOMAS["pt-BR"] = """Detalhe do clima (todos os efeitos)
Mostrar nuvens
Mostrar chuva
Mostrar neve
Mostrar chuva que evapora antes de chegar ao chão
Mostrar raios nas tempestades *
Mostrar nuvens de cinza vulcânica *
Mostrar raios na cinza vulcânica *
Mostrar faíscas elétricas em planetas de metal
Quantidade de nuvens
Quantidade de chuva e neve
Quantas tempestades têm raios *
Quantidade de nuvens de cinza vulcânica *
Quantidade de raios na cinza vulcânica *
Quantidade de faíscas em planetas de metal *
Mostrar opções avançadas
Velocidade das nuvens
Frequência com que as nuvens viram chuva
Frequência com que a chuva vira tempestade
Duração da chuva
Duração das nuvens
Limite de efeitos por planeta
Limite de efeitos do sistema inteiro
Rapidez com que surgem novas nuvens e chuva
Segundos entre atualizações do movimento das nuvens (menos pode causar travadas)
Gravar informações de diagnóstico no log do jogo
Igual aos gráficos do jogo
Baixo
Médio
Alto
Extremo
Personalizado
Ligado
Desligado
Sim
Não
Detalhe
Ligar ou desligar efeitos
Detalhe por efeito
Avançado
Comportamento do clima
Desempenho
Solução de problemas
Menos detalhe mostra menos efeitos do clima e roda melhor em computadores mais lentos. "Igual aos gráficos do jogo" usa o nível da sua Qualidade Geral de Gráficos.
Desligar um efeito não o remove na hora: o que já está no céu some sozinho (até 2 minutos).
* Vale a partir da sua próxima partida.
Extremo mostra 50% a mais que Alto. Se o jogo travar, diminua o detalhe.
Mudar estas opções pode quebrar o mod. Se isso acontecer, clique em __button__.
Arriscado: valores mais altos podem fazer o jogo travar.
Aviso:
normal
partículas
por atualização
Esta tradução foi feita com IA e não foi revisada por um falante nativo, então pode conter erros de tradução. Por favor, informe-os na página do mod.
Os valores padrão estão abertos a sugestões: fale conosco na página do mod."""

IDIOMAS["ru"] = """Детализация погоды (все эффекты)
Показывать облака
Показывать дождь
Показывать снег
Показывать дождь, испаряющийся до земли
Показывать молнии в грозах *
Показывать облака вулканического пепла *
Показывать молнии в вулканическом пепле *
Показывать электрические искры на металлических планетах
Количество облаков
Количество дождя и снега
Сколько гроз с молниями *
Количество облаков вулканического пепла *
Количество молний в вулканическом пепле *
Количество искр на металлических планетах *
Показывать расширенные настройки
Скорость движения облаков
Как часто облака дают дождь
Как часто дождь становится грозой
Длительность дождя
Время жизни облаков
Лимит эффектов на планету
Лимит эффектов на всю систему
Как быстро появляются новые облака и дождь
Секунды между обновлениями движения облаков (меньше — возможны подтормаживания)
Записывать диагностическую информацию в журнал игры
Как графика игры
Низкое
Среднее
Высокое
Экстремальное
Выборочно
Вкл
Выкл
Да
Нет
Детализация
Включение и выключение эффектов
Детализация по эффектам
Расширенные
Поведение погоды
Производительность
Диагностика
Меньшая детализация показывает меньше погодных эффектов и лучше работает на слабых компьютерах. «Как графика игры» использует уровень вашей предустановки качества графики.
Выключение эффекта не убирает его сразу: то, что уже в небе, исчезает само (до 2 минут).
* Применяется со следующего матча.
Экстремальное показывает на 50% больше, чем Высокое. Если игра подтормаживает, уменьшите детализацию.
Изменение этих настроек может сломать мод. Если это случится, нажмите __button__.
Рискованно: более высокие значения могут вызвать подтормаживания.
Внимание:
обычно
частиц
за обновление
Этот перевод сделан ИИ и не проверен носителем языка, поэтому в нём могут быть ошибки. Сообщайте о них на странице мода.
Предложения по значениям по умолчанию приветствуются: пишите на странице мода."""

IDIOMAS["uk"] = """Деталізація погоди (усі ефекти)
Показувати хмари
Показувати дощ
Показувати сніг
Показувати дощ, що випаровується до землі
Показувати блискавки в грозах *
Показувати хмари вулканічного попелу *
Показувати блискавки у вулканічному попелі *
Показувати електричні іскри на металевих планетах
Кількість хмар
Кількість дощу та снігу
Скільки гроз мають блискавки *
Кількість хмар вулканічного попелу *
Кількість блискавок у вулканічному попелі *
Кількість іскор на металевих планетах *
Показувати розширені налаштування
Швидкість руху хмар
Як часто хмари дають дощ
Як часто дощ стає грозою
Тривалість дощу
Тривалість життя хмар
Ліміт ефектів на планету
Ліміт ефектів на всю систему
Як швидко з'являються нові хмари та дощ
Секунди між оновленнями руху хмар (менше — можливі підгальмовування)
Записувати діагностичну інформацію в журнал гри
Як графіка гри
Низька
Середня
Висока
Екстремальна
Власна
Увімк.
Вимк.
Так
Ні
Деталізація
Увімкнення та вимкнення ефектів
Деталізація за ефектами
Розширені
Поведінка погоди
Продуктивність
Діагностика
Нижча деталізація показує менше погодних ефектів і краще працює на слабких комп'ютерах. «Як графіка гри» використовує рівень вашого набору якості графіки.
Вимкнення ефекту не прибирає його одразу: те, що вже в небі, зникає саме (до 2 хвилин).
* Застосовується з наступного матчу.
Екстремальна показує на 50% більше, ніж Висока. Якщо гра підгальмовує, зменште деталізацію.
Зміна цих налаштувань може зламати мод. Якщо це станеться, натисніть __button__.
Ризиковано: вищі значення можуть спричинити підгальмовування.
Увага:
звичайно
частинок
за оновлення
Цей переклад зроблено ШІ, і його не перевіряв носій мови, тож він може містити помилки перекладу. Повідомляйте про них на сторінці мода.
Пропозиції щодо стандартних значень вітаються: пишіть на сторінці мода."""

IDIOMAS["pl-PL"] = """Szczegółowość pogody (wszystkie efekty)
Pokazuj chmury
Pokazuj deszcz
Pokazuj śnieg
Pokazuj deszcz, który paruje przed dotarciem do ziemi
Pokazuj błyskawice w burzach *
Pokazuj chmury popiołu wulkanicznego *
Pokazuj błyskawice w popiele wulkanicznym *
Pokazuj iskry elektryczne na metalowych planetach
Liczba chmur
Ilość deszczu i śniegu
Ile burz ma błyskawice *
Liczba chmur popiołu wulkanicznego *
Ilość błyskawic w popiele wulkanicznym *
Liczba iskier na metalowych planetach *
Pokaż opcje zaawansowane
Prędkość przesuwania się chmur
Jak często z chmur pada deszcz
Jak często deszcz zmienia się w burzę
Czas trwania deszczu
Czas życia chmur
Limit efektów na planetę
Limit efektów dla całego systemu
Jak szybko pojawiają się nowe chmury i deszcz
Sekundy między aktualizacjami ruchu chmur (mniej może powodować przycięcia)
Zapisuj informacje diagnostyczne w dzienniku gry
Jak grafika gry
Niskie
Średnie
Wysokie
Ekstremalne
Własne
Wł.
Wył.
Tak
Nie
Szczegółowość
Włączanie i wyłączanie efektów
Szczegółowość efektów
Zaawansowane
Zachowanie pogody
Wydajność
Rozwiązywanie problemów
Niższa szczegółowość pokazuje mniej efektów pogodowych i działa lepiej na słabszych komputerach. „Jak grafika gry” używa poziomu z gotowych ustawień jakości grafiki.
Wyłączenie efektu nie usuwa go od razu: to, co już jest na niebie, znika samo (do 2 minut).
* Działa od następnego meczu.
Ekstremalne pokazuje o 50% więcej niż Wysokie. Jeśli gra się przycina, zmniejsz szczegółowość.
Zmiana tych opcji może zepsuć moda. Jeśli tak się stanie, kliknij __button__.
Ryzykowne: wyższe wartości mogą powodować przycięcia gry.
Uwaga:
normalnie
cząsteczek
na aktualizację
To tłumaczenie wykonała SI i nie zostało sprawdzone przez rodzimego użytkownika języka, więc może zawierać błędy. Zgłaszaj je na stronie moda.
Sugestie dotyczące wartości domyślnych są mile widziane: napisz na stronie moda."""

IDIOMAS["cs-CZ"] = """Detaily počasí (všechny efekty)
Zobrazit mraky
Zobrazit déšť
Zobrazit sníh
Zobrazit déšť, který se vypaří před dopadem
Zobrazit blesky v bouřích *
Zobrazit mraky sopečného popela *
Zobrazit blesky v sopečném popelu *
Zobrazit elektrické jiskry na kovových planetách
Množství mraků
Množství deště a sněhu
Kolik bouří má blesky *
Množství mraků sopečného popela *
Množství blesků v sopečném popelu *
Množství jisker na kovových planetách *
Zobrazit pokročilé možnosti
Rychlost pohybu mraků
Jak často z mraků prší
Jak často se déšť změní v bouři
Délka deště
Doba trvání mraků
Limit efektů na planetu
Limit efektů pro celý systém
Jak rychle se objevují nové mraky a déšť
Sekundy mezi aktualizacemi pohybu mraků (méně může způsobit zasekávání)
Zapisovat diagnostické informace do protokolu hry
Podle grafiky hry
Nízký
Střední
Vysoký
Extrémní
Vlastní
Zapnuto
Vypnuto
Ano
Ne
Detaily
Zapnutí a vypnutí efektů
Detaily jednotlivých efektů
Pokročilé
Chování počasí
Výkon
Řešení problémů
Nižší detaily zobrazují méně efektů počasí a na slabších počítačích běží lépe. „Podle grafiky hry“ použije úroveň z přednastavení kvality grafiky.
Vypnutí efektu ho neodstraní hned: co už je na obloze, samo zmizí (až 2 minuty).
* Projeví se v příštím zápase.
Extrémní zobrazuje o 50 % více než Vysoký. Pokud se hra zasekává, snižte detaily.
Změna těchto možností může mód rozbít. Pokud se to stane, stiskněte __button__.
Riskantní: vyšší hodnoty mohou způsobit zasekávání hry.
Varování:
normální
částic
za aktualizaci
Tento překlad vytvořila AI a nezkontroloval ho rodilý mluvčí, proto může obsahovat chyby v překladu. Nahlaste je prosím na stránce módu.
Návrhy na výchozí hodnoty jsou vítány: napište nám na stránce modu."""

IDIOMAS["hu-HU"] = """Időjárás részletessége (összes effekt)
Felhők megjelenítése
Eső megjelenítése
Hó megjelenítése
A földet érés előtt elpárolgó eső megjelenítése
Villámok megjelenítése viharokban *
Vulkáni hamufelhők megjelenítése *
Villámok megjelenítése a vulkáni hamuban *
Elektromos szikrák megjelenítése fémbolygókon
Felhők mennyisége
Eső és hó mennyisége
Hány viharban legyen villám *
Vulkáni hamufelhők mennyisége *
Villámok mennyisége a vulkáni hamuban *
Szikrák mennyisége fémbolygókon *
Speciális beállítások megjelenítése
A felhők sebessége
Milyen gyakran lesz a felhőből eső
Milyen gyakran lesz az esőből vihar
Az eső időtartama
A felhők élettartama
Effektkorlát bolygónként
Effektkorlát az egész rendszerre
Milyen gyorsan jelennek meg új felhők és eső
Másodpercek a felhőmozgás frissítései között (kevesebb akadozást okozhat)
Hibakeresési információk írása a játék naplójába
A játék grafikája szerint
Alacsony
Közepes
Magas
Extrém
Egyedi
Be
Ki
Igen
Nem
Részletesség
Effektek be- és kikapcsolása
Részletesség effektenként
Speciális
Az időjárás viselkedése
Teljesítmény
Hibaelhárítás
Az alacsonyabb részletesség kevesebb időjárási effektet mutat, és lassabb gépeken jobban fut. „A játék grafikája szerint” a grafikai minőség előbeállításod szintjét használja.
Egy effekt kikapcsolása nem távolítja el azonnal: ami már az égen van, magától eltűnik (legfeljebb 2 perc).
* A következő meccstől érvényes.
Az Extrém 50%-kal többet mutat, mint a Magas. Ha a játék akadozik, csökkentsd a részletességet.
Ezeknek a beállításoknak a módosítása elronthatja a modot. Ha ez történik, nyomd meg ezt: __button__.
Kockázatos: a magasabb értékek akadozást okozhatnak.
Figyelem:
normál
részecske
frissítésenként
Ezt a fordítást mesterséges intelligencia készítette, és anyanyelvi beszélő nem ellenőrizte, ezért fordítási hibákat tartalmazhat. Kérjük, jelezd őket a mod oldalán.
Az alapértékekkel kapcsolatos javaslatokat szívesen fogadjuk: írj nekünk a mod oldalán."""

IDIOMAS["ro"] = """Detaliu vreme (toate efectele)
Afișează norii
Afișează ploaia
Afișează zăpada
Afișează ploaia care se evaporă înainte de sol
Afișează fulgerele din furtuni *
Afișează norii de cenușă vulcanică *
Afișează fulgerele din cenușa vulcanică *
Afișează scânteile electrice pe planetele metalice
Câți nori
Câtă ploaie și zăpadă
Câte furtuni au fulgere *
Câți nori de cenușă vulcanică *
Câte fulgere în cenușa vulcanică *
Câte scântei pe planetele metalice *
Afișează opțiunile avansate
Viteza norilor
Cât de des norii aduc ploaie
Cât de des ploaia devine furtună
Durata ploii
Durata norilor
Limită de efecte pe planetă
Limită de efecte pentru tot sistemul
Cât de repede apar nori și ploaie noi
Secunde între actualizările mișcării norilor (mai puțin poate cauza sacadări)
Scrie informații de diagnostic în jurnalul jocului
La fel ca grafica jocului
Scăzut
Mediu
Ridicat
Extrem
Personalizat
Pornit
Oprit
Da
Nu
Detaliu
Pornește sau oprește efectele
Detaliu pe efect
Avansat
Comportamentul vremii
Performanță
Depanare
Un detaliu mai mic afișează mai puține efecte meteo și merge mai bine pe calculatoare mai lente. „La fel ca grafica jocului” folosește nivelul setării de calitate grafică.
Oprirea unui efect nu îl elimină imediat: ce e deja pe cer dispare singur (până la 2 minute).
* Se aplică de la următorul meci.
Extrem afișează cu 50% mai mult decât Ridicat. Dacă jocul sacadează, scade detaliul.
Modificarea acestor opțiuni poate strica modul. Dacă se întâmplă, apasă __button__.
Riscant: valorile mai mari pot face jocul să sacadeze.
Atenție:
normal
particule
pe actualizare
Această traducere a fost făcută cu IA și nu a fost verificată de un vorbitor nativ, așa că poate conține greșeli de traducere. Te rugăm să le raportezi pe pagina modului.
Sugestiile pentru valorile implicite sunt binevenite: scrie-ne pe pagina modului."""

IDIOMAS["nl"] = """Weerdetail (alle effecten)
Wolken tonen
Regen tonen
Sneeuw tonen
Regen tonen die verdampt voordat hij de grond raakt
Bliksem in onweersbuien tonen *
Vulkanische aswolken tonen *
Bliksem in vulkanische as tonen *
Elektrische vonken op metaalplaneten tonen
Hoeveel wolken
Hoeveel regen en sneeuw
Hoeveel onweersbuien bliksem hebben *
Hoeveel vulkanische aswolken *
Hoeveel bliksem in vulkanische as *
Hoeveel vonken op metaalplaneten *
Geavanceerde opties tonen
Hoe snel wolken drijven
Hoe vaak wolken regen worden
Hoe vaak regen onweer wordt
Hoe lang regen duurt
Hoe lang wolken blijven
Effectlimiet per planeet
Effectlimiet voor het hele systeem
Hoe snel nieuwe wolken en regen verschijnen
Seconden tussen updates van de wolkbeweging (minder kan haperen)
Diagnose-informatie naar het spellogboek schrijven
Zoals de spelgraphics
Laag
Gemiddeld
Hoog
Extreem
Aangepast
Aan
Uit
Ja
Nee
Detail
Effecten aan- of uitzetten
Detail per effect
Geavanceerd
Weergedrag
Prestaties
Probleemoplossing
Minder detail toont minder weereffecten en werkt beter op tragere computers. 'Zoals de spelgraphics' gebruikt het niveau van je kwaliteits-voorinstelling voor Beeld.
Een effect uitzetten haalt het niet meteen weg: wat al in de lucht is, verdwijnt vanzelf (tot 2 minuten).
* Werkt vanaf je volgende potje.
Extreem toont 50% meer dan Hoog. Als het spel hapert, verlaag dan het detail.
Deze opties wijzigen kan de mod breken. Gebeurt dat, klik dan op __button__.
Riskant: hogere waarden kunnen het spel laten haperen.
Waarschuwing:
normaal
deeltjes
per update
Deze vertaling is gemaakt met AI en niet nagekeken door een moedertaalspreker, dus er kunnen vertaalfouten in zitten. Meld ze op de pagina van de mod.
Suggesties voor de standaardwaarden zijn welkom: laat het ons weten op de modpagina."""

IDIOMAS["da"] = """Vejrdetaljer (alle effekter)
Vis skyer
Vis regn
Vis sne
Vis regn, der fordamper før den rammer jorden
Vis lyn i tordenvejr *
Vis vulkanske askeskyer *
Vis lyn i vulkansk aske *
Vis elektriske gnister på metalplaneter
Hvor mange skyer
Hvor meget regn og sne
Hvor mange tordenvejr har lyn *
Hvor mange vulkanske askeskyer *
Hvor meget lyn i vulkansk aske *
Hvor mange gnister på metalplaneter *
Vis avancerede indstillinger
Hvor hurtigt skyerne driver
Hvor ofte skyer bliver til regn
Hvor ofte regn bliver til tordenvejr
Hvor længe regnen varer
Hvor længe skyerne varer
Effektgrænse pr. planet
Effektgrænse for hele systemet
Hvor hurtigt nye skyer og regn dukker op
Sekunder mellem opdateringer af skyernes bevægelse (færre kan give hakken)
Skriv fejlfindingsinfo i spillets log
Som spillets grafik
Lav
Middel
Høj
Ekstrem
Brugerdefineret
Til
Fra
Ja
Nej
Detaljer
Slå effekter til eller fra
Detaljer pr. effekt
Avanceret
Vejrets opførsel
Ydeevne
Fejlfinding
Færre detaljer viser færre vejreffekter og kører bedre på langsommere computere. "Som spillets grafik" bruger niveauet fra din grafikkvalitet.
At slå en effekt fra fjerner den ikke med det samme: det, der allerede er på himlen, forsvinder af sig selv (op til 2 minutter).
* Træder i kraft i din næste kamp.
Ekstrem viser 50 % mere end Høj. Hvis spillet hakker, så sænk detaljerne.
Ændringer af disse indstillinger kan ødelægge modden. Hvis det sker, så tryk på __button__.
Risikabelt: højere værdier kan få spillet til at hakke.
Advarsel:
normal
partikler
pr. opdatering
Denne oversættelse er lavet med AI og er ikke tjekket af en modersmålstaler, så den kan indeholde oversættelsesfejl. Rapportér dem gerne på moddens side.
Forslag til standardværdierne er velkomne: skriv til os på modsiden."""

IDIOMAS["no"] = """Værdetaljer (alle effekter)
Vis skyer
Vis regn
Vis snø
Vis regn som fordamper før den treffer bakken
Vis lyn i tordenvær *
Vis vulkanske askeskyer *
Vis lyn i vulkansk aske *
Vis elektriske gnister på metallplaneter
Hvor mange skyer
Hvor mye regn og snø
Hvor mange tordenvær har lyn *
Hvor mange vulkanske askeskyer *
Hvor mye lyn i vulkansk aske *
Hvor mange gnister på metallplaneter *
Vis avanserte innstillinger
Hvor raskt skyene driver
Hvor ofte skyer blir til regn
Hvor ofte regn blir til tordenvær
Hvor lenge regnet varer
Hvor lenge skyene varer
Effektgrense per planet
Effektgrense for hele systemet
Hvor raskt nye skyer og regn dukker opp
Sekunder mellom oppdateringer av skybevegelsen (færre kan gi hakking)
Skriv feilsøkingsinfo til spillets logg
Som spillets grafikk
Lav
Middels
Høy
Ekstrem
Tilpasset
På
Av
Ja
Nei
Detaljer
Slå effekter av eller på
Detaljer per effekt
Avansert
Værets oppførsel
Ytelse
Feilsøking
Færre detaljer viser færre væreffekter og går bedre på tregere datamaskiner. «Som spillets grafikk» bruker nivået fra forhåndsinnstillingen for grafikkvalitet.
Å slå av en effekt fjerner den ikke med en gang: det som allerede er på himmelen, forsvinner av seg selv (opptil 2 minutter).
* Gjelder fra neste kamp.
Ekstrem viser 50 % mer enn Høy. Hvis spillet hakker, senk detaljene.
Å endre disse innstillingene kan ødelegge moden. Hvis det skjer, trykk på __button__.
Risikabelt: høyere verdier kan få spillet til å hakke.
Advarsel:
normal
partikler
per oppdatering
Denne oversettelsen er laget med KI og er ikke kontrollert av en som har språket som morsmål, så den kan inneholde oversettelsesfeil. Meld gjerne fra om dem på modens side.
Forslag til standardverdiene er velkomne: skriv til oss på modsiden."""

IDIOMAS["sv"] = """Väderdetaljer (alla effekter)
Visa moln
Visa regn
Visa snö
Visa regn som avdunstar innan det når marken
Visa blixtar i åskväder *
Visa vulkaniska askmoln *
Visa blixtar i vulkanisk aska *
Visa elektriska gnistor på metallplaneter
Hur många moln
Hur mycket regn och snö
Hur många åskväder har blixtar *
Hur många vulkaniska askmoln *
Hur mycket blixtar i vulkanisk aska *
Hur många gnistor på metallplaneter *
Visa avancerade inställningar
Hur snabbt molnen driver
Hur ofta moln blir regn
Hur ofta regn blir åskväder
Hur länge regnet varar
Hur länge molnen varar
Effektgräns per planet
Effektgräns för hela systemet
Hur snabbt nya moln och regn dyker upp
Sekunder mellan uppdateringar av molnens rörelse (färre kan ge hackande)
Skriv felsökningsinformation till spelets logg
Som spelets grafik
Låg
Medel
Hög
Extrem
Anpassad
På
Av
Ja
Nej
Detaljer
Slå på eller av effekter
Detaljer per effekt
Avancerat
Vädrets beteende
Prestanda
Felsökning
Färre detaljer visar färre vädereffekter och fungerar bättre på långsammare datorer. ”Som spelets grafik” använder nivån från dina kvalitetsinställningar för grafik.
Att stänga av en effekt tar inte bort den direkt: det som redan finns på himlen försvinner av sig självt (upp till 2 minuter).
* Gäller från din nästa match.
Extrem visar 50 % mer än Hög. Om spelet hackar, sänk detaljerna.
Att ändra dessa inställningar kan förstöra modden. Om det händer, tryck på __button__.
Riskabelt: högre värden kan få spelet att hacka.
Varning:
normal
partiklar
per uppdatering
Den här översättningen är gjord med AI och har inte granskats av en modersmålstalare, så den kan innehålla översättningsfel. Rapportera dem gärna på moddens sida.
Förslag på standardvärdena är välkomna: skriv till oss på modsidan."""

IDIOMAS["fi"] = """Sään yksityiskohdat (kaikki efektit)
Näytä pilvet
Näytä sade
Näytä lumi
Näytä sade, joka haihtuu ennen maahan osumista
Näytä salamat ukkosmyrskyissä *
Näytä tulivuoren tuhkapilvet *
Näytä salamat tulivuoren tuhkassa *
Näytä sähkökipinät metalliplaneetoilla
Pilvien määrä
Sateen ja lumen määrä
Kuinka monessa ukkosmyrskyssä on salamoita *
Tulivuoren tuhkapilvien määrä *
Salamoiden määrä tulivuoren tuhkassa *
Kipinöiden määrä metalliplaneetoilla *
Näytä lisäasetukset
Kuinka nopeasti pilvet liikkuvat
Kuinka usein pilvistä tulee sadetta
Kuinka usein sade muuttuu ukkosmyrskyksi
Kuinka kauan sade kestää
Kuinka kauan pilvet kestävät
Efektiraja planeettaa kohden
Efektiraja koko järjestelmälle
Kuinka nopeasti uusia pilviä ja sadetta ilmestyy
Sekunteja pilvien liikkeen päivitysten välillä (vähemmän voi aiheuttaa nykimistä)
Kirjoita vianetsintätiedot pelin lokiin
Pelin grafiikan mukaan
Matala
Keskitaso
Korkea
Äärimmäinen
Mukautettu
Päällä
Pois
Kyllä
Ei
Yksityiskohdat
Efektit päälle tai pois
Yksityiskohdat efekteittäin
Lisäasetukset
Sään käyttäytyminen
Suorituskyky
Vianetsintä
Vähemmän yksityiskohtia näyttää vähemmän sääefektejä ja toimii paremmin hitaammilla tietokoneilla. "Pelin grafiikan mukaan" käyttää grafiikan laatuasetuksesi tasoa.
Efektin sammuttaminen ei poista sitä heti: se, mikä on jo taivaalla, häviää itsestään (enintään 2 minuutissa).
* Tulee voimaan seuraavassa ottelussa.
Äärimmäinen näyttää 50 % enemmän kuin Korkea. Jos peli nykii, laske yksityiskohtia.
Näiden asetusten muuttaminen voi rikkoa modin. Jos niin käy, paina __button__.
Riskialtis: suuremmat arvot voivat saada pelin nykimään.
Varoitus:
normaali
partikkelia
päivitystä kohden
Tämä käännös on tehty tekoälyllä, eikä äidinkielinen puhuja ole tarkistanut sitä, joten siinä voi olla käännösvirheitä. Ilmoita niistä modin sivulla.
Ehdotukset oletusarvoihin ovat tervetulleita: kerro meille modin sivulla."""

IDIOMAS["tr-TR"] = """Hava durumu ayrıntısı (tüm efektler)
Bulutları göster
Yağmuru göster
Karı göster
Yere ulaşmadan buharlaşan yağmuru göster
Fırtınalarda şimşekleri göster *
Volkanik kül bulutlarını göster *
Volkanik külde şimşekleri göster *
Metal gezegenlerde elektrik kıvılcımlarını göster
Bulut sayısı
Yağmur ve kar miktarı
Kaç fırtınada şimşek olsun *
Volkanik kül bulutu sayısı *
Volkanik küldeki şimşek miktarı *
Metal gezegenlerdeki kıvılcım sayısı *
Gelişmiş seçenekleri göster
Bulutların hareket hızı
Bulutların ne sıklıkla yağmura dönüştüğü
Yağmurun ne sıklıkla fırtınaya dönüştüğü
Yağmurun süresi
Bulutların süresi
Gezegen başına efekt sınırı
Tüm sistem için efekt sınırı
Yeni bulutların ve yağmurun ne kadar hızlı belirdiği
Bulut hareketi güncellemeleri arasındaki saniye (daha az takılmaya yol açabilir)
Sorun giderme bilgilerini oyun günlüğüne yaz
Oyunun grafikleriyle aynı
Düşük
Orta
Yüksek
Aşırı
Özel
Açık
Kapalı
Evet
Hayır
Ayrıntı
Efektleri aç veya kapat
Efekt başına ayrıntı
Gelişmiş
Hava davranışı
Performans
Sorun giderme
Daha düşük ayrıntı daha az hava efekti gösterir ve yavaş bilgisayarlarda daha iyi çalışır. "Oyunun grafikleriyle aynı", grafik kalite ön ayarınızın seviyesini kullanır.
Bir efekti kapatmak onu hemen kaldırmaz: gökyüzünde olan kendiliğinden kaybolur (en fazla 2 dakika).
* Bir sonraki maçınızda geçerli olur.
Aşırı, Yüksek'ten %50 daha fazla gösterir. Oyun takılırsa ayrıntıyı düşürün.
Bu seçenekleri değiştirmek modu bozabilir. Böyle olursa __button__ düğmesine basın.
Riskli: yüksek değerler oyunun takılmasına yol açabilir.
Uyarı:
normal
parçacık
güncelleme başına
Bu çeviri yapay zekâ ile yapıldı ve anadili konuşan biri tarafından kontrol edilmedi, bu yüzden çeviri hataları içerebilir. Lütfen hataları modun sayfasında bildirin.
Varsayılan değerler için öneriler memnuniyetle karşılanır: mod sayfasında bize yazın."""

IDIOMAS["ar"] = """تفاصيل الطقس (كل التأثيرات)
إظهار السحب
إظهار المطر
إظهار الثلج
إظهار المطر الذي يتبخر قبل أن يصل إلى الأرض
إظهار البرق في العواصف *
إظهار سحب الرماد البركاني *
إظهار البرق في الرماد البركاني *
إظهار الشرارات الكهربائية على الكواكب المعدنية
عدد السحب
كمية المطر والثلج
عدد العواصف التي فيها برق *
عدد سحب الرماد البركاني *
كمية البرق في الرماد البركاني *
عدد الشرارات على الكواكب المعدنية *
إظهار الخيارات المتقدمة
سرعة حركة السحب
عدد مرات تحول السحب إلى مطر
عدد مرات تحول المطر إلى عاصفة
مدة المطر
مدة بقاء السحب
حد التأثيرات لكل كوكب
حد التأثيرات للنظام بأكمله
سرعة ظهور سحب ومطر جديدة
الثواني بين تحديثات حركة السحب (القيم الأقل قد تسبب تقطعاً)
كتابة معلومات التشخيص في سجل اللعبة
مطابق لرسومات اللعبة
منخفض
متوسط
عالي
أقصى
يدوي
تشغيل
إيقاف
نعم
لا
التفاصيل
تشغيل التأثيرات أو إيقافها
التفاصيل لكل تأثير
متقدم
سلوك الطقس
الأداء
استكشاف الأخطاء
التفاصيل الأقل تعرض تأثيرات طقس أقل وتعمل بشكل أفضل على الحواسيب الأبطأ. خيار «مطابق لرسومات اللعبة» يستخدم مستوى الإعداد المسبق لجودة الرسومات.
إيقاف تأثير لا يزيله فوراً: ما هو موجود في السماء يختفي وحده (حتى دقيقتين).
* يسري في مباراتك القادمة.
الأقصى يعرض 50% أكثر من العالي. إذا تقطعت اللعبة، خفّض التفاصيل.
تغيير هذه الخيارات قد يعطل التعديل. إذا حدث ذلك، اضغط __button__.
خطر: القيم الأعلى قد تسبب تقطع اللعبة.
تحذير:
عادي
جسيم
لكل تحديث
هذه الترجمة مصنوعة بالذكاء الاصطناعي ولم يراجعها متحدث أصلي، لذلك قد تحتوي على أخطاء في الترجمة. يرجى الإبلاغ عنها في صفحة التعديل.
نرحب باقتراحات تغيير القيم الافتراضية: أخبرنا في صفحة التعديل."""

IDIOMAS["ja"] = """天候の詳細度(すべてのエフェクト)
雲を表示
雨を表示
雪を表示
地面に届く前に蒸発する雨を表示
嵐の雷を表示 *
火山灰の雲を表示 *
火山灰の中の雷を表示 *
金属惑星の電気火花を表示
雲の量
雨と雪の量
雷を伴う嵐の数 *
火山灰の雲の数 *
火山灰の中の雷の量 *
金属惑星の火花の数 *
詳細設定を表示
雲の流れる速さ
雲が雨になる頻度
雨が嵐になる頻度
雨の長さ
雲の持続時間
惑星ごとのエフェクト上限
システム全体のエフェクト上限
新しい雲と雨の出現速度
雲の移動更新の間隔(秒)(短いとカクつくことがあります)
トラブルシューティング情報をゲームログに書き込む
ゲームのグラフィックに合わせる
低
中
高
最高
カスタム
オン
オフ
はい
いいえ
詳細度
エフェクトのオン/オフ
エフェクトごとの詳細度
詳細設定
天候の挙動
パフォーマンス
トラブルシューティング
詳細度を下げると天候エフェクトが減り、遅いPCでも軽く動きます。「ゲームのグラフィックに合わせる」はグラフィックの品質プリセットのレベルを使います。
エフェクトをオフにしてもすぐには消えません。すでに空にあるものは自然に消えていきます(最大2分)。
* 次の対戦から有効になります。
最高は高より50%多く表示します。ゲームがカクつく場合は詳細度を下げてください。
これらの設定を変更するとMODが壊れることがあります。その場合は __button__ を押してください。
注意:値を上げるとゲームがカクつくことがあります。
警告:
標準
パーティクル
更新ごと
この翻訳はAIによるもので、ネイティブスピーカーによる確認を受けていないため、翻訳の誤りが含まれている可能性があります。誤りはMODのページで報告してください。
初期値への提案を歓迎します:MODのページでお知らせください。"""

IDIOMAS["ko"] = """날씨 세부 수준 (모든 효과)
구름 표시
비 표시
눈 표시
땅에 닿기 전에 증발하는 비 표시
폭풍의 번개 표시 *
화산재 구름 표시 *
화산재 속 번개 표시 *
금속 행성의 전기 불꽃 표시
구름 양
비와 눈의 양
번개가 치는 폭풍 수 *
화산재 구름 수 *
화산재 속 번개 양 *
금속 행성의 불꽃 수 *
고급 옵션 표시
구름이 흘러가는 속도
구름이 비가 되는 빈도
비가 폭풍이 되는 빈도
비가 내리는 시간
구름이 유지되는 시간
행성당 효과 한도
전체 시스템 효과 한도
새 구름과 비가 나타나는 속도
구름 이동 업데이트 간격(초) (짧으면 끊길 수 있음)
문제 해결 정보를 게임 로그에 기록
게임 그래픽에 맞춤
낮음
보통
높음
최고
사용자 설정
켜기
끄기
예
아니요
세부 수준
효과 켜기/끄기
효과별 세부 수준
고급
날씨 동작
성능
문제 해결
세부 수준이 낮으면 날씨 효과가 줄어들고 느린 컴퓨터에서 더 잘 작동합니다. "게임 그래픽에 맞춤"은 그래픽 품질 프리셋의 수준을 사용합니다.
효과를 꺼도 바로 사라지지 않습니다. 이미 하늘에 있는 것은 저절로 사라집니다(최대 2분).
* 다음 경기부터 적용됩니다.
최고는 높음보다 50% 더 많이 표시합니다. 게임이 끊기면 세부 수준을 낮추세요.
이 옵션을 변경하면 모드가 망가질 수 있습니다. 그런 경우 __button__ 버튼을 누르세요.
위험: 값을 높이면 게임이 끊길 수 있습니다.
경고:
기본
입자
업데이트당
이 번역은 AI로 만들어졌으며 원어민의 검토를 거치지 않아 번역 오류가 있을 수 있습니다. 오류는 모드 페이지에 알려 주세요.
기본값에 대한 제안을 환영합니다: 모드 페이지에 알려 주세요."""

IDIOMAS["zh-CN"] = """天气细节(所有效果)
显示云
显示雨
显示雪
显示落地前蒸发的雨
显示风暴中的闪电 *
显示火山灰云 *
显示火山灰中的闪电 *
显示金属星球上的电火花
云的数量
雨雪量
有闪电的风暴数量 *
火山灰云数量 *
火山灰中的闪电数量 *
金属星球上的火花数量 *
显示高级选项
云的飘动速度
云变成雨的频率
雨变成风暴的频率
降雨持续时间
云的持续时间
每个星球的效果上限
整个星系的效果上限
新云和新雨出现的速度
云移动更新间隔(秒)(越短可能越卡顿)
将故障排查信息写入游戏日志
与游戏图像一致
低
中等
高
极高
自定义
打开
关闭
是
否
细节
开关效果
各效果细节
高级
天气行为
性能
故障排查
细节越低,天气效果越少,在较慢的电脑上运行更流畅。“与游戏图像一致”会使用你的图像质量预设等级。
关闭效果不会立即移除:已经在天空中的会自行消散(最多 2 分钟)。
* 下一场对局生效。
极高比高多显示 50%。如果游戏卡顿,请降低细节。
更改这些选项可能会使模组出错。如果发生这种情况,请点击 __button__。
有风险:数值越高,游戏越可能卡顿。
警告:
默认
粒子
每次更新
此翻译由 AI 完成,未经母语者审校,因此可能包含翻译错误。请在模组页面报告。
欢迎对默认值提出建议:请在模组页面告诉我们。"""

IDIOMAS["zh-TW"] = """天氣細節(所有效果)
顯示雲
顯示雨
顯示雪
顯示落地前蒸發的雨
顯示暴風雨中的閃電 *
顯示火山灰雲 *
顯示火山灰中的閃電 *
顯示金屬星球上的電火花
雲的數量
雨雪量
有閃電的暴風雨數量 *
火山灰雲數量 *
火山灰中的閃電數量 *
金屬星球上的火花數量 *
顯示進階選項
雲的飄動速度
雲變成雨的頻率
雨變成暴風雨的頻率
降雨持續時間
雲的持續時間
每顆星球的效果上限
整個星系的效果上限
新雲和新雨出現的速度
雲移動更新間隔(秒)(越短可能越卡頓)
將疑難排解資訊寫入遊戲記錄
與遊戲畫面一致
低
中等
高
極高
客製化
開啟
關閉
是
否
細節
開關效果
各效果細節
進階
天氣行為
效能
疑難排解
細節越低,天氣效果越少,在較慢的電腦上執行更順暢。「與遊戲畫面一致」會使用你的畫質預設等級。
關閉效果不會立即移除:已經在天空中的會自行消散(最多 2 分鐘)。
* 下一場對戰生效。
極高比高多顯示 50%。如果遊戲卡頓,請降低細節。
變更這些選項可能會使模組出錯。如果發生這種情況,請按下 __button__。
有風險:數值越高,遊戲越可能卡頓。
警告:
預設
粒子
每次更新
此翻譯由 AI 完成,未經母語人士審閱,因此可能包含翻譯錯誤。請在模組頁面回報。
歡迎對預設值提出建議:請在模組頁面告訴我們。"""


def main():
    claves = CLAVES.split("\n")
    assert len(claves) == len(set(claves)), "claves repetidas"
    for c in claves:
        assert "'" not in c and '"' not in c, "clave con comillas (rompe data-bind): " + c
        assert ";;" not in c and "::" not in c, "clave con separador de i18n: " + c
    os.makedirs(DESTINO, exist_ok=True)
    for f in os.listdir(DESTINO):
        if f.endswith(".json"):
            os.remove(os.path.join(DESTINO, f))
    for idioma, bloque in sorted(IDIOMAS.items()):
        lineas = bloque.split("\n")
        assert len(lineas) == len(claves), "%s: %d lineas, se esperan %d" % (idioma, len(lineas), len(claves))
        datos = {}
        for c, t in zip(claves, lineas):
            assert t.strip(), "%s: traduccion vacia para %r" % (idioma, c)
            assert ("__button__" in c) == ("__button__" in t), "%s: falta __button__ en %r" % (idioma, c)
            assert c.count("*") == t.count("*") or not c.endswith("*"), "%s: falta * en %r" % (idioma, c)
            datos[c] = {"message": t}
        # Nombre en minusculas: Linux/macOS distinguen mayusculas (opciones.js pide c.toLowerCase()).
        with open(os.path.join(DESTINO, idioma.lower() + ".json"), "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
    print("%d idiomas x %d textos -> %s" % (len(IDIOMAS), len(claves), DESTINO))


if __name__ == "__main__":
    main()
