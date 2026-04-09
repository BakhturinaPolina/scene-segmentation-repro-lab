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
| 0 | Gabriele Reuter From a good family    First part I  A beam of spring sunshine fell wide and bright through the dust | **BORDER** | **BORDER** |
| 74 | As soon as the service was over, Mrs. Heidling hugged her daughter with a kind of sorrowful passion, i.e | **BORDER** | NOBORDER ⚠ |
| 82 | Her brother, the high school graduate, attentively ran back to the church to get her forgotten bouquet, while everyone | **BORDER** | NOBORDER ⚠ |
| 89 | Agathe went into the house alone. | **BORDER** | NOBORDER ⚠ |
| 145 | Agathe sat at the table in front of a plate wreathed with yellow cowslips, between her father and mother. | **BORDER** | NOBORDER ⚠ |
| 168 | Meanwhile, Pastor Kandler was already banging on his glass. | **BORDER** | NOBORDER ⚠ |
| 200 | At this moment a present was given for Agathe. | **BORDER** | NOBORDER ⚠ |
| 271 | Later, when the adults took their digestive nap in all the sofa corners of the rectory  held – one was a bit h | **BORDER** | NOBORDER ⚠ |
| 332 | II The friendship between Agathe Heidling and Eugenie Wutrow has existed for a very long time - ever since they met one morning | **BORDER** | NOBORDER ⚠ |
| 357 | One Sunday afternoon the little friends were sitting on the lowest branch of the low, old yew tree in Wutrow | **BORDER** | NOBORDER ⚠ |
| 384 | When Mama came to kiss her goodnight, she quickly turned her head toward the wall and buried her hot face in it | **BORDER** | NOBORDER ⚠ |
| 392 | »Mrs Wutrow has already sent twice. | **BORDER** | NOBORDER ⚠ |
| 409 | On the way she met a middle-class student she knew. | **BORDER** | NOBORDER ⚠ |
| 415 | In an open space with flower beds she sat down on one of the iron chains that hung between stone pillars | **BORDER** | NOBORDER ⚠ |
| 435 | Then she went with the middle-class student, who had already had lunch at twelve o'clock, drank coffee with her and tried | **BORDER** | NOBORDER ⚠ |
| 446 | But coming home...! | **BORDER** | NOBORDER ⚠ |
| 459 | When she rang the bell timidly and very quietly, Walter opened the door, laughed loudly and shouted: "There it is, the range!" | **BORDER** | NOBORDER ⚠ |
| 472 | When the horrific punishment was over, Ms. Heidling, exhausted, staggered into her bedroom and sank, panting and crying | **BORDER** | NOBORDER ⚠ |
| 478 | The girl was lying on the floorboards in the guest room and was still screaming, swallowing and sobbing, she could hear the sounds | **BORDER** | NOBORDER ⚠ |
| 486 | Her posture became slack, a sullen, tired expression appeared on her little face. | **BORDER** | NOBORDER ⚠ |
| 494 | III Mrs. Heidling cherished the vague ideal of an intimate relationship between a mother and her only daughter | **BORDER** | NOBORDER ⚠ |
| 521 | Since she had a variety of connections in her former place of residence, the capital of the province, she turned there | **BORDER** | NOBORDER ⚠ |
| 527 | Agathe lived in the same dormitory with Eugenie. | **BORDER** | NOBORDER ⚠ |
| 560 | What happiness Agathe felt when Eugenie brought her into her little room one evening and fed her chocolate | **BORDER** | NOBORDER ⚠ |
| 632 | Suddenly, after a short time, she came back to her senses, woken up by a large,  burning feeling of longing, what | **BORDER** | NOBORDER ⚠ |
| 638 | Agathe always had to be amazed at how strongly and securely Eugenie closed her great passion in her heart | **BORDER** | NOBORDER ⚠ |
| 692 | Agathe was also extremely excited. | **BORDER** | NOBORDER ⚠ |
| 711 | In fear and horror, Agathe crept through the dark corridors of the big house, down one staircase and up another | **BORDER** | NOBORDER ⚠ |
| 722 | IV  Summer holidays in the country... Isn't the scent of roses and strawberries wafting by? | **BORDER** | NOBORDER ⚠ |
| 748 | And she could never have decided to tell Eugenie that the bold boy had once met when the two of them were alone | **BORDER** | NOBORDER ⚠ |
| 754 | While Agathe, glowing and out of breath, re-braided and pinned her unraveled braids, she felt very virtuous | **BORDER** | NOBORDER ⚠ |
| 764 | Over the next few days, Martin did not behave like an unhappy lover, nor did he behave in an intrusive manner, but in a boorish manner | **BORDER** | NOBORDER ⚠ |
| 770 | v  Mr. Heidling was, to a certain extent, the le while raising his daughter after her retirement with Pastor Kandler | **BORDER** | NOBORDER ⚠ |
| 804 | As one of the most delicious souvenirs of bygone times, Agathe now buried her toys, which she carefully placed in a box with Kamph | **BORDER** | NOBORDER ⚠ |
| 817 | In contrast to the fatigue and insomnia that Agathe constantly had to fight against during her retirement | **BORDER** | NOBORDER ⚠ |
| 830 | She celebrated her seventeenth birthday in Agathe's comfortably heated bay window room, surrounded by blooming roses and roses | **BORDER** | NOBORDER ⚠ |
| 963 | VI  In the guide for life: "Woman's work as a virgin, wife and mother" it was written: The first ball means | **BORDER** | NOBORDER ⚠ |
| 980 | Martin Greffinger came over from the not very distant university town to take part in the lawyers' ball. | **BORDER** | NOBORDER ⚠ |
| 989 | As a result, an argument arose between her father and Martin, which began over coffee and cake and ended in accordance with | **BORDER** | NOBORDER ⚠ |
| 1000 | When she had finished her toilet, she had to slowly move forward, as if on a turntable, in front of the assembled family and d | **BORDER** | NOBORDER ⚠ |
| 1006 | They didn't want to take a car, it wasn't that far. | **BORDER** | NOBORDER ⚠ |
| 1012 | The young girls stood there in long rows and in small groups - like a huge bed of delicately colored spring | **BORDER** | NOBORDER ⚠ |
| 1029 | Agathe was amazed at the simplicity of Eugenie's suit, which, despite all her requests, no friend had been allowed to see before | **BORDER** | NOBORDER ⚠ |
| 1046 | When Agathe saw the abundance of elegant appearances, she suddenly lost all hope of success. | **BORDER** | NOBORDER ⚠ |
| 1077 | Then suddenly she was noticed and everyone was surprised that she wasn't dancing, she was undoubtedly one of the pretty ones | **BORDER** | NOBORDER ⚠ |
| 1082 | As if every gentleman remembered an unforgivable offense, Agathe was constantly being called on extra trips. | **BORDER** | NOBORDER ⚠ |
| 1089 | It was a relief for her when Uncle Gustav came to fetch her. | **BORDER** | NOBORDER ⚠ |
| 1094 | He was also extremely tastefully dressed - no one knew how he managed that with his meager income | **BORDER** | NOBORDER ⚠ |
| 1100 | When the supper began, Agathe was asked by her master whether it would be okay for her to have dinner with her friend Eugenie | **BORDER** | NOBORDER ⚠ |
| 1125 | The supper was followed by the cotillion. | **BORDER** | NOBORDER ⚠ |
| 1130 | During one of the breaks in the intricate dance, Mama suddenly beckoned her over. | **BORDER** | NOBORDER ⚠ |
| 1142 | She slept very restlessly the night after her first ball; her head was dull and  dazed, she made the decision | **BORDER** | NOBORDER ⚠ |
| 1144 | VII  A great battle was ended in victory and happiness, a German emperor was gloriously crowned, the dream of a nation | **BORDER** | NOBORDER ⚠ |
| 1161 | Another time, Agathe found a book with a red inscription on a black cover on her friend's desk. | **BORDER** | NOBORDER ⚠ |
| 1165 | At other times Martin could be overconfident to the point of madness and, when he came, he was just pushing  Teasing and joking with the b | **BORDER** | NOBORDER ⚠ |
| 1185 | "Lord Byron in Newstead Abbey," the government councilor read from the catalogue. | **BORDER** | NOBORDER ⚠ |
| 1203 | The next morning she went back to the exhibition. | **BORDER** | NOBORDER ⚠ |
| 1206 | During the week the exhibition was mostly empty and no one could observe Agathe. | **BORDER** | NOBORDER ⚠ |
| 1240 | A few days earlier, on a walk together that ended with drinking coffee in a public garden | **BORDER** | NOBORDER ⚠ |
| 1242 | As soon as Agathe was alone with the bride, she couldn't help but remark: »I thought it was M | **BORDER** | NOBORDER ⚠ |
| 1247 | Agathe was tormented by a feeling of dislike and contempt for her new sister-in-law, while everyone she knew wished her luck | **BORDER** | NOBORDER ⚠ |
| 1256 | VIII  When the children were still small, Mrs. Heidling was her mother-in-law's cook after her mother-in-law's death | **BORDER** | NOBORDER ⚠ |
| 1276 | "Miss," said Wiesing one morning as she brought Agathe warm water into her bedroom, and she was standing there | **BORDER** | NOBORDER ⚠ |
| 1336 | First she went to a locksmith and bought a deadbolt with large cramps. | **BORDER** | NOBORDER ⚠ |
| 1350 | So she tormented herself all day long, wishing that Walter would be so busy that a conversation with him would be impossible | **BORDER** | NOBORDER ⚠ |
| 1352 | In the afternoon, Eugenie lasted a quarter of an hour. | **BORDER** | NOBORDER ⚠ |
| 1363 | Walter came back into the room. | **BORDER** | NOBORDER ⚠ |
| 1387 | Later that evening she asked Wiesing if she couldn't go to her parents, if she didn't want to say she was her mother | **BORDER** | NOBORDER ⚠ |
| 1395 | IX  Agathe was now twenty years old. | **BORDER** | NOBORDER ⚠ |
| 1416 | So Mrs. Heidling now also felt that a distraction, a change of impressions, would be healing for Agathe. | **BORDER** | NOBORDER ⚠ |
| 1426 | It was a long time since she had stopped wearing kid gloves when socializing, but rather half-silk ones, and even when she went for a walk | **BORDER** | NOBORDER ⚠ |
| 1451 | Mrs. von Woszenska was waiting for Agathe at the train station and immediately dragged her to her husband's studio. | **BORDER** | NOBORDER ⚠ |
| 1466 | Mrs. von Woszenska had her studio in the apartment so that she could oversee the household in addition to art. | **BORDER** | NOBORDER ⚠ |
| 1474 | The little son Michel came home from school. | **BORDER** | NOBORDER ⚠ |
| 1499 | When Woszenski called his wife by her first name, he found it delightful that the unusual person and her movements | **BORDER** | NOBORDER ⚠ |
| 1503 | In the evening, while the couple sat with their young guest in their living room, a brass lamp hung from the ceiling | **BORDER** | NOBORDER ⚠ |
| 1508 | Agathe lay awake for a long time on the unfamiliar bed, in the room that was still unfamiliar to her. | **BORDER** | NOBORDER ⚠ |
| 1511 | »The child should visit old Captain Gärtner, her mother knows her from before. | **BORDER** | NOBORDER ⚠ |
| 1531 | During the visit, after answering a few questions, she sat quietly and listened to Ms. von Woszenska's conversation | **BORDER** | NOBORDER ⚠ |
| 1552 | He came from the upper floor and met them on the stairs. | **BORDER** | NOBORDER ⚠ |
| 1564 | X  When Agathe returned to her guest room at the Woszenskis', she quickly closed the door behind her. | **BORDER** | NOBORDER ⚠ |
| 1634 | At a concert, Agathe unexpectedly saw him sitting close to her. | **BORDER** | NOBORDER ⚠ |
| 1661 | Woszenski drew Agathe several times as a study for his novice. | **BORDER** | NOBORDER ⚠ |
| 1672 | – Ms. von Woszenska received one of her pictures back from the Munich exhibition. | **BORDER** | NOBORDER ⚠ |
| 1681 | Agathe found it much easier to express her thoughts to Woszenski than to her parents. | **BORDER** | NOBORDER ⚠ |
| 1706 | Once during her stay with the Woszenskis, Agathe saw Lutz from a distance on a deserted street. | **BORDER** | NOBORDER ⚠ |
| 1714 | When five weeks had passed, she returned home. | **BORDER** | NOBORDER ⚠ |
| 1715 | XI  »You know, Agathe, if these Woszenskis are so much more interesting to you than your own parents, then that's it | **BORDER** | NOBORDER ⚠ |
| 1720 | Mrs. Heidling came into her daughter's bedroom one evening. | **BORDER** | NOBORDER ⚠ |
| 1749 | After Agathe had written to Mrs. von Woszenski, she waited every day in breathless excitement for her answer. | **BORDER** | NOBORDER ⚠ |
| 1760 | Early in the morning on September 5th, Agathe read a note in the newspaper: Miss Daniel was a naive person for the theater in M. | **BORDER** | NOBORDER ⚠ |
| 1775 | She first heard about him at Wutrows. | **BORDER** | NOBORDER ⚠ |
| 1800 | XII  Eugenie and Walter's wedding was a big celebration, with hen party performances and all the mental unrest that came with it | **BORDER** | NOBORDER ⚠ |
| 1826 | After dinner, Eugenie took her wreath off her head and placed it on Uncle Gustav's head. | **BORDER** | NOBORDER ⚠ |
| 1838 | After the young couple had left, Agathe retreated to Eugenie's bedroom and stayed there with her | **BORDER** | NOBORDER ⚠ |
| 1841 | The company had dispersed, the strangers had disappeared. | **BORDER** | NOBORDER ⚠ |
| 1845 | Beyond the long corridor, towards the garden, lay Eugenie's boudoir. | **BORDER** | NOBORDER ⚠ |
| 1856 | After their honeymoon, the young Heidlings moved to the upper floor of the Wutrow house, which was modern for them | **BORDER** | NOBORDER ⚠ |
| 1892 | In the meantime, Eugenie was granted the meeting with him that the girl feverishly wanted at every hour. | **BORDER** | NOBORDER ⚠ |
| 1918 | XIII  Towards the end of the winter, M.'s company, mainly at Mrs. Eugenie's instigation, organized a large one | **BORDER** | NOBORDER ⚠ |
| 1938 | A while ago she had noticed Lutz and Miss Daniel in the anteroom saying goodbye to some actors | **BORDER** | NOBORDER ⚠ |
| 1961 | Agathe was fetched by other dancers, strolled around the rooms with her friends, and took her under Eugenie's protection | **BORDER** | NOBORDER ⚠ |
| 1964 | “Dreamwalker,” Eugenie called to her, “shall we send you home in our car? | **BORDER** | NOBORDER ⚠ |
| 1973 | Lutz had spoken to Agathe - in the tobacco smoke of the restaurant - between two and three in the morning - and asked her, | **BORDER** | NOBORDER ⚠ |
| 1976 | The next morning Agathe had to endure a serious lecture. | **BORDER** | NOBORDER ⚠ |
| 1990 | "Agathe, come with me, I'm looking for Walter," said Eugenie. When this time came, her sister-in-law took her breath away | **BORDER** | NOBORDER ⚠ |
| 1992 | Lutz spoke a lot and animatedly, Agathe only answered in low, childish tones, like a timid little girl | **BORDER** | NOBORDER ⚠ |
| 2011 | “Yesterday I met Daniel in the facilities,” said Trainee Dürnheim, “but she fell off! | **BORDER** | NOBORDER ⚠ |
| 2030 | One Sunday came when Eugenie arranged to meet Mr. von Lutz on Breite Strasse to meet him for coffee | **BORDER** | NOBORDER ⚠ |
| 2039 | – – The mocha cups were already empty on Eugenie’s shiny silver coffee table – the captain and the ensign were there | **BORDER** | NOBORDER ⚠ |
| 2045 | He had wanted to send his picture to Paris, but the carpenter let him down - it was the last date for acceptance | **BORDER** | NOBORDER ⚠ |
| 2054 | She didn't prepare - she didn't change anything about her suit. | **BORDER** | NOBORDER ⚠ |
| 2062 | – –. | **BORDER** | NOBORDER ⚠ |
| 2087 | The painter and Heidlings were asked to stay for the evening. | **BORDER** | NOBORDER ⚠ |
| 2099 | Mrs. Heidling said to her daughter one evening gently and gently: “Dear child – you are a sensible girl – Dad | **BORDER** | NOBORDER ⚠ |
| 2100 | Uncle Gustav visited Lutz in his studio and gave Agathe a detailed description of the silver-blue one | **BORDER** | NOBORDER ⚠ |
| 2110 | XIV  Heidlings didn't hear from Martin Greffinger for a long time. | **BORDER** | NOBORDER ⚠ |
| 2130 | Once when she met him on the street and he wanted to pass her with a hasty greeting, she stood still and shook his hand | **BORDER** | NOBORDER ⚠ |
| 2135 | Dad and mom were away, they wanted to spend Easter in Bornau. | **BORDER** | NOBORDER ⚠ |
| 2146 | It was a cloudy evening and a light rain was falling. | **BORDER** | NOBORDER ⚠ |
| 2224 | Agathe held the bundle of forbidden books in her hands and looked down at them with trepidation. | **BORDER** | NOBORDER ⚠ |
| 2273 | Once she started suddenly - she thought someone was surprising her. | **BORDER** | NOBORDER ⚠ |
| 2289 | XV  During the Char week, Agathe went to Bornau. | **BORDER** | NOBORDER ⚠ |
| 2303 | It was already late afternoon. | **BORDER** | NOBORDER ⚠ |
| 2322 | When the high, glass-covered hall was reached, some of the people separated themselves  exits. | **BORDER** | NOBORDER ⚠ |
| 2360 | Startled, she let go of him, as if she had done something wrong because the door was thrown open. | **BORDER** | NOBORDER ⚠ |
| 2431 | XVI  Mrs. Heidling received her daughter at the train station. | **BORDER** | NOBORDER ⚠ |
| 2442 | Agathe heard a long and broad conversation at dinner: Cousin Mimi wanted to become a deaconess, but her parents didn't want to | **BORDER** | NOBORDER ⚠ |
| 2444 | Mimi accompanied her to her room - she had also stayed there during that happy summer stay as a pensioner | **BORDER** | NOBORDER ⚠ |
| 2452 | Agathe had to keep quiet because her parents were sleeping next door, near the door. | **BORDER** | NOBORDER ⚠ |
| 2460 | “Do you have a headache?” | **BORDER** | NOBORDER ⚠ |
| 2485 | In a calm, comforting voice she said: "You lie down quietly - then things will calm down. | **BORDER** | NOBORDER ⚠ |
| 2510 | On the little table next to her were flowers, lilacs and camellias. | **BORDER** | NOBORDER ⚠ |
| 2520 | Eugenie wrote a long, sympathetic letter. | **BORDER** | NOBORDER ⚠ |
| 2527 | – – Now she had also passed this test... | **BORDER** | NOBORDER ⚠ |
| 2538 | But one night, when Mama was giving her something to drink because her mouth was very dry, he suddenly attacked her again. | **BORDER** | NOBORDER ⚠ |
| 2566 | The following morning the old family doctor did not seem particularly disturbed by his description of the night terror | **BORDER** | NOBORDER ⚠ |
| 2585 | Finally the famous, expected and dreaded guest appeared. | **BORDER** | NOBORDER ⚠ |
| 2631 | Suddenly everyone heard the deep, comfortable laugh of the old medical officer. | **BORDER** | NOBORDER ⚠ |
| 2649 | Second part I  Eugenie had become even prettier after the birth of her first child. | **BORDER** | NOBORDER ⚠ |
| 2700 | "There's absolutely nothing left to do with Agathe," explained Eugenie. | **BORDER** | NOBORDER ⚠ |
| 2708 | When the girl came to the young Heidlings and wanted to lift Little Wolf out of the car to play with him, Eugenie pulled | **BORDER** | NOBORDER ⚠ |
| 2712 | In the evening, Agathe lay on her knees in her room for half an hour and prayed, with sobs and tears, for the Lord to come | **BORDER** | NOBORDER ⚠ |
| 2805 | After the dance party at the President's house, he strictly warned her not to behave conspicuously in society. | **BORDER** | NOBORDER ⚠ |
| 2873 | When he came home to dinner, the two women tried to cheer him up in every way. | **BORDER** | NOBORDER ⚠ |
| 2879 | II  The circle of Agathe's friends had thinned out over the last year. | **BORDER** | NOBORDER ⚠ |
| 2912 | It was a hot summer evening, just before the start of the big holidays. | **BORDER** | NOBORDER ⚠ |
| 2993 | She felt a slight trepidation because she was never alone on the street in the evening. | **BORDER** | NOBORDER ⚠ |
| 3023 | Two women walked down the street in front of Agathe. | **BORDER** | NOBORDER ⚠ |
| 3033 | She now had to watch out for a horse-drawn tram coming along in which she would cover the last half of her journey | **BORDER** | NOBORDER ⚠ |
| 3131 | III The sunshine reflected happily on the district administrator's bald head as he lifted his hat to see the approaching one | **BORDER** | NOBORDER ⚠ |
| 3165 | – District Administrator Raikendorf showed the ladies the beautiful carved old cupboards that were part of the apartment's inventory, i.e | **BORDER** | NOBORDER ⚠ |
| 3181 | In the summer sunshine – victory over a cool, tired man’s heart. | **BORDER** | NOBORDER ⚠ |
| 3197 | IV Agathe had previously imagined marriage in the image of a young couple leaning shoulder to shoulder, v | **BORDER** | NOBORDER ⚠ |
| 3258 | The front door was already locked. | **BORDER** | NOBORDER ⚠ |
| 3268 | Agathe ran up the stairs. | **BORDER** | NOBORDER ⚠ |
| 3307 | Early in the morning, when she entered the living room, she suddenly remembered the evening on which Martin Greffinger gave her the | **BORDER** | NOBORDER ⚠ |
| 3336 | The conversation between the government council and Raikendorf lasted a very long time. | **BORDER** | NOBORDER ⚠ |
| 3372 | In the evening, Walter and Eugenie ate with their parents. | **BORDER** | NOBORDER ⚠ |
| 3410 | v  It seemed as if Agathe had become more sensible over time. | **BORDER** | NOBORDER ⚠ |
| 3465 | VI  Heidlings had a lovely party. | **BORDER** | NOBORDER ⚠ |
| 3493 | At midday, Dorte ate at her master's table. | **BORDER** | NOBORDER ⚠ |
| 3501 | Agathe found her there later, the official letter spread out in front of her, her glasses on her nose, laboriously saying word for where | **BORDER** | NOBORDER ⚠ |
| 3511 | From Agathe's diary. | **BORDER** | NOBORDER ⚠ |
| 3533 | VII  An old woman had come up the back stairs and demanded to see Miss Heidling herself | **BORDER** | NOBORDER ⚠ |
| 3562 | There were four years between today and the evening when Wiesing with her drawer and the service book, the quarterly wages and de | **BORDER** | NOBORDER ⚠ |
| 3572 | Agathe walked slowly down the monotonous street lined with tall, dirty houses that led to the city limits | **BORDER** | NOBORDER ⚠ |
| 3601 | Agathe entered a sloping attic room. | **BORDER** | NOBORDER ⚠ |
| 3660 | On the afternoon of the following day, as she was about to leave, a visitor came. | **BORDER** | NOBORDER ⚠ |
| 3664 | As she was about to pass the bar on the ground floor of the house, a few men's heads appeared in the door. | **BORDER** | NOBORDER ⚠ |
| 3695 | On the stairs she remembered the man with the roast goose. | **BORDER** | NOBORDER ⚠ |
| 3704 | For several days she couldn't decide to visit Wiesing again. | **BORDER** | NOBORDER ⚠ |
| 3712 | This time a woman came towards her from the door opposite the shopkeeper's apartment. | **BORDER** | NOBORDER ⚠ |
| 3740 | VIII  If Mama hadn't been so outraged back then and wouldn't have chased Wiesing away so mercilessly - and she herself had | **BORDER** | NOBORDER ⚠ |
| 3752 | Agathe went to her and told her about Luisen's death and about the suffering she was carrying around her - and Mama remained very calm | **BORDER** | NOBORDER ⚠ |
| 3761 | Agathe really had no reason to be constantly upset and complain about her fate. | **BORDER** | NOBORDER ⚠ |
| 3862 | "... Just think, I made a terrible embarrassment of myself the other day," said Lisbeth Wendhagen. | **BORDER** | NOBORDER ⚠ |
| 3871 | IX  She recently found a wonderful book in Dad's library. | **BORDER** | NOBORDER ⚠ |
| 3918 | He had been so terribly surprised when she handed him her wish list. | **BORDER** | NOBORDER ⚠ |
| 3942 | On her Christmas table she found a lovely pink crepe jabot - she had once seen it in a shop window | **BORDER** | NOBORDER ⚠ |
| 3953 | Every time Agathe walked through her father's room and her eyes touched the bookcase, which was now locked, | **BORDER** | NOBORDER ⚠ |
| 3957 | X  Uncle Gustav had died. | **BORDER** | NOBORDER ⚠ |
| 3970 | Now the large armchair by the window in which Uncle Gustav, dressed in a long, gray dressing gown, sat half a J | **BORDER** | NOBORDER ⚠ |
| 3993 | At Uncle Gustav's funeral, Mama caught a cold and now she completely collapsed. | **BORDER** | NOBORDER ⚠ |
| 4004 | "How Agathe can stand it is incomprehensible to me," said Eugenie. | **BORDER** | NOBORDER ⚠ |
| 4008 | Yes – it’s okay! | **BORDER** | NOBORDER ⚠ |
| 4036 | XI  Agathe got down on the floor. | **BORDER** | NOBORDER ⚠ |
| 4080 | Eugenie was waiting in the dining room. | **BORDER** | NOBORDER ⚠ |
| 4086 | Now the toys. | **BORDER** | NOBORDER ⚠ |
| 4105 | XII  The government councilor Heidling heard from all sides that his daughter definitely needed to treat herself to some rest. | **BORDER** | NOBORDER ⚠ |
| 4130 | As a painter, Lutz has not achieved nearly what he once promised. | **BORDER** | NOBORDER ⚠ |
| 4160 | Eight days later, Agathe sat on the veranda of a Swiss guesthouse and looked over the tall pots of geraniums and carnations | **BORDER** | NOBORDER ⚠ |
| 4170 | Because of the long time spent awake at her mother's bedside, she had forgotten how to sleep peacefully. | **BORDER** | NOBORDER ⚠ |
| 4232 | Unfortunately, Dad had the passion of early excursions. | **BORDER** | NOBORDER ⚠ |
| 4252 | XIII  Dad was playing dominoes with a gentleman who had recently spoken to him, a well-educated man, a professor | **BORDER** | NOBORDER ⚠ |
| 4297 | The afternoon was long for her, waiting in silence. | **BORDER** | NOBORDER ⚠ |
| 4319 | When she came home, she saw a gentleman standing on the porch railing next to the waitress and looking over the red carnations at him | **BORDER** | NOBORDER ⚠ |
| 4365 | The Swiss professor's verdict on Greffinger did not remain without influence on the tone in which the government councilor Heidl | **BORDER** | NOBORDER ⚠ |
| 4386 | They sailed on the water, or they sat on the veranda of the little inn down by the lake and talked a variety of things. | **BORDER** | NOBORDER ⚠ |
| 4406 | But she spoke of her relationship with her father, and he heard the accumulated anger in her voice. | **BORDER** | NOBORDER ⚠ |
| 4428 | She wanted to show him that it was worth worrying about her well-being. | **BORDER** | NOBORDER ⚠ |
| 4433 | The government council was not unhappy about his daughter's dealings with Martin. | **BORDER** | NOBORDER ⚠ |
| 4439 | So in the quiet mountain asylum, two worlds worked to save each other. | **BORDER** | NOBORDER ⚠ |
| 4475 | "You have to give me credit for staying here," he once said to Agathe. | **BORDER** | NOBORDER ⚠ |
| 4527 | They returned home in silence, a long way over pale green, heavily scented meadows on which the sun shimmered | **BORDER** | NOBORDER ⚠ |
| 4560 | XIV  Girls with talent are to be envied,” Agathe complained to her cousin. | **BORDER** | NOBORDER ⚠ |
| 4593 | On top of the Hörnli he wrote in the inn's guest book: Mark Anton Grausiger, linen manufacturer and wife. | **BORDER** | NOBORDER ⚠ |
| 4688 | That evening after dinner, Martin asked her to go for a walk with him. | **BORDER** | NOBORDER ⚠ |
| 4709 | Why did she just walk and trot after Martin with her head bowed and her knees shaking unbearably | **BORDER** | NOBORDER ⚠ |
| 4725 | They didn't have to go very far before they came to a bridge that crossed the stream without railings. | **BORDER** | NOBORDER ⚠ |
| 4754 | And she was gone - shot out like lightning into the night and darkness. | **BORDER** | NOBORDER ⚠ |
| 4778 | At last she rose and crept back through the night. | **BORDER** | NOBORDER ⚠ |
| 4789 | XV  Mrs. Lieutenant Heidling was called to Switzerland by a telegram from her father-in-law. | **BORDER** | NOBORDER ⚠ |
| 4810 | When Agathe saw her sister-in-law, she fell into a fit of tears. | **BORDER** | NOBORDER ⚠ |
| 4862 | But when they arrived, he immediately prescribed her a six-week treatment. | **BORDER** | NOBORDER ⚠ |
| 4894 | "This doctor is disgusting to me," Agathe explained after the first consultation. | **BORDER** | NOBORDER ⚠ |
| 4898 | How they were observed when he sat down with them in the evening. | **BORDER** | NOBORDER ⚠ |
| 4975 | When Eugenie came home, she saw her sister-in-law's blinds still closed. | **BORDER** | NOBORDER ⚠ |
| 4991 | The ladies sat and stood together in front of the Kurhaus until late into the night and discussed what had happened. | **BORDER** | NOBORDER ⚠ |

