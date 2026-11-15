"""T02 Raw QC Triage: lightweight CPU-only PoC pipeline.

Copy to repository file: src/pipeline.py
No network, no ground-truth reads. Thresholds are illustrative and must
be frozen on dev before any held-out evaluation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .common.context import RunContext
from .common.decision import Decision, write_decision
from .common.manifest import verify_manifest
from .common.review import (
    apply_overrides,
    load_review_decisions,
    make_review_queue,
    write_review_queue,
)
from .common.contact_sheet import render_contact_sheet
from .common.image_ops import load_rgb, laplacian_variance, brightness_stats, to_gray
from .metrics.tracks import get_track


def _clip(x: float, lo: float, hi: float) -> float:
    return float(np.clip((x - lo) / (hi - lo), 0.0, 1.0))


def _blockiness(gray: np.ndarray) -> float:
    """Simple JPEG 8x8 boundary discontinuity proxy; not a trained classifier."""
    h, w = gray.shape
    if h < 16 or w < 16:
        return 1.0
    dx = np.abs(np.diff(gray, axis=1))
    dy = np.abs(np.diff(gray, axis=0))
    bx = np.arange(1, w) % 8 == 0
    by = np.arange(1, h) % 8 == 0
    edge = (float(dx[:, bx].mean()) + float(dy[by, :].mean())) / 2
    inner = (float(dx[:, ~bx].mean()) + float(dy[~by, :].mean())) / 2
    return (edge + 1.0) / (inner + 1.0)


def _risk_features(rgb: np.ndarray) -> dict[str, float]:
    gray = to_gray(rgb)
    sharpness = laplacian_variance(rgb)
    bright = brightness_stats(rgb)

    # Blur risk: sharpness high -> low risk. Log prevents huge values dominating.
    blur = 1.0 - _clip(float(np.log1p(sharpness)), np.log1p(4), np.log1p(130))

    # A night image with useful bright details need not be defective.
    dark = (
        0.65 * (1.0 - _clip(bright["mean"], 0, 70))
        + 0.35 * (1.0 - _clip(bright["p95"], 0, 115))
    )

    # Look for saturated pixels globally and inside 4x4 tiles (local glare).
    saturated = gray > 245
    tiles = np.array_split(saturated, 4, axis=0)
    max_tile = max(float(piece.mean()) for row in tiles for piece in np.array_split(row, 4, axis=1))
    glare = max(
        _clip(bright["frac_saturated"], 0.06, 0.36),
        _clip(max_tile, 0.32, 0.82),
    )

    blockiness = _blockiness(gray)
    compression = _clip(blockiness, 1.2, 3.0)
    return {
        "blur": float(blur), "glare": float(glare),
        "dark": float(dark), "compression": float(compression),
        "sharpness": float(sharpness), "brightness": float(bright["mean"]),
        "saturated_fraction": float(bright["frac_saturated"]),
        "blockiness": float(blockiness),
    }


# 01: Load and provenance check.
def load(ctx: RunContext) -> dict:
    manifest_path = ctx.input_dir / "manifest.csv"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Missing manifest: {manifest_path}")
    problems = verify_manifest(manifest_path)
    if problems:
        ctx.audit.log(actor="pipeline", action="provenance_problems",
                      item_id=str(manifest_path), after=problems[:20])
        if ctx.config.get("strict_provenance", True):
            raise ValueError(f"Manifest verification failed: {problems[:3]}")

    metadata_path = ctx.input_dir / "images.csv"
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Missing metadata: {metadata_path}")
    images = pd.read_csv(metadata_path, dtype=str).fillna("")
    required = {"image_id", "path", "camera_id", "light", "split"}
    missing = required.difference(images.columns)
    if missing:
        raise ValueError(f"images.csv missing columns: {sorted(missing)}")
    if images.empty or images.image_id.duplicated().any():
        raise ValueError("images.csv is empty or image_id is not unique")
    return {"images": images}


# 02: Compute quality-risk features for every image.
def process(ctx: RunContext, data: dict) -> pd.DataFrame:
    if ctx.track != "t02":
        raise ValueError(f"This pipeline supports only t02, got {ctx.track}")

    rows = []
    root = ctx.input_dir.resolve()
    for item in data["images"].itertuples(index=False):
        path = (root / item.path).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"Image path outside input folder: {item.path}")
        if not path.is_file():
            raise FileNotFoundError(f"Missing image: {path}")

        features = _risk_features(load_rgb(path))
        scores = {name: features[name] for name in ("blur", "glare", "dark", "compression")}
        main_reason = max(("glare", "dark", "blur", "compression"), key=scores.get)
        score = 0.7 * max(scores.values()) + 0.3 * float(np.mean(list(scores.values())))
        pred_type = main_reason if score >= 0.35 else "none"
        action = "RECAPTURE" if score >= 0.55 else "KEEP"
        rows.append({
            "image_id": item.image_id, "score": round(score, 6),
            "pred_defect_type": pred_type, "pred_action": action,
            "reason": main_reason, "path": item.path,
            "camera_id": item.camera_id, "light": item.light,
            "split": item.split, **features,
        })

    scored = pd.DataFrame(rows).sort_values(["score", "image_id"],
                                            ascending=[False, True], kind="mergesort")
    scored.to_csv(ctx.out("feature_table.csv"), index=False)
    ctx.stats["n_items"] = len(scored)
    ctx.stats["n_suspected"] = int((scored.pred_action == "RECAPTURE").sum())
    return scored.reset_index(drop=True)


# 03: Select top-B images for a human review.
def rank(ctx: RunContext, scored: pd.DataFrame) -> pd.DataFrame:
    budget = int(ctx.param("budget", 20))
    if budget <= 0:
        raise ValueError("budget must be positive")
    queue = make_review_queue(
        scored, id_col="image_id", score_col="score", budget=budget,
        reason_col="reason", action_col="pred_action",
        slice_col="light", evidence_col="path",
    )
    write_review_queue(queue, ctx.out("review_queue.csv"))
    render_contact_sheet(queue, ctx.out("contact_sheet.html"),
                         image_root=ctx.input_dir, title="T02 Image QC Review")
    ctx.stats["n_review_target"] = len(queue)
    return queue


# 04: Apply human corrections to pred_action; leave scores unchanged for evaluation.
def review(ctx: RunContext, scored: pd.DataFrame, queue: pd.DataFrame) -> pd.DataFrame:
    ctx.stats.update(n_reviewed=0, n_escalated=0, n_skipped=0)
    review_file = ctx.output_dir / "review_queue_reviewed.csv"
    if not review_file.exists():
        return scored.copy()

    reviewed = load_review_decisions(review_file)
    if reviewed.item_id.duplicated().any():
        raise ValueError("Duplicate item_id in review decisions")
    unexpected = set(reviewed.item_id) - set(queue.item_id)
    if unexpected:
        raise ValueError(f"Review contains images outside current top-B: {sorted(unexpected)[:5]}")

    for r in reviewed.itertuples(index=False):
        if r.reviewer_decision in ("edit", "reject") and r.override_value not in ("KEEP", "RECAPTURE"):
            raise ValueError(f"{r.item_id}: edit/reject requires override_value KEEP or RECAPTURE")
        if r.reviewer_decision not in ("edit", "reject") and r.override_value:
            raise ValueError(f"{r.item_id}: override_value only allowed for edit/reject")
        ctx.audit.log(actor=r.reviewer, action=f"review:{r.reviewer_decision}",
                      item_id=r.item_id, after=r.override_value or r.reviewer_decision,
                      reason=r.review_note)

    corrected = apply_overrides(scored, reviewed, id_col="image_id",
                                value_col="pred_action", audit=ctx.audit)
    ctx.stats["n_reviewed"] = int(reviewed.reviewer_decision.isin(["approve", "edit", "reject"]).sum())
    ctx.stats["n_escalated"] = int((reviewed.reviewer_decision == "escalate").sum())
    ctx.stats["n_skipped"] = int((reviewed.reviewer_decision == "skip").sum())
    return corrected


# 05: Batch-level decision policy (distinct from each image's KEEP/RECAPTURE).
def decide(ctx: RunContext, final: pd.DataFrame) -> Decision:
    target = int(ctx.stats.get("n_review_target", 0))
    reviewed = int(ctx.stats.get("n_reviewed", 0))
    escalated = int(ctx.stats.get("n_escalated", 0))
    queue = pd.read_csv(ctx.out("review_queue.csv"), dtype={"item_id": str})
    top_actions = final[final.image_id.astype(str).isin(queue.item_id)]
    n_recapture = int((top_actions.pred_action == "RECAPTURE").sum())

    if reviewed < target or escalated or ctx.stats.get("n_skipped", 0):
        status, code = "HOLD", "REVIEW_INCOMPLETE"
        reason = f"Completed {reviewed}/{target} reviews; escalations={escalated}."
    elif n_recapture:
        status, code = "REWORK", "RECAPTURE_REQUIRED"
        reason = f"Review completed; {n_recapture} top-B images require recapture."
    else:
        status, code = "GO", "TOP_B_APPROVED"
        reason = f"All {target} top-B images reviewed and none require recapture; unreviewed images remain a sampling risk."

    return Decision(status=status, reason_code=code, reason=reason,
                    owner=str(ctx.config.get("owner") or "UNASSIGNED"),
                    scope=ctx.track,
                    evidence=[str(ctx.out("ranked_review.csv")), str(ctx.out("review_queue.csv")),
                              str(ctx.out("audit_log.jsonl"))],
                    metrics={"n_items": len(final), "reviewed": reviewed,
                             "review_budget": target, "recapture_in_topB": n_recapture})


def run(ctx: RunContext) -> None:
    spec = get_track(ctx.track)
    data = load(ctx)
    scored = process(ctx, data)
    scored.to_csv(ctx.out("ranked_review_raw.csv"), index=False)
    queue = rank(ctx, scored)
    final = review(ctx, scored, queue)
    required = list(spec.pred_columns)
    missing = [c for c in required if c not in final.columns]
    if missing:
        raise ValueError(f"Missing required prediction columns: {missing}")
    ordered = required + [c for c in final.columns if c not in required]
    final[ordered].to_csv(ctx.out(spec.pred_file), index=False)
    write_decision(decide(ctx, final), ctx.out("decision.json"),
                   ctx.out("decision_log.csv"))
