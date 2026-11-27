# AI53 MLOps | Project Phase 2

Use FastAPI to send a bean-leaf photo to the supplied model and get a prediction back. Run automated checks in GitHub Actions, try a release in staging and compare groups of photos with Evidently.

Open the extracted project folder in VS Code or another editor, then follow the five milestones in the Lab Guide. Run commands from the folder containing `pyproject.toml`. The setup uses Git, uv and Python 3.12. The included model and samples work without training or a full dataset download.

| Path | Purpose |
| --- | --- |
| `model/` | Model version, class labels, and ONNX file |
| `app/main.py`, `app/model.py` | API routes and code that runs the model |
| `app/index.html` | Prediction page with image preview and API response |
| `.github/ci-template.yml`, `Dockerfile` | Workflow starter and container build for staging |
| `tools/smoke.py` | Quick check of the running API and model version |
| `app/monitor.py`, `data/` | Evidently comparison and image batches |
| `docs/HINTS.md`, `LAB_REPORT.md` | Implementation hints and evidence template |

Once the server is running, open its base URL to try a prediction. Choose a supplied JPG and select **Send prediction request**. The API also accepts PNG. The page previews the photo and displays the JSON from `POST /predict`. Open **API docs** to see the route details.

Use the supplied public images for hosted staging. The monitoring command compares the included photo groups on your computer and saves the results in `reports/`. The lab ends with a team decision based on those reports.

For the included image subsets and the full Phase 1 dataset, see [Data and attribution](data/README.md).
