# Hints

Try the TODO with the first hint. Open the next hint if you need a more specific pointer.

## Setup · uv does not recognize `--group`

Update uv with the method you used to install it.

- With the standalone installer, run `uv self update`.
- With Homebrew, run `brew upgrade uv`.
- With WinGet, run `winget upgrade --id astral-sh.uv -e`.

Reopen the terminal and repeat **Build and check the local environment** in the Lab Guide.

## Milestone 2 · TODO 1

<details>
<summary>Start from the variables already in the route</summary>

Look at the two lines above the TODO. They give you the loaded model and a decoded RGB image. The route should return a `Prediction`.

</details>

<details>
<summary>Find the helper and the available fields</summary>

Open `app/model.py` and find `predict`. Check its return type and `LeafModel.version`. Compare those values with the three fields of `Prediction` at the top of `app/main.py`.

</details>

<details>
<summary>Use the failing test to narrow it down</summary>

Read `tests/test_api.py` for the keys and HTTP status expected for a valid image. A `501` means the TODO is still in place. If the response has a validation error, check the field types and the confidence range.

</details>

## Milestone 3 · TODO 2

<details>
<summary>Find the two places to edit</summary>

Look for the trigger near the top of `.github/workflows/ci.yml` and the failing command in the API test step. The job already installs the locked environment.

</details>

<details>
<summary>Think about which branch each event filters</summary>

The pull request filter applies to its target branch. The push filter applies to the branch that receives the commit. For both events, use a `branches` list with one entry. Match the indentation in the existing YAML.

</details>

<details>
<summary>Reuse a command that already worked</summary>

Take the exact API test command from Milestone 2. For the image job, read `needs` and compare its value with the ID of the job that runs the tests.

</details>

## Milestone 2 or 4 · Port already in use

If Uvicorn reports that port 8000 is busy, start it on 8001 in the first terminal.

```text
uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8001
```

In Milestone 2, open `http://127.0.0.1:8001` in your browser and continue with the prediction. In Milestone 4, run the command below in the second terminal and record the new URL in your report.

```text
uv run --locked python -m tools.smoke --url http://127.0.0.1:8001
```

## Milestone 3 · Fix a CI failure

Open the failing job and read the first failed step. If the workflow file needs a correction, make it on `ci-checks` and push it to the same pull request.

```text
git add .github/workflows/ci.yml
git commit -m "Fix CI workflow"
git push
```

## Milestone 3 · Workflow push permission

If GitHub rejects the push because the token lacks the `workflow` scope, use the GitHub CLI sign-in commands from Milestone 1 and retry the push. If `gh` is missing, [install GitHub CLI](https://cli.github.com/) and reopen the terminal. If you already use GitHub CLI as your Git credential helper, refresh its scope first.

```text
gh auth refresh --hostname github.com --scopes workflow
gh auth setup-git
git push -u origin ci-checks
```

If the first push still fails, stay on `ci-checks`. Run both commands under **Record your branch and commit** in 3.2 of the Lab Guide and keep committing locally. Use `UNAVAILABLE` for checks you could not run. When GitHub access works again, retry `git push -u origin ci-checks` to publish your local commits.

## Milestone 4 · Staging troubleshooting

If your repository is missing from Render, open [Render on GitHub](https://github.com/apps/render/installations/new). Select your GitHub account, grant Render access to the lab repository and save. Return to the Render service setup and refresh the repository list. See [Render's guide to GitHub permissions](https://render.com/docs/git-provider#fixing-github-app-permissions).

If the local SHA differs from Checkpoint 3, check that you are on the recorded branch. Changes to `LAB_REPORT.md` are expected. Review any other changed files before starting the server. If you want to keep changes to the project files, commit them first.

If you stage a new commit, run the API test command from 3.1 again. Push the new commit if your branch is already on GitHub. Then start at **Record your branch and commit** in 3.2. Update Checkpoint 3 with the new SHA and its matching CI evidence. Use `UNAVAILABLE` for any missing CI evidence.

## Milestone 4 · Optional local container check

If Docker is already installed, stop any local Uvicorn server you started with Ctrl+C. In the first terminal, build the image from the project folder.

```text
docker build -t ai53-leaf-api .
```

In the first terminal, start the container on port 8000 if it is free.

```text
docker run --rm -p 127.0.0.1:8000:8000 ai53-leaf-api
```

If port 8000 is busy, start the container on port 8001. This maps port 8001 on your computer to port 8000 inside the container.

```text
docker run --rm -p 127.0.0.1:8001:8000 ai53-leaf-api
```

After the container starts, open a second terminal in the project folder. Run the smoke command for the port you chose.

**Port 8000**

```text
uv run --locked python -m tools.smoke --url http://127.0.0.1:8000
```

**Port 8001**

```text
uv run --locked python -m tools.smoke --url http://127.0.0.1:8001
```

Stop the container from the first terminal with Ctrl+C.

## Milestone 5 · TODO 3

<details>
<summary>Identify the comparison inputs</summary>

The two tables have one brightness value per photo in the `mean_brightness` column. Look just above TODO 3. `reference = image_features(reference_folder)` makes the brightness table from `data/reference/` in the lab. The next line makes `batch` from the folder picked by `--batch`. Evidently calls that input `current_data`, whether you pass CURRENT or SHIFTED.

</details>

<details>
<summary>Find the Evidently classes</summary>

`Report` and `DataDriftPreset` are already imported. Pass the preset inside a list when creating the report. Find the two input names under [Evidently Report.run](https://evidentlyai.github.io/evidently/api-reference/main/evidently/core/report.html#Report.run). Look for `current_data` and `reference_data`.

</details>

<details>
<summary>Give the rest of the function the object it expects</summary>

The code after the TODO calls `.dict()` and `.save_html()` on `snapshot`. Assign the return value of `.run()` to that name. Attach both tables to their corresponding named arguments.

</details>

## Milestone 5 · Retry an interrupted report

If you see “A report write or recovery is in progress”, wait for the other command if it is still running. If it stopped early, run the line for your batch with a new output folder.

```text
uv run --locked --group monitoring python -m app.monitor --reference data/reference --batch data/current --output reports/current-retry
uv run --locked --group monitoring python -m app.monitor --reference data/reference --batch data/shifted --output reports/shifted-retry
```

If the retry folder already exists, choose a fresh name after `--output`. Once the rerun succeeds, use its `drift.html` and `summary.json` together. The `.report-in-progress/` folder inside the interrupted output may hold copies of the previous report. Keep that folder if you need to recover those files.

## Milestone 5 · Share a commit when the push is blocked

If you could not push your final commit to GitHub, run this from the project folder after your last commit.

```text
git archive --format=zip --output=../lab2-final.zip HEAD
```

The command creates `lab2-final.zip` next to the project folder. It contains the files saved in your final commit. Share it with your repository URL and completed `LAB_REPORT.md`. Include the pull request URL if it is still open. Push the branch when GitHub access returns.
