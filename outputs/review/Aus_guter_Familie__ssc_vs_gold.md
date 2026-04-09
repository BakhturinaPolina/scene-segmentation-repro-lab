# SSC vs Ground Truth — Aus guter Familie

- **Model:** SSC (bert-base-german-cased, 1 epoch, frozen embeddings)
- **Source XMI:** `outputs/ssc/2026-04-05/baseline_bert/stss_test_2/Aus guter Familie.xmi.zip`
- **Sentences:** 5,025
- **Gold scenes:** 219  |  Gold borders: 219
- **Predicted scenes:** 1  |  Predicted borders: 1

| TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|
| 1 | 0 | 218 | 1.000 | 0.005 | 0.009 |

---

## Scene boundary comparison

Only sentences that are gold BORDER or predicted BORDER are shown (to keep the file readable).
All others are NOBORDER/NOBORDER matches (omitted).

| # | Sentence text (first 120 chars) | Gold | Predicted |
|---|---|---|---|
| 0 | Gabriele Reuter Aus guter Familie    Erster Teil I  Breit und hell fiel ein Strahl der Frühlingssonne durch das verstaub | **BORDER** | **BORDER** |
| 74 | Kaum war der Gottesdienst zu Ende, so umarmte Frau Heidling ihre Tochter mit einer Art von kummervoller Leidenschaft, di | **BORDER** | NOBORDER ⚠ |
| 82 | Ihr Bruder, der Abiturient, lief aufmerksam nochmals in die Kirche zurück, ihr vergessenes Bouquet zu holen, während all | **BORDER** | NOBORDER ⚠ |
| 89 | Agathe ging allein ins Haus. | **BORDER** | NOBORDER ⚠ |
| 145 | Agathe saß bei Tisch vor einem Teller, der mit gelben Schlüsselblumen umkränzt war, zwischen Vater und Mutter. | **BORDER** | NOBORDER ⚠ |
| 168 | Inzwischen schlug schon Pastor Kandler an sein Glas. | **BORDER** | NOBORDER ⚠ |
| 200 | In diesem Augenblick wurde noch ein Geschenk für Agathe abgegeben. | **BORDER** | NOBORDER ⚠ |
| 271 | Später, als die Erwachsenen in allen Sofaecken des Pfarrhauses ihr Verdauungsschläfchen  hielten – man war ein bißchen h | **BORDER** | NOBORDER ⚠ |
| 332 | II Die Freundschaft zwischen Agathe Heidling und Eugenie Wutrow bestand schon sehr lange – seitdem sie eines Morgens mit | **BORDER** | NOBORDER ⚠ |
| 357 | Eines Sonntags Nachmittags saßen die kleinen Freundinnen auf dem untersten Ast des niedrigen alten Taxusbaumes in Wutrow | **BORDER** | NOBORDER ⚠ |
| 384 | Als Mama kam, ihr einen Gutenachtkuß zu geben, drehte sie hastig den Kopf nach der Wand und wühlte das heiße Gesicht in  | **BORDER** | NOBORDER ⚠ |
| 392 | »Frau Wutrow schickte schon zweimal. | **BORDER** | NOBORDER ⚠ |
| 409 | Unterwegs traf sie eine Bürgerschülerin, die sie kannte. | **BORDER** | NOBORDER ⚠ |
| 415 | Auf einem freien Platz mit Blumenbeeten setzte sie sich auf eine der eisernen Ketten, die, zwischen Steinpfeilern herabh | **BORDER** | NOBORDER ⚠ |
| 435 | Dann ging sie mit der Bürgerschülerin, die schon um zwölf Uhr zu Mittag gegessen hatte, trank mit ihr Kaffee und versuch | **BORDER** | NOBORDER ⚠ |
| 446 | Aber das Nachhausekommen ...! | **BORDER** | NOBORDER ⚠ |
| 459 | Als sie zaghaft und ganz leise klingelte, riß Walter die Thür auf, lachte laut und rief: »Da ist sie ja, die Range!« | **BORDER** | NOBORDER ⚠ |
| 472 | Als die schauerliche Strafe zu Ende war, wankte Frau Heidling erschöpft in ihr Schlafzimmer und sank keuchend und weinen | **BORDER** | NOBORDER ⚠ |
| 478 | Das Mädchen lag in der Logierstube auf den Dielen und schrie noch immer, schluckend und schluchzend, sie konnte die Töne | **BORDER** | NOBORDER ⚠ |
| 486 | Ihre Haltung wurde schlaff, in ihrem Gesichtchen zeigte sich ein verdrießlicher, müder Zug. | **BORDER** | NOBORDER ⚠ |
| 494 | III Frau Heidling hegte das unbestimmte Ideal eines innigen Verhältnisses zwischen einer Mutter und ihrer einzigen Tocht | **BORDER** | NOBORDER ⚠ |
| 521 | Da sie in ihrem früheren Wohnort, der Hauptstadt der Provinz, mannigfache Beziehungen unterhielt, wandte sie sich dorthi | **BORDER** | NOBORDER ⚠ |
| 527 | Agathe bewohnte mit Eugenie denselben Schlafsaal. | **BORDER** | NOBORDER ⚠ |
| 560 | Welches Glück empfand Agathe daher, als Eugenie sie eines Abends in ihr Kämmerchen herüberholte und mit Chokolade fütter | **BORDER** | NOBORDER ⚠ |
| 632 | Plötzlich, nach kurzer Zeit, kam sie wieder zur Besinnung, geweckt von einem großen,  brennenden Sehnsuchtsgefühl, welch | **BORDER** | NOBORDER ⚠ |
| 638 | Agathe mußte immer aufs neue staunen, wie stark und sicher Eugenie ihre große Leidenschaft in ihrem Herzen verschloß, un | **BORDER** | NOBORDER ⚠ |
| 692 | Auch Agathe war maßlos aufgeregt. | **BORDER** | NOBORDER ⚠ |
| 711 | In Furcht und Grauen schlich Agathe durch die dunklen Korridore des großen Hauses, eine Treppe hinab, eine andere hinauf | **BORDER** | NOBORDER ⚠ |
| 722 | IV  Sommerferien auf dem Lande ... Schwebt nicht ein Duft von Rosen und Erdbeeren vorüber? | **BORDER** | NOBORDER ⚠ |
| 748 | Und niemals hätte sie sich entschließen können, Eugenie zu erzählen, daß der kühne Bursche einmal, als sie beide allein  | **BORDER** | NOBORDER ⚠ |
| 754 | Während Agathe glühend und außer Atem ihre aufgelösten Zöpfe wieder flocht und feststeckte, fühlte sie sich sehr tugendh | **BORDER** | NOBORDER ⚠ |
| 764 | Martin betrug sich in den nächsten Tagen nicht wie ein unglücklich Liebender, auch nicht zudringlich, sondern flegelhaft | **BORDER** | NOBORDER ⚠ |
| 770 | V  Herr Heidling war, während die Erziehung seiner Tochter nach der Pensionszeit bei Pastor Kandler gewissermaßen die le | **BORDER** | NOBORDER ⚠ |
| 804 | Zu den köstlichsten Andenken vergangener Zeiten begrub Agathe nun ihr Spielzeug, das sie in eine Kiste sorgsam mit Kamph | **BORDER** | NOBORDER ⚠ |
| 817 | Im Gegensatz zu der Mattigkeit und Schlafsucht, gegen die Agathe während ihrer Pensionszeit beständig zu kämpfen gehabt  | **BORDER** | NOBORDER ⚠ |
| 830 | In Agathes wohlig durchheiztem Erkerzimmer feierte sie ihren siebzehnten Geburtstag, umgeben von blühenden Rosen und ros | **BORDER** | NOBORDER ⚠ |
| 963 | VI  In dem Leitfaden fürs Leben: »Des Weibes Wirken als Jungfrau, Gattin und Mutter« stand zu lesen: Der erste Ball bede | **BORDER** | NOBORDER ⚠ |
| 980 | Martin Greffinger kam, um den Juristenball mitzumachen, aus der nicht sehr entfernten Universitätsstadt herüber. | **BORDER** | NOBORDER ⚠ |
| 989 | Denn es entstand infolge dessen zwischen ihrem Vater und Martin ein Streit, der, bei Kaffee und Kuchen begonnen, die gem | **BORDER** | NOBORDER ⚠ |
| 1000 | Als sie ihre Toilette beendet hatte, mußte sie sich wie auf einer Drehscheibe langsam vor der versammelten Familie und d | **BORDER** | NOBORDER ⚠ |
| 1006 | Einen Wagen hatte man nicht nehmen wollen, der Weg war ja gar nicht weit. | **BORDER** | NOBORDER ⚠ |
| 1012 | Da standen die jungen Mädchen in langen Reihen und in kleinen Gruppen – wie ein riesenhaftes Beet zartabgetönter Frühlin | **BORDER** | NOBORDER ⚠ |
| 1029 | Agathe erstaunte über die Einfachheit von Eugenies Anzug, den, trotz aller Bitten, keine Freundin vorher hatte sehen dür | **BORDER** | NOBORDER ⚠ |
| 1046 | Als Agathe die Fülle eleganter Erscheinungen sah, verlor sie plötzlich jede Hoffnung auf Erfolg. | **BORDER** | NOBORDER ⚠ |
| 1077 | Da wurde sie plötzlich bemerkt und alles wunderte sich, daß sie nicht tanzte, sie war doch unstreitig eines der hübsches | **BORDER** | NOBORDER ⚠ |
| 1082 | Als erinnere sich jeder Herr eines unverzeihlichen Vergehens, wurde Agathe nun fortwährend zu Extratouren geholt. | **BORDER** | NOBORDER ⚠ |
| 1089 | Es war ihr eine Erlösung, als Onkel Gustav sie einmal holte. | **BORDER** | NOBORDER ⚠ |
| 1094 | Er war auch ausgezeichnet geschmackvoll gekleidet – niemand wußte, wie er das bei seinen spärlichen Einnahmen möglich ma | **BORDER** | NOBORDER ⚠ |
| 1100 | Als das Souper begann, wurde Agathe von ihrem Herrn gefragt, ob es ihr recht sei, wenn sie mit ihrer Freundin Eugenie ei | **BORDER** | NOBORDER ⚠ |
| 1125 | Dem Souper folgte der Kotillon. | **BORDER** | NOBORDER ⚠ |
| 1130 | In einer der Pausen des vielverschlungenen Tanzes winkte Mama sie plötzlich heran. | **BORDER** | NOBORDER ⚠ |
| 1142 | Sie schlief sehr unruhig in der Nacht nach ihrem ersten Ball; der Kopf war ihr dumpf und  benommen, sie faßte den Entsch | **BORDER** | NOBORDER ⚠ |
| 1144 | VII  Ein großer Kampf war in Sieg und Glück beendet, ein deutscher Kaiser war glorreich gekrönt, dem Traum einer Nation  | **BORDER** | NOBORDER ⚠ |
| 1161 | Ein anderes Mal fand Agathe auf dem Schreibtisch ihrer Freundin ein Buch mit roter Inschrift auf schwarzem Deckel. | **BORDER** | NOBORDER ⚠ |
| 1165 | Dann wieder konnte Martin übermütig bis zur Tollheit sein, und trieb, wenn er kam, nur  Neckereien und Scherze mit den b | **BORDER** | NOBORDER ⚠ |
| 1185 | »Lord Byron in Newstead Abbey,« las der Regierungsrat aus dem Kataloge hervor. | **BORDER** | NOBORDER ⚠ |
| 1203 | Am nächsten Morgen ging sie wieder in die Ausstellung. | **BORDER** | NOBORDER ⚠ |
| 1206 | In der Woche war die Ausstellung meist leer und niemand konnte Agathe beobachten. | **BORDER** | NOBORDER ⚠ |
| 1240 | Wenige Tage vorher, bei einem gemeinsamen Spaziergang, der mit Kaffeetrinken in einem öffentlichen Garten endete, hatte  | **BORDER** | NOBORDER ⚠ |
| 1242 | Sobald Agathe mit der Braut allein war, konnte sie nicht unterlassen, die Bemerkung hinzuwerfen: »Ich glaubte, es wäre M | **BORDER** | NOBORDER ⚠ |
| 1247 | Ein Gefühl von Abneigung, von Verachtung gegen die neue Schwägerin peinigte Agathe, während ihr alle Bekannte Glück wüns | **BORDER** | NOBORDER ⚠ |
| 1256 | VIII  Zur Zeit, als die Kinder noch klein waren, hatte Frau Heidling nach dem Tode ihrer Schwiegermutter deren Köchin in | **BORDER** | NOBORDER ⚠ |
| 1276 | »Fräulein,« sagte Wiesing eines Morgens, als sie Agathe warmes Wasser in ihr Schlafzimmer brachte, und dabei stand sie m | **BORDER** | NOBORDER ⚠ |
| 1336 | Zuerst ging sie zu einem Schlosser und kaufte einen Riegel mit großen Krampen. | **BORDER** | NOBORDER ⚠ |
| 1350 | So quälte sie sich den ganzen Tag hin und wünschte, Walter möge so viel Dienst haben, daß eine Unterredung mit ihm unmög | **BORDER** | NOBORDER ⚠ |
| 1352 | Nachmittag kam Eugenie auf eine Viertelstunde. | **BORDER** | NOBORDER ⚠ |
| 1363 | Walter kam ins Zimmer zurück. | **BORDER** | NOBORDER ⚠ |
| 1387 | Später am Abend fragte sie Wiesing, ob sie nicht zu ihren Eltern gehen könne, ob sie nicht sagen wolle, ihre Mutter wäre | **BORDER** | NOBORDER ⚠ |
| 1395 | IX  Agathe war nun schon zwanzig Jahre alt. | **BORDER** | NOBORDER ⚠ |
| 1416 | So fühlte Frau Heidling auch jetzt, daß eine Zerstreuung, ein Wechsel der Eindrücke für Agathe heilsam sein werde. | **BORDER** | NOBORDER ⚠ |
| 1426 | Schon lange trug sie in Gesellschaften keine Glaceehandschuhe mehr, sondern Halbseidene, und auf Spaziergängen sogar Bau | **BORDER** | NOBORDER ⚠ |
| 1451 | Frau von Woszenska erwartete Agathe auf dem Bahnhof und schleppte sie gleich zu ihrem Manne ins Atelier. | **BORDER** | NOBORDER ⚠ |
| 1466 | Frau von Woszenska hatte ihr Atelier in der Wohnung, um neben der Kunst den Haushalt überwachen zu können. | **BORDER** | NOBORDER ⚠ |
| 1474 | Der kleine Sohn Michel kam aus der Schule. | **BORDER** | NOBORDER ⚠ |
| 1499 | Nannte Woszenski seine Frau bei ihrem Vornamen, so fand er es entzückend, daß die ungewöhnliche Person, deren Bewegungen | **BORDER** | NOBORDER ⚠ |
| 1503 | Am Abend, während das Ehepaar mit dem jungen Gast in ihrem Wohnzimmer saß, von dessen Decke eine Messing-Lampe aus einer | **BORDER** | NOBORDER ⚠ |
| 1508 | Agathe lag lange wach auf dem ungewohnten Lager, in dem ihr noch fremden Raum. | **BORDER** | NOBORDER ⚠ |
| 1511 | »Das Kind soll die alte Hauptmann Gärtner besuchen, ihre Mutter kennt sie von früher. | **BORDER** | NOBORDER ⚠ |
| 1531 | Während des Besuches saß sie nach einigen von ihr beantworteten Fragen still und hörte auf Frau von Woszenskas Gespräch  | **BORDER** | NOBORDER ⚠ |
| 1552 | Er kam aus der höheren Etage und traf mit ihnen auf der Treppe zusammen. | **BORDER** | NOBORDER ⚠ |
| 1564 | X  Als Agathe in ihr Gastzimmerchen bei Woszenskis zurückkehrte, schloß sie eilig die Thür hinter sich. | **BORDER** | NOBORDER ⚠ |
| 1634 | In einem Konzert sah Agathe ihn unerwartet dicht vor sich sitzen. | **BORDER** | NOBORDER ⚠ |
| 1661 | Woszenski zeichnete Agathe mehrere Male als Studie zu seiner Novize. | **BORDER** | NOBORDER ⚠ |
| 1672 | – Frau von Woszenska bekam eines ihrer Bilder von der Münchener Ausstellung zurück. | **BORDER** | NOBORDER ⚠ |
| 1681 | Agathe wurde es viel leichter, ihre Gedanken Woszenskis auszusprechen als ihren Eltern. | **BORDER** | NOBORDER ⚠ |
| 1706 | Einmal noch während ihres Aufenthaltes bei Woszenskis sah Agathe Lutz von weitem in einer menschenleeren Straße. | **BORDER** | NOBORDER ⚠ |
| 1714 | Als fünf Wochen verflossen waren, reiste sie nach Haus zurück. | **BORDER** | NOBORDER ⚠ |
| 1715 | XI  »Weißt Du, Agathe, wenn diese Woszenskis Dir so viel interessanter sind, als Deine eigenen Eltern, dann ist es am be | **BORDER** | NOBORDER ⚠ |
| 1720 | Frau Heidling kam eines Abends in ihrer Tochter Schlafzimmer. | **BORDER** | NOBORDER ⚠ |
| 1749 | Nachdem Agathe an Frau von Woszenski geschrieben hatte, wartete sie täglich in atemloser Spannung auf deren Antwort. | **BORDER** | NOBORDER ⚠ |
| 1760 | Am 5. September las Agathe frühmorgens in der Zeitung eine Notiz: Fräulein Daniel war als Naive für das Theater in M. | **BORDER** | NOBORDER ⚠ |
| 1775 | Zuerst hörte sie bei Wutrows von ihm reden. | **BORDER** | NOBORDER ⚠ |
| 1800 | XII  Eugenies und Walters Hochzeit wurde ein großes Fest, mit Polterabendaufführungen und all der sinnigen Unruhe, die d | **BORDER** | NOBORDER ⚠ |
| 1826 | Nach dem Diner nahm Eugenie ihren Kranz vom Haupt und setzte ihn Onkel Gustav auf. | **BORDER** | NOBORDER ⚠ |
| 1838 | Nachdem das junge Paar abgefahren war, zog sich Agathe in Eugenies Schlafzimmer zurück und blieb dort mit dem ausgedient | **BORDER** | NOBORDER ⚠ |
| 1841 | Die Gesellschaft hatte sich zerstreut, die Fremderen waren verschwunden. | **BORDER** | NOBORDER ⚠ |
| 1845 | Jenseits des langen Korridors, nach dem Garten hinaus lag Eugenies Boudoir. | **BORDER** | NOBORDER ⚠ |
| 1856 | Nach der Hochzeitsreise zogen die jungen Heidlings in die obere Etage des Wutrow'schen Hauses, die für sie mit modernen  | **BORDER** | NOBORDER ⚠ |
| 1892 | Inzwischen wurde die Begegnung mit ihm, die das Mädchen sich zu jeder Stunde fieberhaft wünschte, Eugenie zu teil. | **BORDER** | NOBORDER ⚠ |
| 1918 | XIII  Gegen Ende des Winters veranstaltete die Gesellschaft von M., hauptsächlich auf Frau Eugenies Betreiben, einen gro | **BORDER** | NOBORDER ⚠ |
| 1938 | Vor einer Weile hatte sie im Vorzimmer Lutz und Fräulein Daniel bemerkt, die sich von einigen Schauspielern verabschiede | **BORDER** | NOBORDER ⚠ |
| 1961 | Agathe wurde von andern Tänzern geholt, schlenderte mit Freundinnen in den Räumen umher, nahm unter Eugenies Schutz, die | **BORDER** | NOBORDER ⚠ |
| 1964 | »Traumwandlerin,« rief Eugenie sie an, »sollen wir Dich in unsern Wagen nach Haus schicken? | **BORDER** | NOBORDER ⚠ |
| 1973 | Lutz hatte Agathe angesprochen – im Tabaksqualm des Restaurants – zwischen zwei und drei Uhr morgens – und sie gefragt,  | **BORDER** | NOBORDER ⚠ |
| 1976 | Agathe mußte am andern Morgen eine ordentliche Strafpredigt über sich ergehen lassen. | **BORDER** | NOBORDER ⚠ |
| 1990 | »Agathe, kommst Du mit, ich suche Walter,« sagte Eugenie, als dieser Zeitpunkt eingetreten war, faßte ihre Schwägerin un | **BORDER** | NOBORDER ⚠ |
| 1992 | Lutz sprach viel und lebhaft, Agathe hatte nur halblaute, kindische Töne als Antwort, wie ein furchtsames kleines Mädche | **BORDER** | NOBORDER ⚠ |
| 2011 | »Gestern bin ich in den Anlagen der Daniel begegnet«, sagte Referendar Dürnheim, »ist die aber abgefallen! | **BORDER** | NOBORDER ⚠ |
| 2030 | Es kam ein Sonntag, an dem Eugenie in der Breiten Straße mit Herrn von Lutz verabredete, ihn zum Kaffee bei sich zu erwa | **BORDER** | NOBORDER ⚠ |
| 2039 | – – Schon standen die Mokkatäßchen geleert auf Eugenies silberglänzendem Kaffeetisch – der Hauptmann und der Fähnrich ra | **BORDER** | NOBORDER ⚠ |
| 2045 | Er hatte sein Bild nach Paris absenden wollen, der Tischler ließ ihn im Stich – es war der letzte Termin zur Annahme bei | **BORDER** | NOBORDER ⚠ |
| 2054 | Sie bereitete sich nicht vor – sie änderte nichts an ihrem Anzug. | **BORDER** | NOBORDER ⚠ |
| 2062 | – –. | **BORDER** | NOBORDER ⚠ |
| 2087 | Der Maler und Heidlings wurden aufgefordert, zum Abend zu bleiben. | **BORDER** | NOBORDER ⚠ |
| 2099 | Frau Heidling sagte ihrer Tochter eines Abends sanft und schonend: »Liebes Kind – Du bist ein verständiges Mädchen – Pap | **BORDER** | NOBORDER ⚠ |
| 2100 | Onkel Gustav aber besuchte Lutz in seinem Atelier und machte Agathe eine ausführliche Beschreibung von der silberblauen  | **BORDER** | NOBORDER ⚠ |
| 2110 | XIV  Heidlings hörten lange nichts von Martin Greffinger. | **BORDER** | NOBORDER ⚠ |
| 2130 | Als sie ihn einmal auf der Straße traf und er mit eiligem Gruß an ihr vorüber wollte, stand sie still, gab ihm die Hand  | **BORDER** | NOBORDER ⚠ |
| 2135 | Papa und Mama waren verreist, sie wollten das Osterfest in Bornau zubringen. | **BORDER** | NOBORDER ⚠ |
| 2146 | Es war ein trüber Abend, feiner Regen ging nieder. | **BORDER** | NOBORDER ⚠ |
| 2224 | Agathe hielt das Bündel verbotener Bücher in den Händen und blickte beklommen auf sie nieder. | **BORDER** | NOBORDER ⚠ |
| 2273 | Einmal schrak sie jäh zusammen – sie glaubte, es überraschte sie jemand. | **BORDER** | NOBORDER ⚠ |
| 2289 | XV  In der Charwoche fuhr Agathe nach Bornau. | **BORDER** | NOBORDER ⚠ |
| 2303 | Es war schon später Nachmittag. | **BORDER** | NOBORDER ⚠ |
| 2322 | Als die hohe, glasbedeckte Halle erreicht war, sonderte sich ein Teil der Menschen nach dem  Ausgange ab. | **BORDER** | NOBORDER ⚠ |
| 2360 | Erschrocken ließ sie ihn los, als habe sie etwas Unrechtes gethan, weil die Thür aufgerissen wurde. | **BORDER** | NOBORDER ⚠ |
| 2431 | XVI  Frau Heidling empfing ihre Tochter auf dem Bahnhof. | **BORDER** | NOBORDER ⚠ |
| 2442 | Agathe hörte beim Abendessen ein langes und breites Gespräch: Cousine Mimi wollte Diakonissin werden, aber die Eltern wü | **BORDER** | NOBORDER ⚠ |
| 2444 | Mimi begleitete sie zu ihrem Zimmer – sie hatte es auch während jenes fröhlichen Sommeraufenthaltes als Pensionärin bewo | **BORDER** | NOBORDER ⚠ |
| 2452 | Agathe mußte sich ruhig verhalten, denn nebenan, nahe der Thür, schliefen die Eltern. | **BORDER** | NOBORDER ⚠ |
| 2460 | »Hast Du Kopfweh?« | **BORDER** | NOBORDER ⚠ |
| 2485 | Mit einer ruhigen, tröstenden Stimme sagte sie: »Du legst Dich still hin – dann wird sich's schon beruhigen. | **BORDER** | NOBORDER ⚠ |
| 2510 | Auf dem Tischchen neben ihr standen Blumen, Flieder und Kamelien. | **BORDER** | NOBORDER ⚠ |
| 2520 | Eugenie schrieb einen langen, teilnehmenden Brief. | **BORDER** | NOBORDER ⚠ |
| 2527 | – – Nun hatte sie auch diese Prüfung bestanden ... | **BORDER** | NOBORDER ⚠ |
| 2538 | Aber in einer Nacht, als Mama ihr zu trinken gab, weil der Mund ihr sehr trocken war, fiel er sie plötzlich wieder an. | **BORDER** | NOBORDER ⚠ |
| 2566 | Der alte Hausarzt schien am folgenden Morgen durch die Schilderung des nächtlichen Schreckens nicht sonderlich beunruhig | **BORDER** | NOBORDER ⚠ |
| 2585 | Endlich erschien auch der berühmte, erwartete und gefürchtete Gast. | **BORDER** | NOBORDER ⚠ |
| 2631 | Plötzlich hörten alle das tiefe, behagliche Lachen des alten Sanitätsrats. | **BORDER** | NOBORDER ⚠ |
| 2649 | Zweiter Teil I  Eugenie war nach der Geburt ihres ersten Kindes immer noch hübscher geworden. | **BORDER** | NOBORDER ⚠ |
| 2700 | »Mit Agathe ist rein nichts mehr anzufangen,« erklärte Eugenie. | **BORDER** | NOBORDER ⚠ |
| 2708 | Als das Mädchen zu den jungen Heidlings kam und Wölfchen aus dem Wagen heben wollte, um mit ihm zu spielen, riß Eugenie  | **BORDER** | NOBORDER ⚠ |
| 2712 | Abends in ihrem Zimmer lag Agathe halbe Stunden lang auf den Knieen und betete mit Schluchzen und Weinen, der Herr möge  | **BORDER** | NOBORDER ⚠ |
| 2805 | Nach dem Tanzfest beim Oberpräsidenten verwies er ihr strenge, sich in Gesellschaft auffällig zu benehmen. | **BORDER** | NOBORDER ⚠ |
| 2873 | Als er zum Essen nach Haus kam, versuchten die beiden Frauen, ihn auf jede Weise zu erheitern. | **BORDER** | NOBORDER ⚠ |
| 2879 | II  Der Kreis von Agathes Freundinnen hatte sich im letzten Jahre recht gelichtet. | **BORDER** | NOBORDER ⚠ |
| 2912 | Es war ein heißer Sommerabend, kurz vor Beginn der großen Ferien. | **BORDER** | NOBORDER ⚠ |
| 2993 | Sie fühlte ein leichtes Bangen, weil sie sich des Abends niemals allein auf der Straße befand. | **BORDER** | NOBORDER ⚠ |
| 3023 | Vor Agathe gingen zwei Frauen die Straße entlang. | **BORDER** | NOBORDER ⚠ |
| 3033 | Sie hatte nun auf einen daherkommenden Pferdebahnwagen zu achten, in dem sie die letzte Hälfte ihres Weges zurücklegen w | **BORDER** | NOBORDER ⚠ |
| 3131 | III Fröhlich spiegelte sich der Sonnenschein auf der Glatze des Landrats, als er den Hut lüftete, um den heranbrausenden | **BORDER** | NOBORDER ⚠ |
| 3165 | – Landrat Raikendorf zeigte den Damen die schönen geschnitzten alten Schränke, die zum Inventar der Wohnung gehörten, di | **BORDER** | NOBORDER ⚠ |
| 3181 | Im Sommersonnenschein – Sieg über ein kühles, müdes Männerherz. | **BORDER** | NOBORDER ⚠ |
| 3197 | IV Hatte sich Agathe früher die Ehe unter dem Bilde eines jungen Paares vorgestellt, das Schulter an Schulter gelehnt, v | **BORDER** | NOBORDER ⚠ |
| 3258 | Die Hausthür war schon verschlossen. | **BORDER** | NOBORDER ⚠ |
| 3268 | Agathe lief die Treppen hinauf. | **BORDER** | NOBORDER ⚠ |
| 3307 | In der Frühe, als sie das Wohnzimmer betrat, erinnerte sie sich plötzlich an den Abend, an dem ihr Martin Greffinger die | **BORDER** | NOBORDER ⚠ |
| 3336 | Die Unterredung zwischen dem Regierungsrat und Raikendorf dauerte sehr lange. | **BORDER** | NOBORDER ⚠ |
| 3372 | Am Abend aßen Walter und Eugenie bei den Eltern. | **BORDER** | NOBORDER ⚠ |
| 3410 | V  Es schien doch, als ob Agathe mit der Zeit vernünftiger geworden war. | **BORDER** | NOBORDER ⚠ |
| 3465 | VI  Heidlings feierten ein schönes Fest. | **BORDER** | NOBORDER ⚠ |
| 3493 | Mittags aß Dorte am Tische ihrer Herrschaft. | **BORDER** | NOBORDER ⚠ |
| 3501 | Dort fand Agathe sie später, das amtliche Schreiben vor sich ausgebreitet, die Brille auf der Nase, mühselig Wort für Wo | **BORDER** | NOBORDER ⚠ |
| 3511 | Aus Agathes Tagebuch. | **BORDER** | NOBORDER ⚠ |
| 3533 | VII  Eine alte Frau war zur Hintertreppe heraufgekommen und hatte verlangt, das gnädige Fräulein Heidling selbst zu spre | **BORDER** | NOBORDER ⚠ |
| 3562 | Vier Jahre lagen zwischen heut und dem Abend, als Wiesing mit ihrer Lade und dem Dienstbuch, dem Vierteljahrslohn und de | **BORDER** | NOBORDER ⚠ |
| 3572 | Agathe ging langsam die einförmige, von hohen schmutzigen Häusern besetzte Straße hinab, die nach der Stadtgrenze führte | **BORDER** | NOBORDER ⚠ |
| 3601 | Agathe trat in eine schräge Dachkammer. | **BORDER** | NOBORDER ⚠ |
| 3660 | Am Nachmittag des folgenden Tages, als sie eben gehen wollte, kam Besuch. | **BORDER** | NOBORDER ⚠ |
| 3664 | Als sie an der Kneipe im Erdgeschoß des Hauses vorüber wollte, erschienen ein paar Männerköpfe in der Thür. | **BORDER** | NOBORDER ⚠ |
| 3695 | Auf der Treppe fiel ihr der Mann mit dem Gänsebraten wieder ein. | **BORDER** | NOBORDER ⚠ |
| 3704 | Mehrere Tage lang konnte sie sich nicht entschließen, Wiesing wieder zu besuchen. | **BORDER** | NOBORDER ⚠ |
| 3712 | Diesmal trat ihr aus der Thür, die der Wohnung der Krämern gegenüberlag, eine Frau entgegen. | **BORDER** | NOBORDER ⚠ |
| 3740 | VIII  Wäre Mama damals nicht so empört gewesen und hätte Wiesing nicht so schonungslos fortgejagt – und sie selbst hatte | **BORDER** | NOBORDER ⚠ |
| 3752 | Agathe ging zu ihr und sagte ihr von Luisens Tode und von dem Leiden, das sie um sie trug – und Mama blieb ganz ruhig un | **BORDER** | NOBORDER ⚠ |
| 3761 | Agathe hatte wahrhaftig keine Ursache, beständig so verstimmt zu sein und ihr Los zu beklagen. | **BORDER** | NOBORDER ⚠ |
| 3862 | »... Denke Dir, neulich habe ich mich schrecklich blamiert,« sagte Lisbeth Wendhagen. | **BORDER** | NOBORDER ⚠ |
| 3871 | IX  Da hatte sie neulich ein wundervolles Buch in Papas Bibliothek aufgestöbert. | **BORDER** | NOBORDER ⚠ |
| 3918 | Er war so entsetzlich erstaunt gewesen, als sie ihm ihren Wunschzettel überreichte. | **BORDER** | NOBORDER ⚠ |
| 3942 | Auf ihrem Weihnachtstisch fand sie ein reizendes Jabot aus rosa Krepp – sie hatte es einmal in einem Schaufenster bewund | **BORDER** | NOBORDER ⚠ |
| 3953 | Jedesmal, wenn Agathe durch ihres Vaters Zimmer ging und ihr Blick den Bücherschrank streifte, der nun verschlossen war, | **BORDER** | NOBORDER ⚠ |
| 3957 | X  Onkel Gustav war gestorben. | **BORDER** | NOBORDER ⚠ |
| 3970 | Nun war der große Lehnstuhl am Fenster, in dem Onkel Gustav, mit einem langen, grauen Schlafrock bekleidet, ein halbes J | **BORDER** | NOBORDER ⚠ |
| 3993 | Bei Onkel Gustavs Begräbnis holte Mama sich eine Erkältung, und nun brach sie vollends zusammen. | **BORDER** | NOBORDER ⚠ |
| 4004 | »Wie Agathe das aushält, ist mir unbegreiflich,« sagte Eugenie. | **BORDER** | NOBORDER ⚠ |
| 4008 | Ja – schon gut! | **BORDER** | NOBORDER ⚠ |
| 4036 | XI  Agathe stieg auf den Boden. | **BORDER** | NOBORDER ⚠ |
| 4080 | Im Eßzimmer wartete Eugenie. | **BORDER** | NOBORDER ⚠ |
| 4086 | Nun noch das Spielzeug. | **BORDER** | NOBORDER ⚠ |
| 4105 | XII  Der Regierungsrat Heidling hörte von allen Seiten, daß seine Tochter sich durchaus eine Erholung gönnen müsse. | **BORDER** | NOBORDER ⚠ |
| 4130 | Als Maler habe Lutz bei weitem nicht erreicht, was er einst versprochen. | **BORDER** | NOBORDER ⚠ |
| 4160 | Acht Tage später saß Agathe auf der Veranda einer Schweizer-Pension und sah über Geranien- und Nelkentöpfe nach den hohe | **BORDER** | NOBORDER ⚠ |
| 4170 | Durch die lange Zeit des Wachens am Krankenlager ihrer Mutter hatte sie das ruhige Schlafen verlernt. | **BORDER** | NOBORDER ⚠ |
| 4232 | Unglücklicherweise hatte Papa die Leidenschaft der frühen Ausflüge. | **BORDER** | NOBORDER ⚠ |
| 4252 | XIII  Papa spielte Domino mit einem Herrn, der ihn kürzlich angeredet hatte, einem vielseitig gebildeten Mann, Professor | **BORDER** | NOBORDER ⚠ |
| 4297 | Der Nachmittag wurde ihr lang bei dem stillen Warten. | **BORDER** | NOBORDER ⚠ |
| 4319 | Als sie heim kam, sah sie am Geländer der Veranda einen Herrn neben der Kellnerin stehen und über die roten Nelken zu ih | **BORDER** | NOBORDER ⚠ |
| 4365 | Das Urteil des schweizer Professors über Greffinger blieb nicht ohne Einfluß auf den Ton, in dem der Regierungsrat Heidl | **BORDER** | NOBORDER ⚠ |
| 4386 | Sie fuhren auf dem Wasser, oder sie saßen in der Veranda der kleinen Wirtschaft unten am See und sprachen mancherlei. | **BORDER** | NOBORDER ⚠ |
| 4406 | Aber von dem Verhältnis zu ihrem Vater sprach sie, und er hörte den angesammelten Zorn in ihrer Stimme klingen. | **BORDER** | NOBORDER ⚠ |
| 4428 | Sie wollte ihm doch zeigen, daß es wert sei, sich um ihr Wohl zu sorgen. | **BORDER** | NOBORDER ⚠ |
| 4433 | Der Regierungsrat sah den Umgang seiner Tochter mit Martin nicht ungern. | **BORDER** | NOBORDER ⚠ |
| 4439 | So arbeiteten in dem stillen Bergasyl zwei Welten daran, sich gegenseitig zu retten. | **BORDER** | NOBORDER ⚠ |
| 4475 | »Du mußt es mir hoch anrechnen, daß ich hierbleibe,« sagte er einmal zu Agathe. | **BORDER** | NOBORDER ⚠ |
| 4527 | Schweigend kehrten sie heim, einen weiten Weg über fahlgrüne, schwerduftende Matten, auf denen der Sonnenglanz flimmerte | **BORDER** | NOBORDER ⚠ |
| 4560 | XIV  Die Mädchen mit Talent sind doch zu beneiden,« klagte Agathe ihrem Vetter. | **BORDER** | NOBORDER ⚠ |
| 4593 | Obenauf dem Hörnli schrieb er ins Fremdenbuch des Gasthauses: Mark Anton Grausiger, Wäschefabrikant und Gattin. | **BORDER** | NOBORDER ⚠ |
| 4688 | Am Abend nach dem Essen forderte Martin sie auf, noch ein Stück mit ihm spazieren zu gehen. | **BORDER** | NOBORDER ⚠ |
| 4709 | Warum ging sie nur und trottete mit gesenktem Kopf und einem unerträglichen Zittern in den Knieen hinter Martin her, der | **BORDER** | NOBORDER ⚠ |
| 4725 | Sie hatten nicht sehr weit zu gehen, bis sie an eine Brücke kamen, die ohne Geländer über den Bach führte. | **BORDER** | NOBORDER ⚠ |
| 4754 | Und fort war sie – wie der Blitz hinausgeschossen in Nacht und Dunkelheit. | **BORDER** | NOBORDER ⚠ |
| 4778 | Endlich erhob sie sich und schlich durch die Nacht zurück. | **BORDER** | NOBORDER ⚠ |
| 4789 | XV  Frau Lieutenant Heidling wurde durch ein Telegramm ihres Schwiegervaters nach der Schweiz berufen. | **BORDER** | NOBORDER ⚠ |
| 4810 | Als Agathe ihre Schwägerin erblickte, verfiel sie in einen Weinkrampf. | **BORDER** | NOBORDER ⚠ |
| 4862 | Aber als sie ankamen, verordnete er ihr gleich eine sechswöchige Kur. | **BORDER** | NOBORDER ⚠ |
| 4894 | »Dieser Doktor ist mir widerwärtig,« erklärte Agathe schon nach der ersten Sprechstunde. | **BORDER** | NOBORDER ⚠ |
| 4898 | Wie sie beobachtet wurden, als er sich abends zu ihnen setzte. | **BORDER** | NOBORDER ⚠ |
| 4975 | Als Eugenie heimkam, sah sie die Jalousien bei ihrer Schwägerin noch geschlossen. | **BORDER** | NOBORDER ⚠ |
| 4991 | Bis tief in die Nacht hinein saßen und standen vor dem Kurhaus die Damen zusammen und besprachen das Geschehene. | **BORDER** | NOBORDER ⚠ |

