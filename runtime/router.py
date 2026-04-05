"""
router.py — 指令路由器
根據使用者輸入的指令，找到對應的模組定義並驅動 executor 執行。
"""

import logging
from pathlib import Path
from typing import Any

from .loader import PipelineLoader
from .executor import StepExecutor
from .validator import InputValidator


class CommandRouter:
    """將 CLI 指令路由至對應的 pipeline 模組。"""

    def __init__(
        self,
        loader: PipelineLoader,
        project_root: Path,
        logger: logging.Logger,
    ) -> None:
        self.loader = loader
        self.project_root = project_root
        self.logger = logger
        self.executor = StepExecutor(project_root, logger)
        self.validator = InputValidator(logger)

    def dispatch(self, command: str, params: dict[str, Any]) -> bool:
        """根據指令名稱分發至對應模組，回傳是否成功。"""
        mapping = self.loader.get_command_mapping()
        module_ref = mapping.get(command)

        if module_ref is None:
            self.logger.error(f"未知的指令：/{command}")
            return False

        # 找到模組檔案
        module_file = self._resolve_module_file(module_ref)
        if module_file is None:
            self.logger.error(f"找不到模組定義檔案：{module_ref}")
            return False

        module_def = self.loader.load_module(module_file)
        if module_def is None:
            self.logger.error(f"無法載入模組：{module_file}")
            return False

        # 驗證輸入
        inputs_spec = module_def.get("inputs", [])
        if not self.validator.validate(params, inputs_spec):
            return False

        # 執行
        self.logger.info(f"路由至模組：{module_def.get('module_id', module_ref)}")
        return self.executor.run(module_def, params)

    def _resolve_module_file(self, module_ref: str) -> str | None:
        """將 _index.yaml 中的 calls 值對應到實際檔案名稱。"""
        modules = self.loader.list_modules()
        for m in modules:
            file = m.get("file", "")
            # 精確比對 module_ref（如 "0_build_pipeline"）與檔名前綴
            if file.replace(".yaml", "") == module_ref or file == module_ref:
                return file

        # 嘗試直接拼接
        candidate = f"{module_ref}.yaml"
        if (self.project_root / candidate).exists():
            return candidate
        return None