---

## Gold scenes (with opening sentence)

**1.** `Szene Ebene 1` [0–8028]  
→ Gabriele Reuter From a good family    First part I  A beam of spring sunshine fell wide and bright through the dust

**2.** `Szene Ebene 1` [8029–8978]  
→ As soon as the service was over, Mrs. Heidling hugged her daughter with a kind of sorrowful passion, i.e

**3.** `Szene Ebene 1` [8980–9681]  
→ Her brother, the high school graduate, attentively ran back to the church to get her forgotten bouquet, while everyone

**4.** `Szene Ebene 1` [9682–13996]  
→ Agathe went into the house alone.

**5.** `Nicht-Szene` [13997–16542]  
→ Agathe sat at the table in front of a plate wreathed with yellow cowslips, between her father and mother.

**6.** `Szene Ebene 1` [16543–20229]  
→ Meanwhile, Pastor Kandler was already banging on his glass.

**7.** `Szene Ebene 1` [20230–25711]  
→ At this moment a present was given for Agathe.

**8.** `Szene Ebene 1` [25712–32024]  
→ Later, when the adults took their digestive nap in all the sofa corners of the rectory  held – one was a bit h

**9.** `Nicht-Szene` [32028–35999]  
→ II The friendship between Agathe Heidling and Eugenie Wutrow has existed for a very long time - ever since they met one morning