---

## Gold scenes (with opening sentence)

**1.** `Szene Ebene 1` [0–8028]  
→ Gabriele Reuter Aus guter Familie    Erster Teil I  Breit und hell fiel ein Strahl der Frühlingssonne durch das verstaub

**2.** `Szene Ebene 1` [8029–8978]  
→ Kaum war der Gottesdienst zu Ende, so umarmte Frau Heidling ihre Tochter mit einer Art von kummervoller Leidenschaft, di

**3.** `Szene Ebene 1` [8980–9681]  
→ Ihr Bruder, der Abiturient, lief aufmerksam nochmals in die Kirche zurück, ihr vergessenes Bouquet zu holen, während all

**4.** `Szene Ebene 1` [9682–13996]  
→ Agathe ging allein ins Haus.

**5.** `Nicht-Szene` [13997–16542]  
→ Agathe saß bei Tisch vor einem Teller, der mit gelben Schlüsselblumen umkränzt war, zwischen Vater und Mutter.

**6.** `Szene Ebene 1` [16543–20229]  
→ Inzwischen schlug schon Pastor Kandler an sein Glas.

**7.** `Szene Ebene 1` [20230–25711]  
→ In diesem Augenblick wurde noch ein Geschenk für Agathe abgegeben.

**8.** `Szene Ebene 1` [25712–32024]  
→ Später, als die Erwachsenen in allen Sofaecken des Pfarrhauses ihr Verdauungsschläfchen  hielten – man war ein bißchen h

