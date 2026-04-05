# AI 系統設計工作坊
## 用 ExpertAI Course Engine 把課程做成可交付產品

副標：
從課程構想到交付打包的完整 pipeline

---

# 這堂課真正要教的
## 不是寫幾個 Prompt
# 而是設計一條可重複的課程生成流程

你要學的不是零散技巧，
而是如何把一門課變成系統。

---

# 今天你會完成什麼？
# 一整套可交付課程包

包括：

- 課程骨架
- 學員講義
- App 規格文件
- 投影片文本
- 品質驗證
- 交付打包

---

# 多數課程設計為什麼做不穩？
## 常見斷點

- 有想法，沒骨架
- 有課綱，沒講義
- 有講義，沒規格
- 有內容，沒驗證
- 做完之後，無法交付

---

# ExpertAI Course Engine 在解什麼？
# 它不是內容生成器
## 它是一條課程產品化 pipeline

把課程從「想法」
變成「可交付成果」。

---

# Engine 核心指令地圖
# 7 個模組，1 條產線

- /build
- /outline
- /handout
- /sdd
- /deck
- /verify
- /pack

---

# 這 7 個指令不是一堆 Prompt
## 而是有順序、有依賴的系統模組

每個模組都負責：

- 一個任務
- 一個輸出
- 一個驗收點

---

# 整體 Pipeline 一眼看懂
# Build Flow

課程主題  
→ 課程骨架  
→ 學員講義  
→ App 規格  
→ 投影片  
→ 品質驗證  
→ 交付打包

---

# 第一站：/build
# 總控入口

輸入：

- 課程主題
- 天數
- 受眾
- 模組數

輸出：

# 一整套課程交付包

---

# /build 的真正角色
## 不是「直接寫一堆內容」
# 而是啟動整條生成流程

它會依序呼叫：

1. /outline
2. /handout
3. /sdd
4. /deck
5. /verify
6. /pack

---

# 第二站：/outline
# 先做骨架，不先做投影片

因為一門課真正的起點不是簡報，
而是：

# 結構

---

# /outline 產出什麼？
# outline.yaml

它定義：

- 課程目標
- 模組結構
- 學習順序
- 依賴關係
- 實作任務

---

# 一份好的課綱，不只是目錄
## 它要回答 4 件事

1. 學員最後學會什麼？
2. 每模組在解哪段能力？
3. 模組之間怎麼銜接？
4. 每模組怎樣算完成？

---

# 本次案例課程設定
# AI 系統設計工作坊

參數：

- 天數：2 天
- 受眾：Intermediate
- 模組數：4

---

# 本次課程 4 模組骨架
## Day 1

- M1｜System Thinking
- M2｜Prompt → Skill Design

## Day 2

- M3｜Skill → YAML Architecture
- M4｜AI Workflow MVP Build

---

# M1｜System Thinking
# 從做事，到設計流程

學習重點：

- 模組化
- Input / Output
- 依賴關係
- AI 化機會點

---

# M2｜Prompt → Skill Design
# 從一次性 Prompt
# 變成可重用 Skill

學習重點：

- Trigger
- Input
- Instruction
- Output Contract

---

# M3｜Skill → YAML Architecture
# 把想法變成規格

學習重點：

- module_id
- inputs
- steps
- outputs
- validation
- error handling

---

# M4｜AI Workflow MVP Build
# 把模組組成一個可展示成果

重點不是做完整產品，
而是做出：

# 可展示的 MVP

---

# 第三站：/handout
# 真正承接學習的不是簡報
## 而是講義

因為學員不是只要「看懂」，
而是要：

# 做得出來

---

# /handout 的角色
# 把抽象概念變成可操作任務

每份 handout 至少要有：

- 學習目標
- 關鍵概念
- 練習任務
- 成功標準
- 反思問題

---

# 為什麼 handout 很重要？
## 因為只有課綱，不等於能教

沒有 handout，
學員很容易：

- 聽懂，但做不出來
- 知道概念，但無法落地
- 上課有感，課後無法重現

---

# 每模組都要有 Minimum Done
# 這是完成率的關鍵

沒有 Minimum Done，
學員最常發生：

- 做太大
- 做太散
- 做不完
- 不知道什麼叫完成

---

# M1 Minimum Done
## 至少做到這些

- 拆出 4 個模組
- 每模組有 Input / Output
- 至少 1 個依賴關係
- 找出 1 個最值得 AI 化的環節

---

# M2 Minimum Done
## 至少做到這些

- 完成 1 份 Skill 草稿
- 包含 Trigger / Input / Instruction / Output
- 至少 3 個執行步驟
- 至少 2 個固定輸出欄位

---

# M3 Minimum Done
## 至少做到這些

- 完成 1 份 YAML 模組草稿
- 包含 module_id / inputs / steps / outputs
- 至少 1 條 validation
- 至少 1 條 error handling

---

# M4 Minimum Done
## 至少做到這些

