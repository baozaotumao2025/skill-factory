#!/usr/bin/env python3
"""
Skill Factory · 工业级 Agent Skill 一键脚手架生成器 (CLI Scaffold Generator)
功能：输入技能名称、业务标题、产出路径，自动组装出包含密态知识库、三态分流引擎、
No-AI-Slop 质检器及回归测试套件的标准工程。
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

sys.path.insert(0, os.path.join(BASE_DIR, "tools"))
from domain_taxonomy import DOMAINS, VALID_DOMAINS, infer_domain, prompt_user_domain

FORMULAS = {
    "tob-sales": "采购签单 = (量化ROI算账证实 × DMU政治对齐) / 组织决策风险感知",
    "copywriting": "爆款转化 = 黄金前3秒钩子 × 痛点情绪共鸣 × 明确行动呼唤",
    "positioning": "心智胜出 = 非买不可的第一理由 => 确定性体验结果",
}


def create_scaffold(skill_name: str, skill_title: str, skill_desc: str, skill_slogan: str, output_path: str, domain: str = "positioning"):
    target_dir = os.path.abspath(output_path)
    if domain not in VALID_DOMAINS:
        domain = "positioning"
    domain_meta = DOMAINS[domain]
    print(f"▶ 正在初始化工业级 Agent 技能工程: {skill_name} [场景: {domain_meta['name']}]")
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

    os.makedirs(os.path.join(target_dir, "tools"), exist_ok=True)
    tools_src = os.path.join(BASE_DIR, "tools")
    for tool_name in ["agent_targets.py", "install_skill.py", "uninstall_skill.py", "domain_taxonomy.py", "absorb_to_skill_factory.py"]:
        src = os.path.join(tools_src, tool_name)
        if os.path.isfile(src):
            dst = os.path.join(target_dir, "tools", tool_name)
            shutil.copy(src, dst)
            os.chmod(dst, 0o755)

    # 在产出工程根目录下创建快捷安装/卸载/反哺脚本
    for script_name in ["install.py", "uninstall.py", "absorb_to_skill_factory.py"]:
        src_map = {
            "install.py": "install_skill.py",
            "uninstall.py": "uninstall_skill.py",
            "absorb_to_skill_factory.py": "absorb_to_skill_factory.py"
        }
        script_dst = os.path.join(target_dir, script_name)
        shutil.copy(os.path.join(tools_src, src_map[script_name]), script_dst)
        os.chmod(script_dst, 0o755)

    # 快捷命令：经验反哺上报子命令
    absorb_cmd = """---
description: 将本技能调试实战中遇到的新坑与防御对策，脱敏后提交至 Skill Factory 母机提案箱。
---

# 经验反哺母机 (absorbToSkillFactory)

当在使用或调试本技能时发现新坑或总结出更优做法，执行以下确定性脚本向上提交提案：

