# Deployment

## Local Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

Use:

- entry point: `app.py`
- dependency file: `requirements.txt`
- Python version: compatible with Streamlit, pandas, NumPy and scikit-learn in `requirements.txt`

The project uses synthetic CSV data under `data/synthetic`. If files are missing, the loaders can regenerate synthetic data.

## Local SQLite

The educational audit log uses local SQLite under `data/processed`. On hosted environments, local persistence may reset when the app restarts or redeploys.

## Reset Demo State

Delete local generated SQLite audit files under `data/processed/` and rerun the app. Synthetic CSVs can be regenerated with:

```powershell
python -m src.data.generate_synthetic_data
```

## Troubleshooting

- If deployment says the repo is not connected, confirm the current branch is pushed to GitHub.
- If imports fail, run `python -m compileall -q app.py src tests`.
- If packages are missing, reinstall `pip install -r requirements.txt`.
- If Streamlit starts locally but not in cloud, check file-path case sensitivity and committed data/config files.

Hosted deployment was not retested during this final pass; local startup and AppTest checks were run.