**10.** `Szene Ebene 1` [36000–38393]  
→ One Sunday afternoon the little friends were sitting on the lowest branch of the low, old yew tree in Wutrow

**11.** `Nicht-Szene` [38394–39112]  
→ When Mama came to kiss her goodnight, she quickly turned her head toward the wall and buried her hot face in it

**12.** `Szene Ebene 1` [39113–40157]  
→ »Mrs Wutrow has already sent twice.

**13.** `Szene Ebene 1` [40158–40576]  
→ On the way she met a middle-class student she knew.

**14.** `Szene Ebene 1` [40577–41967]  
→ In an open space with flower beds she sat down on one of the iron chains that hung between stone pillars

**15.** `Szene Ebene 1` [41968–42921]  
→ Then she went with the middle-class student, who had already had lunch at twelve o'clock, drank coffee with her and tried

**16.** `Nicht-Szene` [42922–43739]  
→ But coming home...!

**17.** `Szene Ebene 1` [43740–44454]  
→ When she rang the bell timidly and very quietly, Walter opened the door, laughed loudly and shouted: "There it is, the range!"

**18.** `Szene Ebene 1` [44455–44943]  
→ When the horrific punishment was over, Ms. Heidling, exhausted, staggered into her bedroom and sank, panting and crying

**19.** `Szene Ebene 1` [44945–45683]  
→ The girl was lying on the floorboards in the guest room and was still screaming, swallowing and sobbing, she could hear the sounds

