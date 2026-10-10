#!/usr/bin/env python3
"""
tools/uninstall_skill.py - 工业级 Agent Skill 交互式精准卸载器
反向探测 Claude Code / OpenAI Codex / Cline 已安装状态，支持交互式单选/多选安全解挂。
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
    uninstall_skill_from_agent
)


def prompt_uninstall_targets(skill_name: str, installed_statuses: list) -> list:
    print("\n" + "=" * 60)
    print("🗑️  Skill Factory · Agent 技能卸载中心 (2026 Interactive)")
    print(f"目标技能: \033[1;31m{skill_name}\033[0m")
    print("=" * 60)
    print("\n🔍 正在探测该技能在本地环境的挂载情况...")

    for idx, st in enumerate(installed_statuses, 1):
        type_str = "软链接" if st.install_type == "symlink" else ("损坏的死链" if st.is_broken else "物理副本")
        scope_str = "全局" if st.scope == "global" else "项目级"
        print(f"  [{idx}] {st.agent_def.icon} {st.agent_def.display_name:<13} ({scope_str} · {type_str})")
        print(f"      路径: {st.install_dir}")

    print("\n? 请选择要卸载的目标 (输入编号多选，如 1,2 或直接回车全选) [默认: 全部已安装]:")
    choice = input("选择编号 > ").strip()
    selected = []
    if not choice:
        selected = installed_statuses
    else:
        for p in choice.replace("，", ",").split(","):
            p = p.strip()
            if p.isdigit() and 1 <= int(p) <= len(installed_statuses):
                selected.append(installed_statuses[int(p) - 1])
    return selected if selected else installed_statuses


def run_uninstallation(skill_name: str, targets: list, project_root: str | None = None):
    print(f"\n▶ 正在从选定 Agent 中卸载 [{skill_name}]...")
    print("-" * 60)
    for st in targets:
        success, msg = uninstall_skill_from_agent(
            skill_name=skill_name,
            agent_key=st.agent_key,
            scope=st.scope,
            project_root=project_root
        )
        if success:
            print(f"  ✅ {st.agent_def.icon} [{st.agent_def.display_name}] {msg}")
        else:
            print(f"  ❌ {st.agent_def.icon} [{st.agent_def.display_name}] {msg}")
    print("-" * 60)
    print(f"🎉 卸载操作完成！(原始研发目录源码保持完好)")


def detect_current_skill_name(user_input: str | None) -> str:
    if user_input and user_input != ".":
        return os.path.basename(user_input.rstrip("/\\"))
    skills_dir = os.path.abspath("skills")
    if os.path.isdir(skills_dir):
        for sub in os.listdir(skills_dir):
            candidate = os.path.join(skills_dir, sub)
            if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "SKILL.md")):
                return sub
    if os.path.isfile("SKILL.md"):
        return os.path.basename(os.path.abspath("."))
    print("❌ 错误: 未指定技能名称，且当前目录下未探测到技能！")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Skill Factory 工业级 Agent 技能卸载中心")
    parser.add_argument("skill_name", nargs="?", default=None, help="要卸载的技能名称 (在技能工程内可省略)")
    parser.add_argument("-a", "--agents", help="指定卸载的 Agent (支持: claude, codex, cline)")
    parser.add_argument("-s", "--scope", choices=["global", "project"], default=None, help="卸载范围")
    parser.add_argument("-p", "--project-root", default=None, help="项目级根目录路径")
    parser.add_argument("-y", "--yes", action="store_true", help="非交互静默确认")

    args = parser.parse_args()
    skill_name = detect_current_skill_name(args.skill_name)
    project_root = os.path.abspath(args.project_root) if args.project_root else None

    all_statuses = inspect_agent_installations(skill_name, project_root)
    installed = [s for s in all_statuses if s.is_installed]

    if not installed:
        print(f"ℹ️  未在任何已知的 Agent (Claude/Codex/Cline) 目录中检测到 [{skill_name}] 的安装记录。")
        return

    is_interactive = sys.stdin.isatty() and not args.yes and args.agents is None

    if is_interactive:
        selected_targets = prompt_uninstall_targets(skill_name, installed)
        run_uninstallation(skill_name, selected_targets, project_root)
    else:
        filter_agents = [a.strip().lower() for a in args.agents.split(",")] if args.agents else None
        target_list = []
        for s in installed:
            if filter_agents and s.agent_key not in filter_agents:
                continue
            if args.scope and s.scope != args.scope:
                continue
            target_list.append(s)
        if not target_list:
            print("未找到匹配筛选条件的已安装技能。")
            return
        run_uninstallation(skill_name, target_list, project_root)


if __name__ == "__main__":
    main()
