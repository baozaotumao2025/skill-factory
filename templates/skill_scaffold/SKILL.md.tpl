---
name: {{SKILL_NAME}}
description: >
  MUST USE when user wants to {{TRIGGER_ACTION}}
  — e.g. "{{EXAMPLE_PROMPT_1}}", "{{EXAMPLE_PROMPT_2}}".

  Triggers on: {{TRIGGER_KEYWORDS}}.

  NOT for: {{NEGATIVE_EXCLUSIONS}}.
---

# {{SKILL_TITLE}}

{{ONE_LINE_VALUE_PROPOSITION}}

## 常驻守则 (Pre-flight Rules)

1. **先做必要检查**：动手前确认执行前置条件（依赖、路径、参数合法性）。
2. **声明工作流阶段**：在开始执行任务前，简述即将采取的核心步骤。
3. **闭环验证**：执行完毕后必须依据下文的验收标准完成验证。

## 路由与决策图谱

根据用户具体输入，进入对应子阶段或查阅细则：

| 意图场景 | 核心动作 | 深度参考文档 |
| :--- | :--- | :--- |
| **场景 A** | 执行常规流程 A | [references/details.md](references/details.md#phase-a) |
| **场景 B** | 执行专项流程 B | [references/details.md](references/details.md#phase-b) |

---

## 执行工作流 (Execution Workflow)

### 阶段 1：输入解析与状态确认
- 提取用户关键入参。
- 确认目标资源/文件是否准备就绪。

### 阶段 2：执行核心操作
- 遵循确定性步骤执行。
- 若有配套辅助脚本，优先调用 `scripts/` 中的确定性命令。

### 阶段 3：自检与交付闭环 (Verification)
- 验证产出物是否满足目标格式。
- 自查是否触发 `anti_patterns` 中的典型错误。
- 呈现清晰的结果汇报。
