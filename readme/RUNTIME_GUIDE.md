# ExpertAI Course Engine · Runtime 操作指南
> RUNTIME_GUIDE.md · v4.0 · 2026-04-05

這份指南說明如何透過 **Python Runtime（CLI）** 在本地端執行完整的課程生成 Pipeline，適合需要離線執行、自動化整合或版本控管的團隊使用。

> 📌 若你需要在 ChatGPT / Claude 中以對話方式操作，請參閱 [PIPELINE_GUIDE.md](PIPELINE_GUIDE.md)。

---

## 目錄

1. [Runtime vs Pipeline 模式](#1-runtime-vs-pipeline-模式)
2. [環境準備](#2-環境準備)
3. [快速開始（5 分鐘）](#3-快速開始)
4. [CLI 完整指令說明](#4-cli-完整指令說明)
5. [VS Code 整合](#5-vs-code-整合)
6. [專案結構說明](#6-專案結構說明)
7. [Runtime 模組架構](#7-runtime-模組架構)
8. [常見問題與排解](#8-常見問題與排解)
9. [進階：擴展 Runtime](#9-進階擴展-runtime)
10. [貢獻與版本更新](#10-貢獻與版本更新)

---

## 1. Runtime vs Pipeline 模式

| 比較項目 | Pipeline 模式（PIPELINE_GUIDE） | Runtime 模式（本文件） |
|---------|-------------------------------|----------------------|
| 執行環境 | ChatGPT / Claude 對話視窗 | 本地 Python CLI |
| 驅動方式 | 貼入 YAML → AI 模擬執行 | `python -m runtime.main` 直接執行 |
| 適用場景 | 快速原型、單次生成 | 自動化 CI/CD、批次生成、團隊協作 |
| 產物輸出 | AI 回覆中複製 | 直接寫入 `artifacts/` 資料夾 |
| 品質穩定性 | 依賴 AI 模型、上下文長度 | 確定性執行，可重現結果 |
| 除錯方式 | 觀察 AI 輸出 | VS Code Debug、日誌檔、斷點 |

**核心概念不變：** 兩種模式共用同一套 YAML 規格（`_index.yaml`、`0_build_pipeline.yaml` 等）。Runtime 模式由 Python 程式讀取並執行 YAML 中定義的流程，而非由 AI 解讀執行。

```
                    ┌─────────────────────┐
                    │    YAML 模組定義      │
                    │  _index.yaml         │
                    │  0_build_pipeline    │
                    │  1_project_engine    │
                    │  6_verifier          │
                    └────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼                             ▼
   ┌──────────────────┐          ┌──────────────────┐
   │  Pipeline 模式    │          │  Runtime 模式     │
   │  ChatGPT/Claude  │          │  Python CLI       │
   │  ↓ 對話驅動       │          │  ↓ 指令驅動        │
   │  AI 解讀 YAML     │          │  loader → router  │
   │  回覆中輸出產物    │          │  → executor       │
   └──────────────────┘          │  → artifact_writer│
                                 │  → 寫入 artifacts/ │
                                 └──────────────────┘
```

---

## 2. 環境準備

### 系統需求

- Python 3.10+
- pip（隨 Python 安裝）
- VS Code（建議，非必要）

### 建立虛擬環境

```bash
cd yaml_pipeline_explainer
python -m venv .venv
```

啟用虛擬環境：

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux / macOS
source .venv/bin/activate
```

啟用後提示字元會出現 `(.venv)` 前綴，表示你已在隔離環境中。

### 安裝依賴

```bash
pip install -r requirements.txt
```

> 依賴套件：`pyyaml`、`openai`、`python-dotenv`。

### 設定引擎模式（.env）

Runtime 支援兩種引擎模式，透過 `.env` 中的 `ENGINE_MODE` 切換：

| 模式 | 說明 | 需要 API Key？ |
|------|------|---------------|
| **B（預設）** | 本地模板生成 — 快速跑通 pipeline、驗證流程結構 | 否 |
| **A** | OpenAI LLM 生成 — 產出高品質、完整內容 | 是 |

```powershell
# 複製範本
copy .env.example .env
```

`.env` 預設內容（Route B，開箱即用）：

```ini
ENGINE_MODE=B
# OPENAI_API_KEY=sk-your-key-here
# OPENAI_MODEL=gpt-4o
```

當你準備好 OpenAI API Key 後，切換為 Route A：

```ini
ENGINE_MODE=A
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o          # 可選，預設 gpt-4o
```

> ⚠️ `.env` 已列入 `.gitignore`，不會被提交到版本控制。

### 驗證安裝

```bash
python -m runtime.main --help
```

應顯示：

```
usage: ExpertAI_Course_Engine [-h] [--topic TOPIC] [--days DAYS]
                                [--level {beginner,intermediate,advanced}]
                                [--modules MODULES]
                                [--log-level {debug,info,warn,error}]
                                {build,outline,verify}
```

> ⚠️ 所有 `python` 指令請在啟用 `.venv` 後執行，或改用 `.venv/Scripts/python.exe` 完整路徑，以避免污染全域環境。

---

## 3. 快速開始

### Step 1：執行第一次 build

```bash
cd yaml_pipeline_explainer
python -m runtime.main build --topic "AI 系統設計工作坊：從使用者到設計者"
```

### Step 2：觀察輸出

終端機應顯示（預設 Route B）：

```
[INFO] ExpertAI Course Engine 啟動
[INFO] 指令：/build
[INFO] 引擎模式：B — 本地模板
[INFO] 路由至模組：build_pipeline
[INFO] 開始執行模組：build_pipeline
[INFO]   ▶ [1] 生成課程骨架與模組大綱
[INFO]     → 呼叫子模組：1_project_engine
[INFO]     ✓ 本地生成 outline.yaml（4 個模組）
[INFO]   ✓ [1] 完成
[INFO]   ▶ [2] 為每個模組生成學員講義
[INFO]     → 呼叫子模組：2_learner_handout_generator
[INFO]   ✓ [2] 完成
...
[INFO]   ▶ [5] 驗證所有產物品質
[INFO]     → 呼叫子模組：6_verifier_auto_checker
[INFO]   ✓ [5] 完成
[INFO] 模組 build_pipeline 執行完畢
```

> Route B 的產物含 `（請替換為實際概念）` 等佔位符，用於確認 pipeline 結構正確。
> 切換到 Route A（`ENGINE_MODE=A`）後，LLM 會生成完整內容。

### Step 3：檢查產物

```bash
# 查看執行紀錄
cat artifacts/_logs/runtime.log

# 查看生成的產物
ls artifacts/handouts/
ls artifacts/_reports/
```

### Step 4：執行品質驗證

```bash
python -m runtime.main verify
```

---

## 4. CLI 完整指令說明

### 基本語法

```bash
python -m runtime.main <command> [options]
```

### 可用指令

| 指令 | 說明 | 對應 YAML 模組 |
|------|------|---------------|
| `build` | 執行完整 pipeline | `0_build_pipeline.yaml` |
| `outline` | 只生成課程骨架 | `1_project_engine_4.0.yaml` |
| `verify` | 執行品質驗證 | `6_verifier_auto_checker.yaml` |

### 參數一覽

| 參數 | 型別 | 預設值 | 說明 |
|------|------|--------|------|
| `--topic` | string | （必填，build/outline 時） | 課程主題 |
| `--days` | int | 2 | 課程天數 |
| `--level` | string | intermediate | beginner / intermediate / advanced |
| `--modules` | int | 4 | 模組數量（2-10） |
| `--log-level` | string | info | debug / info / warn / error |

### 使用範例

```powershell
# 完整建置：入門級，3 天，6 個模組
python -m runtime.main build --topic "Python 資料分析實戰" --days 3 --level beginner --modules 6

# 只生成骨架
python -m runtime.main outline --topic "LLM 應用開發工作坊"

# 驗證產物品質（無需額外參數）
python -m runtime.main verify

# 開啟 debug 日誌
python -m runtime.main build --topic "AI 系統設計工作坊" --log-level debug
```

---

## 5. VS Code 整合

### 預設 Tasks（Ctrl+Shift+B）

專案的 `.vscode/tasks.json` 已預設三個快捷任務：

| Task 標籤 | 觸發方式 | 說明 |
|-----------|---------|------|
| `build: 執行完整 pipeline` | Ctrl+Shift+B → 選擇 | 會提示輸入課程主題 |
| `outline: 生成課程骨架` | Ctrl+Shift+B → 選擇 | 會提示輸入課程主題 |
| `verify: 執行品質驗證` | Ctrl+Shift+B → 選擇 | 直接執行 |

### Debug 配置（F5）

`.vscode/launch.json` 提供三個偵錯配置，支援在 runtime 程式碼中設定斷點：

| 配置名稱 | 說明 |
|---------|------|
| `Run Pipeline - build` | 以預設主題執行完整 pipeline |
| `Run Pipeline - outline` | 以預設主題生成骨架 |
| `Run Pipeline - verify` | 執行品質驗證 |

**除錯步驟：**

1. 在目標 `.py` 檔案中設定斷點（例如 `executor.py` 第 40 行）
2. 按 F5 選擇對應配置
3. 程式會在斷點暫停，可在 Variables 面板檢視 `module_def`、`params` 等變數

---

## 6. 專案結構說明

```
yaml_pipeline_explainer/
├─ _index.yaml                     # 專案清單：指令對照、模組索引、全域設定
├─ 0_build_pipeline.yaml           # 總指揮：定義執行序列與錯誤處理策略
├─ 1_project_engine_4.0.yaml       # 課程骨架引擎：拆解模組、分配時間
├─ 2_learner_handout_generator.yaml
├─ 3_sdd_auto_generator.yaml
├─ 4_gamma_generator.yaml
├─ 5_notifier_auto_dispatch.yaml
├─ 6_verifier_auto_checker.yaml    # 品質驗證：10 項檢查規則
├─ 7_packager_auto_zipper.yaml
├─ 8_bridge_connector.yaml
├─ 9_meta_loop.yaml
├─ 10_meeting_summary_generator.yaml
│
├─ runtime/                        # ← Python 執行層（本指南重點）
│  ├─ main.py                      #    CLI 入口 + argparse
│  ├─ loader.py                    #    讀取 YAML 定義
│  ├─ router.py                    #    指令 → 模組路由
│  ├─ validator.py                 #    輸入驗證 + 產物驗證
│  ├─ executor.py                  #    步驟依序執行 + 日誌
│  ├─ artifact_writer.py           #    統一寫入 artifacts/
│  └─ utils.py                     #    共用工具（logging / YAML 讀取）
│
├─ artifacts/                      # 所有產物輸出目錄
│  ├─ handouts/                    #    講義（outline.yaml / *.md）
│  ├─ sdd/                         #    App SDD 規格文件
│  ├─ gamma/                       #    投影片文本
│  ├─ bundles/                     #    打包 ZIP
│  ├─ _logs/                       #    執行紀錄（runtime.log）
│  ├─ _reports/                    #    驗證報告（verify.md）
│  ├─ _issues/                     #    問題追蹤
│  └─ _queues/                     #    改善待辦
│
├─ prompts/                        # 模板（Email / LINE / 講義 / SDD）
├─ samples/                        # 範例檔案
├─ readme/                         # 文件
│  ├─ PIPELINE_GUIDE.md            #    ChatGPT/Claude 操作指南
│  └─ RUNTIME_GUIDE.md             #    Python Runtime 操作指南（本文件）
│
├─ .venv/                          # Python 虛擬環境（.gitignore 已排除）
├─ .gitignore                      # 排除 .venv/ / __pycache__/ / .env
├─ requirements.txt                # pip freeze 產出的依賴鎖定檔
│
└─ .vscode/
   ├─ tasks.json                   #    快捷 Task 定義（使用 .venv python）
   └─ launch.json                  #    Debug 配置（使用 .venv python）
```

---

## 7. Runtime 模組架構

### 執行流程

```
使用者輸入 CLI 指令
      ↓
main.py          解析參數（argparse）
      ↓
loader.py        讀取 _index.yaml + 模組 YAML
      ↓
router.py        比對 command → module file
      ↓
validator.py     驗證輸入參數（必填 / 型別 / 範圍）
      ↓
executor.py      依序執行 sequence[] 或 steps[]
      ↓
artifact_writer.py  將產物寫入 artifacts/ 對應子目錄
      ↓
artifacts/_logs/    寫入執行紀錄
```

### 各模組職責

| 模組 | 職責 | 關鍵方法 |
|------|------|---------|
| `main.py` | CLI 入口，組裝各元件 | `main()` → `parse_args()` |
| `loader.py` | 讀取並快取 YAML 定義 | `load_index()`, `load_module()`, `get_command_mapping()` |
| `router.py` | 將指令路由至對應模組 | `dispatch(command, params)` |
| `validator.py` | 驗證輸入與產物品質 | `InputValidator.validate()`, `ArtifactValidator.run_all_checks()` |
| `executor.py` | 依步驟執行模組邏輯 | `run(module_def, params)` |
| `artifact_writer.py` | 統一管理檔案寫入 | `write_yaml()`, `write_markdown()`, `write_log()` |
| `utils.py` | 共用工具函式 | `setup_logging()`, `safe_read_yaml()`, `get_project_root()` |

### 資料流

```
_index.yaml ──→ loader ──→ command_mapping
                              ↓
CLI args ──→ main ──→ router.dispatch("build", params)
                              ↓
0_build_pipeline.yaml ──→ loader ──→ module_def
                                       ↓
                              executor.run(module_def, params)
                                       ↓
                              ┌── step 1: call 1_project_engine
                              │         → 生成 outline.yaml
                              │         → artifacts/handouts/
                              │
                              └── step 2: call 6_verifier
                                        → 讀取 artifacts/**
                                        → artifacts/_reports/verify.md
                                        → artifacts/_issues/ (若有問題)
```

---

## 8. 常見問題與排解

### Q：執行 `python -m runtime.main` 出現 ModuleNotFoundError？

**原因：** 工作目錄不正確，Python 找不到 `runtime` 套件。

**解法：**
```bash
# 確保在專案根目錄執行
cd yaml_pipeline_explainer
python -m runtime.main build --topic "測試"
```

若仍然失敗，確認 `runtime/` 目錄下無 `__init__.py` 遺漏（目前設計為隱式 namespace package，Python 3.3+ 支援）。如需要可手動建立：
```bash
# Windows
echo. > runtime\__init__.py
```

---

### Q：`yaml` 模組找不到（No module named 'yaml'）？

**解法：**
```bash
# 確認已啟用 .venv
.\.venv\Scripts\Activate.ps1    # Windows
source .venv/bin/activate        # Linux/macOS

pip install -r requirements.txt
```

若不想啟用 venv，也可直接使用完整路徑：
```bash
.\.venv\Scripts\pip.exe install -r requirements.txt
```

---

### Q：日誌太多/太少，如何調整？

**解法：** 使用 `--log-level` 參數：

```bash
# 只看錯誤
python -m runtime.main build --topic "..." --log-level error

# 顯示完整 debug 資訊（含 YAML 解析細節）
python -m runtime.main build --topic "..." --log-level debug
```

日誌同時輸出至終端機與 `artifacts/_logs/runtime.log`。

---

### Q：如何清除所有產物重新開始？

**解法：**
```powershell
# Windows PowerShell
Get-ChildItem artifacts -Recurse -File | Where-Object { $_.Name -ne '.gitkeep' } | Remove-Item
```
```bash
# Linux / macOS
find artifacts -type f ! -name '.gitkeep' -delete
```

---

### Q：想新增指令（例如 `/handout`），要改哪些地方？

1. 確認對應的 YAML 模組已存在（如 `2_learner_handout_generator.yaml`）
2. 在 `main.py` 的 `choices` 中加入 `"handout"`
3. 在 `_index.yaml` 的 `commands` 中確認 `/handout` 已定義
4. 若模組有特殊參數，在 `main.py` 的 `parse_args()` 中新增 `--module-id` 等參數
5. （選用）在 `.vscode/tasks.json` 新增對應 Task

---

### Q：Route B 的產物內容都是佔位符，正常嗎？

**正常。** Route B（`ENGINE_MODE=B`）使用本地模板生成，目的是快速驗證 pipeline 流程與檔案結構。產出中的 `（請替換為實際概念）` 等文字是預期行為。

切換到 Route A（`ENGINE_MODE=A` + 設定 `OPENAI_API_KEY`）後，所有內容會由 LLM 生成完整版本。

---

### Q：Route A 執行時出現「未設定 OPENAI_API_KEY」？

**解法：** 確認 `.env` 中 `ENGINE_MODE=A` 且 `OPENAI_API_KEY` 已正確填入（非註解）：

```ini
ENGINE_MODE=A
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 9. 進階：擴展 Runtime

### 雙模式架構（A / B）

`executor.py` 的每個 handler 都支援兩條路徑：

| ENGINE_MODE | 行為 | 適用場景 |
|-------------|------|----------|
| **B**（預設） | 本地模板：從參數直接組合結構化內容 | 快速測試、離線、CI/CD |
| **A** | OpenAI LLM：呼叫 API 生成完整內容 | 正式生成高品質課程 |

每個子模組呼叫（`call`）對應一個 handler，handler 內部根據 `_mode` 分流：

| call target | handler | Route B 產出 | Route A 產出 |
|-------------|---------|-------------|-------------|
| `1_project_engine` | `_run_project_engine()` | 結構化 outline（含佔位符） | LLM 生成完整大綱 |
| `2_learner_handout_generator` | `_run_handout_generator()` | 模板講義 MD | LLM 生成完整講義 |
| `3_sdd_auto_generator` | `_run_sdd_generator()` | 模板 SDD YAML | LLM 生成完整 SDD |
| `4_gamma_generator` | `_run_gamma_generator()` | 從 MD 擷取標題重點 | LLM 壓縮為投影片文字 |
| `6_verifier_auto_checker` | `_run_verifier()` | 掃描 artifacts 生成報告 | 同左（不需 LLM） |
| `5_notifier` / `7_packager` | `_run_noop()` | （尚未實作） | （尚未實作） |

執行流程：
```
executor._execute_task()
    ↓ 取得 call_target
    ↓ _get_handler() → 對應處理函式
    ↓ 檢查 self._mode
    ├─ B → 本地模板生成（不需網路）
    └─ A → LLM: 讀取 YAML 規格 + prompts/ 模板
              → 組合 system_prompt + user_prompt
              → LLMClient.generate() → OpenAI API
              → 解析回覆、移除 code fence
    ↓ ArtifactWriter 寫入 artifacts/
```

### 自訂 LLM 模型

在 `.env` 中設定 `OPENAI_MODEL` 即可切換模型：

```ini
OPENAI_MODEL=gpt-4o-mini    # 更快、更便宜
OPENAI_MODEL=gpt-4o         # 預設，品質最佳
```

### 新增模組 handler

在 `executor.py` 中新增處理函式，並在 `_get_handler()` 的 `handlers` dict 中註冊：

```python
# 1. 新增 handler
def _run_my_module(self, params: dict[str, Any]) -> bool:
    spec = self._load_module_spec("11_my_module.yaml")
    template = self._read_prompt("my_template.md")
    content = self.llm.generate(
        system_prompt=f"你是...\\n{yaml.dump(spec, allow_unicode=True)}",
        user_prompt=f"主題：{params.get('course_topic')}",
    )
    self.writer.write_markdown("handouts/my_output.md", content)
    return True

# 2. 在 _get_handler() 中註冊
handlers = {
    ...
    "11_my_module": self._run_my_module,
}
```

### 搭配 CI/CD

```yaml
# .github/workflows/course-build.yml
name: Course Build
on:
  push:
    paths: ['_index.yaml', '*.yaml']
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python -m runtime.main build --topic "${{ github.event.head_commit.message }}"
      - run: python -m runtime.main verify
      - uses: actions/upload-artifact@v4
        with:
          name: course-artifacts
          path: artifacts/
```

### 搭配 MCP Filesystem（Claude Desktop）

若同時使用 Pipeline 模式（Claude）與 Runtime 模式，可共用同一個 `artifacts/` 目錄：

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/yaml_pipeline_explainer"
      ]
    }
  }
}
```

Claude 透過 MCP 寫入 `artifacts/`，Runtime 的 `verify` 指令可直接驗證 Claude 的輸出品質。

---

## 10. 貢獻與版本更新

### 修改 Runtime 模組的標準流程

```
1. 確認要修改的模組（loader / router / executor / ...）
2. 在對應 .py 檔案中修改邏輯
3. 使用 VS Code Debug（F5）設斷點驗證
4. 確認 artifacts/_logs/runtime.log 無錯誤
5. 執行 verify 確認產物品質未受影響
```

### 新增 YAML 模組與 Runtime 支援的流程

```
1. 建立新的 YAML 模組定義（如 11_new_module.yaml）
2. 在 _index.yaml 的 modules[] 與 commands 中註冊
3. 在 main.py 的 choices 中加入新指令
4. 在 executor.py 中加入對應的執行邏輯
5. （選用）在 .vscode/tasks.json 加入快捷 Task
```

### 建議的 Git 提交格式

```
feat(runtime): add LLM integration in executor
feat(module-11): add new_module YAML definition
fix(validator): handle empty required_sections gracefully
docs: add RUNTIME_GUIDE.md
chore(vscode): update tasks.json for new commands
```

---

*ExpertAI Course Engine v4.0 · Runtime 模式 — 從 YAML 規格到本地自動化執行*
