# Solo blind audit protocol for T02

This is an internal manual audit, not the instructor's hidden ground truth. Since the project is individual, the same author can perform a second-pass blind review, but must label it `solo blind audit` rather than an independent second reviewer.

The 20 rows are sampled with seed 42 from eval images that were not in the first 20-image queue. The reviewer has not previously seen these selected images in that queue. This reduces exposure to the model's earlier suggestions but does not create a second annotator or official gold set.

1. Open only each image path in `fixtures/t02_raw_qc/`; do not open the model score, rank, suggested action, or first-pass review while labeling.
2. Fill `reviewer`, `defect_type` and `is_defect` using the assignment's definitions. Fill `severity` only if the instructor supplied its meaning; otherwise leave it blank.
3. Fill `recognizability_pct`, `reviewer_action`, confidence and note as supplemental internal judgments. Use the scope in `reports/review_guideline_t02.md` (coarse object type, main color, relative position).
4. Save a completed copy as `t02_solo_blind_audit.csv`. Do not change pipeline thresholds based on these held-out images.
5. Report the result as a self-blind audit by one annotator. It cannot establish inter-rater agreement and does not replace instructor GT or official evaluation.
