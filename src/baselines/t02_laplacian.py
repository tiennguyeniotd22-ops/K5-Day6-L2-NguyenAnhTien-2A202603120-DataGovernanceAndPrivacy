"""Deterministic T02 baseline using one global Laplacian blur threshold.

The cutoff is the 20th percentile of dev sharpness (computed without labels).
The continuous score is monotonic in inverse sharpness so the evaluator can
rank all images; held-out labels are never read or used for tuning.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from ..common.contact_sheet import render_contact_sheet
from ..common.context import RunContext
from ..common.decision import Decision, write_decision
from ..common.image_ops import laplacian_variance, load_rgb
from ..common.manifest import verify_manifest
from ..common.review import make_review_queue, write_review_queue
from ..metrics.tracks import get_track


def run(ctx: RunContext) -> None:
    if ctx.track != "t02":
        raise ValueError(f"T02 Laplacian baseline supports only t02, got {ctx.track}")

    manifest = ctx.input_dir / "manifest.csv"
    problems = verify_manifest(manifest)
    if problems and ctx.config.get("strict_provenance", True):
        raise ValueError(f"Manifest verification failed: {problems[:3]}")

    metadata = pd.read_csv(ctx.input_dir / "images.csv", dtype=str).fillna("")
    required = {"image_id", "path", "camera_id", "light", "split"}
    missing = required.difference(metadata.columns)
    if missing:
        raise ValueError(f"images.csv missing columns: {sorted(missing)}")
    if metadata.empty or metadata.image_id.duplicated().any():
        raise ValueError("images.csv is empty or image_id is not unique")

    root = ctx.input_dir.resolve()
    sharpness = []
    for item in metadata.itertuples(index=False):
        image_path = (root / item.path).resolve()
        if not image_path.is_relative_to(root):
            raise ValueError(f"Image path outside input folder: {item.path}")
        if not image_path.is_file():
            raise FileNotFoundError(f"Missing image: {image_path}")
        sharpness.append(float(laplacian_variance(load_rgb(image_path))))

    features = metadata.copy()
    features["laplacian_variance"] = sharpness
    dev_values = features.loc[features.split == "dev", "laplacian_variance"].to_numpy(float)
    if not len(dev_values):
        raise ValueError("T02 baseline needs at least one dev image to freeze its global threshold")

    quantile = 0.20
    threshold = float(np.quantile(dev_values, quantile))
    # Strictly monotonic ranking; no threshold or labels from eval are used.
    features["score"] = 1.0 / (1.0 + features.laplacian_variance)
    features["pred_defect_type"] = np.where(features.laplacian_variance < threshold, "blur", "none")
    features["pred_action"] = np.where(features.laplacian_variance < threshold, "RECAPTURE", "KEEP")
    features["reason"] = "global_laplacian_threshold"
    features = features.sort_values(["score", "image_id"], ascending=[False, True], kind="mergesort")
    features.to_csv(ctx.out("baseline_features.csv"), index=False)
    with ctx.out("baseline_config.json").open("w", encoding="utf-8") as f:
        json.dump({"threshold_method": "dev_sharpness_quantile", "quantile": quantile,
                   "laplacian_variance_threshold": threshold, "n_dev": int(len(dev_values)),
                   "seed": ctx.seed}, f, indent=2)
        f.write("\n")

    budget = int(ctx.param("budget", 20))
    if budget <= 0:
        raise ValueError("budget must be positive")
    queue = make_review_queue(features, id_col="image_id", score_col="score", budget=budget,
                              reason_col="reason", action_col="pred_action", slice_col="light",
                              evidence_col="path")
    write_review_queue(queue, ctx.out("review_queue.csv"))
    render_contact_sheet(queue, ctx.out("contact_sheet.html"), image_root=ctx.input_dir,
                         title="T02 Laplacian Baseline Review")
    ranked = features.sort_values(["score", "image_id"], ascending=[False, True], kind="mergesort")
    ranked[["image_id", "score"]].to_csv(ctx.out(get_track(ctx.track).pred_file), index=False)
    ctx.stats.update(n_items=len(features), n_review_target=len(queue), n_dev=len(dev_values),
                     laplacian_threshold=threshold)
    write_decision(
        Decision(status="HOLD", reason_code="BASELINE_ONLY",
                 reason="Laplacian baseline output; not a release decision.",
                 owner=str(ctx.config.get("owner") or "UNASSIGNED"), scope=ctx.track,
                 evidence=[str(ctx.out("ranked_review.csv")), str(ctx.out("baseline_config.json"))]),
        ctx.out("decision.json"), ctx.out("decision_log.csv"))
