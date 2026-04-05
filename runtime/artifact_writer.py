"""
artifact_writer.py — 產物寫入器
負責將生成的內容寫入 artifacts/ 目錄下的正確位置。
"""

import logging
from pathlib import Path
from typing import Any

import yaml


class ArtifactWriter:
    """統一管理 artifacts/ 目錄下的檔案寫入。"""

    def __init__(self, artifacts_dir: Path, logger: logging.Logger) -> None:
        self.artifacts_dir = artifacts_dir
        self.logger = logger
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """確保所有子目錄存在。"""
        subdirs = [
            "handouts",
            "sdd",
            "gamma",
            "bundles",
            "_logs",
            "_reports",
            "_issues",
            "_queues",
        ]
        for d in subdirs:
            (self.artifacts_dir / d).mkdir(parents=True, exist_ok=True)

    def write_yaml(self, relative_path: str, data: dict[str, Any]) -> Path:
        """將字典寫入 YAML 檔案。"""
        target = self.artifacts_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
        target.write_text(content, encoding="utf-8")
        self.logger.info(f"已寫入 YAML：{target}")
        return target

    def write_markdown(self, relative_path: str, content: str) -> Path:
        """將 Markdown 內容寫入檔案。"""
        target = self.artifacts_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self.logger.info(f"已寫入 MD：{target}")
        return target

    def write_log(self, filename: str, content: str) -> Path:
        """寫入執行紀錄至 _logs/。"""
        return self.write_markdown(f"_logs/{filename}", content)

    def write_report(self, filename: str, content: str) -> Path:
        """寫入報告至 _reports/。"""
        return self.write_markdown(f"_reports/{filename}", content)

    def write_issue(self, filename: str, content: str) -> Path:
        """寫入問題至 _issues/。"""
        return self.write_markdown(f"_issues/{filename}", content)
