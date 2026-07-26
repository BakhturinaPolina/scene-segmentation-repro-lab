# dProse — Why Some Books Get Too Few or Too Many Borders

**Purpose:** Short reference of *text-structure causes* behind unusually **low** or **high** BORDER rates in the full-corpus run (Prompt Family B). Not a pipeline bug log — outliers usually match how the story is written.

**Source:** Manual spot-checks in [DPROSE_CORPUS_SPOT_CHECKS.md](./DPROSE_CORPUS_SPOT_CHECKS.md), with German quotes from `predictions.jsonl`.

**How to read rates:** Corpus median is roughly **22–25%** BORDER. Here, **low** ≈ under ~14%; **high** ≈ over ~30%. A “BORDER” means the model marks a new scene/event beat at that sentence.

---

## Quick map of cause types

| Direction | Cause type | What happens |
|-----------|------------|--------------|
| **Too low** | Long dialogue / one social event | Many turns, same room, same evening → few borders |
| **Too low** | Realist continuous scene | Same place and action stretch for pages |
| **Too low** | Embedded anecdote / flashback block | A memory is told as one unbroken block |
| **Too high** | Fairy-tale / summary montage | One sentence = one time jump or plot beat |
| **Too high** | Rapid dialogue & emotional micro-beats | Almost every line feels like a new cut |
| **Too high** | Paratext (titles, part headers, essay frame) | Meta text and section starts pile up as borders |
| **Too high** | Story-in-story / nested frames | Each frame open/close is a border |
| **Too high** | Lyric / ecstatic monologue | Short spiritual or poetic sentences, each bordered |
| **Too high** | Exit / travel micro-montage | Leave room → street → bar → see person = many borders |
| **Too high** | Naturalist observation chain | Animal/landscape micro-events, sentence by sentence |

---

# A. Causes of a **too low** BORDER rate

## A1. Long dialogue / one social event

**Idea:** People talk (or argue, bargain, investigate) in one place. The model treats the whole stretch as *one* scene.

**Typical books:** `dprose_137` (*Das höllische Automobil*, 14.5%), Dagobert Trostler detective stories `dprose_693`–`702` (~12–13%), beach dialogue `dprose_1593` (15%).

### Example — comic folk dialogue (`dprose_137`)

Giant Rumbo threatens a cheeky little man (Frechdachs). For **54 sentences** (idx 40–94) there is almost no BORDER — one continuous quarrel/bargain.

> **[41] NOBORDER**  
> *Du lachst noch?« brüllte Rumbo, »dich werde ich übermorgen fressen.« »Mich?« rief der Mensch, – »dazu bist du ja viel zu dumm.*  
> **EN:** “You’re still laughing?” Rumbo roared. “The day after tomorrow I’ll eat you.” “Me?” cried the man — “you’re far too stupid for that.”

> **[85] NOBORDER**  
> *Wie willst du lieber heißen: General oder Hofmarschall?« »Gar nichts will ich heißen,« sagte Frechdachs; »Lohn will ich haben.« »Also wie viel denn?« fragte Rumbo.*  
> **EN:** “What would you rather be called: general or court marshal?” “I don’t want a title,” said Frechdachs; “I want pay.” “So how much?” asked Rumbo.

**Why low rate:** Quips and threats advance *the same encounter*, not a new time or place.

---

### Example — club dinner as one macro-scene (`dprose_693`)

Detective story *Der große Schmuckdiebstahl*. After title/setup, a long board meeting / dinner stays NOBORDER.

> **[0] BORDER**  
> *Der große Schmuckdiebstahl. Ein vollständig verunglücktes Diner.*  
> **EN:** “The Great Jewel Theft. A completely ruined dinner.”

> **[2] BORDER**  
> *Andreas Grumbach … hatte … den Vorstand und den Ausschuß des Klubs zu einer Sitzung in seiner Wohnung geladen.*  
> **EN:** Grumbach had invited the club board to a meeting at his flat.

> **[8] / [20] / [40] NOBORDER** — small talk about seating, Dagobert’s reputation, who chooses the fruit… all still *the same gathering*.

**Why low rate:** One reception = one scene until someone arrives late or time clearly jumps (“Essenszeit geworden”).

---

## A2. Realist continuous scene (same place, same action)

