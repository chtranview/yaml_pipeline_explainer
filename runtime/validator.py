"""
validator.py — 輸入與產物驗證器
驗證使用者輸入是否符合模組 inputs 規範，
以及產物是否通過 6_verifier_auto_checker 的檢查規則。
"""

import logging
import re
from pathlib import Path
from typing import Any


class InputValidator:
    """驗證使用者提供的參數是否符合模組的 inputs 規範。"""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def validate(self, params: dict[str, Any], inputs_spec: list[dict]) -> bool:
        """檢查 params 是否滿足 inputs_spec 中的必填與型別要求。"""
        all_ok = True
        for spec in inputs_spec:
            field = spec.get("field", "")
            required = spec.get("required", False)
            value = params.get(field)

            if required and not value:
                self.logger.error(f"缺少必填參數：{field}")
                all_ok = False
                continue

            if value is not None:
                expected_type = spec.get("type", "string")
                if not self._check_type(value, expected_type):
                    self.logger.error(
                        f"參數 {field} 型別錯誤：預期 {expected_type}，實際 {type(value).__name__}"
                    )
                    all_ok = False

                options = spec.get("options")
                if options and value not in options:
                    self.logger.warning(
                        f"參數 {field} 的值 '{value}' 不在允許選項 {options} 中"
                    )
        return all_ok

    @staticmethod
    def _check_type(value: Any, expected: str) -> bool:
        type_map = {
            "string": str,
            "integer": int,
            "list": list,
            "boolean": bool,
        }
        return isinstance(value, type_map.get(expected, str))


class ArtifactValidator:
    """根據 6_verifier_auto_checker.yaml 的規則驗證產物品質。"""

    def __init__(self, artifacts_dir: Path, logger: logging.Logger) -> None:
        self.artifacts_dir = artifacts_dir
        self.logger = logger
        self.issues: list[dict[str, Any]] = []

    def check_file_exists(self, pattern: str) -> bool:
        """檢查是否存在匹配 pattern 的檔案。"""
        matches = list(self.artifacts_dir.glob(pattern))
        return len(matches) > 0

    def check_required_sections(
        self, filepath: Path, sections: list[str]
    ) -> list[str]:
        """檢查 Markdown 檔案是否包含所有必要段落，回傳缺少的段落。"""
        if not filepath.exists():
            return sections
        content = filepath.read_text(encoding="utf-8")
        missing = [s for s in sections if s not in content]
        return missing

    def check_no_placeholders(self, filepath: Path) -> list[dict[str, Any]]:
        """檢查檔案中是否有未替換的佔位符。"""
        pattern = re.compile(r"\{\{.*?\}\}|\[待填入\]|TODO|PLACEHOLDER")
        findings: list[dict[str, Any]] = []
        if not filepath.exists():
            return findings
        lines = filepath.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines, start=1):
            for match in pattern.finditer(line):
                findings.append(
                    {"file": str(filepath), "line": i, "text": match.group()}
                )
        return findings

    def run_all_checks(self, checks_config: list[dict]) -> dict[str, Any]:
        """執行所有驗證規則，回傳摘要報告。"""
        passed = 0
        failed = 0
        critical_count = 0

        for check in checks_config:
            check_type = check.get("type", "")
            severity = check.get("severity", "info")

            ok = self._dispatch_check(check)
            if ok:
                passed += 1
            else:
                failed += 1
                if severity == "critical":
                    critical_count += 1

        return {
            "passed": passed,
            "failed": failed,
            "total": passed + failed,
            "critical_count": critical_count,
            "issues": self.issues,
        }

    def _dispatch_check(self, check: dict) -> bool:
        """依據 check type 分派對應的驗證邏輯。"""
        check_type = check.get("type", "")
        if check_type == "structural":
            return self._run_structural(check)
        elif check_type == "content":
            return self._run_content(check)
        elif check_type == "schema":
            return self._run_schema(check)
        return True

    def _run_structural(self, check: dict) -> bool:
        rule = check.get("rule", {})
        assertion = rule.get("assert", "")
        if "EXISTS" in assertion:
            pattern = assertion.split(" ")[0]
            exists = self.check_file_exists(pattern)
            if not exists:
                self.issues.append(
                    {"check_id": check["check_id"], "message": f"缺少：{pattern}"}
                )
            return exists
        return True

    def _run_content(self, check: dict) -> bool:
        sections = check.get("required_sections", [])
        if sections:
            for md_file in self.artifacts_dir.glob("handouts/*.md"):
                missing = self.check_required_sections(md_file, sections)
                if missing:
                    self.issues.append(
                        {
                            "check_id": check["check_id"],
                            "message": f"{md_file.name} 缺少：{missing}",
                        }
                    )
                    return False
        return True

    def _run_schema(self, _check: dict) -> bool:
        # Schema 驗證需搭配具體 YAML schema 解析，此處為預留介面
        return True
