# 工业级 Agent Skill 知识蒸馏与生产 SOP 规约 (Standard Operating Procedure)

> 本规范指导 AI 编码 Agent（Claude Code / Codex / Copilot CLI）如何将一份任意领域的“原始教材 / 课件 / PDF / 操盘笔记”，工业级标准化转译为高确定性、零 AI 味的专属 Agent Skill。

---
---

## 阶段零：编码与架构契约审查 (Architecture & Communication Contracts)

在启动任何技能生成之前，必须强制挂载 `rules/05_architecture_and_communication_principles.md`，对技能的思考与沟通逻辑进行工程级锁死：

1. **沟通原则强制绑定金字塔原理**：
   - 先结论后论据，先全局拓扑后局部细节；严禁流水账堆砌细节。
   - 结构化信息严格执行 **MECE 分组**（相互独立、完全穷尽）。若原始教材逻辑散乱，必须主动重组后再输出。
2. **严禁拟人化中二角色扮演 (AP-006 防御)**：
   - 技能 Prompt 只能定义能力边界、分析模型、输入输出契约，严禁定义中二戏剧化性格、江湖隐喻或夸张人设。
   - 统一采用“优秀技术架构师 / 商业系统工程师”的客观中立语调。
3. **目标驱动执行与硬性 DoD (AP-007 防御)**：
   - 给足可验证成功标准（Definition of Done），将祈使句翻转为包含量化边界、自检条件的工程任务，让 Agent 自循环达标。


## 阶段一：教材解构与知识蒸馏 (Knowledge Distillation)

面对原始教材，严禁直接把全文无脑粘进 Prompt，必须执行三级提纯：
### 0. 明确商业细分场景归属 (Sub-Domain Triage)
在解构教材前，必须通过“最终成果主要给谁看”强制收敛到唯一的垂直场景，锁死专属因果公式与防御规则（严禁落入 universal，防止经验反哺时毒化系统公共底座）：
- **`tob-sales` (ToB大客户与组织销售)**：给客户老板/采购/CFO 看。聚焦采购决策链、DMU 组织政治、招投标攻防与 CFO 财务算账；
- **`copywriting` (公私域内容与爆款文案)**：给大众消费者/读者看。聚焦小红书种草、短视频脚本、信息流广告与高点击转化；
- **`positioning` (战略定位与品牌心智)**：给公司创始人/高管层看。聚焦第一购买理由、心智占位、超级口号与排他性卖点；
- **复合教材处理铁律**：若资料包罗万象，强制按主要受众收敛至单一主责场景，或拆解为多个独立技能，绝不生产模棱两可的泛化巨石。



### 1. 提炼核心心智模型 (Mental Model & Formulas)
- **寻找核心数学/逻辑因果**：该行业解决问题的最底层公式是什么？（例如商业定位的：`非买不可因 => 必然体验果`；销售的：`BANT/MEDDIC 模型`；短视频的：`黄金前3秒钩子 × 情绪共鸣 × 行动呼唤`）。
- **确定价值标尺与分类**：将行业对象分层（如品类刚性/弹性；用户高中低意向度；企业大中小规模）。

### 2. 挖掘反常识与不可能三角 (Anti-Intuition & Trade-offs)
- 找出教材中“打破行业小白认知”的冲突点（如：“填空式定位是自嗨内鬼”、“无形服务业严禁牺牲品牌名”）。
- 提炼该领域经典的“不可能三角”，**并执行品类载体分流判定 (Carrier Dichotomy)**：
  - 快消实体货架品类允许牺牲品牌名，100% 聚焦购买理由（如“大自然的搬运工”）；
  - 无形服务 / 高客单决策 / 口碑转介绍品类严禁牺牲品牌名，必须执行【品牌即动作】（Brand-as-a-Verb），防范【AP-008 品类替罪羊】。

### 3. 编撰自嗨骗局与排雷手册 (`anti-patterns.md`)
- 梳理目标领域最常见的 3~5 个“文科自嗨病症”（如：假大空形容词、企业自我标榜、伪专业术语骗局，以及品类替罪羊与品牌无主游魂等 AP-001 ~ AP-008）。

---

## 阶段二：垂直子命令规划与三态引擎 (Sub-Commands & 3-State Engine)

### 1. 子命令规划原则（2~4 个，职责绝对单一）
- **命令 1：极速生成/出招器**（跳过长篇理论，直出实战方案）；
- **命令 2：照妖镜排雷/审查器**（诊断现有方案的致命死穴，给出手术重写）；
- **命令 3：场景落地/触点改装器**（全触点落地施工图纸）。

