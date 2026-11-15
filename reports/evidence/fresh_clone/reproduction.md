# T02 fresh-clone reproduction evidence

## Checkout and environment

- Tested commit: `fa71e62` (`main`, source state before adding this evidence bundle).
- Checkout: fresh clone of the published repository into a temporary directory.
- Python: 3.11.5; new `.venv` created inside the clone; dependencies installed from `requirements.txt`. Exact resolved package versions are in `requirements_frozen.txt`.
- The original reviewed CSV was copied from `reports/t02_review_evidence.csv` into `out/poc/review_queue_reviewed.csv` before rerunning.

## Results

| Check/run | Result |
|---|---|
| `tools.preflight` | 0 failures; 2 optional warnings for real-data/model packs not needed by T02 |
| `pytest -q` | Exit 0; GT-dependent tests skipped because instructor overlay is absent |
| Laplacian baseline | Exit 0; 96 rows; dev threshold 186.9665985107422; runtime 0.9754 s; `HOLD / BASELINE_ONLY` |
| T02 PoC | Exit 0; 96 rows; 24 suspected; review 20/20; runtime 2.0317 s; `REWORK / RECAPTURE_REQUIRED` |

The ranking CSVs from the fresh clone are byte-for-byte identical to the prior local run. SHA-256:

- Baseline: `c3510dac921d0813e53bad8cacbc65bce374b0af6d827acf2c2eb23f0d722bbe`
- PoC: `23e2579da2aa101f6af4c1b2088c6c9ccf69cebe2cc1a32aa6bb2b4ac6821498`

This establishes reproducibility of the current code and output ranking. It does not establish model quality: no instructor GT was available, so Recall@B/Precision@B and the official baseline-vs-PoC comparison remain pending.

## Reproduction commands (Windows PowerShell)

```powershell
$clone = Join-Path $env:TEMP 'Day6-T02-repro'
git clone --branch main --single-branch https://github.com/tiennguyeniotd22-ops/K5-Day6-L2-NguyenAnhTien-2A202603120-DataGovernanceAndPrivacy.git $clone
Set-Location $clone
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m tools.preflight
.\.venv\Scripts\python.exe -m pytest -q
New-Item -ItemType Directory -Force out\poc | Out-Null
Copy-Item reports\t02_review_evidence.csv out\poc\review_queue_reviewed.csv
.\.venv\Scripts\python.exe -m src.main --track t02 --pipeline src.baselines.t02_laplacian --input fixtures/t02_raw_qc --config configs/lab.yaml --output out/baseline --offline --seed 42 --run-name baseline
.\.venv\Scripts\python.exe -m src.main --track t02 --input fixtures/t02_raw_qc --config configs/lab.yaml --output out/poc --offline --seed 42 --run-name poc
Get-FileHash out\baseline\ranked_review.csv,out\poc\ranked_review.csv -Algorithm SHA256
```

The temp folder used for this recorded run was unique. Choose a new folder name if `Day6-T02-repro` already exists.
