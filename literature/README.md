# LSC5 research index

Checked: **2026-11-10**, America/Bogota. Stage 2: literature/tool research, promising adjacent-field transfers and a prioritized resource table. Experiments, implementation, training and dataset/model downloads remain outside this authorization.

## Canonical records

- [Problem definition](../docs/01_problem_definition.md): task, priorities, data contract, integrity rules and unresolved organizer questions.
- [Research synthesis](../docs/03_state_of_art.md): Spanish interpretation of the evidence, alternatives, limitations and transition to later work.
- [resources.csv](resources.csv): **canonical resource-level evidence index**; update it when a source or artifact changes.
- [01_priority_table.md](01_priority_table.md): human-readable view derived from the CSV; regenerate after index changes instead of maintaining independent facts.

**Inventory: 87 distinct resources with paper, preprint or tool available, plus one announcement-only 2027 project.** Availability is not peer review. The 87 comprise 25 sign-related resources, 22 skeleton/action resources, 22 visual/video resources and 18 temporal/domain-transfer resources. Related versions are deduplicated at contribution level; the Mantis family is deliberately consolidated.

| Available resource year | Count |
|---|---:|
| 2022 | 19 |
| 2023 | 20 |
| 2024 | 21 |
| 2025 | 17 |
| 2026 | 10 |

The 2027 horizon contains CSLR-XL as an announcement with paper/code pending. SignSeek already has a September 2026 preprint, and is counted once as 2026 even though its authors announce WACV 2027. No claim is made about the complete future 2027 literature or independently confirmed future conference acceptance.

## Research question and temporal boundaries

Which 2022–2027 recognition methods, pretrained representations and tools supply evidence or plausible mechanisms for five-class isolated Colombian Sign Language recognition with 1,125 training clips, three training signers, variable-length MediaPipe landmarks, RGB video and an unseen evaluation signer?

The lower bound is a 2022 publication or preprint. Earlier preprints with verified 2022 publication are retained with chronology disclosed. A substantive successor is distinct; preprint/conference versions of the same contribution are one entry. Supporting current documentation for older tools is discussed separately and does not inflate the minimum count.

The requested 2027 horizon extends beyond the checked date. Distinguish available publications/preprints/tools, future-venue announcements for already available 2026 manuscripts, and announcement-only future resources. Work released after the cutoff is outside the evidence assessed here. A journal volume labeled 2027 may be announced earlier; that label alone does not prove article/code availability.

## Search coverage and query log

Discovery used public web search followed by opening primary papers, proceedings, author projects, official repositories and model cards. Snippets and third-party summaries were leads only. When a primary site returned403/anti-bot pages, ordinary public HTTP GET, arXiv or an author repository provided a fallback. No private account or protected access was used.

| Stream | Executed query coverage / representative queries | Primary sources opened |
|---|---|---|
| Sign recognition | SPOTER; OpenHands; SignBERT+; BEST; NLA-SLR; TwoStream-SLR; SignCLIP; SignRep; SHuBERT; DSTA-SLR; HWGAT; Siformer; MediaPipe reconstruction/anchors; robust sign embeddings; cross-view recognition; SegSLR; GSP-MC; ASL Citizen; Icelandic low-resource 2026; PoET; SignVLM; Uni-Sign; VSNet; VLM evaluation 2026. | ACL Anthology, CVF, arXiv, publishers, university/author projects, official code and model cards. |
| Skeleton/action | PoseC3D; InfoGCN; EfficientGCN; PYSKL; STTFormer; Hyperformer; FR-Head; HD-GCN; MAMP; graph SkeletonMAE; AimCLR; HiCLR; MotionBERT; SkeleTR; SkateFormer; BlockGCN; HaLP; ProtoGCN; ActionMamba; SkeletonMamba; Simba; SkeletonGCL, including explicit 2025/2026 queries. | CVF, arXiv, Springer editorial and author repositories. |
| Video/visual | VideoMAE/v2; ST-Adapter; AdaptFormer; AIM; VideoMamba; VideoPrism; InternVideo2/2.5; V-JEPA/2/2.1; DINOv2/v3; UniFormer/v2; EVL; ViFi-CLIP; FROSTER; Task-Adapter; Perception Encoder; SigLIP2, including encoders/adaptation 2026. | Original papers/proceedings, author projects/repos and official model cards/catalogues. |
| Time series | "TS2Vec AAAI 2022 universal representation time series official github"; "TimeSiam ICML 2024 time series siamese pretraining official"; "MOMENT time series foundation models ICML 2024 official"; TF-C NeurIPS 2022; TimeMIL; TSLANet; ModernTCN; UniTS; TimeDART. | AAAI/arXiv, NeurIPS, PMLR, laboratory pages, official repos/model cards. |
| Recent temporal alternatives and audits | "time series classification 2026 foundation models OpenReview"; "Mantis classification github Feofanov 2026"; "ModernTCN Revisited github reproducibility"; UniShape 2026; TimEE 2026; TS2Vec-FM 2026; UniMTS. | Original articles/preprints, author code and model cards; audit's final OpenReview text was inaccessible, so its author repo is the evidence. |
| Domain generalization | "Fishr Invariant Gradient Variances Domain Generalization ICML 2022 paper"; "SAGM Sharpness Aware Gradient Matching domain generalization CVPR 2023"; "MIRO Domain Generalization by Mutual-Information Regularization with Pre-trained Models ECCV 2022". | PMLR, ECVA, arXiv and official repos. |
| 2027 horizon | "sign language recognition 2027 paper"; "skeleton action recognition 2027 ICLR"; "video recognition 2027 ICLR"; "isolated sign language recognition 2027 preprint"; "sign language ICLR 2027 recognition"; "sign language recognition 2026 2027 transformer". | CogVis projects, SignSeek manuscript and CSLR-XL announcement; Monash SignMAE/publisher leads inspected without creating unsupported performance claims. |
| Supporting software | MMAction2 model zoo/repo; MMPose WholeBody; MediaPipe Gesture Recognizer. | Official docs/repos, discussed separately from the counted methods. |