**Idea:** Slow realist prose: weather, walking, small talk, observation — still one situation.

**Typical books:** `dprose_661` (*Der Wurzgartner*, **8.9%**), `dprose_1075` (11.1%), `dprose_2006` (**10.0%**).

### Example — judge arrives in Tyrol (`dprose_661`)

> **[0] BORDER**  
> *Der Wurzgartner. Der Herr Amtsrichter Friedrich Wilhelm Schüttke war das erste Mal in Tirol.*  
> **EN:** “The Wurzgartner. Magistrate Schüttke was in Tyrol for the first time.”

> **[1] NOBORDER** *Sein Arzt hatte es ihm dringend geraten.* — His doctor had strongly advised it.  
> **[2] NOBORDER** *Er müsse mal 'rein ins Gebirge.* — He needed to get into the mountains.  
> **[15] NOBORDER** — still character sketch of a local.  
> **[45] NOBORDER** — someone starts whistling; still the same outdoor/social stretch.

**Why low rate:** Many sentences thicken *one* arrival/setting, they do not start new scenes.

---

## A3. Embedded anecdote / flashback told as one block

**Idea:** A narrator dips into memory. Inside the memory, dozens of sentences stay NOBORDER. Borders appear mainly when returning to the “now.”

**Typical book:** `dprose_753` (*Die Geschichte vom abgerissenen Knopfe*, 13.3%).

### Example — return from flashback (`dprose_753`, idx 159–164)

After a long Lore/Berta memory, the text snaps back; then several short BORDERs mark the return:

> **[159] BORDER** *Für mich aber gehörte von diesem Augenblicke an jener Name zur Illusion.*  
> **EN:** From that moment on, that name belonged to illusion for me.

> **[160] BORDER** *Lore!*  
> **[161] BORDER** *Wie bei dem Klange wieder alles lebendig wurde!*  
> **EN:** How everything came alive again at that sound!

> **[164] BORDER** *Ich sah meinen Vetter an.* — I looked at my cousin. (back in the present)

**Why overall rate is still low:** The long flashback *before* this burst was almost all NOBORDER — one embedded story inside the frame.

---

# B. Causes of a **too high** BORDER rate

## B1. Fairy-tale / summary montage

**Idea:** Fairy-tale or chronicle style: each sentence jumps time, place, or plot step (“then he returned… then he ruled… then war began”).

**Typical books:** `dprose_52` (*Die drei Prinzen*, 32.8%), `dprose_1913` (36.7%), `dprose_965` (*Der Narr auf Manegg*, 36.4%).

### Example — return journey, six borders in six sentences (`dprose_52`, idx 57–62)

Satirical fairy tale about three princes. The trip home is told as a compressed summary:

> **[57] BORDER** On the way back the courtiers keep saying “Aha,” hinting they already know secrets…  
> **[58] BORDER** *Also erreichten sie wieder die Residenz… kamen sie von der Reise nicht klüger zurück…*  
> **EN:** So they reached the residence again… and came back no wiser than they left.

> **[59] BORDER** The royal uncle welcomes the nephew, hands over the government, retires to a hunting lodge.  
> **[60] BORDER** *Sohin führte der zweitältere Prinz probeweise das Regiment.* — So the second-oldest prince ruled on trial.  
> **[61] BORDER** First manifesto: revive heroic past…  
> **[62] BORDER** Constant calls to arms / endless war.

**Why high rate:** Each sentence is a new chapter of plot in miniature — good for fine event labels, too dense for “film scenes.”

### Example — fisherman fairy tale time jumps (`dprose_1913`, idx 17–19)

> **[17] BORDER** He takes the magical gift home, grateful.  
> **[18] BORDER** *…sodass er fortan fast mehr Fische fing, als er verkaufen konnte.*  
> **EN:** …so that from then on he caught almost more fish than he could sell.  
> **[19] BORDER** Strong longing to see the water-woman again; she never returns.

Markers like *fortan* (“from then on”) push the model to cut.

---

## B2. Rapid dialogue & emotional micro-beats

**Idea:** Short lines, quick mood flips, or line-by-line comedy. Almost every sentence feels like a cut.

