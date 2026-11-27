# AI53 Phase 2 lab report

At each milestone, copy the observed results under **Checkpoint**, then answer the matching **Question** from the Lab Guide.

## Milestone 1 · Inspect the model handoff

### Checkpoint 1 · Evidence

- GitHub repository URL: https://github.com/PierreGuerout/AI53_MLOPS_TP
- Expected model version: `phase1-reference-v1`
- Three class labels: `angular_leaf_spot`, `bean_rust`, `healthy`
- First pushed commit SHA: 64d6c0a33db5e2e606b61aa5132bb5105b4df66a

### Question 1 · Explanation

Answer: Le git sert à identifier de manière unique chaque version du code et à s'assurer de son authenticité.

## Milestone 2 · Serve predictions with FastAPI

### Checkpoint 2 · Evidence

- Final API test count after TODO 1: 7
- Browser prediction JSON for `data/current/leaf-01.jpg` (`UNAVAILABLE` and the error shown if the page gives no prediction): {
  "label": "angular_leaf_spot",
  "confidence": 0.5016346573829651,
  "model_version": "phase1-reference-v1"
}

### Question 2 · Explanation

Answer: ready check si la page est prete a etre afficher. La version est utile pour comprendre le resultat comme vu en cours. 

## Milestone 3 · Run tests and build in GitHub Actions

### Checkpoint 3 · Evidence

- Local branch:
- Local commit SHA:
- Local API test count:
- Actions run source (`main`, `PULL REQUEST` or `UNAVAILABLE`):
- Actions run URL:
- `tests` job status:
- `docker-build` job status:
- Container smoke result or first failed CI step:

For the two job statuses, use `PASS`, `FAIL`, `PENDING`, `SKIPPED`, `CANCELLED` or `UNAVAILABLE`. Use `SKIPPED` when Actions shows that a job was skipped. Use `UNAVAILABLE` for missing CI evidence.

### Question 3 · Explanation

Answer:

## Milestone 4 · Verify a staging release

### Checkpoint 4 · Evidence

- Mode (`RENDER` or `LOCAL`):
- Target URL:
- Tested commit SHA:
- Expected model version from Checkpoint 1:
- Observed model version from `/ready` (`UNAVAILABLE` if it returned none):
- Smoke check result (`PASS` or `FAIL`):
- First error, if any:
- Earlier Render attempt, if switching to local (URL if available and reason for switching):

### Question 4 · Explanation

Answer:

## Milestone 5 · Compare input distributions

### Checkpoint 5 · Evidence

Fill each row from its own `summary.json`. Use the file from the CURRENT report for the first row and the file from the SHIFTED report for the second. In both files, `current_mean` is the mean brightness of the batch you checked. Use the exact `score` (p-value) and `threshold` (cutoff). Enter `DRIFT` when `drift_detected` is true and `NO DRIFT` when it is false.

| Batch | Reference mean (`reference_mean`) | Batch mean (`current_mean`) | Method | Score | Threshold | Result (`DRIFT` or `NO DRIFT`) |
| --- | --- | --- | --- | --- | --- | --- |
| `CURRENT` | | | | | | |
| `SHIFTED` | | | | | | |

- Final full test count:

### Question 5 · Explanation

Answer:
