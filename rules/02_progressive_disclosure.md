# 02. 渐进式披露与上下文预算控制 (Progressive Disclosure)

## 核心原则
Agent 的上下文窗口（Context Window）是非常昂贵的共享资源。
- 如果将所有专业领域的细则、数百行规则、大段字典和案例全部堆叠在 `SKILL.md` 中，每次该技能被匹配，系统上下文都会被瞬间挤爆，导致主任务遗忘、推理延迟急剧上升。
- **渐进式披露（Progressive Disclosure）** 规定：**一级入口仅提供路由图谱，二级细节按需延迟加载**。

---

## 预算与分层标准

### 层级 1：`SKILL.md`（一级路由与状态机）
- **预算控制**：严格控制在 500 行以内（通常推荐 100~300 行）。
- **包含内容**：
  - Frontmatter（名称、高准度 description）
  - 前置校验与防御性守则（Pre-flight Checklist）
  - 路由决策表（Decision Table / Dispatcher）
  - 核心工作流步骤骨架（Phase 1 -> Phase 2 -> Phase 3）
  - 验收闭环规范（Post-flight Verification）
- **禁止包含**：全量字典枚举、完整行业案例、长篇背景理论、大型 JSON/YAML 配置。

### 层级 2：`references/*.md`（二级知识库）
- 按领域维度解耦拆分，例如：
  - `references/rules_detail.md`（详细校验清单）
  - `references/styles.md`（视觉或风格规范）
  - `references/api_specs.md`（接口协议与参数字典）
- **加载机制**：在 `SKILL.md` 的工作流中明确告知 Agent：“当命中场景 A 时，读取 `[references/rules_detail.md](references/rules_detail.md)` 获取具体细则”。

---

## 避坑规则 (Anti-Patterns)
- ❌ **巨石型 SKILL.md**：单个文件超过 1000 行，迫使 Agent 无论执行多小的子任务都背负沉重上下文。
- ❌ **孤岛式引用**：在 `references/` 里放置了文件，但 `SKILL.md` 中没有任何指引告诉 Agent 何时该去查阅它。