**Typical books:** `dprose_642` (33%), `dprose_843` (31%), `dprose_2476` (35%), `dprose_2051` (38% — overall rate; dense lyric cuts also contribute).

### Example — emotional climax, seven borders (`dprose_843`, idx 354–360)

Night scene: love turns to anger in a few lines.

> **[354] BORDER** *Auf einmal warf er das Licht wieder fort.* — Suddenly he threw the light away again.  
> **[355] BORDER** He falls to his knees, weeps…  
> **[356] BORDER** *Und da auf einmal hörte er sie ganz laut lachen.* — And suddenly he heard her laugh out loud.  
> **[357] BORDER** *Und das verträgt kein Mann.* — And no man can bear that.  
> **[358] BORDER** *Seine ganze Liebe war weg.* — All his love was gone.  
> **[359] BORDER** *Er war plötzlich wie ein Stein.* — He was suddenly like stone.  
> **[360] BORDER** He stands, finds the light, goes downstairs.

**Why high rate:** Each emotional turn is treated as a new event, though a human might keep one “bedroom climax” scene.

---

## B3. Paratext (titles, part headers, essay framing)

**Idea:** Non-story packaging — titles, part names, magazine intros, holiday essays — sits next to story text. The model borders almost every meta sentence.

**Typical books:** `dprose_119` (frame end + new part title), `dprose_859` (periodical memoir preamble).

### Example — end of frame story + new section title (`dprose_119`, idx 155–161)

School memoir: Part 1 (“tent of the Samoyeds”) closes; Part 2 (*Ein Ferienabenteuer*) begins with a holiday essay.

> **[157] BORDER** *Im Zelt der Samojeden war es einmal wieder urgemütlich…*  
> **EN:** In the Samoyed tent it was cozy again… (closing the old frame)

> **[158] BORDER** *Heraklit der Dunkle blieb uns ein guter Freund…*  
> **EN:** Heraclitus the Dark remained a good friend to us…

> **[159] BORDER** *Ein Ferienabenteuer Ferien – schönstes Wort im Sprachschatze der studierenden Jugend!*  
> **EN:** “A Holiday Adventure” — Holidays: the loveliest word in a student’s vocabulary! ← **new section / title-like text**

> **[160] BORDER** *Weihnachtsferien, Osterferien, Pfingstferien, o wonnevolle Zeiten!*  
> **EN:** Christmas, Easter, Whitsun holidays — O blissful times!

> **[161] BORDER** Autumn holidays are the crown… (still preamble, not the adventure yet)

**Why high (locally):** Frame coda + title + lyric preamble = a stack of structural borders. Good merge target for coarse scenes.

### Example — magazine intro with date stamps (`dprose_859`, idx 2–8)

Memoir of poet Peter Hille; opening is essay/paratext:

> **[2] BORDER** *Wir bringen heute eine Erinnerung an Hille von Julius Hart…*  
> **EN:** Today we present a memory of Hille by Julius Hart… (editor voice)

> **[3] BORDER** *Um die Mitte der sechziger Jahre…* — Around the mid-1860s…  
> **[4] BORDER** Peter Hille has been living with me for some weeks…  
> **[6] BORDER** I had not seen him for a few years…  
> **[7] BORDER** Suddenly, unexpectedly, he arrived one day…  
> **[8] BORDER** The doorbell rings; the landlady comes in looking startled…

**Why high at opening:** Each dated or framing sentence is a border; the middle of the piece is calmer (overall rate only ~15%).

---

## B4. Story-in-story / nested narrative frames

**Idea:** A tale inside a tale (letter, object narrator, “I will now tell you briefly…”). Each *frame switch* gets a BORDER.

**Typical books:** `dprose_738` (broom as narrator), `dprose_516` (letter / published report inside a book), `dprose_1474` (memoir + nested flashback).

### Example — object narrator opens (`dprose_738`, idx 173–179)

A broom starts speaking its life story inside the outer satire:

> **[173] BORDER** *Dieser Besen war ich.* — That broom was I.  
> **[174] BORDER** The woman tucks me under her arm, walks through streets, enters a house.  
> **[175] BORDER** *In diesem Kaufe ging nun mein Unglück erst recht an.* — With that purchase my misfortune really began.  
> **[176] BORDER** What I lived through in half a year would fill a book.  
> **[177] BORDER** *Ich will mich aber kurz fassen…* — But I will be brief… (meta: narrator addressing listener)  
> **[179] BORDER** *Das Haus bewohnte ein junges Ehepaar.* — A young couple lived in the house. (starts the inner plot)