```bash
python3 absorb_to_skill_factory.py
```
"""
    with open(os.path.join(target_dir, ".claude", "commands", "absorb-to-skill-factory.md"), "w", encoding="utf-8") as f:
        f.write(absorb_cmd)

    # 确保脚本有可执行权限
    for sname in ["build_db.py", "retrieve.py", "slop_filter.py"]:
        p = os.path.join(target_dir, "skills", skill_name, sname)
        os.chmod(p, 0o755)

    # 3. 渲染主规约 SKILL.md
    with open(os.path.join(TEMPLATES_DIR, "SKILL.template.md"), "r", encoding="utf-8") as f:
        skill_template = f.read()

    core_formula = FORMULAS.get(domain, FORMULAS["positioning"])
    rendered_skill = skill_template \
        .replace("{{SKILL_NAME}}", skill_name) \
        .replace("{{SKILL_DOMAIN}}", domain) \
        .replace("{{SKILL_TITLE}}", skill_title) \
        .replace("{{SKILL_DESC}}", skill_desc) \
        .replace("{{SKILL_SLOGAN}}", skill_slogan) \
        .replace("{{CORE_FORMULA}}", core_formula) \
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
# 1. 交互式挂载到本地 Agent (Claude Code / OpenAI Codex / Cline)
python3 install.py

# 2. 运行回归测试
python3 tests/test_suite.py

# 3. 文案去 AI 味排雷审查
python3 skills/{skill_name}/slop_filter.py "待检测文案"

# 4. 如需解绑或卸载
python3 uninstall.py

# 5. 实战调试踩坑经验反哺母机 (absorbToSkillFactory)
python3 absorb_to_skill_factory.py
# 或在 Claude Code 中执行 /absorb-to-skill-factory
```

---

## 版权声明
本项目属于私有专有资产（Proprietary Assets），保留所有权利（All Rights Reserved）。未经授权严禁擅自分发。
"""
    with open(os.path.join(target_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    # 7. 生成工厂血统清单文件 .skill-factory.json
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    patches = [
        "AP-006-theatrical-persona",
        "AP-007-hard-dod-pyramid"
    ]
    if domain == "positioning":
        patches.append("AP-008-category-martyr-brand-action")

    manifest = {
        "generator": "skill-factory",
        "version": "2.1.0",
        "skill_name": skill_name,
        "domain": domain,
        "factory_root": BASE_DIR,
        "created_at": now_iso,
        "updated_at": now_iso,
        "applied_patches": patches
    }
    with open(os.path.join(target_dir, ".skill-factory.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n🎉 技能脚手架工程创建成功！")
    print(f"👉 下一步请参考: {os.path.join(BASE_DIR, 'SOP_SKILL_DISTILLATION.md')}")
    print(f"   将教材放入 docs/raw_corpus/，蒸馏后运行 build_db.py 即可生成知识库！")

    return os.path.join(target_dir, "skills", skill_name)


def main():
    parser = argparse.ArgumentParser(description="Skill Factory CLI - Agent 技能生产母机")
    parser.add_argument("--name", required=True, help="技能英文标识 (如: sales-forge, copy-master)")
    parser.add_argument("--title", required=True, help="技能中文名称 (如: 销售铁军商机攻防局)")
    parser.add_argument("--desc", default="专业级工业化智能体技能", help="技能一句话定位说明")
    parser.add_argument("--slogan", default="讲求实战，拒绝假大空自嗨！", help="技能口号/业务信念")
    parser.add_argument("-o", "--output", required=True, help="生成新技能的目标目录路径")
    parser.add_argument(
        "--domain",
        choices=["tob-sales", "copywriting", "positioning"],
        default=None,
        help="商业细分场景 (三选一): tob-sales(ToB大客户销售) | copywriting(公私域爆款文案) | positioning(战略品牌定位)"
    )
    parser.add_argument("--install", action="store_true", help="创建后直接进入交互式安装挂载流程")
    parser.add_argument("-y", "--yes", "--auto", action="store_true", help="非交互式自动模式")

    args = parser.parse_args()

    # 领域细分推断或探针交互
    domain = args.domain
    combined_info = f"{args.title} {args.desc} {args.name}"
    if not domain:
        if not args.yes and sys.stdin.isatty():
            domain = prompt_user_domain(text_for_inference=combined_info)
        else:
            inferred, conf, reason = infer_domain(combined_info)
            domain = inferred
            print(f"💡 自动推断商业细分场景: {DOMAINS[domain]['name']} ({domain}) [{reason}]")

    skill_created_path = create_scaffold(args.name, args.title, args.desc, args.slogan, args.output, domain=domain)

    should_install = args.install
    if not should_install and not args.yes and sys.stdin.isatty():
        try:
            c = input("\n? 是否立即将新生成的技能安装挂载到本地 Agent (Claude/Codex/Cline)? [y/N]: ").strip().lower()
            if c in ("y", "yes"):
                should_install = True
        except (KeyboardInterrupt, EOFError):
            pass

    if should_install:
        import subprocess
        install_script = os.path.join(BASE_DIR, "tools", "install_skill.py")
        subprocess.run([sys.executable, install_script, skill_created_path])


if __name__ == "__main__":
    main()