**9.** `Nicht-Szene` [32028–35999]  
→ II Die Freundschaft zwischen Agathe Heidling und Eugenie Wutrow bestand schon sehr lange – seitdem sie eines Morgens mit

**10.** `Szene Ebene 1` [36000–38393]  
→ Eines Sonntags Nachmittags saßen die kleinen Freundinnen auf dem untersten Ast des niedrigen alten Taxusbaumes in Wutrow

**11.** `Nicht-Szene` [38394–39112]  
→ Als Mama kam, ihr einen Gutenachtkuß zu geben, drehte sie hastig den Kopf nach der Wand und wühlte das heiße Gesicht in 

**12.** `Szene Ebene 1` [39113–40157]  
→ »Frau Wutrow schickte schon zweimal.

**13.** `Szene Ebene 1` [40158–40576]  
→ Unterwegs traf sie eine Bürgerschülerin, die sie kannte.

**14.** `Szene Ebene 1` [40577–41967]  
→ Auf einem freien Platz mit Blumenbeeten setzte sie sich auf eine der eisernen Ketten, die, zwischen Steinpfeilern herabh

**15.** `Szene Ebene 1` [41968–42921]  
→ Dann ging sie mit der Bürgerschülerin, die schon um zwölf Uhr zu Mittag gegessen hatte, trank mit ihr Kaffee und versuch