**Why high (locally):** Outer story → object voice → summary → meta aside → new cast = five+ frame borders in a row.

### Example — published report inside a letter-frame (`dprose_516`, idx 74–82)

Narrator decides to print case stories; then a nested childhood anecdote begins:

> **[76] BORDER** *Ich will nicht mehr ins Blaue hinein klagen, sondern einzelne Fälle veröffentlichen.*  
> **EN:** I no longer want to complain vaguely; I will publish individual cases.

> **[79] BORDER** *Da diese Darstellung … noch nicht gegenstandslos geworden ist, so lasse ich sie hier folgen.*  
> **EN:** Since that account is still relevant, I let it follow here.

> **[80] BORDER** *… Es war im Jahre 1858, und ich damals ein zehnjähriger Bube.*  
> **EN:** It was 1858, and I was a ten-year-old boy. ← **inner story starts**

---

## B5. Lyric / ecstatic monologue

**Idea:** Mystical or poetic prose in very short sentences. Each cry or vision is a border.

**Typical books:** `dprose_898` (*Die Seele*, 33.3%, median scene length **1**), mythic `dprose_166`.

### Example (`dprose_898`, idx 416–423)

Cloister ecstasy:

> **[416] BORDER** *Mich läßt man gehen.* — They let me go.  
> **[417] BORDER** *Wohl euch!* — Lucky you!  
> **[418] BORDER** Yesterday, while speaking, I fell face-down and could not wake for a long time.  
> **[420] BORDER** *Jubel, Jubel!* — Jubilation, jubilation!  
> **[421] BORDER** *Deine Hochzeitsnacht, meine Seele, naht!* — Your wedding night, my soul, is near!  
> **[423] BORDER** *Ich lag auf der Erde und streichelte sie.* — I lay on the earth and stroked it.

**Why high rate:** Sentence = spiritual beat. Coarse “one prayer scene” would merge most of these.

---

## B6. Exit / travel micro-montage

**Idea:** Leaving a room is told step by step: air → headache → street → bar → elbow → turn → see someone. Each micro-step is BORDER.

**Typical books:** `dprose_979` (11× run at normal overall rate), `dprose_151` journey home, `dprose_1712` funeral phone/car montage.

### Example — leave dinner, eleven borders (`dprose_979`, idx 149–159)

Davos social novel *Die überlaute Frau Bautz*. Overall rate ~20.5% (normal), but this exit is extreme:

> **[149] BORDER** “Come, you must go to bed.” Sylvester bows.  
> **[150] BORDER** *Er mußte noch ein paar Minuten an die frische Luft.* — He still needed a few minutes of fresh air.  
> **[151] BORDER** *Er spürte Kopfweh.* — He had a headache.  
> **[152] BORDER** *Er ging die Schiastraße entlang.* — He walked along the Schia street.  
> **[153] BORDER** A lieutenant brushes past him.  
> **[154] BORDER** He heads for the bar, to Kolbinger.  
> **[155] BORDER** *»Sekt!« sagte er strahlend.* — “Champagne!” he said, beaming.  
> **[156] BORDER** Steps behind him in soft snow.  
> **[157] BORDER** A hard elbow in his right hip.  
> **[158] BORDER** *Er drehte den Kopf.* — He turned his head.  
> **[159] BORDER** A girl in a blue sports jacket looks at him.

**Why “too high” here:** One continuous walk would be one scene for film; the model cuts on every sensory beat.

### Example — disoriented journey home (`dprose_151`, idx 259–263)

> **[259] BORDER** *Sie fror.* — She was cold.  
> **[260] BORDER** *Die Dinge verschwammen.* — Things blurred.  
> **[261] BORDER** A train whistle somewhere; smell of wet clothes; people bump her.  
> **[262] BORDER** Familiar voices; doors she has often passed; a sawmill; a brook.  
> **[263] BORDER** She crosses her own threshold, falls to her knees by the bed…

Same montage pattern: perception → transport → arrival.

---

## B7. Naturalist observation chain

