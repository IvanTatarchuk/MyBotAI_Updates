import logging
import logging.handlers
import os
from pathlib import Path

_LOG_DIR = Path(os.path.expanduser("~/.agent_programista/logs"))
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = _LOG_DIR / "agent.log"

_logger = logging.getLogger("agent_programista")
_logger.setLevel(logging.INFO)

_formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_file_handler = logging.handlers.RotatingFileHandler(
    _LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
)
_file_handler.setFormatter(_formatter)

if not any(isinstance(h, logging.handlers.RotatingFileHandler) for h in _logger.handlers):
    _logger.addHandler(_file_handler)


def get_logger() -> logging.Logger:
    return _logger