**20.** `Nicht-Szene` [45684–46661]  
→ Her posture became slack, a sullen, tired expression appeared on her little face.

**21.** `Nicht-Szene` [46666–49957]  
→ III Mrs. Heidling cherished the vague ideal of an intimate relationship between a mother and her only daughter

**22.** `Szene Ebene 1` [49958–50766]  
→ Since she had a variety of connections in her former place of residence, the capital of the province, she turned there

**23.** `Nicht-Szene` [50767–54756]  
→ Agathe lived in the same dormitory with Eugenie.

**24.** `Szene Ebene 1` [54757–59381]  
→ What happiness Agathe felt when Eugenie brought her into her little room one evening and fed her chocolate

**25.** `Szene Ebene 1` [59382–59919]  
→ Suddenly, after a short time, she came back to her senses, woken up by a large,  burning feeling of longing, what

**26.** `Nicht-Szene` [59920–66139]  
→ Agathe always had to be amazed at how strongly and securely Eugenie closed her great passion in her heart

**27.** `Szene Ebene 1` [66140–67420]  
→ Agathe was also extremely excited.

**28.** `Szene Ebene 1` [67421–68701]  
→ In fear and horror, Agathe crept through the dark corridors of the big house, down one staircase and up another

**29.** `Nicht-Szene` [68703–72538]  
→ IV  Summer holidays in the country... Isn't the scent of roses and strawberries wafting by?

