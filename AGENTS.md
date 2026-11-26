# Seña a seña - LSC5

This project combines a classifier for five isolated Colombian Sign Language signs with a camera practice prototype. Work covers applied ML, product experience and the exploration of a credible value proposition. Reply in Spanish; keep agent instructions in English.

## Start here

- Read [the project index](docs/00_INDEX.md) for current authorization and the next action. Keep stage status there; preserve completed technical work when moving to product or pitch preparation.
- For product and pitch work, read [the product context](docs/10_product_and_pitch_context.md), then [README](README.md) and [demo documentation](demo/README.md). Follow their evidence links as needed. [01](docs/01_problem_definition.md) owns competition rules and data boundaries; it is not a validated customer problem statement.
- Use `delivery-coordination` for continuation. Load `product-design` for experience and scope, `business-strategy` for buyers, positioning, sales and economics, and `proposal-writing` for a pitch or call, only as needed. Adapt to existing records rather than creating parallel templates.

## Product and pitch perspective

- Connect the user's problem, current alternatives, intended outcome and product journey. Explain how implemented design choices support that outcome; distinguish intended benefits from measured benefits.
- Distinguish learner, beneficiary, buyer and decision-maker. Explore a concrete offer, distribution channel, price hypothesis and cost drivers before making commercial claims. Keep product hypotheses and decisions in 10; keep authorization in the index.
- Build a clear, persuasive story from problem, experience, evidence, team and a specific ask. Establish audience, purpose, format and any rubric before drafting the pitch. Label proposed capabilities and validation plans separately from what works today.
- Separate model evaluation, usability, learning outcomes and commercial evidence. Development accuracy is not educational efficacy or customer traction. Use [canonical results](docs/07_results_and_publication_protocol.md) for figures and qualifications; never invent market size, customers, revenue, partners or an official score.
- Preserve confirmed attribution: alternatives were evaluated as a team; Camilo Cuellar developed the implementation, reproducible experiments and demo. Keep the five-sign scope explicit. Broader recognition, new features and model development need their own scope decision.

## Data, publication and verification

- Keep `data/` read-only. Test payloads are reserved for fixed-model inference. Exclude test from exploration, fitting, calibration, pretraining and selection. Never recover hidden labels or use label-bearing filenames as predictive features.
- Cite papers by DOI, stable primary reference or bibliography. Keep local full-text copies and private data and artifacts out of the public repository. Reuse the authorized anonymized figure with its simulated states identified; this does not grant permission to distribute dataset assets or remove demo access controls.
- Describe privacy accurately: the browser extracts landmarks from camera video and sends landmarks to the server for prediction and feedback. Never claim that all processing stays on the device.
- Use the approved item and its referenced contracts when implementing. Preserve architecture and OpenSpec review. Record actual evidence and links in canonical records.
- Checks: `.venv/bin/python -m pytest -q`; `openspec validate --all --strict`; `python3 -m json.tool docs/02_data_audit_public.json`. Verify local Markdown links. Implemented pilot commands and future interfaces are distinguished in the architecture record.