### 2. 强制锁死三态分流引擎 (3-State Input Triage)
每个子命令的 Input Schema 必须内置 3 种状态流转：
- **State 1（白纸引导）**：用户全无想法时，输出 3 道降维探针单选题，拒绝报错；
- **State 2（直通锻造）**：要素齐全时，免除寒暄，直出卡片；
- **State 3（模糊单句）**：用户给一句话时，自动反推 2 组硬核商业假设，带假设一键直接交付。

---

## 阶段三：密态知识库构建 (Local Encrypted Vault)

1. 将蒸馏出的教材核心章节存入临时 `chapters/` 目录（约 8~15 篇，每篇聚焦一个核心主题）；
2. 运行 `build_db.py`，自动压缩打包为 `knowledge.db` 二进制 SQLite 数据库；
3. 将检索脚本 `retrieve.py` 挂载就绪；
4. **彻底删除 `chapters/` 明文目录**，确保肉眼不可读、防直接白嫖。

---

## 阶段四：No-AI-Slop 双层质检拦截 (Slop Filtering)

1. **静态脚本层**：运行 `slop_filter.py` 静态排查文案；
2. **模型提示词层**：将 `slop-filter.md` 嵌入到每个子命令的 Pipeline 末尾；
3. **强制通过可移植性测试 (Portability Test)**：换成同行名字依然通顺的文案一律不合格，必须重写为具体参数、时长、金额或物理因果；
4. **强制通过品类替罪羊质检 (Category Martyr Test)**：针对无形服务与高客单口碑品类，口号与核心卖点必须绑定品牌名或专属动作入口，严禁输出替行业当免费雷锋的无主口号。

---

## 阶段五：自动化测试与交付验证 (Verification & Delivery)

1. 自动生成 `tests/test_suite.py`；
2. 执行回归测试，验证：
   - 知识库列表检索、多 ID 解压与自然语言检索正常；
   - 静态去 AI 味排雷脚本拦截正常；
   - 各子命令三态引擎与强契约完整；
3. 输出整洁规范的 `README.md` 与 Git 初始化。

---

## 阶段六：宿主多端挂载与生命周期管理 (Host Mount & Lifecycle)

生产完成的技能包必须遵循 2026 年行业规范完成受控交付：

1. **宿主健康审计 (Host Audit)**：
   - 运行 `python3 tools/lint_skill.py skills/<skill-name> --check-install` 校验权限与链接有效性。
2. **交互式受控挂载 (Interactive Install)**：
   - 运行 `python3 install_skill.py skills/<skill-name>`；
   - 遵循用户意图勾选目标 Agent：
     - `[1] Claude Code` (`~/.claude/skills`)
     - `[2] OpenAI Codex` (`~/.codex/skills`)
     - `[3] Cline` (`~/.cline/skills`)
   - 研发态优先选用 **软链接 (Symlink)**，确保工厂源码迭代即时生效；生产部署选用 **物理拷贝 (Copy)**。
3. **退役与安全卸载 (Safe Uninstall)**：
   - 当技能重构或退役时，运行 `python3 uninstall_skill.py <skill-name>`；
   - 精准解挂对应宿主，坚决保护原始研发源码资产。

---

## 阶段七：端侧反哺与经验自进化 (Feedback & Evolution)

技能在现场执行或调试踩坑后，必须遵循权责分明的双层闭环反哺母机：

1. **端侧上报提案 (absorbToSkillFactory)**：
   - 在技能工程根目录下执行 `python3 absorb_to_skill_factory.py`（或在 Agent 中输入 `/absorb-to-skill-factory`）；
   - 记录典型错误、后果与验证有效的解法；系统自动脱敏并锁定所属 `domain`，生成结构化提案提交至母机 `rules/proposals/`，端侧任务即刻闭环退出。
2. **母机统筹审核入库 (三态决断与历史审计)**：
   - 工厂管理员在 `skill-factory` 运行 `python3 absorb_proposal.py`；
   - 支持三态操作：
     - **[1] 同意 (Accept)**：自动赋予官方 AP 编号写入 `rules/anti_patterns.md`，归档至 `accepted/`；
     - **[2] 拒绝 (Reject)**：记录驳回原因并归档至 `rejected/`，不污染规则库；
     - **[3] 暂不处理 (Skip)**：保留在待处理箱，下次依然可见；
   - 随时运行 `python3 absorb_proposal.py --history` 查看全量历史审计台账。
3. **母机统筹发版广播**：
   - 在母机运行 `python3 upgrade_skill.py --scan`，精准按领域将最新基因推送至全网同类存量技能。