**30.** `Szene Ebene 1` [72539–73453]  
→ And she could never have decided to tell Eugenie that the bold boy had once met when the two of them were alone

**31.** `Szene Ebene 1` [73454–74395]  
→ While Agathe, glowing and out of breath, re-braided and pinned her unraveled braids, she felt very virtuous

**32.** `Nicht-Szene` [74396–74942]  
→ Over the next few days, Martin did not behave like an unhappy lover, nor did he behave in an intrusive manner, but in a boorish manner

**33.** `Nicht-Szene` [74944–79396]  
→ v  Mr. Heidling was, to a certain extent, the le while raising his daughter after her retirement with Pastor Kandler

**34.** `Szene Ebene 1` [79397–81131]  
→ As one of the most delicious souvenirs of bygone times, Agathe now buried her toys, which she carefully placed in a box with Kamph

**35.** `Nicht-Szene` [81132–82732]  
→ In contrast to the fatigue and insomnia that Agathe constantly had to fight against during her retirement

**36.** `Szene Ebene 1` [82733–90899]  
→ She celebrated her seventeenth birthday in Agathe's comfortably heated bay window room, surrounded by blooming roses and roses

**37.** `Nicht-Szene` [90901–92940]  
→ VI  In the guide for life: "Woman's work as a virgin, wife and mother" it was written: The first ball means

**38.** `Szene Ebene 1` [92941–93713]  
→ Martin Greffinger came over from the not very distant university town to take part in the lawyers' ball.

**39.** `Nicht-Szene` [93714–95334]  
→ As a result, an argument arose between her father and Martin, which began over coffee and cake and ended in accordance with

**40.** `Szene Ebene 1` [95335–96151]  
→ When she had finished her toilet, she had to slowly move forward, as if on a turntable, in front of the assembled family and d

**41.** `Szene Ebene 1` [96152–96788]  
→ They didn't want to take a car, it wasn't that far.

**42.** `Nicht-Szene` [96789–99886]  
→ The young girls stood there in long rows and in small groups - like a huge bed of delicately colored spring

**43.** `Szene Ebene 1` [99887–101625]  
→ Agathe was amazed at the simplicity of Eugenie's suit, which, despite all her requests, no friend had been allowed to see before

**44.** `Szene Ebene 1` [101626–104604]  
→ When Agathe saw the abundance of elegant appearances, she suddenly lost all hope of success.

**45.** `Szene Ebene 1` [104605–105377]  
→ Then suddenly she was noticed and everyone was surprised that she wasn't dancing, she was undoubtedly one of the pretty ones

**46.** `Nicht-Szene` [105378–106398]  
→ As if every gentleman remembered an unforgivable offense, Agathe was constantly being called on extra trips.

**47.** `Szene Ebene 1` [106399–106964]  
→ It was a relief for her when Uncle Gustav came to fetch her.

**48.** `Nicht-Szene` [106965–107680]  
→ He was also extremely tastefully dressed - no one knew how he managed that with his meager income

**49.** `Szene Ebene 1` [107681–111284]  
→ When the supper began, Agathe was asked by her master whether it would be okay for her to have dinner with her friend Eugenie

**50.** `Szene Ebene 1` [111285–111856]  
→ The supper was followed by the cotillion.

**51.** `Szene Ebene 1` [111858–112824]  
→ During one of the breaks in the intricate dance, Mama suddenly beckoned her over.

**52.** `Nicht-Szene` [112826–113259]  
→ She slept very restlessly the night after her first ball; her head was dull and  dazed, she made the decision

