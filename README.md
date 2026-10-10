# Skill Factory (技能工厂)

工业级 Agent Skill 生产平台与自进化脚手架（基于 2026 前沿行业实践）。

---

## 核心设计思想：双飞轮架构

`skill-factory` 不仅仅是一个存放技能的代码库，而是一个具备**“正向标准生产”**与**“逆向经验自学习”**的工业化体系：

1. **正向生产流水线 (Production Line)**：
   遵循 **Distill ➔ Scaffold ➔ Lint & Test** 标准化步骤，产出结构受控、确定性高、低 Token 损耗的专业技能。
2. **动态进化飞轮 (Evolution Engine)**：
   每次在制作、测试或调试技能时踩到的坑（如误触发、路径死链、命令嵌套挂起），自动沉淀到 `rules/` 和 `templates/` 中，让后续生产出的所有技能自动继承更优的设计基因。

---

## 运行模式：双模驱动 (Dual Execution Modes)

针对不同场景和用户偏好，提供两种生成体验：

### 1. 逐步交互协同模式（默认模式 - 推荐）
- **特点**：在 4 个核心业务里程碑（检查哨）停下来与你汇报进展并确认方向，确保充分契合个性化业务诉求。
- **极致防呆**：每个检查哨都会标出 **`[选项 1 (推荐方案)]`**。如果你对细节不了解或想省事，直接回复 `1` 或 `好` 即可按照行业最佳实践继续推进。
- **命令**：
  ```bash
  /make-skill docs/*.pdf --name my-skill
  ```

### 2. 全自主无人值守模式（Autonomous Mode）
- **特点**：一键直通交付，适合批量导入、CI/CD 自动化构建或对资料完全放心的场景。多源冲突自动依据内置 Heuristic 启发式规则做出最优权衡。
- **命令**：
  ```bash
  /make-skill docs/*.pdf --name my-skill --auto
  # 或添加 --yes / -y
  ```

---

## 交互模式下的 4 个核心里程碑检查哨

```
                   输入文档 (docs/*.pdf)
                            │
                            ▼
     [🛑 检查哨 1：跨语料聚类与架构对齐]
        - 汇报主题簇划分（4~6 个领域模块）
        - 确认业务侧重点权重
                            │ 用户确认 (或默认 1)
                            ▼
     [🛑 检查哨 2：多源冲突与术语消歧]
        - 对比不同资料的观点矛盾
        - 对齐统一的业务术语字典 (Glossary)
                            │ 用户确认 (或默认 1)
                            ▼
     [🛑 检查哨 3：触发词与正负边界确认]
        - 对齐 MUST USE 触发短语
        - 锁定 NOT for 负向排除场景（防误触）
                            │ 用户确认 (或默认 1)
                            ▼
     [🛑 检查哨 4：交付验收与模拟演练]
        - 输出静态门禁质检 (Lint) 结果
        - 现场模拟一条真实 Prompt 演示效果
```

---
## 商业操盘唯一大类下的垂直场景细分 (Domain Taxonomy)

本工厂深耕**商业操盘与实战转化**这一核心大类。为杜绝不同商业场景的经验规则相互污染（例如将品牌定位的口号规则误推给写大客户算账的技能），内置 **3 个强制收敛的细分垂直场景**（`universal` 仅作为工厂底层系统铁律，禁止被实例化为业务标签，彻底杜绝经验反哺毒化）：

1. **`tob-sales`（ToB 大客户采购与组织销售）**：
   - 成果受众：**最终方案给客户老板 / 采购 / CFO 看**；
   - 核心法则：`采购签单 = (量化ROI算账证实 × DMU政治对齐) / 组织决策风险感知`；
   - 专属特性：严禁 C 端煽情；强制输出 CFO 财务算账模型、免责信任背书与 DMU 政治对齐。
2. **`copywriting`（公私域内容与爆款转化文案）**：
   - 成果受众：**最终内容发给大众消费者 / 读者看**；
   - 核心法则：`爆款转化 = 黄金前3秒钩子 × 痛点情绪共鸣 × 明确行动呼唤`；
   - 专属特性：直接转化导向；强力过滤 15 类 AI 八股腔调（“不是…而是…”等假深刻二元对立）；强制通过同行可移植性测试。