**16.** `Nicht-Szene` [42922–43739]  
→ Aber das Nachhausekommen ...!

**17.** `Szene Ebene 1` [43740–44454]  
→ Als sie zaghaft und ganz leise klingelte, riß Walter die Thür auf, lachte laut und rief: »Da ist sie ja, die Range!«

**18.** `Szene Ebene 1` [44455–44943]  
→ Als die schauerliche Strafe zu Ende war, wankte Frau Heidling erschöpft in ihr Schlafzimmer und sank keuchend und weinen

**19.** `Szene Ebene 1` [44945–45683]  
→ Das Mädchen lag in der Logierstube auf den Dielen und schrie noch immer, schluckend und schluchzend, sie konnte die Töne

**20.** `Nicht-Szene` [45684–46661]  
→ Ihre Haltung wurde schlaff, in ihrem Gesichtchen zeigte sich ein verdrießlicher, müder Zug.

**21.** `Nicht-Szene` [46666–49957]  
→ III Frau Heidling hegte das unbestimmte Ideal eines innigen Verhältnisses zwischen einer Mutter und ihrer einzigen Tocht

**22.** `Szene Ebene 1` [49958–50766]  
→ Da sie in ihrem früheren Wohnort, der Hauptstadt der Provinz, mannigfache Beziehungen unterhielt, wandte sie sich dorthi

