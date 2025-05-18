from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

MODELS_DIR = BASE_DIR / "detection" / "models"
XRAYS_DIR = BASE_DIR / "detection" / "xrays"
TEETH_DIR = BASE_DIR / "detection" / "teeth_img"