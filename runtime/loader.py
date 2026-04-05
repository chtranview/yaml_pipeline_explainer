"""
loader.py — YAML Pipeline 載入器
負責讀取 _index.yaml 及各模組 YAML 定義。
"""

from pathlib import Path
from typing import Any

import yaml

from .utils import safe_read_yaml


class PipelineLoader:
    """載入並快取 pipeline YAML 檔案。"""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self._cache: dict[str, Any] = {}

    def load_index(self) -> dict[str, Any] | None:
        """載入 _index.yaml 專案清單。"""
        return self._load("_index.yaml")

    def load_module(self, filename: str) -> dict[str, Any] | None:
        """載入指定的模組 YAML 定義。"""
        return self._load(filename)

    def list_modules(self) -> list[dict[str, Any]]:
        """回傳 _index.yaml 中的模組列表。"""
        index = self.load_index()
        if index is None:
            return []
        return index.get("modules", [])

    def get_command_mapping(self) -> dict[str, str]:
        """回傳 command → module file 的對應表。"""
        index = self.load_index()
        if index is None:
            return {}
        commands = index.get("commands", {})
        mapping: dict[str, str] = {}
        for cmd_name, cmd_def in commands.items():
            clean_name = cmd_name.lstrip("/")
            calls = cmd_def.get("calls", "")
            mapping[clean_name] = calls
        return mapping

    # ── 內部方法 ──────────────────────────────────────────

    def _load(self, filename: str) -> dict[str, Any] | None:
        if filename in self._cache:
            return self._cache[filename]
        filepath = self.project_root / filename
        data = safe_read_yaml(filepath)
        if data is not None:
            self._cache[filename] = data
        return data
