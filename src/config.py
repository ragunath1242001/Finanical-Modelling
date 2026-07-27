from pathlib import Path

APP_NAME = "European Banking Risk & Governance Lab"
APP_TAGLINE = "Interactive banking risk, regulatory reporting, data governance and model governance learning lab."
PORTFOLIO_DISCLAIMER = (
    "This is an independent educational portfolio project using synthetic data and simplified financial and "
    "regulatory assumptions. It was not developed for, deployed by or validated within a bank, regulator, "
    "employer or client."
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "synthetic"
AUDIT_DB = BASE_DIR / "data" / "processed" / "audit.sqlite"

DATA_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DB.parent.mkdir(parents=True, exist_ok=True)