**Idea:** Hunting / nature prose lists micro-events (hares, birds, weather). Each observation is a border.

**Typical book:** `dprose_1113` (*Der Feldhase*, **41.4%** — among highest in corpus).

### Example (`dprose_1113`, idx 107–116)

> **[108] BORDER** *Über zweihundertsiebzig nehmen die Jäger mit nach der Stadt.*  
> **EN:** The hunters take more than two hundred seventy [hares] into town.

> **[109] BORDER** *Es ist recht still geworden in der Jagd.* — It has grown quite quiet in the hunting grounds.  
> **[112] BORDER** Since the great snowstorm the weather stayed good; in late January the hares are busy preserving their kind…  
> **[113] BORDER** *Die Morgensonne scheint so schön warm in den Wald.* — The morning sun shines so warmly into the forest.  
> **[114] BORDER** Titmice whistle, bullfinch calls, jay squawks, crows fight, squirrels climb…  
> **[116] BORDER** A hare appears, hops onto the clearing, scrapes snow, nibbles half-wilted grass…

**Why high rate:** Documentary montage at sentence grain — not wrong for event labels; too fine for coarse scenes.

---

## B8. Allegorical / essay montage (related to B5–B6)

**Idea:** Philosophical or insect-parable prose jumps argument beat by beat (sometimes with fake “diary dates”).

**Typical book:** `dprose_1060` — **13 consecutive BORDERs** (corpus record run), ant-colony allegory idx 438–450.

> **[438] BORDER** *Den ganzen Staat für einen Menschen, die Welt um ein Weibchen?*  
> **EN:** A whole state for one person, the world for a little female?

> **[440] BORDER** *Wie weise sind doch die Einrichtungen der Ameisen!*  
> **EN:** How wise the institutions of the ants are!

> **[443] BORDER** *Hochzeitssonne 3.* — Wedding-sun 3. (allegorical “date”)  
> **[447] BORDER** Time to remove the useless males…  
> **[448] BORDER** *Hochzeitssonne 5.*

**Why high:** Each thesis line = new border; one “parable section” would merge them.

---

## B9. Essayistic vignette chain (window diary)

**Idea:** Narrator watches the street day by day; each small anecdote is its own bordered unit.

**Typical book:** `dprose_739` (*Aus dem Leben eines Vielgeprüften*, 33.6%).

> **[0] BORDER** *Jeden Morgen nach dem Frühstück setze ich mich … an das Fenster … und schaue … auf den Franziskanerplatz hinab.*  
> **EN:** Every morning after breakfast I sit at the window and look down on Franciscan Square.

> **[5] BORDER** *Was aber seit einigen Wochen meine Aufmerksamkeit täglich auf sich zieht, das ist ein alter Gaul…*  
> **EN:** What has drawn my attention daily for some weeks is an old nag…

**Why high rate:** Form is “one observation = one scene,” by design of the text.

---

# C. Same book, two effects (mixed cases)

Some texts are **low overall** but have a **high local run** (or the reverse).

| Pattern | Example | What to remember |
|---------|---------|------------------|
| Calm middle, hot opening | `dprose_859` (~15%, but 7× borders in preamble) | Paratext opening ≠ whole-book rate |
| Normal rate, extreme exit | `dprose_979` (~20.5%, but 11× exit montage) | Look at consecutive runs, not only % |
| Low rate, short return burst | `dprose_753` | Flashback NOBORDER; return = border cluster |

---

# D. Practical takeaway

1. **Low outliers** are usually *long same-place dialogue* or *realist continuity* — often correct for coarse scenes.  
2. **High outliers** are usually *montage / fairy summary / lyric / paratext / frame switches* — often correct for fine events, too dense for film-like scenes.  
3. For coarse scene boundaries, the spot-checks repeatedly suggest **post-process merges** on consecutive BORDER runs (travel montage, frame coda + title, exit walks), not full re-runs.

---

**Related:** [DPROSE_CORPUS_SPOT_CHECKS.md](./DPROSE_CORPUS_SPOT_CHECKS.md) · edit copy [DPROSE_CORPUS_SPOT_CHECKS_EDIT.md](./DPROSE_CORPUS_SPOT_CHECKS_EDIT.md)

*Living notes — add examples as you edit.*
