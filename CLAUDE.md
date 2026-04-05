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