- 串起至少 2 個模組
- 有明確輸入與輸出
- 有一段可展示流程
- 能在 3 分鐘內完成 Demo

---

# 第四站：/sdd
# 從練習，走到可 build 規格

這一步是多數課程最容易缺的。

很多課程做到這裡前就停了：
> 做完一個練習

但真正高價值的下一步是：

# 讓成果可開發、可延伸

---

# /sdd 在做什麼？
# 把實作成果轉成 App 規格文件

它產出的不是心得，
而是：

# Software Design Document（SDD）

---

# SDD 的價值
## 不是寫給工程師看而已
# 而是讓想法能被 build

很多作品做不下去，
不是因為不會做，
而是因為：

# 沒有人把需求講清楚

---

# 一份最小可行 SDD 要有什麼？
## 6 個核心區塊

- Overview
- Goal
- User Stories
- Feature List
- Success Criteria
- Out of Scope

---

# 第五站：/deck
# 把內容轉成可上課節奏

這一步不是把講義切頁，
而是把內容設計成：

# 可以被教、被理解、被吸收

---

# 很多人做簡報太早
## 所以最後會變成：

- 內容堆疊
- 重點模糊
- 節奏鬆散
- 視覺很滿但學習很弱

---

# 正確順序是這樣
# 不是先做 Slides

而是：

Outline  
→ Handout  
→ SDD  
→ Deck

---

# 投影片真正的角色
# 它不是內容本身
## 它是教學介面

好的投影片要承接：

- 節奏
- 互動
- 轉場
- 示範
- 實作
- 收斂

---

# 第六站：/verify
# 做完內容，不代表可以交付

最常見的問題不是「沒有內容」，
而是：

# 內容看起來很多，但其實不穩

---

# /verify 在驗什麼？
# 它驗的是交付品質

包含：

- 模組完整性
- 學習目標一致性
- Hands-on 可執行性
- 講義與課綱對齊度
- Deck 可教學性
- 成果可驗收性

---

# verify 的真正價值
## 不是找錯字
# 而是防止你把草稿當成產品

這是「內容完成」和「產品可交付」
之間最重要的一步。

---

# 第七站：/pack
# 最後不是存檔
## 而是打包交付

真正交付時，
別人需要的不是一堆散檔案，
而是：

# 一套可接手的結構化成果

---

# /pack 最後會產出什麼？
# AI_System_Design_Workshop_Beta_Pack

一個可直接交接的交付包。

---

# 最終交付包結構
# Delivery Pack

- 01_outline
- 02_handouts
- 03_sdd
- 04_gamma_slides
- 05_quality_reports
- 99_readme

---

# 01_outline
# 骨架真源

檔案：

- outline.yaml

角色：

# 所有內容的 source of truth

---

# 02_handouts
# 學員講義

檔案：

- M1_system_thinking.md
- M2_prompt_skill_design.md
- M3_yaml_course_architecture.md
- M4_workshop_mvp_build.md

---

# 03_sdd
# 可 build 的規格文件

檔案：

- M2_prompt_skill_design_sdd.yaml
- M2_prompt_skill_design_sdd_brief.md
- M3_yaml_course_architecture_sdd.yaml
- M3_yaml_course_architecture_sdd_brief.md
- M4_workshop_mvp_build_sdd.yaml
- M4_workshop_mvp_build_sdd_brief.md

---

# 04_gamma_slides
# 可直接上台的簡報文本

檔案：

- ai_system_design_workshop_gamma.md
- ai_system_design_workshop_gamma_speaker_notes.md

---

# 05_quality_reports
# 品質驗證報告

檔案：

- verify_report.md
- verify_issues.yaml

作用：

# 讓交付不是靠感覺，而是有依據

---

# 99_readme
# 交接與使用說明

檔案：

- README_delivery.md

作用：

# 讓不是你的人，也能接手這套課

---

# 真正重要的不是檔案變多
## 而是它們之間有沒有邏輯關係

成熟課程產品的關鍵不是內容量，
而是這 4 件事：

- Source of Truth
- Dependency
- Validation
- Delivery Structure

---

# 這就是課程產品化的本質
# 不是把課做得更華麗
## 而是讓它變得：

- 可重複
- 可維護
- 可驗證
- 可交付
- 可擴充

---

# 今天最重要的學習，不只是這門課
## 而是一種方法

# 任何知識、任何課程、任何工作坊
# 都可以被設計成生成 pipeline

---

# 這套方法可以用在哪裡？
## 你可以延伸到：

- 企業內訓
- 顧問式工作坊
- 內部知識系統
- SOP 培訓
- AI 賦能課程
- 教學產品化專案

---

# 最後一句話
## 不要急著做更多內容
# 先把你的課變成一套可穩定交付的系統

真正有價值的，
不是一份漂亮課綱。

而是：

# 一套可重複交付的課程產品

---

# Thank You
## Q&A