#!/usr/bin/env python3
"""
tools/scaffold.py - 标准技能骨架初始化生成器

用法:
  python3 tools/scaffold.py <skill_name> [--desc "简短用途描述"]
"""

import sys
import os
import argparse

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates", "skill_scaffold")
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")

def create_scaffold(name, title=None, desc=None):
    target_dir = os.path.join(SKILLS_DIR, name)
    if os.path.exists(target_dir):
        print(f"❌ 目录已存在: {target_dir}")
        return False

    os.makedirs(os.path.join(target_dir, "references"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "scripts"), exist_ok=True)

    skill_title = title or name.replace("-", " ").title()
    desc_val = desc or f"Agent skill for {name}"

    # 读取 SKILL.md.tpl
    with open(os.path.join(TEMPLATE_DIR, "SKILL.md.tpl"), "r", encoding="utf-8") as f:
        tpl = f.read()

    rendered = tpl.replace("{{SKILL_NAME}}", name)
    rendered = rendered.replace("{{SKILL_TITLE}}", skill_title)
    rendered = rendered.replace("{{TRIGGER_ACTION}}", f"perform {name} operations or related workflows")
    rendered = rendered.replace("{{EXAMPLE_PROMPT_1}}", f"帮我执行 {name} 相关任务")
    rendered = rendered.replace("{{EXAMPLE_PROMPT_2}}", f"check or run {name}")
    rendered = rendered.replace("{{TRIGGER_KEYWORDS}}", f"{name}, workflow, operations")
    rendered = rendered.replace("{{NEGATIVE_EXCLUSIONS}}", "通用闲聊或与本技能无关的常规问答")
    rendered = rendered.replace("{{ONE_LINE_VALUE_PROPOSITION}}", desc_val)

    with open(os.path.join(target_dir, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(rendered)

    # 读取 details.md.tpl
    with open(os.path.join(TEMPLATE_DIR, "references", "details.md.tpl"), "r", encoding="utf-8") as f:
        ref_tpl = f.read()

    ref_rendered = ref_tpl.replace("{{SKILL_NAME}}", skill_title)
    with open(os.path.join(target_dir, "references", "details.md"), "w", encoding="utf-8") as f:
        f.write(ref_rendered)

    # 创建 scripts 占位
    gitkeep = os.path.join(target_dir, "scripts", ".gitkeep")
    with open(gitkeep, "w") as f:
        pass

    print(f"🎉 成功创建标准化技能脚手架: {target_dir}")
    print(f"   ├── SKILL.md (已注入 2026 前沿触发规则)")
    print(f"   ├── references/details.md (渐进式披露二级文档)")
    print(f"   └── scripts/ (用于存放确定性工具)")
    print(f"   └── 安装提示: 可运行 `python3 install_skill.py {name}` 交互式挂载到本地 Agent")

    return True

def main():
    parser = argparse.ArgumentParser(description="Skill Factory 标准脚手架生成器")
    parser.add_argument("name", help="技能标识 (kebab-case, 如 code-auditor)")
    parser.add_argument("--title", help="技能展示标题", default=None)
    parser.add_argument("--desc", help="一句话功能介绍", default=None)

    args = parser.parse_args()
    success = create_scaffold(args.name, args.title, args.desc)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
