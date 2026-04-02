# ExpertAI Course Engine v4.0

> AI 課程自動化生成系統 · 從主題輸入到完整交付包

## 快速開始

在 ChatGPT 中貼入 `_index.yaml` 作為 System Prompt，然後輸入：

```
/build
課程主題：AI 系統設計工作坊
天數：2
受眾：intermediate
```

## 模組一覽

| 模組 | 檔案 | 職責 | 觸發 |
|------|------|------|------|
| 0 | `0_build_pipeline.yaml` | 總指揮，依序呼叫所有子模組 | `/build` |
| 1 | `1_project_engine_4.0.yaml` | 課程骨架與教案大綱 | `/outline` |
| 2 | `2_learner_handout_generator.yaml` | 學員講義（逐模組生成） | `/handout` |
| 3 | `3_sdd_auto_generator.yaml` | App SDD 規格文件 | `/sdd` |
| 4 | `4_gamma_generator.yaml` | Gamma 投影片文本 | `/deck` |
| 5 | `5_notifier_auto_dispatch.yaml` | Email / LINE 通知 | `/notify` |
| 6 | `6_verifier_auto_checker.yaml` | 品質驗證（10 項規則） | `/verify` |
| 7 | `7_packager_auto_zipper.yaml` | ZIP 交付包 | `/pack` |
| 8 | `8_bridge_connector.yaml` | 外部資料橋接 | `/bridge` |
| 9 | `9_meta_loop.yaml` | 改善建議 · 閉環優化 | `/meta` |

## Artifacts 結構

```
artifacts/
├── handouts/     ← 模組 1、2 生成
├── sdd/          ← 模組 3 生成
├── gamma/        ← 模組 4 生成
├── bundles/      ← 模組 7 打包（對外交付）
├── _reports/     ← 模組 6、9 生成
├── _logs/        ← 所有模組寫入
├── _issues/      ← 模組 6 標記問題
└── _queues/      ← 模組 9 改善待辦
```

## 環境變數（需要外部整合時設定）

複製 `.env.example`（見 `readme/` 目錄）並填入真實值。
