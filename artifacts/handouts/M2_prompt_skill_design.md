
---

# artifacts/handouts/M2_prompt_skill_design.md

```md id="4j5x4u"
# 從 Prompt 到 Skill：設計可重用的 AI 任務單元

- **所屬天次 / 順序**：Day 1 / Module 2
- **預計時長**：90 分鐘
- **難度**：🔶 中階

## 學習目標
- 能夠將單次 Prompt 重構為可重複使用的 Skill
- 學會撰寫包含 trigger、instruction、output 的任務規格
- 建立一份可直接操作的 AI Skill 定義稿

## 核心概念

### 1. Prompt vs Skill
**一句話定義**：Prompt 是一次性指令，Skill 是可重複執行的任務規格。  
**比喻**：Prompt 像臨時口頭交代；Skill 像標準作業流程（SOP）。  
**例子**：  
- Prompt：「幫我整理這篇文章」  
- Skill：「當我貼入文章時，請輸出摘要、重點、可行動項目，格式固定」

### 2. Trigger
**一句話定義**：定義什麼情境下應該啟動這個 Skill。  
**比喻**：像快捷鍵，按下時就啟動對應工作。  
**例子**：當我輸入「/summary」並附上一段長文時，自動啟動摘要 Skill。

### 3. Instruction
**一句話定義**：明確規定 AI 要如何思考與處理任務。  
**比喻**：像給實習生的工作說明，不說清楚就會做偏。  
**例子**：先辨識受眾，再摘要，再列出三個建議，不可直接複製原文。

### 4. Output Contract
**一句話定義**：事先定義輸出格式與品質標準。  
**比喻**：不是只說「做一份報告」，而是指定要有封面、摘要、結論。  
**例子**：輸出一定要有：
- 一句話摘要
- 三個重點
- 一個下一步建議

## 概念關係圖

```mermaid
flowchart LR
A[使用情境] --> B[Trigger]
B --> C[Instruction]
C --> D[Output Contract]
D --> E[可重用 Skill]