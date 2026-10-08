#!/usr/bin/env python3
"""
Skill Factory · 工业级 Agent Skill 一键脚手架生成器 (CLI Scaffold Generator)
功能：输入技能名称、业务标题、产出路径，自动组装出包含密态知识库、三态分流引擎、
No-AI-Slop 质检器及回归测试套件的标准工程。
"""

import argparse
import os
import shutil
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


def create_scaffold(skill_name: str, skill_title: str, skill_desc: str, skill_slogan: str, output_path: str):
    target_dir = os.path.abspath(output_path)
    print(f"▶ 正在初始化工业级 Agent 技能工程: {skill_name}")
    print(f"  目标路径: {target_dir}")

    # 1. 创建标准工程目录树
    os.makedirs(os.path.join(target_dir, ".claude", "commands"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "skills", skill_name, "commands"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "tests"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "docs", "raw_corpus"), exist_ok=True)

    # 2. 复制零依赖工具脚本至技能内部
    shutil.copy(os.path.join(TEMPLATES_DIR, "build_db.py"), os.path.join(target_dir, "skills", skill_name, "build_db.py"))
    shutil.copy(os.path.join(TEMPLATES_DIR, "retrieve.py"), os.path.join(target_dir, "skills", skill_name, "retrieve.py"))
    shutil.copy(os.path.join(TEMPLATES_DIR, "slop_filter.py"), os.path.join(target_dir, "skills", skill_name, "slop_filter.py"))
    shutil.copy(os.path.join(TEMPLATES_DIR, "slop-filter.md"), os.path.join(target_dir, "skills", skill_name, "slop-filter.md"))

    # 确保脚本有可执行权限
    for sname in ["build_db.py", "retrieve.py", "slop_filter.py"]:
        p = os.path.join(target_dir, "skills", skill_name, sname)
        os.chmod(p, 0o755)

    # 3. 渲染主规约 SKILL.md
    with open(os.path.join(TEMPLATES_DIR, "SKILL.template.md"), "r", encoding="utf-8") as f:
        skill_template = f.read()

    rendered_skill = skill_template \
        .replace("{{SKILL_NAME}}", skill_name) \
        .replace("{{SKILL_TITLE}}", skill_title) \
        .replace("{{SKILL_DESC}}", skill_desc) \
        .replace("{{SKILL_SLOGAN}}", skill_slogan) \
        .replace("{{CORE_FORMULA}}", "业务成果 = 底层事实机制 × 场景精准命中") \
        .replace("{{SKILL_TRIGGERS}}", f"- 唤醒词: \"{skill_title}\", \"{skill_name}\"") \
        .replace("{{PROGRESSIVE_DISCLOSURE_ROWS}}", f"| **核心规则与底层知识**：按需密态召回 | `python3 retrieve.py ch01` |\n") \
        .replace("{{SUB_COMMANDS_DOCS}}", f"子命令位于 `commands/` 目录，由脚手架按业务场景自动挂载。\n")

    with open(os.path.join(target_dir, "skills", skill_name, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(rendered_skill)

    # 4. 渲染单元测试套件 tests/test_suite.py
    with open(os.path.join(TEMPLATES_DIR, "test_suite.template.py"), "r", encoding="utf-8") as f:
        test_template = f.read()

    rendered_test = test_template \
        .replace("{{SKILL_NAME}}", skill_name) \
        .replace("{{SKILL_TITLE}}", skill_title)

    test_file_path = os.path.join(target_dir, "tests", "test_suite.py")
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(rendered_test)
    os.chmod(test_file_path, 0o755)

    # 5. 生成标准 Git 忽略配置
    with open(os.path.join(target_dir, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(".DS_Store\n*.DS_Store\n__pycache__/\n*.pyc\n")

    # 6. 生成标准 README.md
    readme_content = f"""# {skill_title} ({skill_name})

> **“{skill_slogan}”**  
> 遵循 2026 年 **Open Agent Skills Specification** 工业级标准，开箱即用，内置三态分流引擎与 No-AI-Slop 质检器。

---

## 项目工程结构

```
.
├── .claude/
│   └── commands/                   # 项目级快捷子命令
├── skills/
│   └── {skill_name}/                # 核心 Agent Skill 资产
│       ├── SKILL.md                # 技能主规约 (Prompt Spec & 状态机)
│       ├── knowledge.db            # 密态知识库 (SQLite+zlib二进制，肉眼不可读)
│       ├── retrieve.py             # 零依赖流式检索引擎
│       ├── slop_filter.py          # 独立静态去 AI 味排雷脚本
│       ├── slop-filter.md          # 提示词中间件去 AI 味质检闸口
│       ├── commands/               # 技能私有命令副本
│       └── build_db.py             # 知识库编译打包工具
├── tests/
│   └── test_suite.py               # 自动化全流程回归测试套件
├── docs/
│   └── raw_corpus/                 # 原始教材与参考文档归档
├── .gitignore                      # Git 忽略配置
└── README.md                       # 交付使用文档
```

---

## 快速使用

```bash
# 1. 运行回归测试
python3 tests/test_suite.py

# 2. 文案去 AI 味排雷审查
python3 skills/{skill_name}/slop_filter.py "待检测文案"
```

---

## 版权声明
本项目属于私有专有资产（Proprietary Assets），保留所有权利（All Rights Reserved）。未经授权严禁擅自分发。
"""
    with open(os.path.join(target_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"\n🎉 技能脚手架工程创建成功！")
    print(f"👉 下一步请参考: {os.path.join(BASE_DIR, 'SOP_SKILL_DISTILLATION.md')}")
    print(f"   将教材放入 docs/raw_corpus/，蒸馏后运行 build_db.py 即可生成知识库！")


def main():
    parser = argparse.ArgumentParser(description="Skill Factory CLI - Agent 技能生产母机")
    parser.add_argument("--name", required=True, help="技能英文标识 (如: sales-forge, copy-master)")
    parser.add_argument("--title", required=True, help="技能中文名称 (如: 销售铁军商机攻防局)")
    parser.add_argument("--desc", default="专业级工业化智能体技能", help="技能一句话定位说明")
    parser.add_argument("--slogan", default="讲求实战，拒绝假大空自嗨！", help="技能口号/业务信念")
    parser.add_argument("-o", "--output", required=True, help="生成新技能的目标目录路径")

    args = parser.parse_args()
    create_scaffold(args.name, args.title, args.desc, args.slogan, args.output)


if __name__ == "__main__":
    main()
