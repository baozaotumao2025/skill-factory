#!/usr/bin/env python3
"""
tools/lint_skill.py - Skill Factory 工业级静态门禁校验器

基于 2026 年主流 Agent Skill 规范，静态扫描指定技能目录，重点排查：
1. Frontmatter 完整性 (name, description)
2. 触发词工程规范 (必须包含 MUST USE, 必须包含 NOT for 负向排除)
3. 渐进式披露合规 (检查 SKILL.md 行数与体积，避免上下文膨胀)
4. 引用死链检查 (检查 Markdown 中的本地相对链接是否真实存在)
"""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent_targets import inspect_agent_installations
from domain_taxonomy import DOMAINS, infer_domain


MAX_RECOMMENDED_LINES = 500

def lint_skill(skill_dir):
    skill_dir = os.path.abspath(skill_dir)
    skill_md = os.path.join(skill_dir, "SKILL.md")

    errors = []
    warnings = []

    if not os.path.isdir(skill_dir):
        return [f"目录不存在: {skill_dir}"], []

    if not os.path.isfile(skill_md):
        return [f"缺少入口文件: {skill_md}"], []

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.splitlines()

    # 1. 检查行数预算 (Progressive Disclosure)
    if len(lines) > MAX_RECOMMENDED_LINES:
        warnings.append(
            f"SKILL.md 当前有 {len(lines)} 行 (建议不超过 {MAX_RECOMMENDED_LINES} 行)。"
            f"建议将详细规则拆解下沉到 references/ 目录下以节省 Context Window。"
        )

    # 2. 检查 Frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    domain = None
    if not fm_match:
        errors.append("SKILL.md 缺少标准的 YAML Frontmatter (以 --- 开头和结尾)。")
    else:
        fm_content = fm_match.group(1)
        if not re.search(r"^name:\s*[\w\-\_]+", fm_content, re.MULTILINE):
            errors.append("Frontmatter 缺少有效的 'name:' 字段。")

        d_match = re.search(r"^domain:\s*([\w\-]+)", fm_content, re.MULTILINE)
        if d_match:
            domain = d_match.group(1).strip()

        if not re.search(r"^description:\s*", fm_content, re.MULTILINE):
            errors.append("Frontmatter 缺少 'description:' 字段。")
        else:
            # 3. 检查触发工程规范 (Trigger Engineering)
            if "MUST USE" not in fm_content and "must use" not in fm_content.lower():
                warnings.append("description 建议使用明确的 'MUST USE when...' 指导 Agent 何时激活。")
            if "not for" not in fm_content.lower() and "NOT for" not in fm_content:
                warnings.append("description 缺少 'NOT for:' 负向排除声明，极易引发日常泛化问候时的全域误触发。")

    if not domain:
        domain, _, _ = infer_domain(f"{os.path.basename(skill_dir)} {content[:1000]}")

    # 4. 检查 Markdown 相对链接死链
    link_pattern = re.compile(r"\[.*?\]\((?!https?://|mailto:|#)(.*?)\)")
    for match in link_pattern.finditer(content):
        raw_path = match.group(1).split("#")[0].strip()
        if not raw_path:
            continue
        target_path = os.path.join(skill_dir, raw_path)
        if not os.path.exists(target_path):
            errors.append(f"发现断头死链: 引用了不存在的本地文件 '{raw_path}' (对应物理路径: {target_path})。")

    # 5. 检查 AP-008 (品类替罪羊与品牌无主游魂) 质检覆盖度 (仅在 positioning 品牌战略定位场景中生效)
    if domain == "positioning":
        slop_filter_path = os.path.join(skill_dir, "slop-filter.md")
        if os.path.exists(slop_filter_path):
            with open(slop_filter_path, "r", encoding="utf-8") as sf_f:
                sf_content = sf_f.read()
                if "品类替罪羊" not in sf_content and "品牌无主游魂" not in sf_content:
                    warnings.append("slop-filter.md 缺少对 AP-008 (品类替罪羊与品牌无主游魂) 的质检项，定位类业务易发生品牌资产流失。")

    # 6. 检查确定性脚本执行权限 (Executable-First)
    for root, _, files in os.walk(skill_dir):
        for fname in files:
            if fname.endswith((".py", ".sh")):
                fpath = os.path.join(root, fname)
                if not os.access(fpath, os.X_OK):
                    rel = os.path.relpath(fpath, skill_dir)
                    warnings.append(f"脚本文件 '{rel}' 缺少可执行权限 (+x)，宿主 Agent 调用时可能报 Permission denied。建议: chmod +x {rel}")

    return errors, warnings

def check_host_mounts(skill_dir):
    skill_name = os.path.basename(os.path.abspath(skill_dir))
    statuses = inspect_agent_installations(skill_name)
    installed = [s for s in statuses if s.is_installed]

    print(f"\n🌐 [宿主挂载健康审计 - {skill_name}]:")
    if not installed:
        print("  ℹ️  该技能尚未挂载到任何已知 Agent (Claude Code / OpenAI Codex / Cline)。")
        print("     提示: 运行 `python3 install_skill.py <path>` 即可交互式挂载。")
        return

    for s in installed:
        if s.is_broken:
            print(f"  ❌ {s.agent_def.icon} [{s.agent_def.display_name}] 损坏的软链接 -> {s.target_path}")
        elif s.install_type == "symlink":
            print(f"  ✅ {s.agent_def.icon} [{s.agent_def.display_name}] 软链接健康挂载 -> {s.target_path}")
        else:
            print(f"  📦 {s.agent_def.icon} [{s.agent_def.display_name}] 物理副本独立挂载 ({s.install_dir})")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Skill Factory 工业级静态门禁校验器")
    parser.add_argument("skill_dir", help="待校验技能目录路径")
    parser.add_argument("--check-install", action="store_true", help="联动审计该技能在 Claude/Codex/Cline 中的安装状态")
    args = parser.parse_args()

    skill_path = args.skill_dir
    print(f"🔍 正在执行静态质检: {skill_path}")
    errors, warnings = lint_skill(skill_path)

    if warnings:
        print("\n⚠️  [警告项 - 建议优化]:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n❌ [错误项 - 阻止交付]:")
        for e in errors:
            print(f"  - {e}")
        print("\n❌ 质检未通过，请修复上述硬性缺陷！")
        sys.exit(1)
    else:
        print("\n✅ 静态质检通过！完全符合 2026 Agent Skill 规范。")

    if args.check_install:
        check_host_mounts(skill_path)

    sys.exit(0)

if __name__ == "__main__":
    main()
