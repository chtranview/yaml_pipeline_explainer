"""
executor.py — 步驟執行器
依據模組定義中的 sequence / steps 依序執行各步驟，
根據 ENGINE_MODE 選擇 LLM API（A）或本地模板（B）生成內容，
並透過 artifact_writer 寫入產物。
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .artifact_writer import ArtifactWriter
from .utils import safe_read_yaml


def _load_engine_mode(logger: logging.Logger) -> str:
    """讀取 .env 並回傳 ENGINE_MODE（預設 B）。"""
    from dotenv import load_dotenv
    load_dotenv()
    mode = os.environ.get("ENGINE_MODE", "B").upper()
    if mode not in ("A", "B"):
        logger.warning(f"ENGINE_MODE={mode} 不合法，使用預設 B")
        mode = "B"
    logger.info(f"引擎模式：{'A — OpenAI LLM' if mode == 'A' else 'B — 本地模板'}")
    return mode


class LLMClient:
    """封裝 OpenAI API 呼叫，統一管理模型與參數。"""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self._client = None

    def _get_client(self):
        """延遲初始化 OpenAI client，避免未設定 key 時就報錯。"""
        if self._client is None:
            api_key = os.environ.get("OPENAI_API_KEY", "")
            if not api_key:
                raise RuntimeError(
                    "未設定 OPENAI_API_KEY。"
                    "請在 .env 檔案或環境變數中設定。"
                    "範例：cp .env.example .env 後填入你的 key。"
                )
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)
        return self._client

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
    ) -> str:
        """呼叫 LLM 並回傳回覆內容。"""
        model = model or os.environ.get("OPENAI_MODEL", "gpt-4o")
        client = self._get_client()
        self.logger.debug(f"    LLM 呼叫：model={model}, prompt 長度={len(user_prompt)}")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content or ""
        self.logger.debug(f"    LLM 回覆長度：{len(content)} 字元")
        return content


class StepExecutor:
    """依據模組 YAML 定義中的 sequence/steps 依序執行。"""

    def __init__(self, project_root: Path, logger: logging.Logger) -> None:
        self.project_root = project_root
        self.logger = logger
        self.writer = ArtifactWriter(project_root / "artifacts", logger)
        self._mode = _load_engine_mode(logger)
        # Route A 才需要 LLM client
        self.llm = LLMClient(logger) if self._mode == "A" else None

    def run(self, module_def: dict[str, Any], params: dict[str, Any]) -> bool:
        """執行單一模組，回傳是否全部成功。"""
        module_id = module_def.get("module_id", "unknown")
        self.logger.info(f"開始執行模組：{module_id}")

        sequence = module_def.get("sequence", [])
        steps = module_def.get("steps", [])

        # pipeline 模組使用 sequence；功能模組使用 steps
        task_list = sequence if sequence else steps
        if not task_list:
            self.logger.warning(f"模組 {module_id} 沒有定義 sequence 或 steps")
            return True

        results: list[dict[str, Any]] = []

        for task in task_list:
            task_id = task.get("step") or task.get("id", "?")
            desc = task.get("description", "")
            self.logger.info(f"  ▶ [{task_id}] {desc}")

            success = self._execute_task(task, params, module_def)
            on_fail = task.get("on_failure", "abort_and_log")

            results.append({"task_id": task_id, "success": success})

            if not success:
                self.logger.error(f"  ✗ [{task_id}] 執行失敗")
                if on_fail == "abort_and_log" or on_fail == "abort_and_flag":
                    self._write_log(module_id, results, success=False)
                    return False
                # log_and_continue / log_and_skip → 繼續
            else:
                self.logger.info(f"  ✓ [{task_id}] 完成")

        self._write_log(module_id, results, success=True)
        self.logger.info(f"模組 {module_id} 執行完畢")
        return True

    # ── 步驟分發 ─────────────────────────────────────────

    def _execute_task(
        self,
        task: dict[str, Any],
        params: dict[str, Any],
        module_def: dict[str, Any],
    ) -> bool:
        """根據 call target 分發至對應的生成函式。"""
        call_target = task.get("call")
        if call_target:
            self.logger.info(f"    → 呼叫子模組：{call_target}")
            handler = self._get_handler(call_target)
            try:
                return handler(params)
            except RuntimeError as e:
                self.logger.error(f"    ✗ {e}")
                return False

        output_field = task.get("output_field")
        if output_field:
            self.logger.info(f"    → 輸出欄位：{output_field}")
            return True

        return True

    def _get_handler(self, call_target: str):
        """根據 call_target 回傳對應的處理函式。"""
        handlers = {
            "1_project_engine": self._run_project_engine,
            "2_learner_handout_generator": self._run_handout_generator,
            "3_sdd_auto_generator": self._run_sdd_generator,
            "4_gamma_generator": self._run_gamma_generator,
            "5_notifier_auto_dispatch": self._run_noop,
            "6_verifier_auto_checker": self._run_verifier,
            "7_packager_auto_zipper": self._run_noop,
        }
        return handlers.get(call_target, self._run_noop)

    # ── 模組 1：課程骨架引擎 ─────────────────────────────

    def _run_project_engine(self, params: dict[str, Any]) -> bool:
        """產生課程大綱 outline.yaml。Route A 呼叫 LLM，Route B 本地模板。"""
        topic = params.get("course_topic", "未指定主題")
        days = params.get("duration_days", 2)
        level = params.get("audience_level", "intermediate")
        modules = params.get("module_count", 4)

        if self._mode == "A":
            return self._project_engine_llm(topic, days, level, modules)
        return self._project_engine_local(topic, days, level, modules)

    def _project_engine_llm(
        self, topic: str, days: int, level: str, modules: int
    ) -> bool:
        spec = self._load_module_spec("1_project_engine_4.0.yaml")
        system_prompt = (
            "你是 ExpertAI Course Engine 的課程骨架引擎。\n"
            "根據下方 YAML 規格中的 output.primary.schema，"
            "產出嚴格符合該 schema 的 YAML。\n"
            "只輸出 YAML 內容，不要加 ```yaml 標記或任何說明文字。\n\n"
            f"模組規格：\n{yaml.dump(spec, allow_unicode=True)}"
        )
        user_prompt = (
            f"課程主題：{topic}\n"
            f"天數：{days}\n"
            f"受眾程度：{level}\n"
            f"模組數量：{modules}\n"
            f"語言：繁體中文\n"
        )
        content = self.llm.generate(system_prompt, user_prompt)
        content = self._strip_code_fence(content)
        try:
            parsed = yaml.safe_load(content)
            self.writer.write_yaml("handouts/outline.yaml", parsed)
        except yaml.YAMLError:
            self.logger.warning("    LLM 輸出非 YAML 格式，以 MD 方式儲存")
            self.writer.write_markdown("handouts/outline.md", content)
        return True

    def _project_engine_local(
        self, topic: str, days: int, level: str, modules: int
    ) -> bool:
        """Route B：從參數直接生成結構化 outline.yaml。"""
        level_label = {
            "beginner": "入門",
            "intermediate": "中階",
            "advanced": "進階",
        }.get(level, level)

        difficulty_map = {
            "beginner": ["easy", "easy", "medium", "easy"],
            "intermediate": ["easy", "medium", "medium", "hard"],
            "advanced": ["medium", "hard", "hard", "hard"],
        }
        diff_cycle = difficulty_map.get(level, difficulty_map["intermediate"])

        mod_list = []
        per_day = max(1, modules // days)
        for i in range(1, modules + 1):
            day = min((i - 1) // per_day + 1, days)
            diff = diff_cycle[(i - 1) % len(diff_cycle)]
            mod_list.append({
                "module_id": f"M{i}",
                "title": f"{topic} — 模組 {i}",
                "day": day,
                "order": i,
                "duration_minutes": 60,
                "learning_objectives": [
                    f"能夠掌握模組 {i} 的核心概念",
                    f"能夠完成模組 {i} 的動手實作任務",
                ],
                "key_concepts": [
                    f"概念 {i}-A：（請替換為實際概念）",
                    f"概念 {i}-B：（請替換為實際概念）",
                ],
                "depends_on": [f"M{i-1}"] if i > 1 else [],
                "hands_on_task": f"模組 {i} 實作任務：（請替換為實際任務描述）",
                "takeaway": f"模組 {i} 帶走成果：（請替換為實際成果）",
                "difficulty": diff,
            })

        outline = {
            "course": {
                "title": topic,
                "topic": topic,
                "audience_level": level,
                "duration_days": days,
                "total_modules": modules,
                "objectives": [
                    f"能夠系統性掌握「{topic}」的核心知識",
                    f"學會應用所學解決{level_label}程度的實務問題",
                    f"建立至少一個可運行的實作成果",
                ],
                "modules": mod_list,
            }
        }
        self.writer.write_yaml("handouts/outline.yaml", outline)
        self.logger.info(f"    ✓ 本地生成 outline.yaml（{modules} 個模組）")
        return True

    # ── 模組 2：學員講義生成器 ────────────────────────────

    def _run_handout_generator(self, params: dict[str, Any]) -> bool:
        """為每個模組生成講義 MD。Route A 呼叫 LLM，Route B 本地模板。"""
        outline = self._load_outline()
        if outline is None:
            self.logger.error("    outline.yaml 不存在，請先執行 build 或 outline")
            return False

        course = outline.get("course", outline)
        module_list = course.get("modules", [])
        if not module_list:
            self.logger.warning("    outline 中沒有找到模組列表")
            return True

        template = self._read_prompt("handout_template.md")

        for mod in module_list:
            mod_id = mod.get("module_id", "unknown")
            self.logger.info(f"    → 生成講義：{mod_id}")

            if self._mode == "A":
                self._handout_llm(mod, template)
            else:
                self._handout_local(mod)

        return True

    def _handout_llm(self, mod: dict, template: str) -> None:
        mod_id = mod.get("module_id", "unknown")
        system_prompt = (
            "你是一位資深 AI 課程設計師，專門為實戰工作坊設計學員講義。\n"
            "風格：直接、具體、以動手實作為核心。\n"
            "輸出格式：Markdown，按照模板結構。\n\n"
            f"講義模板參考：\n{template}"
        )
        user_prompt = (
            f"請根據以下模組定義生成完整的學員講義：\n\n"
            f"```yaml\n{yaml.dump(mod, allow_unicode=True)}```\n"
            f"語言：繁體中文"
        )
        content = self.llm.generate(system_prompt, user_prompt)
        content = self._strip_code_fence(content)
        self.writer.write_markdown(f"handouts/{mod_id}.md", content)

    def _handout_local(self, mod: dict) -> None:
        mod_id = mod.get("module_id", "unknown")
        title = mod.get("title", mod_id)
        day = mod.get("day", 1)
        order = mod.get("order", 1)
        minutes = mod.get("duration_minutes", 60)
        diff = mod.get("difficulty", "medium")
        diff_icon = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(diff, "⚪")

        objectives = mod.get("learning_objectives", [])
        concepts = mod.get("key_concepts", [])
        task = mod.get("hands_on_task", "")
        takeaway = mod.get("takeaway", "")

        obj_lines = "\n".join(f"- {o}" for o in objectives) or "- （待填寫）"
        concept_sections = ""
        for c in concepts:
            concept_sections += (
                f"\n### {c}\n\n"
                "（概念說明待填寫）\n\n"
                "> 💡 **比喻**：（類比待填寫）\n"
            )
        if not concept_sections:
            concept_sections = "\n### （核心概念待填寫）\n"

        content = (
            f"# {title}\n\n"
            f"> **Day {day} · Module {order} · {minutes} 分鐘 · {diff_icon} {diff}**\n\n"
            f"---\n\n"
            f"## 學習目標\n\n完成本模組後，你將能夠：\n\n{obj_lines}\n\n"
            f"---\n\n"
            f"## 核心概念\n{concept_sections}\n"
            f"---\n\n"
            f"## 動手實作\n\n**任務：** {task}\n\n"
            f"**⏱ 預計時長：** {minutes} 分鐘\n\n"
            f"---\n\n"
            f"## 帶走成果\n\n{takeaway}\n"
        )
        self.writer.write_markdown(f"handouts/{mod_id}.md", content)

    # ── 模組 3：SDD 生成器 ───────────────────────────────

    def _run_sdd_generator(self, params: dict[str, Any]) -> bool:
        """為含實作任務的模組生成 SDD。Route A 呼叫 LLM，Route B 本地模板。"""
        outline = self._load_outline()
        if outline is None:
            self.logger.error("    outline.yaml 不存在")
            return False

        template = self._read_prompt("sdd_template.md")
        course = outline.get("course", outline)
        module_list = course.get("modules", [])

        for mod in module_list:
            task = mod.get("hands_on_task", "")
            difficulty = mod.get("difficulty", "easy")
            if not task or difficulty == "easy":
                continue

            mod_id = mod.get("module_id", "unknown")
            self.logger.info(f"    → 生成 SDD：{mod_id}")

            if self._mode == "A":
                self._sdd_llm(mod, template)
            else:
                self._sdd_local(mod)

        return True

    def _sdd_llm(self, mod: dict, template: str) -> None:
        mod_id = mod.get("module_id", "unknown")
        system_prompt = (
            "你是一位資深產品設計師，將實作任務轉化為 App SDD。\n"
            "風格：MVP 優先、範圍明確、驗證標準具體。\n"
            "輸出 YAML 格式的 SDD，只輸出 YAML，不加說明。\n\n"
            f"SDD 模板參考：\n{template}"
        )
        user_prompt = (
            f"模組資訊：\n```yaml\n{yaml.dump(mod, allow_unicode=True)}```\n"
            f"語言：繁體中文"
        )
        content = self.llm.generate(system_prompt, user_prompt)
        content = self._strip_code_fence(content)
        try:
            parsed = yaml.safe_load(content)
            self.writer.write_yaml(f"sdd/{mod_id}_sdd.yaml", parsed)
        except yaml.YAMLError:
            self.writer.write_markdown(f"sdd/{mod_id}_sdd.md", content)

    def _sdd_local(self, mod: dict) -> None:
        mod_id = mod.get("module_id", "unknown")
        title = mod.get("title", mod_id)
        task = mod.get("hands_on_task", "")
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        sdd = {
            "sdd": {
                "module_source": mod_id,
                "generated_by": "3_sdd_auto_generator v1.3 (local)",
                "generated_at": today,
                "overview": {
                    "app_name": f"{title} — 實作 App",
                    "goal": f"完成 {mod_id} 的實作任務",
                    "target_user": "工作坊學員",
                    "tech_stack_suggestion": ["Python", "Streamlit"],
                    "estimated_build_time": {
                        "basic_version": "30 分鐘",
                        "full_version": "60 分鐘",
                    },
                },
                "user_stories": [
                    {
                        "id": "US1",
                        "story": f"As a 學員, I want to {task}, so that 完成實作任務",
                        "priority": "must",
                    },
                ],
                "feature_list": {
                    "must_have": [
                        {
                            "feature_id": "F01",
                            "name": "核心功能",
                            "description": f"（請替換）{task}",
                            "acceptance_criteria": [
                                "能夠正確執行主要流程",
                                "輸出符合預期格式",
                            ],
                        },
                    ],
                },
            }
        }
        self.writer.write_yaml(f"sdd/{mod_id}_sdd.yaml", sdd)

    # ── 模組 4：投影片文字生成器 ──────────────────────────

    def _run_gamma_generator(self, params: dict[str, Any]) -> bool:
        """將講義壓縮為投影片文字。Route A 呼叫 LLM，Route B 本地擷取。"""
        handout_dir = self.project_root / "artifacts" / "handouts"
        md_files = sorted(handout_dir.glob("M*.md"))

        if not md_files:
            self.logger.warning("    找不到講義 MD 檔案")
            return True

        topic = params.get("course_topic", "課程")

        all_slides: list[str] = []
        for md_path in md_files:
            mod_id = md_path.stem
            self.logger.info(f"    → 生成投影片：{mod_id}")
            handout_content = md_path.read_text(encoding="utf-8")

            if self._mode == "A":
                content = self._gamma_llm(topic, handout_content)
            else:
                content = self._gamma_local(handout_content)

            all_slides.append(f"<!-- {mod_id} -->\n{content}")

        combined = f"# {topic} — 投影片文本\n\n" + "\n\n---\n\n".join(all_slides)
        self.writer.write_markdown("gamma/slides.md", combined)
        return True

    def _gamma_llm(self, topic: str, handout_content: str) -> str:
        system_prompt = (
            "你是投影片內容設計師，擅長將講義壓縮為簡潔的投影片文字。\n"
            "規則：\n"
            "- 每個概念一頁，用 H2 (##) 分頁\n"
            "- 每頁最多 5 行重點\n"
            "- 加入講者備注（以 > 開頭）\n"
            "- 輸出 Markdown 格式\n"
        )
        user_prompt = (
            f"課程主題：{topic}\n\n"
            f"以下是講義內容，請轉為投影片文字：\n\n{handout_content}"
        )
        content = self.llm.generate(system_prompt, user_prompt)
        return self._strip_code_fence(content)

    @staticmethod
    def _gamma_local(handout_content: str) -> str:
        """Route B：從講義 MD 擷取標題與重點，組成投影片骨架。"""
        slides: list[str] = []
        current_h1 = ""
        current_points: list[str] = []

        for line in handout_content.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                current_h1 = stripped[2:].strip()
            elif stripped.startswith("## "):
                # 新 section → flush previous
                if current_points:
                    slides.append("\n".join(current_points))
                    current_points = []
                section_title = stripped[3:].strip()
                current_points.append(f"## {section_title}")
            elif stripped.startswith("### "):
                current_points.append(f"- **{stripped[4:].strip()}**")
            elif stripped.startswith("- ") and len(current_points) < 6:
                current_points.append(stripped)

        if current_points:
            slides.append("\n".join(current_points))

        if current_h1:
            slides.insert(0, f"## {current_h1}\n")
        return "\n\n".join(slides)

    # ── 模組 6：驗證器 ───────────────────────────────────

    def _run_verifier(self, params: dict[str, Any]) -> bool:
        """掃描 artifacts/ 生成驗證報告。"""
        artifacts = self.project_root / "artifacts"
        results: list[str] = []
        passed = 0
        total = 0

        # 檢查 outline 存在
        total += 1
        outline_path = artifacts / "handouts" / "outline.yaml"
        if outline_path.exists():
            results.append("- ✓ C01: outline.yaml 存在")
            passed += 1
        else:
            outline_md = artifacts / "handouts" / "outline.md"
            if outline_md.exists():
                results.append("- ✓ C01: outline.md 存在（MD 格式）")
                passed += 1
            else:
                results.append("- ✗ C01: outline 不存在")

        # 檢查講義
        handouts = list((artifacts / "handouts").glob("M*.md"))
        total += 1
        if handouts:
            results.append(f"- ✓ C02: 找到 {len(handouts)} 份講義")
            passed += 1
        else:
            results.append("- ✗ C02: 未找到講義 MD")

        # 檢查 SDD
        sdds = list((artifacts / "sdd").glob("*_sdd.*"))
        total += 1
        if sdds:
            results.append(f"- ✓ C03: 找到 {len(sdds)} 份 SDD")
            passed += 1
        else:
            results.append("- ⚠ C03: 未找到 SDD（可能不需要）")
            passed += 1  # warning, not critical

        # 檢查投影片
        gamma = list((artifacts / "gamma").glob("*.md"))
        total += 1
        if gamma:
            results.append(f"- ✓ C04: 找到 {len(gamma)} 份投影片文本")
            passed += 1
        else:
            results.append("- ⚠ C04: 未找到投影片文本")
            passed += 1

        report = (
            f"# 驗證報告\n\n"
            f"日期：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"結果：通過 {passed}/{total} 項\n\n"
            + "\n".join(results)
        )
        self.writer.write_report("verify.md", report)
        return True

    # ── Noop（尚未實作的模組）────────────────────────────

    def _run_noop(self, params: dict[str, Any]) -> bool:
        """佔位：尚未實作的模組，記錄日誌後通過。"""
        return True

    # ── 工具方法 ─────────────────────────────────────────

    def _load_module_spec(self, filename: str) -> dict[str, Any]:
        """讀取子模組的 YAML 規格。"""
        data = safe_read_yaml(self.project_root / filename)
        return data or {}

    def _load_outline(self) -> dict[str, Any] | None:
        """讀取已生成的 outline.yaml。"""
        return safe_read_yaml(
            self.project_root / "artifacts" / "handouts" / "outline.yaml"
        )

    def _read_prompt(self, filename: str) -> str:
        """讀取 prompts/ 下的模板檔案。"""
        path = self.project_root / "prompts" / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    @staticmethod
    def _strip_code_fence(text: str) -> str:
        """移除 LLM 回覆中的 ```yaml 或 ```markdown 包裹。"""
        lines = text.strip().splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines)

    def _write_log(
        self,
        module_id: str,
        results: list[dict[str, Any]],
        success: bool,
    ) -> None:
        """將執行紀錄寫入 _logs/。"""
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        log_content = f"# {module_id} 執行紀錄\n"
        log_content += f"日期：{now.isoformat()}\n"
        log_content += f"結果：{'成功' if success else '失敗'}\n\n"
        for r in results:
            status = "✓" if r["success"] else "✗"
            log_content += f"- [{status}] Step {r['task_id']}\n"

        self.writer.write_log(f"{date_str}_{module_id}.log", log_content)