**53.** `Nicht-Szene` [113261–115717]  
→ VII  A great battle was ended in victory and happiness, a German emperor was gloriously crowned, the dream of a nation

**54.** `Szene Ebene 1` [115718–115989]  
→ Another time, Agathe found a book with a red inscription on a black cover on her friend's desk.

**55.** `Nicht-Szene` [115990–118675]  
→ At other times Martin could be overconfident to the point of madness and, when he came, he was just pushing  Teasing and joking with the b

**56.** `Szene Ebene 1` [118676–119677]  
→ "Lord Byron in Newstead Abbey," the government councilor read from the catalogue.

**57.** `Szene Ebene 1` [119678–119908]  
→ The next morning she went back to the exhibition.

**58.** `Nicht-Szene` [119909–123972]  
→ During the week the exhibition was mostly empty and no one could observe Agathe.

**59.** `Szene Ebene 1` [123973–124289]  
→ A few days earlier, on a walk together that ended with drinking coffee in a public garden

**60.** `Szene Ebene 1` [124290–124644]  
→ As soon as Agathe was alone with the bride, she couldn't help but remark: »I thought it was M

**61.** `Nicht-Szene` [124645–125633]  
→ Agathe was tormented by a feeling of dislike and contempt for her new sister-in-law, while everyone she knew wished her luck

**62.** `Nicht-Szene` [125635–128652]  
→ VIII  When the children were still small, Mrs. Heidling was her mother-in-law's cook after her mother-in-law's death

**63.** `Szene Ebene 1` [128654–132147]  
→ "Miss," said Wiesing one morning as she brought Agathe warm water into her bedroom, and she was standing there

**64.** `Szene Ebene 1` [132149–133516]  
→ First she went to a locksmith and bought a deadbolt with large cramps.

**65.** `Nicht-Szene` [133517–133665]  
→ So she tormented herself all day long, wishing that Walter would be so busy that a conversation with him would be impossible

**66.** `Szene Ebene 1` [133666–134640]  
→ In the afternoon, Eugenie lasted a quarter of an hour.

**67.** `Szene Ebene 1` [134641–136102]  
→ Walter came back into the room.

**68.** `Szene Ebene 1` [136103–136931]  
→ Later that evening she asked Wiesing if she couldn't go to her parents, if she didn't want to say she was her mother

**69.** `Nicht-Szene` [136933–139728]  
→ IX  Agathe was now twenty years old.

**70.** `Szene Ebene 1` [139729–140586]  
→ So Mrs. Heidling now also felt that a distraction, a change of impressions, would be healing for Agathe.

**71.** `Nicht-Szene` [140587–143374]  
→ It was a long time since she had stopped wearing kid gloves when socializing, but rather half-silk ones, and even when she went for a walk

**72.** `Szene Ebene 1` [143375–145276]  
→ Mrs. von Woszenska was waiting for Agathe at the train station and immediately dragged her to her husband's studio.

**73.** `Szene Ebene 1` [145277–146237]  
→ Mrs. von Woszenska had her studio in the apartment so that she could oversee the household in addition to art.

**74.** `Szene Ebene 1` [146238–148211]  
→ The little son Michel came home from school.

**75.** `Nicht-Szene` [148212–149153]  
→ When Woszenski called his wife by her first name, he found it delightful that the unusual person and her movements

**76.** `Szene Ebene 1` [149154–150176]  
→ In the evening, while the couple sat with their young guest in their living room, a brass lamp hung from the ceiling

**77.** `Nicht-Szene` [150177–150493]  
→ Agathe lay awake for a long time on the unfamiliar bed, in the room that was still unfamiliar to her.

**78.** `Szene Ebene 1` [150494–152260]  
→ »The child should visit old Captain Gärtner, her mother knows her from before.

**79.** `Szene Ebene 1` [152261–153501]  
→ During the visit, after answering a few questions, she sat quietly and listened to Ms. von Woszenska's conversation

**80.** `Szene Ebene 1` [153502–154340]  
→ He came from the upper floor and met them on the stairs.

**81.** `Szene Ebene 1` [154342–160586]  
→ X  When Agathe returned to her guest room at the Woszenskis', she quickly closed the door behind her.

**82.** `Szene Ebene 1` [160587–162773]  
→ At a concert, Agathe unexpectedly saw him sitting close to her.

**83.** `Nicht-Szene` [162774–163690]  
→ Woszenski drew Agathe several times as a study for his novice.

**84.** `Szene Ebene 1` [163691–164647]  
→ – Ms. von Woszenska received one of her pictures back from the Munich exhibition.

**85.** `Nicht-Szene` [164648–168043]  
→ Agathe found it much easier to express her thoughts to Woszenski than to her parents.

**86.** `Szene Ebene 1` [168044–168895]  
→ Once during her stay with the Woszenskis, Agathe saw Lutz from a distance on a deserted street.

**87.** `Nicht-Szene` [168896–168958]  
→ When five weeks had passed, she returned home.

**88.** `Szene Ebene 1` [168960–169907]  
→ XI  »You know, Agathe, if these Woszenskis are so much more interesting to you than your own parents, then that's it

**89.** `Szene Ebene 1` [169908–171635]  
→ Mrs. Heidling came into her daughter's bedroom one evening.

**90.** `Nicht-Szene` [171636–172577]  
→ After Agathe had written to Mrs. von Woszenski, she waited every day in breathless excitement for her answer.

**91.** `Szene Ebene 1` [172578–173886]  
→ Early in the morning on September 5th, Agathe read a note in the newspaper: Miss Daniel was a naive person for the theater in M.

**92.** `Szene Ebene 1` [173887–175538]  
→ She first heard about him at Wutrows.

**93.** `Nicht-Szene` [175540–178309]  
→ XII  Eugenie and Walter's wedding was a big celebration, with hen party performances and all the mental unrest that came with it

**94.** `Szene Ebene 1` [178310–179297]  
→ After dinner, Eugenie took her wreath off her head and placed it on Uncle Gustav's head.

**95.** `Szene Ebene 1` [179298–179607]  
→ After the young couple had left, Agathe retreated to Eugenie's bedroom and stayed there with her

**96.** `Nicht-Szene` [179608–180090]  
→ The company had dispersed, the strangers had disappeared.

**97.** `Szene Ebene 1` [180091–181290]  
→ Beyond the long corridor, towards the garden, lay Eugenie's boudoir.

**98.** `Nicht-Szene` [181291–185139]  
→ After their honeymoon, the young Heidlings moved to the upper floor of the Wutrow house, which was modern for them

**99.** `Szene Ebene 1` [185140–186772]  
→ In the meantime, Eugenie was granted the meeting with him that the girl feverishly wanted at every hour.

**100.** `Nicht-Szene` [186774–189898]  
→ XIII  Towards the end of the winter, M.'s company, mainly at Mrs. Eugenie's instigation, organized a large one

**101.** `Szene Ebene 1` [189899–191878]  
→ A while ago she had noticed Lutz and Miss Daniel in the anteroom saying goodbye to some actors

**102.** `Nicht-Szene` [191879–192253]  
→ Agathe was fetched by other dancers, strolled around the rooms with her friends, and took her under Eugenie's protection

**103.** `Szene Ebene 1` [192254–192739]  
→ “Dreamwalker,” Eugenie called to her, “shall we send you home in our car?

**104.** `Szene Ebene 1` [192740–193018]  
→ Lutz had spoken to Agathe - in the tobacco smoke of the restaurant - between two and three in the morning - and asked her,

**105.** `Nicht-Szene` [193019–194199]  
→ The next morning Agathe had to endure a serious lecture.

