# 03. 确定性脚本优先原则 (Executable First)

## 核心原则
大语言模型擅长**语义理解、目标规划与内容润色**，但不擅长**复杂数学计算、精确正则表达式提取、环境探查与复杂文件 I/O**。

如果一项操作能够写成确定性的 Python/Shell/Node.js 脚本或调用专门的 CLI/MCP 工具，**绝不要让 LLM 用 Prompt 自由猜测执行**。

---

## 落地规范

### 1. 结构划分
任何非纯文本指导的复杂 Skill，结构应包含：
```text
my-skill/
├── SKILL.md
├── scripts/
│   ├── detect_env.sh      # 环境或依赖探测脚本
│   ├── extract_meta.py    # 确定性数据提炼脚本
│   └── validate_output.py # 结果检验闭环脚本
└── references/
```

### 2. 脚本设计要求
- **独立可执行**：支持 CLI 参数输入（如 `--input`, `--format`），避免硬编码绝对路径。
- **结构化输出**：默认通过标准输出返回 JSON 或紧凑的 Markdown，便于 Agent 准确解析结果。
- **防御性错误处理**：若执行失败，输出清晰的 Exit Code 和带有修复建议的 Error Message。

---

## 避坑规则 (Anti-Patterns)
- ❌ **让 LLM 手工解析上百行的长文本格式**：让 Agent 在 Prompt 里逐行挑错极易漏项，编写针对性 Linter 脚本运行一次仅需 10ms 且准确率 100%。
- ❌ **在 Prompt 里写死环境变量与临时路径**：导致跨设备迁移或不同用户使用时全面失效。
