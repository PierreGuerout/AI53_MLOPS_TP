# Monitoring images

The photos come from the part of the Beans dataset used to check the model in Phase 1. A batch is a group of photos. Each of the three batches has 30.

| Folder | Images |
| --- | --- |
| `reference/` | REFERENCE. The starting group has ten original photos per class. |
| `current/` | CURRENT. This group has ten different original photos per class. Treat them as incoming photos. |
| `shifted/` | SHIFTED. These are the same photos as CURRENT, darkened to 35% of their original brightness to mimic poor lighting. |

`manifest.csv` records the original validation filenames and SHA-256 hashes. Compare REFERENCE with CURRENT first, then with SHIFTED. The `--batch` option chooses the group to check. By default, the bundled CURRENT and SHIFTED runs save to `reports/current/` and `reports/shifted/` respectively. For a custom comparison, use `--output` to name the report folder. If you omit it, the command saves the report to a new folder under `reports/` and prints its path. `DRIFT` means the test found evidence of a brightness change. `NO DRIFT` means the evidence was too weak. The script measures each photo on a scale from 0 (black) to 1 (white). Evidently checks how the brightness values are spread across the two batches.

## Use a fresh download

The three folders are ready to use. To rebuild them from the original dataset, open the Phase 1 project and run one of its documented acquisition commands. Use the download command for an online copy.

```text
uv run --locked python scripts/download_dataset.py
```

Back in the Phase 2 project, use the resulting `data/raw/validation` folder and a fresh destination. Replace the quoted example path with the actual path on your machine.

```text
uv run --locked python tools/prepare_fixture_data.py "../AI53_MLOps_Project_Phase1_Starter/data/raw/validation" rebuilt-data
```

The rebuilt batch folders appear under `rebuilt-data/`. To compare the rebuilt groups, run the command below. It saves a separate report alongside the two lab reports.

```text
uv run --locked --group monitoring python -m app.monitor --reference rebuilt-data/reference --batch rebuilt-data/current --output reports/rebuilt-current
```

The original dataset is available from Makerere AI Lab. [Dataset repository](https://github.com/AI-Lab-Makerere/ibean) · [Beans dataset](https://huggingface.co/datasets/AI-Lab-Makerere/beans)

## Attribution

Makerere AI Lab, *Bean Disease Dataset*, 2020. Data collection in collaboration with the National Crops Resources Research Institute (NaCRRI), Uganda. See [MIT license notice](LICENSE.txt).
