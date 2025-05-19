from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

DB_PATH = BASE_DIR / "bot/db.sqlite3"

MODELS_DIR = BASE_DIR / "detection" / "models"
XRAYS_DIR = BASE_DIR / "detection" / "xrays"
TEETH_DIR = BASE_DIR / "detection" / "teeth_img"