**23.** `Nicht-Szene` [50767–54756]  
→ Agathe bewohnte mit Eugenie denselben Schlafsaal.

**24.** `Szene Ebene 1` [54757–59381]  
→ Welches Glück empfand Agathe daher, als Eugenie sie eines Abends in ihr Kämmerchen herüberholte und mit Chokolade fütter

**25.** `Szene Ebene 1` [59382–59919]  
→ Plötzlich, nach kurzer Zeit, kam sie wieder zur Besinnung, geweckt von einem großen,  brennenden Sehnsuchtsgefühl, welch

**26.** `Nicht-Szene` [59920–66139]  
→ Agathe mußte immer aufs neue staunen, wie stark und sicher Eugenie ihre große Leidenschaft in ihrem Herzen verschloß, un

**27.** `Szene Ebene 1` [66140–67420]  
→ Auch Agathe war maßlos aufgeregt.

**28.** `Szene Ebene 1` [67421–68701]  
→ In Furcht und Grauen schlich Agathe durch die dunklen Korridore des großen Hauses, eine Treppe hinab, eine andere hinauf

**29.** `Nicht-Szene` [68703–72538]  
→ IV  Sommerferien auf dem Lande ... Schwebt nicht ein Duft von Rosen und Erdbeeren vorüber?

**30.** `Szene Ebene 1` [72539–73453]  
→ Und niemals hätte sie sich entschließen können, Eugenie zu erzählen, daß der kühne Bursche einmal, als sie beide allein 

**31.** `Szene Ebene 1` [73454–74395]  
→ Während Agathe glühend und außer Atem ihre aufgelösten Zöpfe wieder flocht und feststeckte, fühlte sie sich sehr tugendh

**32.** `Nicht-Szene` [74396–74942]  
→ Martin betrug sich in den nächsten Tagen nicht wie ein unglücklich Liebender, auch nicht zudringlich, sondern flegelhaft

**33.** `Nicht-Szene` [74944–79396]  
→ V  Herr Heidling war, während die Erziehung seiner Tochter nach der Pensionszeit bei Pastor Kandler gewissermaßen die le

**34.** `Szene Ebene 1` [79397–81131]  
→ Zu den köstlichsten Andenken vergangener Zeiten begrub Agathe nun ihr Spielzeug, das sie in eine Kiste sorgsam mit Kamph

**35.** `Nicht-Szene` [81132–82732]  
→ Im Gegensatz zu der Mattigkeit und Schlafsucht, gegen die Agathe während ihrer Pensionszeit beständig zu kämpfen gehabt 

**36.** `Szene Ebene 1` [82733–90899]  
→ In Agathes wohlig durchheiztem Erkerzimmer feierte sie ihren siebzehnten Geburtstag, umgeben von blühenden Rosen und ros

**37.** `Nicht-Szene` [90901–92940]  
→ VI  In dem Leitfaden fürs Leben: »Des Weibes Wirken als Jungfrau, Gattin und Mutter« stand zu lesen: Der erste Ball bede

**38.** `Szene Ebene 1` [92941–93713]  
→ Martin Greffinger kam, um den Juristenball mitzumachen, aus der nicht sehr entfernten Universitätsstadt herüber.

**39.** `Nicht-Szene` [93714–95334]  
→ Denn es entstand infolge dessen zwischen ihrem Vater und Martin ein Streit, der, bei Kaffee und Kuchen begonnen, die gem

**40.** `Szene Ebene 1` [95335–96151]  
→ Als sie ihre Toilette beendet hatte, mußte sie sich wie auf einer Drehscheibe langsam vor der versammelten Familie und d

**41.** `Szene Ebene 1` [96152–96788]  
→ Einen Wagen hatte man nicht nehmen wollen, der Weg war ja gar nicht weit.

**42.** `Nicht-Szene` [96789–99886]  
→ Da standen die jungen Mädchen in langen Reihen und in kleinen Gruppen – wie ein riesenhaftes Beet zartabgetönter Frühlin

**43.** `Szene Ebene 1` [99887–101625]  
→ Agathe erstaunte über die Einfachheit von Eugenies Anzug, den, trotz aller Bitten, keine Freundin vorher hatte sehen dür

**44.** `Szene Ebene 1` [101626–104604]  
→ Als Agathe die Fülle eleganter Erscheinungen sah, verlor sie plötzlich jede Hoffnung auf Erfolg.

**45.** `Szene Ebene 1` [104605–105377]  
→ Da wurde sie plötzlich bemerkt und alles wunderte sich, daß sie nicht tanzte, sie war doch unstreitig eines der hübsches

**46.** `Nicht-Szene` [105378–106398]  
→ Als erinnere sich jeder Herr eines unverzeihlichen Vergehens, wurde Agathe nun fortwährend zu Extratouren geholt.

**47.** `Szene Ebene 1` [106399–106964]  
→ Es war ihr eine Erlösung, als Onkel Gustav sie einmal holte.

**48.** `Nicht-Szene` [106965–107680]  
→ Er war auch ausgezeichnet geschmackvoll gekleidet – niemand wußte, wie er das bei seinen spärlichen Einnahmen möglich ma

**49.** `Szene Ebene 1` [107681–111284]  
→ Als das Souper begann, wurde Agathe von ihrem Herrn gefragt, ob es ihr recht sei, wenn sie mit ihrer Freundin Eugenie ei

