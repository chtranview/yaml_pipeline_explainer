"""
utils.py — 共用工具函式
"""

import logging
import sys
from pathlib import Path
from typing import Any

import yaml


def get_project_root() -> Path:
    """回傳專案根目錄（runtime/ 的上一層）。"""
    return Path(__file__).resolve().parent.parent


def setup_logging(level: str, project_root: Path) -> logging.Logger:
    """設定 logger，同時輸出至 console 與 _logs/ 檔案。"""
    log_dir = project_root / "artifacts" / "_logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger("ExpertAI")
    logger.setLevel(numeric_level)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(numeric_level)
    fmt = logging.Formatter("[%(levelname)s] %(message)s")
    console.setFormatter(fmt)
    logger.addHandler(console)

    # File handler
    file_handler = logging.FileHandler(
        log_dir / "runtime.log", encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    return logger


def safe_read_yaml(filepath: Path) -> dict[str, Any] | None:
    """安全讀取 YAML 檔案，失敗時回傳 None。"""
    if not filepath.exists():
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError:
        return None
