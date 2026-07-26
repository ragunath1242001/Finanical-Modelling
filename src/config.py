from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "synthetic"
AUDIT_DB = BASE_DIR / "data" / "processed" / "audit.sqlite"

DATA_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DB.parent.mkdir(parents=True, exist_ok=True)
