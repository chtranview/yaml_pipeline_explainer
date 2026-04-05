
---

# artifacts/handouts/M3_yaml_course_architecture.md

```md id="iv8n1e"
# YAML 作為 AI 系統藍圖：把流程變成可執行規格

- **所屬天次 / 順序**：Day 2 / Module 3
- **預計時長**：90 分鐘
- **難度**：🔶 中階

## 學習目標
- 能夠用 YAML 結構化描述 AI 模組邏輯
- 學會設計模組之間的依賴、輸入與輸出欄位
- 建立一份可讀、可維護的系統規格草案

## 核心概念

### 1. YAML Schema
**一句話定義**：用欄位與階層，把系統設計寫成機器與人都能讀的規格。  
**比喻**：像建築藍圖，不是房子本身，但決定房子怎麼蓋。  
**例子**：用 `inputs / steps / outputs / validation` 描述一個 AI 任務模組。

### 2. Execution Logic
**一句話定義**：定義系統應該如何執行與依序處理。  
**比喻**：像食譜裡的步驟，不只是材料清單。  
**例子**：先產生 outline，再生成 handout，最後做 verify。

### 3. Artifact Thinking
**一句話定義**：先定義要交付什麼，再回推該怎麼設計流程。  
**比喻**：先想「我要交什麼作品」，再決定用什麼工具做。  
**例子**：如果最後要交付的是 `outline.yaml`，那前面就要先定義清楚 schema。

### 4. Validation Rules
**一句話定義**：讓輸出可檢查、可驗證，而不是只靠感覺判斷好不好。  
**比喻**：像考試評分標準，不然每次都會標不一樣。  
**例子**：規定 learning objectives 必須以動詞開頭、最多 3 條。

## 概念關係圖

```mermaid
flowchart TD
A[Skill 草稿] --> B[YAML Schema]
B --> C[Execution Logic]
C --> D[Outputs]
D --> E[Validation Rules]