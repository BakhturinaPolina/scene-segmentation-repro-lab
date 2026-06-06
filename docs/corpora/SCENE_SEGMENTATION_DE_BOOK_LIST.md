# scene_segmentation_de — Book Catalog

**Date:** 2026-06-05  
**Purpose:** Reference list for full replication of [Assessing the State of the Art in Scene Segmentation](https://aclanthology.org/2025.naacl-long.500/) (NAACL 2025) and for closing gaps in [`REPRODUCIBILITY_GAP_REVIEW.md`](../reproducibility/REPRODUCIBILITY_GAP_REVIEW.md).  
**Local raw texts:** `data/raw/scene_segmentation_de/` (40 files; 41 paper titles — Harry Potter chapters merged locally)  
**Upstream annotations:** `upstream/scene-segmentation/data/standoff/` and `upstream/scene-segmentation/data/full/`

---

## 1) Author and title list (41 texts)

Titles follow NAACL 2025 Appendix Table 6 (train/test split).  
Author names follow STSS 2021 shared-task metadata ([Table 3](https://ceur-ws.org/Vol-3001/paper1.pdf)) where the text appeared in STSS; later NAACL additions use standard bibliographic attribution.

| # | Author | Title | Author source |
|---|--------|-------|---------------|
| 1 | Jason Dark | Der Turm der 1000 Schrecken | STSS 2021 Table 3 |
| 2 | Andreas Kufsteiner | Wechselhaft wie der April | STSS 2021 Table 3 |
| 3 | Verena Kufsteiner | Lass Blumen sprechen | STSS 2021 Table 3 |
| 4 | Jana Paradigi; Ramon M. Randle | Deus Ex Machina | STSS 2021 Table 3 |
| 5 | Hugh Walker | Der Sohn des Kometen | STSS 2021 Table 3 |
| 6 | Frank Callahan | Die Abrechnung | STSS 2021 Table 3 |
| 7 | Jerry Cotton | Die Widows Connection | STSS 2021 Table 3 |
| 8 | Frank Rehfeld | Hetzjagd durch die Zeit | STSS 2021 Table 3 |
| 9 | Wolfgang Hohlbein | Als der Meister starb | STSS 2021 Table 3 |
| 10 | Manfred Weinland | Prophet der Apokalypse | STSS 2021 Table 3 |
| 11 | Jack Slade | Ein sündiges Erbe | STSS 2021 Table 3 |
| 12 | O. S. Winterfield | Immer wenn der Sturm kommt | STSS 2021 Table 3 |
| 13 | Friederike von Buchner | Wir schaffen es - auch ohne Mann | STSS 2021 Table 3 |
| 14 | G. F. Unger | Tausend Pferde | STSS 2021 Table 3 |
| 15 | Roma Lentz | Widerstand zwecklos | STSS 2021 Table 3 |
| 16 | Regine König | Bezaubernde neue Mutti | STSS 2021 Table 3 |
| 17 | Patricia Vandenberg | Die hochmütigen Fellmann-Kinder | STSS 2021 Table 3 |
| 18 | Marina Anders | Ein Weihnachtslied für Dr. Bergen | STSS 2021 Table 3 |
| 19 | Hedwig Courths-Mahler | Verschmäht | STSS 2021 Table 3 |
| 20 | Hedwig Courths-Mahler | Griseldis | STSS 2021 Table 3 |
| 21 | Marie von Ebner-Eschenbach | Krambambuli | Bibliographic (public domain) |
| 22 | Heinrich von Kleist | Das Erdbeben in Chili | Bibliographic (public domain) |
| 23 | Franz Kafka | Die Verwandlung | Bibliographic (public domain) |
| 24 | Annette von Droste-Hülshoff | Die Judenbuche | Bibliographic (public domain) |
| 25 | Theodor Storm | Der Schimmelreiter | Bibliographic (public domain) |
| 26 | Amy J. Fetzer | Im Dschungel der Lust | Bibliographic |
| 27 | Günter Dönges | Agenten und Spione | Bibliographic |
| 28 | Chrissie Black | Wenn Tote plötzlich wieder sprechen | Bibliographic |
| 29 | Walther Kabel / W. Belka | Der Geisterfelsen im Baikal-See | Bibliographic |
| 30 | Michelle Willingham | Die Braut des irischen Kriegers | Bibliographic |
| 31 | Katherine Garbera | Nur noch eine heiße Nacht mit dir! | Bibliographic |
| 32 | H. C. Hollister | In den Dreck getreten | Bibliographic |
| 33 | Peter Heben | Bomben für Dortmund | STSS 2021 Table 3 (Track 1 test) |
| 34 | Alfred Bekker | Die Begegnung | STSS 2021 Table 3 (Track 1 test) |
| 35 | Diana Laurent | Hochzeit wider Willen | STSS 2021 Table 3 (Track 1 test) |
| 36 | Emily Blake | Im Bann der Vampire | STSS 2021 Table 3 (Track 1 test) |
| 37 | Gabriele Reuter | Aus guter Familie | STSS 2021 Table 3 (Track 2 test) |
| 38 | Theodor Fontane | Effi Briest | STSS 2021 Table 3 (Track 2 test) |
| 39 | J. K. Rowling | Harry Potter VI - Kapitel Der Slug Club | Bibliographic (copyrighted; standoff only upstream) |
| 40 | J. K. Rowling | Harry Potter VI - Kapitel Schleim | Bibliographic (copyrighted; standoff only upstream) |
| 41 | Brüder Grimm | Hänsel und Gretel | Bibliographic (public domain) |

**Notes on authors**

- Dime-novel rows (#1–20, plus Track 1 test #33–36) use publisher/series pseudonyms in many cases; STSS Table 3 is the canonical project metadata.
- `Jerry Cotton` is a house pseudonym for the Jerry Cotton crime series (Bastei Lübbe), not a personal author name.
- `Walther Kabel` and `W. Belka` are pseudonyms used for the same work (*Der Geisterfelsen im Baikal-See*).

---

## 2) Paper train/test assignment (NAACL 2025 Table 6)

Cumulative training sets and evaluation subsets used in the paper:

| Paper subset | Texts in subset | Count |
|--------------|-----------------|------:|
| **STSS-Train** | Der Turm der 1000 Schrecken; Wechselhaft wie der April; Lass Blumen sprechen; Deus Ex Machina; Der Sohn des Kometen; Die Abrechnung; Die Widows Connection; Hetzjagd durch die Zeit; Als der Meister starb; Prophet der Apokalypse; Ein sündiges Erbe; Immer wenn der Sturm kommt; Wir schaffen es - auch ohne Mann; Tausend Pferde; Widerstand zwecklos; Bezaubernde neue Mutti; Die hochmütigen Fellmann-Kinder; Ein Weihnachtslied für Dr. Bergen; Verschmäht; Griseldis | 20 |
| **Train-with-High** | STSS-Train + Krambambuli; Das Erdbeben in Chili; Die Verwandlung; Die Judenbuche; Der Schimmelreiter | 25 |
| **Train-Full** | Train-with-High + Im Dschungel der Lust; Agenten und Spione; Wenn Tote plötzlich wieder sprechen; Der Geisterfelsen im Baikal-See; Die Braut des irischen Kriegers; Nur noch eine heiße Nacht mit dir!; In den Dreck getreten | 32 |
| **STSS-Test-1** | Bomben für Dortmund; Die Begegnung; Hochzeit wider Willen; Im Bann der Vampire | 4 |
| **STSS-Test-2** | Aus guter Familie; Effi Briest | 2 |
| **OOD-Test** | Harry Potter VI - Kapitel Der Slug Club; Harry Potter VI - Kapitel Schleim; Hänsel und Gretel | 3 |
| **Test-Full** | STSS-Test-1 + STSS-Test-2 + OOD-Test | 9 |

Per-title eval split (leave-one-text-out target when the text is not in Train-Full):

| Title | Eval split | In Train-Full |
|-------|------------|:-------------:|
| Der Turm der 1000 Schrecken | — (train) | ✓ |
| Wechselhaft wie der April | — (train) | ✓ |
| Lass Blumen sprechen | — (train) | ✓ |
| Deus Ex Machina | — (train) | ✓ |
| Der Sohn des Kometen | — (train) | ✓ |
| Die Abrechnung | — (train) | ✓ |
| Die Widows Connection | — (train) | ✓ |
| Hetzjagd durch die Zeit | — (train) | ✓ |
| Als der Meister starb | — (train) | ✓ |
| Prophet der Apokalypse | — (train) | ✓ |
| Ein sündiges Erbe | — (train) | ✓ |
| Immer wenn der Sturm kommt | — (train) | ✓ |
| Wir schaffen es - auch ohne Mann | — (train) | ✓ |
| Tausend Pferde | — (train) | ✓ |
| Widerstand zwecklos | — (train) | ✓ |
| Bezaubernde neue Mutti | — (train) | ✓ |
| Die hochmütigen Fellmann-Kinder | — (train) | ✓ |
| Ein Weihnachtslied für Dr. Bergen | — (train) | ✓ |
| Verschmäht | — (train) | ✓ |
| Griseldis | — (train) | ✓ |
| Krambambuli | — (train) | ✓ |
| Das Erdbeben in Chili | — (train) | ✓ |
| Die Verwandlung | — (train) | ✓ |
| Die Judenbuche | — (train) | ✓ |
| Der Schimmelreiter | — (train) | ✓ |
| Im Dschungel der Lust | — (train) | ✓ |
| Agenten und Spione | — (train) | ✓ |
| Wenn Tote plötzlich wieder sprechen | — (train) | ✓ |
| Der Geisterfelsen im Baikal-See | — (train) | ✓ |
| Die Braut des irischen Kriegers | — (train) | ✓ |
| Nur noch eine heiße Nacht mit dir! | — (train) | ✓ |
| In den Dreck getreten | — (train) | ✓ |
| Bomben für Dortmund | STSS-Test-1 | |
| Die Begegnung | STSS-Test-1 | |
| Hochzeit wider Willen | STSS-Test-1 | |
| Im Bann der Vampire | STSS-Test-1 | |
| Aus guter Familie | STSS-Test-2 | |
| Effi Briest | STSS-Test-2 | |
| Harry Potter VI - Kapitel Der Slug Club | OOD-Test | |
| Harry Potter VI - Kapitel Schleim | OOD-Test | |
| Hänsel und Gretel | OOD-Test | |

---

## 3) Local file mapping (`data/raw/scene_segmentation_de/`)

Expected filename pattern: `{Title} - {Author}.txt`

| Title | Local file present | Notes |
|-------|:------------------:|-------|
| All titles except Harry Potter (×2) | ✓ | 39 distinct files cover 39 titles |
| Harry Potter VI - Kapitel Der Slug Club | partial | Merged into `Harry Potter VI - J. K. Rowling.txt` |
| Harry Potter VI - Kapitel Schleim | partial | Merged into `Harry Potter VI - J. K. Rowling.txt` |

**Known local corpus issues** (see [`SCENE_SEGMENTATION_DE_COST_ESTIMATE.md`](SCENE_SEGMENTATION_DE_COST_ESTIMATE.md)):

- `Der Geisterfelsen im Baikal-See` and `Im Bann der Vampire` are byte-identical (duplicate content).
- `Die Verwandlung` and `Hänsel und Gretel` PDFs failed extraction in the cost-estimate pass.
- Several files are EPUB/PDF/RTF misnamed as `.txt`.

---

## 4) Upstream gold-annotation availability

| Annotation type | Location | Coverage |
|-----------------|----------|----------|
| Standoff JSON (MD5 + scene/sentence spans) | `upstream/scene-segmentation/data/standoff/{stss_train,stss_test_1,stss_test_2,ood_test,train_with_high,train_full,test_full}/` | All 41 titles |
| Full UIMA XMI (public-domain only) | `upstream/scene-segmentation/data/full/stss_test_2/` | STSS-Test-2 only (2 novels) |

Standoff folders mirror the paper subsets (`train_full`, `test_full`, etc.). Copyrighted texts (dime novels, Harry Potter, most Train-Full additions) ship as standoff annotations only; matching raw text must be sourced separately (as in `scene_segmentation_de`).

---

## 5) Reproducibility checklist linkage

| Gap (from `REPRODUCIBILITY_GAP_REVIEW.md`) | Status with this catalog |
|------------------------------------------|--------------------------|
| Missing paper-aligned evaluation corpus (Test-Full) | **Partially addressed:** titles and splits documented; raw texts mostly local; only STSS-Test-2 XMI verified in manifest |
| No pinned split/selection specification | **Addressed:** Table 6 mapping above |
| Missing Train-Full / STSS-Test-1 / OOD-Test assets | **Open:** need manifests + text–annotation MD5 verification per title |

**Next steps for full paper replication**

1. Split `Harry Potter VI - J. K. Rowling.txt` into the two OOD-Test chapters named in Table 6.
2. Verify each local raw file against upstream standoff `md5` hashes.
3. Add `data/manifests/scene_segmentation_de.json` with per-file checksums and split labels.
4. Extend reproduction entrypoint beyond STSS-Test-2 to Test-Full and Train-Full leave-one-text-out runs.

---

## References

- Zehe, Konle, et al. (2025). *Assessing the State of the Art in Scene Segmentation.* NAACL 2025. [ACL Anthology](https://aclanthology.org/2025.naacl-long.500/)
- Zehe, Konle, et al. (2021). *Shared Task on Scene Segmentation @ KONVENS 2021.* CEUR-WS Vol-3001. [Proceedings](https://ceur-ws.org/Vol-3001/paper1.pdf)
- Upstream repo: [LSX-UniWue/scene-segmentation](https://github.com/LSX-UniWue/scene-segmentation)
