"""Rebuild the monitoring batches from the Phase 1 Beans validation split."""

import argparse
import csv
import hashlib
from pathlib import Path
from shutil import copyfile

from PIL import Image, ImageEnhance


CLASSES = ("angular_leaf_spot", "bean_rust", "healthy")
SAMPLES_PER_CLASS = 10
DARKENING_FACTOR = 0.35


def write_batches(validation_dir: Path, output_dir: Path) -> None:
    selected = {"reference": [], "current": []}
    for label in CLASSES:
        candidates = sorted(
            (validation_dir / label).glob("*.jpg"),
            key=lambda path: hashlib.sha256(path.name.encode()).digest(),
        )
        if len(candidates) < 2 * SAMPLES_PER_CLASS:
            raise ValueError(f"Expected at least {2 * SAMPLES_PER_CLASS} JPEGs in {validation_dir / label}")
        selected["reference"].extend(candidates[:SAMPLES_PER_CLASS])
        selected["current"].extend(candidates[SAMPLES_PER_CLASS : 2 * SAMPLES_PER_CLASS])

    for batch in ("reference", "current", "shifted"):
        if (output_dir / batch).exists():
            raise FileExistsError(f"Choose a fresh output directory. Found {output_dir / batch}")

    manifest = []
    for batch, images in (*selected.items(), ("shifted", selected["current"])):
        target = output_dir / batch
        target.mkdir(parents=True)
        for index, source in enumerate(images, start=1):
            filename = f"leaf-{index:02d}.jpg"
            destination = target / filename
            if batch == "shifted":
                with Image.open(source) as image:
                    darkened = ImageEnhance.Brightness(image.convert("RGB")).enhance(DARKENING_FACTOR)
                    darkened.save(destination, format="JPEG", quality=92)
            else:
                copyfile(source, destination)
            manifest.append(
                {
                    "batch": batch,
                    "file": filename,
                    "validation_source": source.relative_to(validation_dir).as_posix(),
                    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                }
            )

    with (output_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(manifest[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("validation_dir", type=Path, help="Phase 1 data/raw/validation directory")
    parser.add_argument("output_dir", type=Path, help="Destination for the rebuilt batches")
    args = parser.parse_args()
    write_batches(args.validation_dir, args.output_dir)


if __name__ == "__main__":
    main()