3. **`positioning`（战略定位与品牌心智）**：
   - 成果受众：**最终战略给公司创始人 / 高管层看**；
   - 核心法则：`心智胜出 = 非买不可的第一理由 => 确定性体验结果`；
   - 专属特性：专享 AP-008 载体分流；服务/高客单强制“品牌即动作”；严禁输出无品牌名的行业公德口号。

> **终极防呆机制（基于“成果给谁看”强制三选一）**：
> - 创建技能时若未指定 `--domain`，系统自动进行语义打分；
> - 交互模式下通过“**方案对谁负责（客户CFO / 消费者 / 创始人）**”单选探针强制收敛，**杜绝提供“通用/随便”第四逃避选项**；
> - 无人值守模式下特征不明显时强制收敛至主干定位场景 (`positioning`)，严禁将业务技能打上 `universal` 标签。

---


## 核心规范体系 (`rules/`)

根据 2026 年主流 Agent 实践（Anthropic 官方规范、OpenAI 技能生态与开源社区标准），工厂内置四大基因模块：

- [`rules/01_trigger_engineering.md`](rules/01_trigger_engineering.md)：**触发词与路由工程**
  - Frontmatter 采用三段式强制结构：`MUST USE`、`Triggers on` 与 `NOT for` 负向排除，杜绝误唤醒与泛化误触。
- [`rules/02_progressive_disclosure.md`](rules/02_progressive_disclosure.md)：**渐进式披露与上下文预算控制**
  - `SKILL.md` 仅承担一级路由与工作流骨架（行数严格压制在 500 行以内）。
  - 深度领域字典、规则手册按需下沉到 `references/*.md`，防止挤爆 Agent Context Window。
- [`rules/03_executable_first.md`](rules/03_executable_first.md)：**确定性脚本优先原则**
  - 不可依赖 LLM 自由推理复杂正则、计算或高危命令；确定性逻辑全部下沉为 `scripts/` 工具。
- [`rules/04_multidoc_distillation.md`](rules/04_multidoc_distillation.md)：**多源语料消歧与蒸馏规约**
  - 多套文档交叉提纯、打破知识割裂，构建高聚合的领域语义网络。
- [`rules/05_architecture_and_communication_principles.md`](rules/05_architecture_and_communication_principles.md)：**编码与架构原则：金字塔原理与目标驱动执行**
  - 严禁中二戏剧化角色扮演；强制结论先行、MECE 结构化分类与硬性可验证验收标准（DoD）。
- [`rules/anti_patterns.md`](rules/anti_patterns.md)：**实战踩坑与反模式黑名单**
  - 动态记录历史生产中暴露的陷阱（如 AP-001 泛化污染、AP-006 角色扮演反噬、AP-007 倒金字塔细节堆砌、AP-008 品类替罪羊与品牌无主游魂）。

---

## 项目工程结构

```text
skill-factory/
├── rules/                         # 【核心资产】进化的规则与前沿实践库
│   ├── 01_trigger_engineering.md  # 触发词工程与正负排除规范
│   ├── 02_progressive_disclosure.md# 渐进式披露与 Token 预算
│   ├── 03_executable_first.md     # 确定性脚本优先规范
│   ├── 04_multidoc_distillation.md# 多源语料消歧与蒸馏规约
│   ├── 05_architecture_and_communication_principles.md # 金字塔与DoD执行原则
│   └── anti_patterns.md           # 踩坑黑名单与反模式
│
├── templates/                     # 【动态模板与中间件】
│   ├── SKILL.template.md          # 商业技能主规约模板
│   ├── slop-filter.md             # 去 AI 味提示词中间件闸口
│   ├── slop_filter.py             # 静态去 AI 味排雷脚本
│   ├── build_db.py                # 密态知识库编译器
│   ├── retrieve.py                # 零依赖流式检索引擎
│   └── skill_scaffold/            # 轻量脚手架模板
│
├── tools/                         # 【工业级自动化工具链】
│   ├── agent_targets.py           # Claude / Codex / Cline 宿主中枢
│   ├── domain_taxonomy.py         # 商业场景细分模型与语义打分引擎
│   ├── install_skill.py           # 交互式多端挂载安装器
│   ├── uninstall_skill.py         # 反向探测与精准安全卸载器
│   ├── upgrade_skill.py           # 全域扫描去重、多端热升级器
│   ├── absorb_to_skill_factory.py # 端侧经验反哺上报工具
│   ├── absorb_proposal.py         # 母机提案审核吸收中心
│   ├── scaffold.py                # 标准脚手架一键生成器
│   └── lint_skill.py              # 静态门禁与宿主挂载健康校验器
│
├── install_skill.py -> tools/install_skill.py      # 根目录快捷安装命令
├── uninstall_skill.py -> tools/uninstall_skill.py  # 根目录快捷卸载命令
├── upgrade_skill.py -> tools/upgrade_skill.py      # 根目录快捷升级命令
├── absorb_proposal.py -> tools/absorb_proposal.py  # 根目录快捷提案审核命令
├── make_skill.py                  # 工业级 Agent Skill 生产母机
├── skills/                        # 【技能交付区】
└── docs/                          # 补充文档与研究报告
```

