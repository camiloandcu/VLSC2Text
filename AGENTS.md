# LatAm IA Challenge — LSC5

This project develops an offline classifier for five isolated Colombian Sign Language classes. Read [the project index](docs/00_INDEX.md) for the current stage, authorization and canonical records. Keep stage status in the index.

- Keep `data/` read-only. Test payloads are reserved for fixed-model inference. Exclude test from exploration, fitting, calibration, pretraining and selection. Never recover hidden labels or use label-bearing filenames as predictive features.
- Cite papers by DOI, stable primary reference or bibliography. Keep local full-text copies and private data and artifacts out of the public repository. Review the publication scope in the indexed plan.
- Use the approved item and its referenced contracts when implementing. Preserve architecture and OpenSpec review. Record actual evidence and links in canonical records.
- Checks: `.venv/bin/python -m pytest -q`; `openspec validate --all --strict`; `python3 -m json.tool docs/02_data_audit_public.json`. Verify local Markdown links. Implemented pilot commands and future interfaces are distinguished in the architecture record.