Queries above are normalized coverage records, not a complete engine transcript. This is a decision-oriented scoping review with targeted deep reading, not a PRISMA census. A fixed search ranking, exhaustive discovery count, recall guarantee and universal novelty claim are unavailable. Source/reference following extended discovery; absence from the index does not prove absence from the field.

## Inclusion and evidence depth

Include a distinct resource with an opened original source and a concrete connection to task, representation, generalization, data efficiency, computation, reproducibility or tooling. One dataset/benchmark contribution and a methodological audit are retained where useful. Popularity in image recognition or forecasting alone does not establish relevance.

Exclude duplicate versions, pre-2022 background from the count, unverified snippet-only leads and future claims without source evidence. Forecasting-only discoveries such as TimePFN/TimesFM did not become classification recommendations. A 2026 aggregate TSC-FM leaderboard with undisclosed dataset identities was not used as comparative authority. SKIM's future-code notice did not establish an executable resource. Publisher-blocked 2027 leads were not converted into measured evidence from snippets.

All 88 rows have an opened primary source. Review depth:

- **29**: selected primary-text method/result/limitation sections, with locators in notes.
- **55**: original abstract/page and artifact evidence as specified per row.
- **3**: author repository evidence; article text not verified in this consultation.
- **1**: project announcement with article pending.

"Selected sections" does not mean every page was audited. No result was locally reproduced. There is no blanket scientific-validity sign-off for all original studies.

Code, weights and licenses have separate fields. Empty code/weights URLs mean unverified, not proven absent. Promised releases are not released implementations. Model cards/catalogues establish listings, not successful download, binary integrity, full licensing review or environment compatibility. Benchmark dataset names provide evidence context; no external data was downloaded or approved for contest use.

## Prioritization and comparison

Available resources have **32 P1, 45 P2 and 10 P3** priorities; the separate 2027 announcement is P3.

- **P1**: first-reading value from direct fit, useful relevant mechanisms, artifacts or essential critical evidence. No deployment/4 GiB feasibility promise.
- **P2**: credible transfer with a material schema, domain, computation or integration mismatch.
- **P3**: exploratory, expensive, incompletely available or conditional under contest rules.

These are contextual reviewer judgments. Pros/cons/applicability/qualitative compute are interpretations, distinct from reported findings. Explicit author limitations remain separate from unextracted ones. Relative compute bands are not VRAM/runtime measurements; pretraining, adaptation and inference are separate costs.

Never build a common leaderboard from different datasets, signer/view splits, per-instance/per-class definitions, probes, fine-tuning, retrieval, WER or ensembles. Few labeled samples amid abundant unlabeled pretraining do not equal scarcity of total training data.

## Schema and maintenance

Fields: `id,priority,category,year,title,resource_type,modality,summary,evidence,dataset_protocol,author_limitations,transfer_pros,transfer_cons,applicability,compute,code_url,weights_url,artifact_status,license,source_url,source_type,verified_date,status,next_agent_note,review_depth,temporal_status`.

IDs are stable: S=sign, K=skeleton, V=visual/video, T=temporal/domain, A=horizon cases. Exact titles and primary arXiv/DOI/repository URLs support deduplication. Publication/first-preprint chronology is retained in notes/status. Year is bibliographic/resource year, not experiment year. Temporal flags distinguish announcement-only from available evidence.

When extending the CSV, open the original source and artifact pages, preserve IDs, update checked dates and reconcile affected synthesis claims. Never guess missing code, weights, licenses, author conclusions or first-online dates. Regenerate the Markdown table using the same IDs/fields; it presents source, modality/summary, review depth, contextual pros/cons, cost and artifact/license status. Intermediate input CSVs are removed after consolidation.

## Integration obligations

ML/data must reconcile topology, confidence/depth, handedness, missingness, clip length and signer grouping. Architecture/platform must distinguish backbone execution from trainable parameters and obtain UNAB's real quotas before commitments. Domain/privacy must preserve LSC semantics, attribution and separate data/code/weight permissions. Quality must retain benchmark protocols and artifact caveats.

All methods inherit the fixed-inference restriction. Do not learn from test, estimate target statistics, pseudo-label it or select against leaderboard feedback. Query/episode coupling requires mechanism review; deterministic per-sample transformations differ from target adaptation. Never retrieve labeled external copies of LSC5 or attempt hidden-label recovery.

This stage supplies evidence and reading priorities. Architecture selection, experimental design and implementation remain subsequent authorized work.

## Verification

Canonical CSV and table generation verified 88 unique IDs/titles/primary URLs, normalized arXiv-version deduplication, 26 fields, valid 2022–2027 bibliographic years, cutoff dates, nonempty required evidence and correct separation of 87 available resources from one announcement. Independent review passed: counts, table/source correspondence, date histories and author artifact caveats were checked. Primary-source spot checks covered SkeletonMamba, Hyperformer, SkateFormer, ProtoGCN, VideoPrism, V-JEPA 2.1, Task-Adapter, TS2Vec-FM, TimEE, SignSeek and CSLR-XL, plus OpenHands/DSTA-SLR/graph-SkeletonMAE availability notices. Local links and all 88 table rows (eight cells each) passed. Editorial spacing corrections were incorporated. This is a research-deliverable review, not reproduction of all studies, measured LSC5 feasibility, human design acceptance or authorization to implement.