---

## 快速上手与日常使用指南

### 1. 生成一个新技能
在根目录下运行脚手架生成器，快速创建符合 2026 规范的标准骨架：
```bash
python3 tools/scaffold.py my-new-skill --desc "技能定位与功能简述"
```

这会在 `skills/my-new-skill/` 生成标准目录结构：
- `SKILL.md`（已注入预设三段式触发器与分阶段状态机）
- `references/details.md`（二级知识库占位）
- `scripts/`（存放该技能专属的确定性脚本）

### 2. 编写与填充领域知识
- 在 `SKILL.md` 中完善具体的工作流与路由。
- 将细节规则写入 `references/`，保持主入口紧凑。
- 将复杂提取或校验逻辑放入 `scripts/`。

### 3. 执行静态门禁体检 (Lint)
在交付技能前，使用内置 Linter 进行体检，并可联动探测宿主挂载健康度：
```bash
# 基础静态门禁校验
python3 tools/lint_skill.py skills/my-new-skill

# 联动审计宿主挂载健康度
python3 tools/lint_skill.py skills/my-new-skill --check-install
```
校验器会自动检查：
- [x] Frontmatter 是否完整 (`name`, `description`)
- [x] 是否包含 `MUST USE` 和 `NOT for` 排除规则
- [x] 行数预算是否合理（渐进式披露检查）
- [x] 本地相对 Markdown 超链接是否存在死链
- [x] 确定性脚本是否具备可执行权限 (`+x`)，防止 Agent 调用时被拒绝
- [x] 宿主安装健康度审计（软链接健康、物理副本孤立、断头死链排查）

### 4. 交互式多端挂载安装 (`install_skill.py`)
遵循 2026 年主流交互规范，支持自主选择挂载到特定 Agent，拒绝后台盲目静默挂载：

```bash
# 启动交互式安装向导 (支持 Claude Code / OpenAI Codex / Cline)
python3 install_skill.py skills/my-new-skill

# 或在 CI/CD 与自动化脚本中使用非交互参数
python3 install_skill.py skills/my-new-skill --agents claude,cline --mode symlink --yes
```

- **三大主流宿主精准对齐**：
  - 🟣 **Claude Code**：`~/.claude/skills/`
  - 🟢 **OpenAI Codex**：`~/.codex/skills/`
  - 🔵 **Cline**：`~/.cline/skills/`
- **双模挂载选择**：
  - **软链接 (Symlink - 推荐)**：本地开发修改实时在 Agent 中生效，零复制损耗；
  - **物理拷贝 (Copy)**：独立隔离部署，脱离工厂源码库。

### 5. 精准反向探测与安全卸载 (`uninstall_skill.py`)
当技能需要解绑或下线时，卸载器自动反向扫描所有宿主环境，由你决定卸载范围：

```bash
# 启动交互式卸载向导
python3 uninstall_skill.py my-new-skill

# 非交互指定卸载
python3 uninstall_skill.py my-new-skill --agents claude --yes
```
- **核心保障**：仅解除 Agent 端的软链接或移除部署副本，**坚决不触碰原始研发工程中的源码与知识库资产**。

