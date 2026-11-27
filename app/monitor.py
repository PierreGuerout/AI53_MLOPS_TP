import argparse
import json
from pathlib import Path
from shutil import copyfile
from uuid import uuid4

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset
from PIL import Image, ImageStat

FEATURE = "mean_brightness"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def image_features(folder: Path) -> pd.DataFrame:
    values = []
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            with Image.open(path) as image:
                values.append(ImageStat.Stat(image.convert("L")).mean[0] / 255)
    if not values:
        raise ValueError(f"No JPEG or PNG images found in {folder}.")
    return pd.DataFrame({FEATURE: values})


def run_monitoring(reference_folder: Path, current_folder: Path, output: Path) -> dict:
    reference = image_features(reference_folder)
    batch = image_features(current_folder)

    # TODO 3
    raise NotImplementedError("Complete TODO 3 first.")

    # Read the preset's results for the single feature in these reports.
    metrics = snapshot.dict()["metrics"]
    counts = next(item for item in metrics if item["metric_name"].startswith("DriftedColumnsCount("))
    drift = next(item for item in metrics if item["metric_name"].startswith("ValueDrift("))
    summary = {
        "feature": FEATURE,
        "reference_images": len(reference),
        "current_images": len(batch),
        "reference_mean": float(reference[FEATURE].mean()),
        "current_mean": float(batch[FEATURE].mean()),
        "method": drift["config"]["method"],
        "score": float(drift["value"]),
        "threshold": float(drift["config"]["threshold"]),
        "drift_detected": bool(counts["value"]["count"]),
    }

    save_report(snapshot, summary, output)
    return summary


def save_report(snapshot, summary: dict, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    pending = output / ".report-in-progress"
    try:
        pending.mkdir()
    except FileExistsError as error:
        raise OSError(
            f"A report write or recovery is in progress in {pending}. "
            "See docs/HINTS.md for the retry steps."
        ) from error

    filenames = ("drift.html", "summary.json")
    keep_backups = False
    try:
        snapshot.save_html(str(pending / "drift.html"))
        (pending / "summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )

        # Keep the previous report available if either replacement fails.
        for filename in filenames:
            existing = output / filename
            if existing.exists():
                copyfile(existing, pending / f"previous-{filename}")

        try:
            for filename in filenames:
                (pending / filename).replace(output / filename)
        except (OSError, KeyboardInterrupt):
            try:
                for filename in reversed(filenames):
                    if (pending / filename).exists():
                        continue
                    backup = pending / f"previous-{filename}"
                    if backup.exists():
                        backup.replace(output / filename)
                    else:
                        (output / filename).unlink()
            except OSError as error:
                keep_backups = True
                raise OSError(f"Report recovery files are in {pending}.") from error
            raise
    finally:
        if not keep_backups:
            for filename in filenames:
                (pending / filename).unlink(missing_ok=True)
                (pending / f"previous-{filename}").unlink(missing_ok=True)
            pending.rmdir()


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare brightness between two image batches.")
    parser.add_argument(
        "--reference", type=Path, default=Path("data/reference"),
        help="Starting group to compare against.",
    )
    parser.add_argument(
        "--batch", "--current", dest="batch", type=Path, default=Path("data/current"),
        help="Group of photos to check. --current is an older name for this option.",
    )
    parser.add_argument(
        "--output", type=Path,
        help="Report folder. Custom comparisons use a new folder when omitted.",
    )
    options = parser.parse_args()
    try:
        output = options.output
        if output is None:
            data = Path("data").resolve()
            batch = options.batch.resolve()
            bundled_pair = (
                options.reference.resolve() == data / "reference"
                and batch in (data / "current", data / "shifted")
            )
            folder = batch.name if bundled_pair else f"comparison-{uuid4().hex}"
            output = Path("reports") / folder
        summary = run_monitoring(options.reference, options.batch, output)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(summary, indent=2))
    print(f"Report saved to {output / 'drift.html'}")


if __name__ == "__main__":
    main()
