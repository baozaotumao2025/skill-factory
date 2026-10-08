# 技能兵工厂 (Skill Factory) · Agent Skill 生产母机

> **专门用于将任意领域的“原始教材/课件/PDF/操盘笔记”，全自动化流水线编译为工业级 Agent Skill 的元工具工程。**

---

## 核心设计理念

传统的 Agent 技能通常只是简单地写一段 System Prompt，往往存在以下致命缺陷：
1. **AI 幻觉与自由发挥**：没有输入/输出契约与状态机流转；
2. **大部头上下文塞爆**：把几十万字直接丢给模型，导致注意力涣散；
3. **明文易泄露/白嫖**：商业核心方法论直接以 Markdown 暴露；
4. **AI 味浓厚**：充斥“二元对立、假深刻结语、空洞赋能”等套路。

**Skill Factory** 提炼了 `core-forge` 的成功经验，为每个新生产的技能自动装配 **4 大工业级护甲**：
- **三态分流引擎 (3-State Triage)**：自动处理用户“白纸没想法（探针引导）”、“原料完备（直通生成）”、“模糊一句话（逆向补全）”；
- **密态二进制知识库 (Encrypted Local Vault)**：教材自动编译为二进制 SQLite + zlib 字节流，零 pip 依赖，毫秒级流式召回，人类肉眼不可读；
- **No-AI-Slop 双层质检闸口**：内置静态排雷脚本 `slop_filter.py` 与提示词中间件 `slop-filter.md`，强制过滤 15 类 AI 腔调；
- **确定性契约子命令 (Deterministic Sub-commands)**：划分 2~4 个职责单一的垂直子命令，锁死输出 Schema。

---

## 目录结构

```
/Users/cherubines/Downloads/skill-factory/
├── README.md                      # 母机使用说明
├── SOP_SKILL_DISTILLATION.md      # 教材解构与子命令拆解工业级 SOP 指南
├── make_skill.py                  # 一键生成新技能骨架的 CLI 引擎
│
├── templates/                     # 核心标准模板库（母版）
│   ├── SKILL.template.md          # 技能主规约模板（预置三态分流引擎）
│   ├── sub_command.template.md    # 垂直子命令模板
│   ├── slop-filter.md             # 去 AI 味提示词中间件质检闸口
│   ├── slop_filter.py             # 零依赖静态去 AI 味排雷脚本
│   ├── build_db.py                # 密态知识库自动打包编译器
│   ├── retrieve.py                # 零依赖流式检索引擎
│   └── test_suite.template.py     # 自动化回归测试套件模板
│
└── examples/                      # 最佳实践标杆参考
```

---

## 如何从一份新教材生产新技能？（极简 3 步走）

### 第一步：一键初始化新技能工程
在终端中运行 `make_skill.py`：
```bash
python3 make_skill.py \
  --name "sales-forge" \
  --title "大客户销售商机攻防局" \
  --desc "B2B大客户销售决策链破局与排雷" \
  --slogan "成交靠算账，拒绝自嗨PPT！" \
  -o "../sales-forge"
```
*脚手架会自动在目标目录建立包含所有工具、规约和测试套件的标准工程。*

### 第二步：知识蒸馏与教材编译 (按 SOP 指南)
1. 将您的原始教材（PDF、Word、Markdown）放入新工程的 `docs/raw_corpus/` 目录；
2. 按照 [`SOP_SKILL_DISTILLATION.md`](SOP_SKILL_DISTILLATION.md) 让 Agent 执行知识提炼：
   - 梳理底层心智模型与算账公式；
   - 提炼反直觉原则与排雷清单 (`anti-patterns.md`)；
   - 规划 2~3 个垂直子命令；
   - 提取 8~12 个核心章节存入临时 `chapters/` 目录；
3. 在新工程下运行 `python3 skills/<skill-name>/build_db.py`，教材将自动编译为二进制 `knowledge.db`，随后即可清除明文 chapters。

### 第三步：全流程回归测试与验证
在新工程下运行测试套件：
```bash
python3 tests/test_suite.py
```
全部通过后，新技能即达工业级交付标准！