**106.** `Szene Ebene 1` [194200–194522]  
→ "Agathe, come with me, I'm looking for Walter," said Eugenie. When this time came, her sister-in-law took her breath away

**107.** `Nicht-Szene` [194523–196875]  
→ Lutz spoke a lot and animatedly, Agathe only answered in low, childish tones, like a timid little girl

**108.** `Szene Ebene 1` [196876–198308]  
→ “Yesterday I met Daniel in the facilities,” said Trainee Dürnheim, “but she fell off!

**109.** `Nicht-Szene` [198309–199741]  
→ One Sunday came when Eugenie arranged to meet Mr. von Lutz on Breite Strasse to meet him for coffee

**110.** `Szene Ebene 1` [199742–200231]  
→ – – The mocha cups were already empty on Eugenie’s shiny silver coffee table – the captain and the ensign were there

**111.** `Szene Ebene 1` [200232–200846]  
→ He had wanted to send his picture to Paris, but the carpenter let him down - it was the last date for acceptance

**112.** `Szene Ebene 1` [200847–201944]  
→ She didn't prepare - she didn't change anything about her suit.

**113.** `Szene Ebene 1` [201945–204265]  
→ – –.

**114.** `Szene Ebene 1` [204266–205278]  
→ The painter and Heidlings were asked to stay for the evening.

**115.** `Szene Ebene 1` [205279–205522]  
→ Mrs. Heidling said to her daughter one evening gently and gently: “Dear child – you are a sensible girl – Dad

**116.** `Nicht-Szene` [205523–207262]  
→ Uncle Gustav visited Lutz in his studio and gave Agathe a detailed description of the silver-blue one

**117.** `Nicht-Szene` [207264–209362]  
→ XIV  Heidlings didn't hear from Martin Greffinger for a long time.

**118.** `Szene Ebene 1` [209363–209802]  
→ Once when she met him on the street and he wanted to pass her with a hasty greeting, she stood still and shook his hand

**119.** `Nicht-Szene` [209803–210806]  
→ Dad and mom were away, they wanted to spend Easter in Bornau.

**120.** `Szene Ebene 1` [210807–215842]  
→ It was a cloudy evening and a light rain was falling.

**121.** `Szene Ebene 1` [215843–220023]  
→ Agathe held the bundle of forbidden books in her hands and looked down at them with trepidation.

**122.** `Szene Ebene 1` [220025–221707]  
→ Once she started suddenly - she thought someone was surprising her.

**123.** `Szene Ebene 1` [221709–222699]  
→ XV  During the Char week, Agathe went to Bornau.

**124.** `Szene Ebene 1` [222700–224089]  
→ It was already late afternoon.

**125.** `Szene Ebene 1` [224090–227083]  
→ When the high, glass-covered hall was reached, some of the people separated themselves  exits.

**126.** `Szene Ebene 1` [227085–231894]  
→ Startled, she let go of him, as if she had done something wrong because the door was thrown open.

**127.** `Szene Ebene 1` [231896–233416]  
→ XVI  Mrs. Heidling received her daughter at the train station.

**128.** `Szene Ebene 1` [233417–233877]  
→ Agathe heard a long and broad conversation at dinner: Cousin Mimi wanted to become a deaconess, but her parents didn't want to

**129.** `Szene Ebene 1` [233878–234986]  
→ Mimi accompanied her to her room - she had also stayed there during that happy summer stay as a pensioner

**130.** `Szene Ebene 1` [234987–235925]  
→ Agathe had to keep quiet because her parents were sleeping next door, near the door.

**131.** `Szene Ebene 1` [235926–237917]  
→ “Do you have a headache?”

**132.** `Szene Ebene 1` [237918–240404]  
→ In a calm, comforting voice she said: "You lie down quietly - then things will calm down.

**133.** `Nicht-Szene` [240405–241378]  
→ On the little table next to her were flowers, lilacs and camellias.

**134.** `Szene Ebene 1` [241379–241989]  
→ Eugenie wrote a long, sympathetic letter.

**135.** `Nicht-Szene` [241990–242768]  
→ – – Now she had also passed this test...

**136.** `Szene Ebene 1` [242769–245467]  
→ But one night, when Mama was giving her something to drink because her mouth was very dry, he suddenly attacked her again.

**137.** `Nicht-Szene` [245469–248068]  
→ The following morning the old family doctor did not seem particularly disturbed by his description of the night terror

**138.** `Szene Ebene 1` [248069–251336]  
→ Finally the famous, expected and dreaded guest appeared.

**139.** `Szene Ebene 1` [251337–253025]  
→ Suddenly everyone heard the deep, comfortable laugh of the old medical officer.

**140.** `Nicht-Szene` [253033–258481]  
→ Second part I  Eugenie had become even prettier after the birth of her first child.

**141.** `Szene Ebene 1` [258482–259273]  
→ "There's absolutely nothing left to do with Agathe," explained Eugenie.

**142.** `Szene Ebene 1` [259274–259953]  
→ When the girl came to the young Heidlings and wanted to lift Little Wolf out of the car to play with him, Eugenie pulled

**143.** `Nicht-Szene` [259954–271340]  
→ In the evening, Agathe lay on her knees in her room for half an hour and prayed, with sobs and tears, for the Lord to come

**144.** `Szene Ebene 1` [271341–276668]  
→ After the dance party at the President's house, he strictly warned her not to behave conspicuously in society.

**145.** `Szene Ebene 1` [276669–277102]  
→ When he came home to dinner, the two women tried to cheer him up in every way.

**146.** `Nicht-Szene` [277104–280292]  
→ II  The circle of Agathe's friends had thinned out over the last year.

**147.** `Nonscene` [280293–289047]  
→ It was a hot summer evening, just before the start of the big holidays.

**148.** `Nicht-Szene` [289048–291964]  
→ She felt a slight trepidation because she was never alone on the street in the evening.

**149.** `Szene Ebene 1` [291965–292652]  
→ Two women walked down the street in front of Agathe.

**150.** `Szene Ebene 1` [292653–298734]  
→ She now had to watch out for a horse-drawn tram coming along in which she would cover the last half of her journey

**151.** `Nicht-Szene` [298735–301930]  
→ III The sunshine reflected happily on the district administrator's bald head as he lifted his hat to see the approaching one

**152.** `Szene Ebene 1` [301931–303406]  
→ – District Administrator Raikendorf showed the ladies the beautiful carved old cupboards that were part of the apartment's inventory, i.e

**153.** `Nicht-Szene` [303407–304537]  
→ In the summer sunshine – victory over a cool, tired man’s heart.

**154.** `Nicht-Szene` [304538–309516]  
→ IV Agathe had previously imagined marriage in the image of a young couple leaning shoulder to shoulder, v

**155.** `Szene Ebene 1` [309517–310053]  
→ The front door was already locked.

**156.** `Szene Ebene 1` [310054–312274]  
→ Agathe ran up the stairs.

**157.** `Szene Ebene 1` [312275–314064]  
→ Early in the morning, when she entered the living room, she suddenly remembered the evening on which Martin Greffinger gave her the

**158.** `Szene Ebene 1` [314065–316516]  
→ The conversation between the government council and Raikendorf lasted a very long time.

**159.** `Szene Ebene 1` [316517–319132]  
→ In the evening, Walter and Eugenie ate with their parents.

**160.** `Nicht-Szene` [319134–324867]  
→ v  It seemed as if Agathe had become more sensible over time.

**161.** `Szene Ebene 1` [324869–328021]  
→ VI  Heidlings had a lovely party.

**162.** `Szene Ebene 1` [328022–329504]  
→ At midday, Dorte ate at her master's table.

