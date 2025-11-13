import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class WivernoConfig:
    BASE_DIR = Path(__file__).resolve().parent.parent
    DEFAULT_TEMPLATE_PATH = BASE_DIR / "static" / "templates"
