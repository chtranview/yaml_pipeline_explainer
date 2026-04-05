# ExpertAI Course Engine · 團隊操作指南
> PIPELINE_GUIDE.md · v4.1 · 2026-04-05

這份指南說明如何在 **ChatGPT**、**Claude** 或 **Gemini** 環境中執行完整的課程生成流程，適合講師、課程設計師與助理使用。

> 📌 若你需要在本地端以 Python CLI 執行（離線、CI/CD、版本控管），請參閱 [RUNTIME_GUIDE.md](RUNTIME_GUIDE.md)。

---

## 目錄

1. [系統概覽](#1-系統概覽)
2. [快速開始（5 分鐘）](#2-快速開始)
3. [完整流程步驟](#3-完整流程步驟)
4. [各指令說明](#4-各指令說明)
5. [常見問題與排解](#5-常見問題與排解)
6. [進階：搭配外部工具](#6-進階搭配外部工具)
7. [貢獻與版本更新](#7-貢獻與版本更新)

---

## 1. 系統概覽

```
使用者輸入 /build
      ↓
0_build_pipeline（總指揮）── 依序執行 7 步
      ↓
Step 1 → 1_project_engine      → outline.yaml
      ↓
Step 2 → 2_handout_generator   → handouts/*.md
      ↓
Step 3 → 3_sdd_generator       → sdd/*.yaml       （非必要，失敗可跳過）
      ↓
Step 4 → 4_gamma_generator     → gamma/*.md        （非必要，失敗可跳過）
      ↓
Step 5 → 6_verifier            → verify.md         （失敗則中止）
      ↓
Step 6 → 7_packager            → bundles/*.zip
      ↓
Step 7 → 5_notifier            → Email / LINE

課程結束後：
9 → Meta Loop（improvement.yaml）← 閉環回到 Step 1
```

**核心原則：** 系統不是「魔法」，ChatGPT / Claude / Gemini 是**解讀並模擬執行** YAML 規格的角色。你貼入的 YAML 越完整，輸出品質越穩定。

> 💡 **Pipeline vs Runtime：** 本指南透過 AI 對話模擬執行 YAML 規格。若需要确定性執行、版本控管或 CI/CD 整合，請參閱 [RUNTIME_GUIDE.md](RUNTIME_GUIDE.md) 以 Python CLI 在本地執行同一套 YAML 流程。

---

## 2. 快速開始

### Step 1：設定 System Prompt

#### ChatGPT

打開 ChatGPT，建立新的 **Custom GPT** 或 **Project**，在 System Instructions 貼入：

```
你是 ExpertAI Course Engine v4.0。
請完整閱讀並嚴格遵守以下 YAML 規格執行所有課程生成任務。

[貼入 _index.yaml 全文]
[貼入 0_build_pipeline.yaml 全文]
[貼入 1_project_engine_4.0.yaml 全文]
[貼入 2_learner_handout_generator.yaml 全文]
... （依需求加入其他模組）
```

> **提示：** 不需要一次貼入全部 10 個模組。先貼 0、1、2，確認能正常運作後再逐步加入其他模組。

#### Claude Code

Claude Code 使用專案根目錄下的 `CLAUDE.md` 作為 System Prompt。在 `yaml_pipeline_explainer/` 根目錄建立此檔案：

```bash
# 進入專案目錄
cd yaml_pipeline_explainer
```

建立 `CLAUDE.md`，內容如下：

```markdown
# ExpertAI Course Engine v4.0

你是 ExpertAI Course Engine 的課程生成助手。
請嚴格遵守本專案中的 YAML 規格執行所有課程生成任務。

## 專案結構

- `_index.yaml` — 指令對照表與模組索引
- `0_build_pipeline.yaml` — /build 完整 pipeline 定義（7 步依序執行）
- `1_project_engine_4.0.yaml` — 課程骨架引擎
- `2_learner_handout_generator.yaml` — 學員講義生成器
- `3_sdd_auto_generator.yaml` — App SDD 生成器
- `4_gamma_generator.yaml` — 投影片文字生成器
- `5_notifier_auto_dispatch.yaml` — 通知寄送
- `6_verifier_auto_checker.yaml` — 品質驗證（10 項檢查規則）
- `7_packager_auto_zipper.yaml` — 打包交付

## 執行規則

1. 收到 `/build`、`/outline`、`/verify` 等指令時，讀取對應的 YAML 模組定義並依序執行
2. 所有產物寫入 `artifacts/` 對應子目錄（handouts/、sdd/、gamma/、_reports/）
3. 講義格式參照 `prompts/handout_template.md`，SDD 格式參照 `prompts/sdd_template.md`
4. 執行 /build 時依照 `0_build_pipeline.yaml` 的 `sequence` 依序 7 步完成
5. 輸出語言預設繁體中文
```

Claude Code 啟動時會自動讀取 `CLAUDE.md`，無需手動貼入 YAML 全文。它可以直接讀取專案中的 `.yaml` 檔案。

> **優勢：** Claude Code 透過檔案系統存取完整專案，不受上下文視窗限制，且產物直接寫入本地 `artifacts/` 資料夾。

#### Gemini

打開 [Google AI Studio](https://aistudio.google.com/)，建立新的 **Chat Prompt**，在 **System Instructions** 貼入：

```
你是 ExpertAI Course Engine v4.0。
請完整閱讀並嚴格遵守以下 YAML 規格執行所有課程生成任務。

[貼入 _index.yaml 全文]
[貼入 0_build_pipeline.yaml 全文]
[貼入 1_project_engine_4.0.yaml 全文]
[貼入 2_learner_handout_generator.yaml 全文]
... （依需求加入其他模組）
```

> **提示：** Gemini 的上下文視窗較大（100 萬+ tokens），可一次貼入更多模組 YAML。建議將常用的 0、1、2、6 一次貼入以獲得更一致的輸出。

### Step 2：執行第一次 /build

```
/build
課程主題：AI 系統設計工作坊：從使用者到設計者
天數：2
受眾：intermediate
模組數量：4
```

### Step 3：觀察輸出

系統應依序輸出 7 個步驟（對應 `0_build_pipeline.yaml` 的 `sequence`）：

```
╔══════════════════════════════════════════╗
║  ExpertAI Course Engine · /build 啟動      ║
╚══════════════════════════════════════════╝

▶ [1/7] project_engine
  ✓ outline.yaml 已生成（4 個模組）

▶ [2/7] learner_handout_generator
  ✓ M1_architecture.md 已生成
  ✓ M2_skill_design.md 已生成
  ✓ M3_yaml_pipeline.md 已生成
  ✓ M4_mcp_integration.md 已生成

▶ [3/7] sdd_auto_generator
  ✓ M3_yaml_pipeline_sdd.yaml 已生成
  ✓ M4_mcp_integration_sdd.yaml 已生成

▶ [4/7] gamma_generator
  ✓ slides.md 已生成

▶ [5/7] verifier_auto_checker
  ✓ verify.md — 通過 4/4 項

▶ [6/7] packager_auto_zipper
  ✓ 打包完成

▶ [7/7] notifier_auto_dispatch
  ✓ 通知草稿已生成
```

> 💡 **提示：** 若 AI 輸出中斷（上下文視窗不足），可輸入「繼續」讓它從中斷處接續輸出。

---

## 3. 完整流程步驟

### 標準執行流程（新課程）

```
第一天準備：
1. /build → 生成完整材料
2. /verify → 確認品質
3. 手動檢查 _issues/ 中的問題
4. 修復後重新執行 /verify
5. /pack → 生成交付包
6. /notify → 發送學員通知

課程結束後：
7. /meta → 分析問題，生成改善建議
8. 人工審閱 _queues/improvement.yaml
9. 更新對應模組 YAML
10. 下次課程品質自動提升
```

### 快速迭代流程（修改單一模組）

```
發現問題 →
/handout M2_skill_design  （重新生成指定模組講義）
/verify                    （驗證修復結果）
/pack                      （重新打包）
```

### 範例驅動流程（參考 samples/）

```
1. 打開 samples/5_sample_M1_course.yaml 理解目標格式
2. 以此為範本修改課程主題
3. 執行 /build 生成你的版本
4. 對照 samples/sdd_M1_example.yaml 確認 SDD 品質
5. 對照 samples/gamma_example.yaml 確認投影片文本品質
```

---

## 4. 各指令說明

| 指令 | 格式 | 說明 | 必要條件 |
|------|------|------|---------|
| `/build` | `/build` + 參數 | 執行完整 pipeline | 無 |
| `/outline` | `/outline` | 只生成課程骨架 | 無 |
| `/handout` | `/handout [module_id]` | 生成指定講義（留空=全部） | outline.yaml 存在 |
| `/sdd` | `/sdd [module_id]` | 生成 SDD 規格 | handout 存在 |
| `/deck` | `/deck [module_id]` | 生成 Gamma 文本 | handout 存在 |
| `/verify` | `/verify` | 執行 10 項品質驗證 | 有 artifacts |
| `/pack` | `/pack` | 生成打包清單 | verify 通過 |
| `/notify` | `/notify` | 生成通知草稿 | bundle 存在 |
| `/bridge` | `/bridge [connection_id]` | 同步外部資料 | .env 設定 |
| `/meta` | `/meta` | 執行 Meta Loop 分析 | 有 logs/issues |

---

## 5. 常見問題與排解

### Q：執行 /build 後輸出格式不一致？

**原因：** System Prompt 中的 YAML 未完整貼入，或 ChatGPT 上下文視窗超出限制。

**解法：**
1. 確認 `_index.yaml` 中的 `output_format` 設定已貼入
2. 開啟新對話，重新貼入 System Prompt
3. 若 YAML 太長，只保留最常用的模組（0、1、2、6）

---

### Q：/verify 報告有很多 C05（缺少步驟說明）？

**原因：** `2_learner_handout_generator.yaml` 的 `hands_on_task` 段落生成時未包含步驟。

**解法：**
```
/handout [問題模組 ID]
```
在提示中加入：「請確保動手實作段落包含 3-5 個編號步驟」

若反覆發生，執行 `/meta` 讓系統生成改善建議，並更新 YAML 的 `quality_rules`。

---

### Q：Gamma 匯入後版面跑版？

**原因：** `gamma_example.yaml` 的 `---` 換頁符前後需有空行。

**解法：** 確認 `deck_markdown` 中每個 `---` 前後各有一個空行：

```markdown
...上一頁最後一行

---

# 下一頁標題
```

---

### Q：/notify 生成的 Email 主旨含有 `{{bundle_download_link}}` 未替換？

**原因：** `7_packager` 尚未執行或未提供雲端下載連結。

**解法：**
1. 先執行 `/pack` 確認打包完成
2. 手動上傳 ZIP 至 Google Drive / Dropbox，取得分享連結
3. 重新執行 `/notify`，在提示中加入：`下載連結：https://...`

---

### Q：想要生成繁體中文以外的語言？

**解法：** 在 `/build` 指令後加入語言參數：

```
/build
課程主題：AI System Design Workshop
語言：en
受眾：intermediate
```

---

## 6. 進階：搭配外部工具

### 搭配 MCP Filesystem（Claude Desktop）

可讓 Claude 直接寫入本地資料夾，不需手動複製輸出。

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

設定後，Claude 執行 `/build` 時可直接將輸出寫入 `artifacts/` 資料夾。而 Runtime 模式的 `verify` 指令可直接驗證 Claude 的輸出品質。

---

### 搭配 Zapier 自動發送通知

1. 建立 Zapier Zap：**Webhook (Catch Hook)** → **Gmail** → **LINE Notify**
2. 將 Webhook URL 填入 `8_bridge_connector.yaml` 的 `LINE_WEBHOOK_URL`
3. 執行 `/notify` 時，系統自動觸發 Webhook，Zapier 負責實際發送

---

### 搭配 Google Sheets 學員名單

1. 建立 Google Sheets，欄位：姓名 / Email / LINE ID / 程度 / 備注
2. 取得 Sheet ID（URL 中的長串字元）
3. 填入 `.env`：`GOOGLE_SHEETS_ID=your_sheet_id`
4. 執行 `/bridge google_sheets` 載入學員名單
5. 後續 `/notify` 自動使用個人化稱呼

---

## 7. 貢獻與版本更新

### 更新模組的標準流程

```
1. 執行 /meta 取得改善建議
2. 審閱 _queues/improvement.yaml
3. 選擇要更新的建議（REC_xxx）
4. 修改對應的 .yaml 模組
5. 將 improvement.yaml 中該 REC 的 status 改為 applied
6. 下次執行 /meta 時系統會驗證是否真的改善
```

### 版本號規則

- `MAJOR.MINOR`（例：4.0 → 4.1）
- MINOR 升版：新增欄位、調整規則、優化輸出格式
- MAJOR 升版：架構性變更（新增/移除模組、改變執行順序）

### 建議的 Git 提交格式

```
feat(module-2): add step_by_step required validation
fix(module-6): C05 now correctly handles nested lists
docs: update PIPELINE_GUIDE with Zapier integration steps
```

---

*ExpertAI Course Engine v4.1 · 從主題到交付，系統自動運作*
