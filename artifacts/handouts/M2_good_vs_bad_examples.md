# M2｜壞例子 vs 好例子
## Prompt → Skill 設計對照

---

## 壞例子：一次性 Prompt（Bad Example）

> 幫我整理這篇文章，寫成摘要、重點跟結論，然後如果有需要也幫我整理成適合內訓的內容，越完整越好。

### 問題在哪？
- 沒有明確 Trigger
- 沒有定義 Input
- Instruction 太模糊
- Output 格式不固定
- 太依賴 AI 自己猜

---

## 好例子：可重用 Skill（Good Example）

### Skill Name
Article Summary for Internal Training

### Trigger
當使用者輸入 `/article_summary` 並貼上一篇文章時

### Input
- article_text

### Instruction
1. 先辨識文章主題
2. 再整理 3 個關鍵重點
3. 最後轉寫成適合內部培訓的說明語氣

### Output Contract
請固定輸出：
- 一句話摘要
- 三個重點
- 一段內訓版說明
- 一個建議延伸討論問題

### Constraints
- 使用繁體中文
- 總字數控制在 400 字內

---

## 關鍵差異

### 壞 Prompt 的問題
> AI 要自己猜很多事情

### 好 Skill 的特徵
> 使用情境、處理步驟、輸出格式都被定義清楚