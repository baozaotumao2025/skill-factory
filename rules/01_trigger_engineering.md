# 01. 触发词与路由工程规范 (Trigger Engineering)

## 核心原则
Agent 调度技能完全依赖其系统提示中暴露的技能描述。如果技能的描述过于泛化，会导致高频**误召回（False Positive）**；如果缺少关键词，会导致**漏召回（False Negative）**。

因此，2026 年高质量 Agent Skill 的 Frontmatter `description` 必须遵循 **三段式强制结构**：
1. **MUST USE 显式激活条件**：用户表达的具体意图、高频触发动词/名词（支持中英文双语）。
2. **场景扩展与典型 Prompt 列举**：提供 3~5 个具有区分度的真实 Query 示例。
3. **NOT FOR 负向排除约束**：显式声明什么场景**绝对不要调用**本 Skill（通常指向通用回答、已有其他专属 Skill 的场景）。

---

## Frontmatter 标准范式

```yaml
---
name: my-skill-slug
description: >
  MUST USE when user wants to [核心动作/意图: 如 调研/审核/代码重构/生成流程图]
  — e.g. "帮我审核这份方案", "重构这个模块", "analyze this codebase".
  
  Triggers on: [领域核心实体与名词群: 如 React 19, Kubernetes, 文案诊断, 竞品分析].

  NOT for: [负向排除边界，例如：通用闲聊、仅需输出简单文本解释、已有专门 skill 的场景 (如使用 code-review 代替)].
---
```

---

## 避坑规则 (Anti-Patterns)
- ❌ **禁止使用万能动词作为主要触发词**：如仅声明 `help`, `process`, `optimize`, `处理`, `优化`，容易引发全场景误触。
- ❌ **禁止省略负向排除 (NOT FOR)**：缺少边界约束会导致 Agent 在面对复合任务时反复陷入工具竞争。
- ✅ **推荐提供具体领域名词**：如特定库名、协议、文件格式或业务术语。