**50.** `Szene Ebene 1` [111285–111856]  
→ Dem Souper folgte der Kotillon.

**51.** `Szene Ebene 1` [111858–112824]  
→ In einer der Pausen des vielverschlungenen Tanzes winkte Mama sie plötzlich heran.

**52.** `Nicht-Szene` [112826–113259]  
→ Sie schlief sehr unruhig in der Nacht nach ihrem ersten Ball; der Kopf war ihr dumpf und  benommen, sie faßte den Entsch

**53.** `Nicht-Szene` [113261–115717]  
→ VII  Ein großer Kampf war in Sieg und Glück beendet, ein deutscher Kaiser war glorreich gekrönt, dem Traum einer Nation 

**54.** `Szene Ebene 1` [115718–115989]  
→ Ein anderes Mal fand Agathe auf dem Schreibtisch ihrer Freundin ein Buch mit roter Inschrift auf schwarzem Deckel.

**55.** `Nicht-Szene` [115990–118675]  
→ Dann wieder konnte Martin übermütig bis zur Tollheit sein, und trieb, wenn er kam, nur  Neckereien und Scherze mit den b

**56.** `Szene Ebene 1` [118676–119677]  
→ »Lord Byron in Newstead Abbey,« las der Regierungsrat aus dem Kataloge hervor.

**57.** `Szene Ebene 1` [119678–119908]  
→ Am nächsten Morgen ging sie wieder in die Ausstellung.

**58.** `Nicht-Szene` [119909–123972]  
→ In der Woche war die Ausstellung meist leer und niemand konnte Agathe beobachten.

**59.** `Szene Ebene 1` [123973–124289]  
→ Wenige Tage vorher, bei einem gemeinsamen Spaziergang, der mit Kaffeetrinken in einem öffentlichen Garten endete, hatte 

**60.** `Szene Ebene 1` [124290–124644]  
→ Sobald Agathe mit der Braut allein war, konnte sie nicht unterlassen, die Bemerkung hinzuwerfen: »Ich glaubte, es wäre M

**61.** `Nicht-Szene` [124645–125633]  
→ Ein Gefühl von Abneigung, von Verachtung gegen die neue Schwägerin peinigte Agathe, während ihr alle Bekannte Glück wüns

**62.** `Nicht-Szene` [125635–128652]  
→ VIII  Zur Zeit, als die Kinder noch klein waren, hatte Frau Heidling nach dem Tode ihrer Schwiegermutter deren Köchin in

**63.** `Szene Ebene 1` [128654–132147]  
→ »Fräulein,« sagte Wiesing eines Morgens, als sie Agathe warmes Wasser in ihr Schlafzimmer brachte, und dabei stand sie m

**64.** `Szene Ebene 1` [132149–133516]  
→ Zuerst ging sie zu einem Schlosser und kaufte einen Riegel mit großen Krampen.

**65.** `Nicht-Szene` [133517–133665]  
→ So quälte sie sich den ganzen Tag hin und wünschte, Walter möge so viel Dienst haben, daß eine Unterredung mit ihm unmög

**66.** `Szene Ebene 1` [133666–134640]  
→ Nachmittag kam Eugenie auf eine Viertelstunde.

**67.** `Szene Ebene 1` [134641–136102]  
→ Walter kam ins Zimmer zurück.

**68.** `Szene Ebene 1` [136103–136931]  
→ Später am Abend fragte sie Wiesing, ob sie nicht zu ihren Eltern gehen könne, ob sie nicht sagen wolle, ihre Mutter wäre

**69.** `Nicht-Szene` [136933–139728]  
→ IX  Agathe war nun schon zwanzig Jahre alt.

**70.** `Szene Ebene 1` [139729–140586]  
→ So fühlte Frau Heidling auch jetzt, daß eine Zerstreuung, ein Wechsel der Eindrücke für Agathe heilsam sein werde.

**71.** `Nicht-Szene` [140587–143374]  
→ Schon lange trug sie in Gesellschaften keine Glaceehandschuhe mehr, sondern Halbseidene, und auf Spaziergängen sogar Bau

**72.** `Szene Ebene 1` [143375–145276]  
→ Frau von Woszenska erwartete Agathe auf dem Bahnhof und schleppte sie gleich zu ihrem Manne ins Atelier.

**73.** `Szene Ebene 1` [145277–146237]  
→ Frau von Woszenska hatte ihr Atelier in der Wohnung, um neben der Kunst den Haushalt überwachen zu können.

**74.** `Szene Ebene 1` [146238–148211]  
→ Der kleine Sohn Michel kam aus der Schule.

**75.** `Nicht-Szene` [148212–149153]  
→ Nannte Woszenski seine Frau bei ihrem Vornamen, so fand er es entzückend, daß die ungewöhnliche Person, deren Bewegungen

**76.** `Szene Ebene 1` [149154–150176]  
→ Am Abend, während das Ehepaar mit dem jungen Gast in ihrem Wohnzimmer saß, von dessen Decke eine Messing-Lampe aus einer

**77.** `Nicht-Szene` [150177–150493]  
→ Agathe lag lange wach auf dem ungewohnten Lager, in dem ihr noch fremden Raum.

**78.** `Szene Ebene 1` [150494–152260]  
→ »Das Kind soll die alte Hauptmann Gärtner besuchen, ihre Mutter kennt sie von früher.

**79.** `Szene Ebene 1` [152261–153501]  
→ Während des Besuches saß sie nach einigen von ihr beantworteten Fragen still und hörte auf Frau von Woszenskas Gespräch 

**80.** `Szene Ebene 1` [153502–154340]  
→ Er kam aus der höheren Etage und traf mit ihnen auf der Treppe zusammen.

**81.** `Szene Ebene 1` [154342–160586]  
→ X  Als Agathe in ihr Gastzimmerchen bei Woszenskis zurückkehrte, schloß sie eilig die Thür hinter sich.

**82.** `Szene Ebene 1` [160587–162773]  
→ In einem Konzert sah Agathe ihn unerwartet dicht vor sich sitzen.

**83.** `Nicht-Szene` [162774–163690]  
→ Woszenski zeichnete Agathe mehrere Male als Studie zu seiner Novize.

**84.** `Szene Ebene 1` [163691–164647]  
→ – Frau von Woszenska bekam eines ihrer Bilder von der Münchener Ausstellung zurück.

**85.** `Nicht-Szene` [164648–168043]  
→ Agathe wurde es viel leichter, ihre Gedanken Woszenskis auszusprechen als ihren Eltern.

**86.** `Szene Ebene 1` [168044–168895]  
→ Einmal noch während ihres Aufenthaltes bei Woszenskis sah Agathe Lutz von weitem in einer menschenleeren Straße.

**87.** `Nicht-Szene` [168896–168958]  
→ Als fünf Wochen verflossen waren, reiste sie nach Haus zurück.

**88.** `Szene Ebene 1` [168960–169907]  
→ XI  »Weißt Du, Agathe, wenn diese Woszenskis Dir so viel interessanter sind, als Deine eigenen Eltern, dann ist es am be

**89.** `Szene Ebene 1` [169908–171635]  
→ Frau Heidling kam eines Abends in ihrer Tochter Schlafzimmer.

**90.** `Nicht-Szene` [171636–172577]  
→ Nachdem Agathe an Frau von Woszenski geschrieben hatte, wartete sie täglich in atemloser Spannung auf deren Antwort.

**91.** `Szene Ebene 1` [172578–173886]  
→ Am 5. September las Agathe frühmorgens in der Zeitung eine Notiz: Fräulein Daniel war als Naive für das Theater in M.

**92.** `Szene Ebene 1` [173887–175538]  
→ Zuerst hörte sie bei Wutrows von ihm reden.

**93.** `Nicht-Szene` [175540–178309]  
→ XII  Eugenies und Walters Hochzeit wurde ein großes Fest, mit Polterabendaufführungen und all der sinnigen Unruhe, die d

**94.** `Szene Ebene 1` [178310–179297]  
→ Nach dem Diner nahm Eugenie ihren Kranz vom Haupt und setzte ihn Onkel Gustav auf.

**95.** `Szene Ebene 1` [179298–179607]  
→ Nachdem das junge Paar abgefahren war, zog sich Agathe in Eugenies Schlafzimmer zurück und blieb dort mit dem ausgedient

**96.** `Nicht-Szene` [179608–180090]  
→ Die Gesellschaft hatte sich zerstreut, die Fremderen waren verschwunden.

**97.** `Szene Ebene 1` [180091–181290]  
→ Jenseits des langen Korridors, nach dem Garten hinaus lag Eugenies Boudoir.

**98.** `Nicht-Szene` [181291–185139]  
→ Nach der Hochzeitsreise zogen die jungen Heidlings in die obere Etage des Wutrow'schen Hauses, die für sie mit modernen 

**99.** `Szene Ebene 1` [185140–186772]  
→ Inzwischen wurde die Begegnung mit ihm, die das Mädchen sich zu jeder Stunde fieberhaft wünschte, Eugenie zu teil.

**100.** `Nicht-Szene` [186774–189898]  
→ XIII  Gegen Ende des Winters veranstaltete die Gesellschaft von M., hauptsächlich auf Frau Eugenies Betreiben, einen gro

**101.** `Szene Ebene 1` [189899–191878]  
→ Vor einer Weile hatte sie im Vorzimmer Lutz und Fräulein Daniel bemerkt, die sich von einigen Schauspielern verabschiede

**102.** `Nicht-Szene` [191879–192253]  
→ Agathe wurde von andern Tänzern geholt, schlenderte mit Freundinnen in den Räumen umher, nahm unter Eugenies Schutz, die

**103.** `Szene Ebene 1` [192254–192739]  
→ »Traumwandlerin,« rief Eugenie sie an, »sollen wir Dich in unsern Wagen nach Haus schicken?

