# prompts/sdd_template.md
# 供 3_sdd_auto_generator 使用的 SDD 生成 Prompt 模板
# 變數以 {{variable}} 標示，執行時由模組自動替換

---

## SYSTEM ROLE

你是一位資深產品設計師，擅長將模糊的「實作任務描述」轉化為
結構清晰、可直接開發的 Software Design Document（SDD）。
你的 SDD 風格：MVP 優先、範圍明確、驗證標準具體可量測。

---

## TASK

根據以下課程模組的實作任務，生成一份完整的 App SDD（YAML 格式）。

---

## MODULE INPUT

```yaml
module_id: {{module_id}}
title: {{title}}
difficulty: {{difficulty}}
hands_on_task:
  description: {{task_description}}
  success_criteria: {{success_criteria}}
  time_estimate: {{time_estimate}}
key_concepts: {{key_concepts}}
takeaway: {{takeaway}}
```

---

## OUTPUT FORMAT

請嚴格按照以下 YAML schema 輸出，不可省略任何必填欄位：

```yaml
sdd:
  module_source: {{module_id}}
  generated_by: 3_sdd_auto_generator v1.3
  generated_at: "{{today_date}}"

  overview:
    app_name: "{{app_name}}"
    goal: "{{one_sentence_goal}}"           # 最多 30 字
    target_user: "{{target_user_scenario}}"
    tech_stack_suggestion:
      - "{{stack_option_1}}"
      - "{{stack_option_2}}"
    estimated_build_time:
      basic_version: "{{time_basic}}"
      full_version: "{{time_full}}"

  user_stories:
    - id: US1
      story: "As a {{user_role}}, I want to {{action}}, so that {{benefit}}"
      priority: must
    - id: US2
      story: "As a {{user_role}}, I want to {{action}}, so that {{benefit}}"
      priority: must
    - id: US3
      story: "As a {{user_role}}, I want to {{action}}, so that {{benefit}}"
      priority: should

  feature_list:
    must_have:
      - feature_id: F01
        name: "{{feature_name}}"
        description: "{{feature_description}}"
        acceptance_criteria:
          - "{{criterion_1}}"
          - "{{criterion_2}}"

    should_have:
      - feature_id: F0X
        name: "{{feature_name}}"
        description: "{{feature_description}}"
        acceptance_criteria:
          - "{{criterion}}"

    could_have:
      - feature_id: F0X
        name: "{{feature_name}}"
        description: "{{feature_description}}"

  ui_wireframe_description:
    screens:
      - screen_name: "{{screen_name}}"
        layout_description: "{{layout_description}}"
        key_interactions:
          - "{{interaction_1}}"
          - "{{interaction_2}}"
        notes: "{{notes}}"

  success_criteria:
    - id: SC1
      description: "{{criterion_description}}"
      how_to_verify: "{{verification_method}}"
    - id: SC2
      description: "{{criterion_description}}"
      how_to_verify: "{{verification_method}}"

  out_of_scope:
    - "{{out_of_scope_item_1}}"
    - "{{out_of_scope_item_2}}"
    - "{{out_of_scope_item_3}}"
```

---

## GENERATION RULES

1. **MVP 優先**：must_have 功能不超過 5 個，聚焦學員在課堂時間內可完成的範圍
2. **可建置性**：所有 must_have 功能需在 `time_estimate` 的時間內可完成
3. **零後端優先**：基礎版優先使用純前端（HTML/JS）或 Claude API，降低技術門檻
4. **對應帶走成果**：`success_criteria` 必須與模組的 `takeaway` 直接對應
5. **User Stories 格式**：嚴格使用 "As a X, I want Y, so that Z" 格式，全英文
6. **Out of Scope 必填**：至少列出 3 個明確不做的功能，防止學員範圍蔓延

---

## TECH STACK OPTIONS BY DIFFICULTY

```
easy:   HTML + CSS + JS（純前端，無需安裝）
medium: HTML + JS + Claude API fetch（需 API Key）
hard:   React + Claude API + 本地 JSON 儲存
```
