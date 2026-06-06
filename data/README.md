# Data layout

Cookiecutter-style pipeline folders. Large binaries stay gitignored; checksum manifests under `manifests/` are tracked.

```
data/
├── manifests/              # pinned checksums (tracked)
│   ├── raw_txt.json
│   ├── stss_test_2.json
│   └── excel_prompting.json
├── raw/                    # untouched sources (gitignored)
│   ├── kleist_multilingual/   # DE/EN/RU Kleist smoke texts (+ EPUB source)
│   ├── excel/                 # sentence-level annotation workbooks
│   ├── dprose/                # dProse sentence CSV exports (327 files)
│   └── scene_segmentation_de/ # 40 German full-text novels
├── interim/                # derived, reproducible intermediates
├── processed/              # model-ready inputs (e.g. excel_prompting/)
└── review/                 # human review artifacts
    └── excel/              # workbooks with model predictions filled in
```

## Conventions

- **Manifests** list file names, optional `path` (relative to `data/`), size, and MD5.
- **STSS-Test-2 XMI** lives in `upstream/scene-segmentation/data/full/stss_test_2/`; verify with `python src/data/verify_data_manifest.py`.
- **Regenerate TXT manifest:** `python src/data/build_txt_manifest.py`
- **Regenerate Excel manifest:** `python scripts/data/prepare_excel_prompting_inputs.py`