**104.** `Szene Ebene 1` [192740–193018]  
→ Lutz hatte Agathe angesprochen – im Tabaksqualm des Restaurants – zwischen zwei und drei Uhr morgens – und sie gefragt, 

**105.** `Nicht-Szene` [193019–194199]  
→ Agathe mußte am andern Morgen eine ordentliche Strafpredigt über sich ergehen lassen.

**106.** `Szene Ebene 1` [194200–194522]  
→ »Agathe, kommst Du mit, ich suche Walter,« sagte Eugenie, als dieser Zeitpunkt eingetreten war, faßte ihre Schwägerin un

**107.** `Nicht-Szene` [194523–196875]  
→ Lutz sprach viel und lebhaft, Agathe hatte nur halblaute, kindische Töne als Antwort, wie ein furchtsames kleines Mädche

**108.** `Szene Ebene 1` [196876–198308]  
→ »Gestern bin ich in den Anlagen der Daniel begegnet«, sagte Referendar Dürnheim, »ist die aber abgefallen!

**109.** `Nicht-Szene` [198309–199741]  
→ Es kam ein Sonntag, an dem Eugenie in der Breiten Straße mit Herrn von Lutz verabredete, ihn zum Kaffee bei sich zu erwa

**110.** `Szene Ebene 1` [199742–200231]  
→ – – Schon standen die Mokkatäßchen geleert auf Eugenies silberglänzendem Kaffeetisch – der Hauptmann und der Fähnrich ra

**111.** `Szene Ebene 1` [200232–200846]  
→ Er hatte sein Bild nach Paris absenden wollen, der Tischler ließ ihn im Stich – es war der letzte Termin zur Annahme bei

**112.** `Szene Ebene 1` [200847–201944]  
→ Sie bereitete sich nicht vor – sie änderte nichts an ihrem Anzug.

**113.** `Szene Ebene 1` [201945–204265]  
→ – –.

**114.** `Szene Ebene 1` [204266–205278]  
→ Der Maler und Heidlings wurden aufgefordert, zum Abend zu bleiben.

**115.** `Szene Ebene 1` [205279–205522]  
→ Frau Heidling sagte ihrer Tochter eines Abends sanft und schonend: »Liebes Kind – Du bist ein verständiges Mädchen – Pap

**116.** `Nicht-Szene` [205523–207262]  
→ Onkel Gustav aber besuchte Lutz in seinem Atelier und machte Agathe eine ausführliche Beschreibung von der silberblauen 

**117.** `Nicht-Szene` [207264–209362]  
→ XIV  Heidlings hörten lange nichts von Martin Greffinger.

**118.** `Szene Ebene 1` [209363–209802]  
→ Als sie ihn einmal auf der Straße traf und er mit eiligem Gruß an ihr vorüber wollte, stand sie still, gab ihm die Hand 

**119.** `Nicht-Szene` [209803–210806]  
→ Papa und Mama waren verreist, sie wollten das Osterfest in Bornau zubringen.

**120.** `Szene Ebene 1` [210807–215842]  
→ Es war ein trüber Abend, feiner Regen ging nieder.

**121.** `Szene Ebene 1` [215843–220023]  
→ Agathe hielt das Bündel verbotener Bücher in den Händen und blickte beklommen auf sie nieder.

**122.** `Szene Ebene 1` [220025–221707]  
→ Einmal schrak sie jäh zusammen – sie glaubte, es überraschte sie jemand.

**123.** `Szene Ebene 1` [221709–222699]  
→ XV  In der Charwoche fuhr Agathe nach Bornau.

**124.** `Szene Ebene 1` [222700–224089]  
→ Es war schon später Nachmittag.

**125.** `Szene Ebene 1` [224090–227083]  
→ Als die hohe, glasbedeckte Halle erreicht war, sonderte sich ein Teil der Menschen nach dem  Ausgange ab.

**126.** `Szene Ebene 1` [227085–231894]  
→ Erschrocken ließ sie ihn los, als habe sie etwas Unrechtes gethan, weil die Thür aufgerissen wurde.

**127.** `Szene Ebene 1` [231896–233416]  
→ XVI  Frau Heidling empfing ihre Tochter auf dem Bahnhof.

**128.** `Szene Ebene 1` [233417–233877]  
→ Agathe hörte beim Abendessen ein langes und breites Gespräch: Cousine Mimi wollte Diakonissin werden, aber die Eltern wü

**129.** `Szene Ebene 1` [233878–234986]  
→ Mimi begleitete sie zu ihrem Zimmer – sie hatte es auch während jenes fröhlichen Sommeraufenthaltes als Pensionärin bewo

**130.** `Szene Ebene 1` [234987–235925]  
→ Agathe mußte sich ruhig verhalten, denn nebenan, nahe der Thür, schliefen die Eltern.

**131.** `Szene Ebene 1` [235926–237917]  
→ »Hast Du Kopfweh?«

**132.** `Szene Ebene 1` [237918–240404]  
→ Mit einer ruhigen, tröstenden Stimme sagte sie: »Du legst Dich still hin – dann wird sich's schon beruhigen.

**133.** `Nicht-Szene` [240405–241378]  
→ Auf dem Tischchen neben ihr standen Blumen, Flieder und Kamelien.

**134.** `Szene Ebene 1` [241379–241989]  
→ Eugenie schrieb einen langen, teilnehmenden Brief.

**135.** `Nicht-Szene` [241990–242768]  
→ – – Nun hatte sie auch diese Prüfung bestanden ...

**136.** `Szene Ebene 1` [242769–245467]  
→ Aber in einer Nacht, als Mama ihr zu trinken gab, weil der Mund ihr sehr trocken war, fiel er sie plötzlich wieder an.

**137.** `Nicht-Szene` [245469–248068]  
→ Der alte Hausarzt schien am folgenden Morgen durch die Schilderung des nächtlichen Schreckens nicht sonderlich beunruhig

**138.** `Szene Ebene 1` [248069–251336]  
→ Endlich erschien auch der berühmte, erwartete und gefürchtete Gast.

**139.** `Szene Ebene 1` [251337–253025]  
→ Plötzlich hörten alle das tiefe, behagliche Lachen des alten Sanitätsrats.

**140.** `Nicht-Szene` [253033–258481]  
→ Zweiter Teil I  Eugenie war nach der Geburt ihres ersten Kindes immer noch hübscher geworden.

**141.** `Szene Ebene 1` [258482–259273]  
→ »Mit Agathe ist rein nichts mehr anzufangen,« erklärte Eugenie.

**142.** `Szene Ebene 1` [259274–259953]  
→ Als das Mädchen zu den jungen Heidlings kam und Wölfchen aus dem Wagen heben wollte, um mit ihm zu spielen, riß Eugenie 

**143.** `Nicht-Szene` [259954–271340]  
→ Abends in ihrem Zimmer lag Agathe halbe Stunden lang auf den Knieen und betete mit Schluchzen und Weinen, der Herr möge 

**144.** `Szene Ebene 1` [271341–276668]  
→ Nach dem Tanzfest beim Oberpräsidenten verwies er ihr strenge, sich in Gesellschaft auffällig zu benehmen.

**145.** `Szene Ebene 1` [276669–277102]  
→ Als er zum Essen nach Haus kam, versuchten die beiden Frauen, ihn auf jede Weise zu erheitern.

**146.** `Nicht-Szene` [277104–280292]  
→ II  Der Kreis von Agathes Freundinnen hatte sich im letzten Jahre recht gelichtet.

**147.** `Nonscene` [280293–289047]  
→ Es war ein heißer Sommerabend, kurz vor Beginn der großen Ferien.

**148.** `Nicht-Szene` [289048–291964]  
→ Sie fühlte ein leichtes Bangen, weil sie sich des Abends niemals allein auf der Straße befand.

**149.** `Szene Ebene 1` [291965–292652]  
→ Vor Agathe gingen zwei Frauen die Straße entlang.

**150.** `Szene Ebene 1` [292653–298734]  
→ Sie hatte nun auf einen daherkommenden Pferdebahnwagen zu achten, in dem sie die letzte Hälfte ihres Weges zurücklegen w

**151.** `Nicht-Szene` [298735–301930]  
→ III Fröhlich spiegelte sich der Sonnenschein auf der Glatze des Landrats, als er den Hut lüftete, um den heranbrausenden

**152.** `Szene Ebene 1` [301931–303406]  
→ – Landrat Raikendorf zeigte den Damen die schönen geschnitzten alten Schränke, die zum Inventar der Wohnung gehörten, di

**153.** `Nicht-Szene` [303407–304537]  
→ Im Sommersonnenschein – Sieg über ein kühles, müdes Männerherz.

**154.** `Nicht-Szene` [304538–309516]  
→ IV Hatte sich Agathe früher die Ehe unter dem Bilde eines jungen Paares vorgestellt, das Schulter an Schulter gelehnt, v

**155.** `Szene Ebene 1` [309517–310053]  
→ Die Hausthür war schon verschlossen.

**156.** `Szene Ebene 1` [310054–312274]  
→ Agathe lief die Treppen hinauf.

**157.** `Szene Ebene 1` [312275–314064]  
→ In der Frühe, als sie das Wohnzimmer betrat, erinnerte sie sich plötzlich an den Abend, an dem ihr Martin Greffinger die

**158.** `Szene Ebene 1` [314065–316516]  
→ Die Unterredung zwischen dem Regierungsrat und Raikendorf dauerte sehr lange.

**159.** `Szene Ebene 1` [316517–319132]  
→ Am Abend aßen Walter und Eugenie bei den Eltern.

**160.** `Nicht-Szene` [319134–324867]  
→ V  Es schien doch, als ob Agathe mit der Zeit vernünftiger geworden war.

**161.** `Szene Ebene 1` [324869–328021]  
→ VI  Heidlings feierten ein schönes Fest.

**162.** `Szene Ebene 1` [328022–329504]  
→ Mittags aß Dorte am Tische ihrer Herrschaft.

