#!/usr/bin/env python3
"""
tools/install_skill.py - 工业级 Agent Skill 交互式多端挂载安装器
支持交互式多选目标 Agent (Claude Code / OpenAI Codex / Cline)，以及软链接 / 物理拷贝双模式。
"""

import argparse
import os
import sys

_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _CUR_DIR)
sys.path.insert(0, os.path.join(_CUR_DIR, "tools"))

from agent_targets import (
    SUPPORTED_AGENTS,
    inspect_agent_installations,
    install_skill_to_agent
)


def resolve_skill_source(target_input: str | None) -> tuple[str, str]:
    if not target_input or target_input == ".":
        skills_dir = os.path.abspath("skills")
        if os.path.isdir(skills_dir):
            for sub in os.listdir(skills_dir):
                candidate = os.path.join(skills_dir, sub)
                if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "SKILL.md")):
                    return candidate, sub
        if os.path.isfile("SKILL.md"):
            cur = os.path.abspath(".")
            return cur, os.path.basename(cur)
        print("❌ 错误: 未指定技能路径，且当前目录下未探测到有效的技能资产！")
        sys.exit(1)

    target_path = os.path.abspath(target_input)
    if os.path.isdir(target_path) and os.path.isfile(os.path.join(target_path, "SKILL.md")):
        return target_path, os.path.basename(target_path)

    factory_skills = os.path.abspath(os.path.join(_CUR_DIR, "..", "skills", target_input))
    if os.path.isdir(factory_skills) and os.path.isfile(os.path.join(factory_skills, "SKILL.md")):
        return factory_skills, target_input

    proj_skills = os.path.abspath(os.path.join("skills", target_input))
    if os.path.isdir(proj_skills) and os.path.isfile(os.path.join(proj_skills, "SKILL.md")):
        return proj_skills, target_input

    if os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            if "SKILL.md" in files:
                return root, os.path.basename(root)

    print(f"❌ 错误: 未在 '{target_input}' 找到包含 SKILL.md 的有效技能目录！")
    sys.exit(1)


def prompt_user_selection(source_dir: str, skill_name: str) -> tuple[list[str], str, str, str | None]:
    print("\n" + "=" * 60)
    print("📦 Skill Factory · Agent 技能安装中心 (2026 Interactive)")
    print(f"目标技能: \033[1;36m{skill_name}\033[0m")
    print(f"源路径: {source_dir}")
    print("=" * 60)

    statuses = inspect_agent_installations(skill_name)
    installed_map = {s.agent_key: s for s in statuses if s.scope == "global" and s.is_installed}

    agents_keys = list(SUPPORTED_AGENTS.keys())
    print("\n? 请选择目标 Agent (输入编号多选，如 1,3 或回车全选) [默认: 全部]:")
    for idx, key in enumerate(agents_keys, 1):
        agent = SUPPORTED_AGENTS[key]
        tag = ""
        if key in installed_map:
            st = installed_map[key]
            tag = f" \033[33m({'软链接' if st.install_type == 'symlink' else '实体'})已存在\033[0m"
        print(f"  [{idx}] {agent.icon} {agent.display_name:<13} ({agent.global_rel_path}){tag}")

    choice = input("选择编号 > ").strip()
    selected = []
    if not choice:
        selected = agents_keys
    else:
        for p in choice.replace("，", ",").split(","):
            p = p.strip()
            if p.isdigit() and 1 <= int(p) <= len(agents_keys):
                selected.append(agents_keys[int(p) - 1])
            elif p.lower() in SUPPORTED_AGENTS:
                selected.append(p.lower())
    if not selected:
        selected = agents_keys

    print("\n? 请选择安装范围 [默认: 1]:")
    print("  [1] 全局用户空间 (Global Scope) [推荐]")
    print("  [2] 指定项目目录 (Project Local Scope)")
    c_scope = input("选择编号 > ").strip()
    scope = "project" if c_scope == "2" else "global"
    project_root = None
    if scope == "project":
        proj_in = input("请输入目标项目根目录路径 [默认: 当前目录]: ").strip()
        project_root = os.path.abspath(proj_in or ".")

    print("\n? 请选择安装方式 [默认: 1]:")
    print("  [1] 软链接挂载 (Symlink - 推荐研发态，改源码即生效) [推荐]")
    print("  [2] 独立完整拷贝 (Copy - 独立分发)")
    c_mode = input("选择编号 > ").strip()
    mode = "copy" if c_mode == "2" else "symlink"

    return selected, scope, mode, project_root


def run_installation(source_dir: str, skill_name: str, agents: list[str], scope: str, mode: str,
                     project_root: str | None = None, force: bool = False):
    print(f"\n▶ 正在挂载技能: [{skill_name}] (模式: {mode.upper()}, 范围: {scope.upper()})...")
    print("-" * 60)
    all_success = True
    for key in agents:
        agent = SUPPORTED_AGENTS[key]
        success, msg = install_skill_to_agent(
            source_skill_dir=source_dir,
            skill_name=skill_name,
            agent_key=key,
            scope=scope,
            project_root=project_root,
            mode=mode,
            overwrite=force
        )
        if success:
            print(f"  ✅ {agent.icon} [{agent.display_name}] {msg}")
        else:
            print(f"  ❌ {agent.icon} [{agent.display_name}] {msg}")
            all_success = False
    print("-" * 60)
    if all_success:
        print(f"🎉 技能 [{skill_name}] 安装成功！")
    else:
        print(f"⚠️  部分挂载未完成，如需覆盖请附带 --force 参数。")


def main():
    parser = argparse.ArgumentParser(description="Skill Factory 工业级 Agent 技能安装中心")
    parser.add_argument("skill", nargs="?", default=None, help="技能目录路径或名称 (在技能工程内可省略)")
    parser.add_argument("-a", "--agents", help="目标 Agent (如: claude,codex,cline)")
    parser.add_argument("-s", "--scope", choices=["global", "project"], default=None, help="安装范围")
    parser.add_argument("-p", "--project-root", default=None, help="项目根路径")
    parser.add_argument("-m", "--mode", choices=["symlink", "copy"], default=None, help="安装方式")
    parser.add_argument("-f", "--force", action="store_true", help="强制覆盖已存在目标")
    parser.add_argument("-y", "--yes", action="store_true", help="非交互静默模式")

    args = parser.parse_args()
    source_dir, skill_name = resolve_skill_source(args.skill)

    is_interactive = sys.stdin.isatty() and not args.yes and (args.agents is None or args.scope is None or args.mode is None)
    if is_interactive:
        selected, scope, mode, project_root = prompt_user_selection(source_dir, skill_name)
        run_installation(source_dir, skill_name, selected, scope, mode, project_root, force=True)
    else:
        selected = [a.strip().lower() for a in args.agents.split(",")] if args.agents else list(SUPPORTED_AGENTS.keys())
        scope = args.scope or "global"
        mode = args.mode or "symlink"
        project_root = os.path.abspath(args.project_root) if args.project_root else None
        run_installation(source_dir, skill_name, selected, scope, mode, project_root, force=args.force)


if __name__ == "__main__":
    main()