**163.** `Szene Ebene 1` [329505–330485]  
→ Agathe found her there later, the official letter spread out in front of her, her glasses on her nose, laboriously saying word for where

**164.** `Nicht-Szene` [330486–331905]  
→ From Agathe's diary.

**165.** `Szene Ebene 1` [331907–334742]  
→ VII  An old woman had come up the back stairs and demanded to see Miss Heidling herself

**166.** `Nicht-Szene` [334743–335613]  
→ There were four years between today and the evening when Wiesing with her drawer and the service book, the quarterly wages and de

**167.** `Szene Ebene 1` [335615–337554]  
→ Agathe walked slowly down the monotonous street lined with tall, dirty houses that led to the city limits

**168.** `Szene Ebene 1` [337555–341087]  
→ Agathe entered a sloping attic room.

**169.** `Nonscene` [341089–341376]  
→ On the afternoon of the following day, as she was about to leave, a visitor came.

**170.** `Szene Ebene 1` [341377–343469]  
→ As she was about to pass the bar on the ground floor of the house, a few men's heads appeared in the door.

**171.** `Szene Ebene 1` [343470–343896]  
→ On the stairs she remembered the man with the roast goose.

**172.** `Nicht-Szene` [343897–344636]  
→ For several days she couldn't decide to visit Wiesing again.

**173.** `Szene Ebene 1` [344637–346240]  
→ This time a woman came towards her from the door opposite the shopkeeper's apartment.

**174.** `Nicht-Szene` [346242–347739]  
→ VIII  If Mama hadn't been so outraged back then and wouldn't have chased Wiesing away so mercilessly - and she herself had

**175.** `Szene Ebene 1` [347740–348356]  
→ Agathe went to her and told her about Luisen's death and about the suffering she was carrying around her - and Mama remained very calm

**176.** `Nicht-Szene` [348357–358802]  
→ Agathe really had no reason to be constantly upset and complain about her fate.

**177.** `Szene Ebene 1` [358803–359355]  
→ "... Just think, I made a terrible embarrassment of myself the other day," said Lisbeth Wendhagen.

**178.** `Nicht-Szene` [359357–364013]  
→ IX  She recently found a wonderful book in Dad's library.

**179.** `Szene Ebene 1` [364014–365458]  
→ He had been so terribly surprised when she handed him her wish list.

**180.** `Szene Ebene 1` [365459–366900]  
→ On her Christmas table she found a lovely pink crepe jabot - she had once seen it in a shop window

**181.** `Nicht-Szene` [366901–367537]  
→ Every time Agathe walked through her father's room and her eyes touched the bookcase, which was now locked,

**182.** `Nicht-Szene` [367539–369068]  
→ X  Uncle Gustav had died.

**183.** `Szene Ebene 1` [369069–370817]  
→ Now the large armchair by the window in which Uncle Gustav, dressed in a long, gray dressing gown, sat half a J

**184.** `Nicht-Szene` [370818–371820]  
→ At Uncle Gustav's funeral, Mama caught a cold and now she completely collapsed.

**185.** `Szene Ebene 1` [371821–372077]  
→ "How Agathe can stand it is incomprehensible to me," said Eugenie.

**186.** `Nicht-Szene` [372078–375254]  
→ Yes – it’s okay!

**187.** `Szene Ebene 1` [375256–379736]  
→ XI  Agathe got down on the floor.

**188.** `Szene Ebene 1` [379737–380465]  
→ Eugenie was waiting in the dining room.

**189.** `Szene Ebene 1` [380466–382703]  
→ Now the toys.

**190.** `Nicht-Szene` [382705–385441]  
→ XII  The government councilor Heidling heard from all sides that his daughter definitely needed to treat herself to some rest.

**191.** `Szene Ebene 1` [385442–387824]  
→ As a painter, Lutz has not achieved nearly what he once promised.

**192.** `Szene Ebene 1` [387825–388500]  
→ Eight days later, Agathe sat on the veranda of a Swiss guesthouse and looked over the tall pots of geraniums and carnations

**193.** `Szene Ebene 1` [388501–392152]  
→ Because of the long time spent awake at her mother's bedside, she had forgotten how to sleep peacefully.

**194.** `Nicht-Szene` [392153–394266]  
→ Unfortunately, Dad had the passion of early excursions.

**195.** `Szene Ebene 1` [394268–397430]  
→ XIII  Dad was playing dominoes with a gentleman who had recently spoken to him, a well-educated man, a professor

**196.** `Szene Ebene 1` [397431–399160]  
→ The afternoon was long for her, waiting in silence.

**197.** `Szene Ebene 1` [399161–401657]  
→ When she came home, she saw a gentleman standing on the porch railing next to the waitress and looking over the red carnations at him

**198.** `Szene Ebene 1` [401658–403166]  
→ The Swiss professor's verdict on Greffinger did not remain without influence on the tone in which the government councilor Heidl

**199.** `Szene Ebene 1` [403168–404678]  
→ They sailed on the water, or they sat on the veranda of the little inn down by the lake and talked a variety of things.

**200.** `Szene Ebene 1` [404679–405851]  
→ But she spoke of her relationship with her father, and he heard the accumulated anger in her voice.

**201.** `Nicht-Szene` [405852–406262]  
→ She wanted to show him that it was worth worrying about her well-being.

**202.** `Szene Ebene 1` [406263–406817]  
→ The government council was not unhappy about his daughter's dealings with Martin.

**203.** `Nicht-Szene` [406818–409702]  
→ So in the quiet mountain asylum, two worlds worked to save each other.

**204.** `Szene Ebene 1` [409703–412538]  
→ "You have to give me credit for staying here," he once said to Agathe.

**205.** `Nicht-Szene` [412539–415140]  
→ They returned home in silence, a long way over pale green, heavily scented meadows on which the sun shimmered

**206.** `Szene Ebene 1` [415142–417602]  
→ XIV  Girls with talent are to be envied,” Agathe complained to her cousin.

**207.** `Szene Ebene 1` [417603–425664]  
→ On top of the Hörnli he wrote in the inn's guest book: Mark Anton Grausiger, linen manufacturer and wife.

**208.** `Szene Ebene 1` [425665–427019]  
→ That evening after dinner, Martin asked her to go for a walk with him.

**209.** `Szene Ebene 1` [427020–428642]  
→ Why did she just walk and trot after Martin with her head bowed and her knees shaking unbearably

**210.** `Szene Ebene 1` [428643–430863]  
→ They didn't have to go very far before they came to a bridge that crossed the stream without railings.

**211.** `Szene Ebene 1` [430864–432505]  
→ And she was gone - shot out like lightning into the night and darkness.

**212.** `Szene Ebene 1` [432506–433267]  
→ At last she rose and crept back through the night.

**213.** `Szene Ebene 1` [433269–434512]  
→ XV  Mrs. Lieutenant Heidling was called to Switzerland by a telegram from her father-in-law.

**214.** `Szene Ebene 1` [434513–438450]  
→ When Agathe saw her sister-in-law, she fell into a fit of tears.

**215.** `Nicht-Szene` [438451–442481]  
→ But when they arrived, he immediately prescribed her a six-week treatment.

**216.** `Szene Ebene 1` [442482–442750]  
→ "This doctor is disgusting to me," Agathe explained after the first consultation.

**217.** `Nicht-Szene` [442751–448943]  
→ How they were observed when he sat down with them in the evening.

**218.** `Szene Ebene 1` [448944–450084]  
→ When Eugenie came home, she saw her sister-in-law's blinds still closed.

**219.** `Nicht-Szene` [450085–453778]  
→ The ladies sat and stood together in front of the Kurhaus until late into the night and discussed what had happened.