**163.** `Szene Ebene 1` [329505–330485]  
→ Dort fand Agathe sie später, das amtliche Schreiben vor sich ausgebreitet, die Brille auf der Nase, mühselig Wort für Wo

**164.** `Nicht-Szene` [330486–331905]  
→ Aus Agathes Tagebuch.

**165.** `Szene Ebene 1` [331907–334742]  
→ VII  Eine alte Frau war zur Hintertreppe heraufgekommen und hatte verlangt, das gnädige Fräulein Heidling selbst zu spre

**166.** `Nicht-Szene` [334743–335613]  
→ Vier Jahre lagen zwischen heut und dem Abend, als Wiesing mit ihrer Lade und dem Dienstbuch, dem Vierteljahrslohn und de

**167.** `Szene Ebene 1` [335615–337554]  
→ Agathe ging langsam die einförmige, von hohen schmutzigen Häusern besetzte Straße hinab, die nach der Stadtgrenze führte

**168.** `Szene Ebene 1` [337555–341087]  
→ Agathe trat in eine schräge Dachkammer.

**169.** `Nonscene` [341089–341376]  
→ Am Nachmittag des folgenden Tages, als sie eben gehen wollte, kam Besuch.

**170.** `Szene Ebene 1` [341377–343469]  
→ Als sie an der Kneipe im Erdgeschoß des Hauses vorüber wollte, erschienen ein paar Männerköpfe in der Thür.

**171.** `Szene Ebene 1` [343470–343896]  
→ Auf der Treppe fiel ihr der Mann mit dem Gänsebraten wieder ein.

**172.** `Nicht-Szene` [343897–344636]  
→ Mehrere Tage lang konnte sie sich nicht entschließen, Wiesing wieder zu besuchen.

**173.** `Szene Ebene 1` [344637–346240]  
→ Diesmal trat ihr aus der Thür, die der Wohnung der Krämern gegenüberlag, eine Frau entgegen.

**174.** `Nicht-Szene` [346242–347739]  
→ VIII  Wäre Mama damals nicht so empört gewesen und hätte Wiesing nicht so schonungslos fortgejagt – und sie selbst hatte

**175.** `Szene Ebene 1` [347740–348356]  
→ Agathe ging zu ihr und sagte ihr von Luisens Tode und von dem Leiden, das sie um sie trug – und Mama blieb ganz ruhig un

**176.** `Nicht-Szene` [348357–358802]  
→ Agathe hatte wahrhaftig keine Ursache, beständig so verstimmt zu sein und ihr Los zu beklagen.

**177.** `Szene Ebene 1` [358803–359355]  
→ »... Denke Dir, neulich habe ich mich schrecklich blamiert,« sagte Lisbeth Wendhagen.

**178.** `Nicht-Szene` [359357–364013]  
→ IX  Da hatte sie neulich ein wundervolles Buch in Papas Bibliothek aufgestöbert.

**179.** `Szene Ebene 1` [364014–365458]  
→ Er war so entsetzlich erstaunt gewesen, als sie ihm ihren Wunschzettel überreichte.

**180.** `Szene Ebene 1` [365459–366900]  
→ Auf ihrem Weihnachtstisch fand sie ein reizendes Jabot aus rosa Krepp – sie hatte es einmal in einem Schaufenster bewund

**181.** `Nicht-Szene` [366901–367537]  
→ Jedesmal, wenn Agathe durch ihres Vaters Zimmer ging und ihr Blick den Bücherschrank streifte, der nun verschlossen war,

**182.** `Nicht-Szene` [367539–369068]  
→ X  Onkel Gustav war gestorben.

**183.** `Szene Ebene 1` [369069–370817]  
→ Nun war der große Lehnstuhl am Fenster, in dem Onkel Gustav, mit einem langen, grauen Schlafrock bekleidet, ein halbes J

**184.** `Nicht-Szene` [370818–371820]  
→ Bei Onkel Gustavs Begräbnis holte Mama sich eine Erkältung, und nun brach sie vollends zusammen.

**185.** `Szene Ebene 1` [371821–372077]  
→ »Wie Agathe das aushält, ist mir unbegreiflich,« sagte Eugenie.

**186.** `Nicht-Szene` [372078–375254]  
→ Ja – schon gut!

**187.** `Szene Ebene 1` [375256–379736]  
→ XI  Agathe stieg auf den Boden.

**188.** `Szene Ebene 1` [379737–380465]  
→ Im Eßzimmer wartete Eugenie.

**189.** `Szene Ebene 1` [380466–382703]  
→ Nun noch das Spielzeug.

**190.** `Nicht-Szene` [382705–385441]  
→ XII  Der Regierungsrat Heidling hörte von allen Seiten, daß seine Tochter sich durchaus eine Erholung gönnen müsse.

**191.** `Szene Ebene 1` [385442–387824]  
→ Als Maler habe Lutz bei weitem nicht erreicht, was er einst versprochen.

**192.** `Szene Ebene 1` [387825–388500]  
→ Acht Tage später saß Agathe auf der Veranda einer Schweizer-Pension und sah über Geranien- und Nelkentöpfe nach den hohe

**193.** `Szene Ebene 1` [388501–392152]  
→ Durch die lange Zeit des Wachens am Krankenlager ihrer Mutter hatte sie das ruhige Schlafen verlernt.

**194.** `Nicht-Szene` [392153–394266]  
→ Unglücklicherweise hatte Papa die Leidenschaft der frühen Ausflüge.

**195.** `Szene Ebene 1` [394268–397430]  
→ XIII  Papa spielte Domino mit einem Herrn, der ihn kürzlich angeredet hatte, einem vielseitig gebildeten Mann, Professor

**196.** `Szene Ebene 1` [397431–399160]  
→ Der Nachmittag wurde ihr lang bei dem stillen Warten.

**197.** `Szene Ebene 1` [399161–401657]  
→ Als sie heim kam, sah sie am Geländer der Veranda einen Herrn neben der Kellnerin stehen und über die roten Nelken zu ih

**198.** `Szene Ebene 1` [401658–403166]  
→ Das Urteil des schweizer Professors über Greffinger blieb nicht ohne Einfluß auf den Ton, in dem der Regierungsrat Heidl

**199.** `Szene Ebene 1` [403168–404678]  
→ Sie fuhren auf dem Wasser, oder sie saßen in der Veranda der kleinen Wirtschaft unten am See und sprachen mancherlei.

**200.** `Szene Ebene 1` [404679–405851]  
→ Aber von dem Verhältnis zu ihrem Vater sprach sie, und er hörte den angesammelten Zorn in ihrer Stimme klingen.

**201.** `Nicht-Szene` [405852–406262]  
→ Sie wollte ihm doch zeigen, daß es wert sei, sich um ihr Wohl zu sorgen.

**202.** `Szene Ebene 1` [406263–406817]  
→ Der Regierungsrat sah den Umgang seiner Tochter mit Martin nicht ungern.

**203.** `Nicht-Szene` [406818–409702]  
→ So arbeiteten in dem stillen Bergasyl zwei Welten daran, sich gegenseitig zu retten.

**204.** `Szene Ebene 1` [409703–412538]  
→ »Du mußt es mir hoch anrechnen, daß ich hierbleibe,« sagte er einmal zu Agathe.

**205.** `Nicht-Szene` [412539–415140]  
→ Schweigend kehrten sie heim, einen weiten Weg über fahlgrüne, schwerduftende Matten, auf denen der Sonnenglanz flimmerte

**206.** `Szene Ebene 1` [415142–417602]  
→ XIV  Die Mädchen mit Talent sind doch zu beneiden,« klagte Agathe ihrem Vetter.

**207.** `Szene Ebene 1` [417603–425664]  
→ Obenauf dem Hörnli schrieb er ins Fremdenbuch des Gasthauses: Mark Anton Grausiger, Wäschefabrikant und Gattin.

**208.** `Szene Ebene 1` [425665–427019]  
→ Am Abend nach dem Essen forderte Martin sie auf, noch ein Stück mit ihm spazieren zu gehen.

**209.** `Szene Ebene 1` [427020–428642]  
→ Warum ging sie nur und trottete mit gesenktem Kopf und einem unerträglichen Zittern in den Knieen hinter Martin her, der

**210.** `Szene Ebene 1` [428643–430863]  
→ Sie hatten nicht sehr weit zu gehen, bis sie an eine Brücke kamen, die ohne Geländer über den Bach führte.

**211.** `Szene Ebene 1` [430864–432505]  
→ Und fort war sie – wie der Blitz hinausgeschossen in Nacht und Dunkelheit.

**212.** `Szene Ebene 1` [432506–433267]  
→ Endlich erhob sie sich und schlich durch die Nacht zurück.

**213.** `Szene Ebene 1` [433269–434512]  
→ XV  Frau Lieutenant Heidling wurde durch ein Telegramm ihres Schwiegervaters nach der Schweiz berufen.

**214.** `Szene Ebene 1` [434513–438450]  
→ Als Agathe ihre Schwägerin erblickte, verfiel sie in einen Weinkrampf.

**215.** `Nicht-Szene` [438451–442481]  
→ Aber als sie ankamen, verordnete er ihr gleich eine sechswöchige Kur.

**216.** `Szene Ebene 1` [442482–442750]  
→ »Dieser Doktor ist mir widerwärtig,« erklärte Agathe schon nach der ersten Sprechstunde.

**217.** `Nicht-Szene` [442751–448943]  
→ Wie sie beobachtet wurden, als er sich abends zu ihnen setzte.

**218.** `Szene Ebene 1` [448944–450084]  
→ Als Eugenie heimkam, sah sie die Jalousien bei ihrer Schwägerin noch geschlossen.

**219.** `Nicht-Szene` [450085–453778]  
→ Bis tief in die Nacht hinein saßen und standen vor dem Kurhaus die Damen zusammen und besprachen das Geschehene.
