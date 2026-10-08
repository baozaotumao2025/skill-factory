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

## 新教材如何一键变成新 Skill？（只需 3 步）

未来无论您拿到什么领域的教材（销售、管理、短视频、研发等），只需执行以下标准工作流：

### 第一步：运行母机脚手架，一键初始化新工程骨架

```bash
python3 /Users/cherubines/Downloads/skill-factory/make_skill.py \
  --name "你的技能英文名" \
  --title "你的技能中文名" \
  --desc "一句话定位" \
  --slogan "业务信念/口号" \
  -o "../你的新工程目录"
```

*脚手架会自动在新目录下创建标准的目录树，并自动把 `build_db.py`、`retrieve.py`、`slop_filter.py`、`slop-filter.md`、`test_suite.py` 装备齐全。*

### 第二步：教材知识蒸馏（丢给 Agent 执行 `SOP_SKILL_DISTILLATION.md`）

1. 把新教材放入新工程的 `docs/raw_corpus/` 目录；
2. 告诉 Agent：**“按照 `SOP_SKILL_DISTILLATION.md` 对这本教材进行提纯，提炼底层公式、四大自嗨骗局，规划 2~3 个垂直子命令，并提取出核心章节放入临时 `chapters/`”**；
3. 运行 `python3 skills/<skill_name>/build_db.py`，教材将被自动压缩编译为二进制密态库 `knowledge.db`，然后直接删除明文 `chapters/`，彻底防白嫖。

### 第三步：一键运行回归测试

在新工程目录下直接运行：

```bash
python3 tests/test_suite.py
```

全部通过后，一个全新的工业级、零 AI 味、带密态知识库的专属 Agent Skill 即正式完工！

