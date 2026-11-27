import json
from pathlib import Path

import pytest

from app.monitor import run_monitoring

DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.mark.parametrize("batch, expected_drift", [("current", False), ("shifted", True)])
def test_bundled_batches_produce_a_report(tmp_path, batch, expected_drift):
    summary = run_monitoring(DATA / "reference", DATA / batch, tmp_path)
    assert summary["feature"] == "mean_brightness"
    assert summary["reference_images"] == summary["current_images"] == 30
    assert summary["drift_detected"] is expected_drift
    assert (tmp_path / "drift.html").stat().st_size > 1_000
    assert json.loads((tmp_path / "summary.json").read_text(encoding="utf-8")) == summary