### 6. 存量历史技能一键热升级 (`upgrade_skill.py`)
当 `skill-factory` 自身完成规范升级（如模板更新、提示词中间件增强、新反模式规则注入、多端安装套件更新）后，可直接使用升级工具无损同步存量技能：

```bash
# 1. 全域扫描探测并进入交互式选择 (支持按序号勾选升级指定技能，如 1,2 或 all)
python3 upgrade_skill.py --scan

# 2. 命令行精准指定序号升级（免手动复制冗长路径）
python3 upgrade_skill.py --scan --pick 1,2

# 3. 按技能名称批量精准升级
python3 upgrade_skill.py --name core-forge,copywrite-forge

# 4. 预览指定技能的升级内容（只读 Dry-run）
python3 upgrade_skill.py /path/to/skill --dry-run

# 5. 外科手术式无损升级单技能
python3 upgrade_skill.py /path/to/skill

# 6. 全域一键无人值守全量升级
python3 upgrade_skill.py --scan --upgrade-all
```

**升级器核心特性**：
- **血统指纹优先 + 向后兼容特征嗅探**：通过 `generator: skill-factory` 与 `.skill-factory.json` 锁定己方资产，绝不误触系统其他外部第三方 Skill；
- **全域多端归一化与交互选拔**：自动接入 Claude、Codex、Cline 技能池，通过真实文件系统路径去重，支持终端直接输入序号选择性升级；
- **老技能自动补齐安装套件**：升级历史老技能时，自动注入 `install.py` 与 `uninstall.py`，抹平新老技能体验代差；
- **断头死链智能排查**：主动识别宿主目录中因源文件移动产生的损坏符号链接；
- **资产解耦保护**：绝对不破坏历史技能专有的业务 Prompt、`knowledge.db` 与行业心智模型；
- **智能增量打补丁**：安全热替换 `slop-filter.md` 等基础设施，向 `SKILL.md` 与子命令质检流智能追加最新工程铁律（如 AP-008 品牌即动作、金字塔原理、DoD 验收标准）；
- **出厂自动上牌**：老版本历史技能在升级完成后自动植入 `.skill-factory.json`，实现一次升级、永久纳管。

### 7. 进化机制：端侧经验反哺 (absorbToSkillFactory) 与母机审核统筹发版

工厂采用严格权责分明的双层自进化架构：**端侧负责单向脱敏上报提案，母机负责统筹评审与分发广播**，杜绝端侧越权破坏环境：

```
 【阶段 A：端侧技能实战踩坑】
   在具体的业务技能工程目录 (如 ~/Downloads/tob-master/) 内运行：
   python3 absorb_to_skill_factory.py
   # 或在 Claude Code 中输入 /absorb-to-skill-factory

   - 作用：引导记录踩坑现象、严重后果与正确解法；
   - 安全：自动脱敏敏感词，锁定该技能 domain（绝不泛化为 universal）；
   - 边界：只生成提案递交母机提案箱 (rules/proposals/)，任务即刻闭环退出。
            │
            ▼
 【阶段 B：母机统筹审核入库与历史台账】
   在工厂母机根目录下运行提案中心，支持三态审查与历史审计：
   python3 absorb_proposal.py          # 启动交互式审查面板
   python3 absorb_proposal.py --history# 查看历史归档台账 (已同意 / 已驳回)

   - 三态决断面板：
     [1] ✅ 同意 (Accept)  ：分配 AP 编号、写入 rules/anti_patterns.md 规范库，并归档至 accepted/
     [2] ❌ 拒绝 (Reject)  ：记录驳回原因并归档至 rejected/，不入母机规范库
     [3] ⏳ 暂不处理 (Skip)：保留在待处理箱，下次打开依然可见
   - 历史审计：运行 `python3 absorb_proposal.py --history` 查看全生命周期归档记录。
            │
            ▼
 【阶段 C：母机发版全量广播】
   由工厂管理员主动统筹升级全网同类技能：
   python3 upgrade_skill.py --scan --upgrade-all
```

---

## 许可证
MIT
