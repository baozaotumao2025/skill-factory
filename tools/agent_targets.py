#!/usr/bin/env python3
"""
tools/agent_targets.py - Agent 目标与宿主契约中枢 (Claude / Codex / Cline)
定义 2026 年主流 Agent 的技能发现路径、宿主挂载协议与状态探测能力。
"""

import os
import shutil
from typing import Dict, List, Optional, Tuple


class AgentDefinition:
    def __init__(self, key: str, display_name: str, icon: str, global_rel_path: str, project_rel_path: str):
        self.key = key
        self.display_name = display_name
        self.icon = icon
        self.global_rel_path = global_rel_path
        self.project_rel_path = project_rel_path

    @property
    def global_dir(self) -> str:
        return os.path.expanduser(self.global_rel_path)

    def get_project_dir(self, project_root: str) -> str:
        return os.path.join(os.path.abspath(project_root), self.project_rel_path)


SUPPORTED_AGENTS: Dict[str, AgentDefinition] = {
    "claude": AgentDefinition("claude", "Claude Code", "🟣", "~/.claude/skills", ".claude/skills"),
    "codex": AgentDefinition("codex", "OpenAI Codex", "🟢", "~/.codex/skills", ".codex/skills"),
    "cline": AgentDefinition("cline", "Cline", "🔵", "~/.cline/skills", ".cline/skills"),
}

VENDOR_NEUTRAL_GLOBAL_PATH = os.path.expanduser("~/.agents/skills")


class HostInstallStatus:
    def __init__(self, agent_key: str, scope: str, install_dir: str, is_installed: bool,
                 install_type: Optional[str] = None, target_path: Optional[str] = None, is_broken: bool = False):
        self.agent_key = agent_key
        self.scope = scope
        self.install_dir = install_dir
        self.is_installed = is_installed
        self.install_type = install_type
        self.target_path = target_path
        self.is_broken = is_broken

    @property
    def agent_def(self) -> AgentDefinition:
        return SUPPORTED_AGENTS[self.agent_key]


def inspect_agent_installations(skill_name: str, project_root: Optional[str] = None) -> List[HostInstallStatus]:
    results = []
    for key, agent_def in SUPPORTED_AGENTS.items():
        # 全局路径
        global_path = os.path.join(agent_def.global_dir, skill_name)
        results.append(_check_path_status(key, "global", global_path))
        # 项目级路径
        if project_root:
            proj_path = os.path.join(agent_def.get_project_dir(project_root), skill_name)
            results.append(_check_path_status(key, "project", proj_path))
    return results


def _check_path_status(agent_key: str, scope: str, path: str) -> HostInstallStatus:
    if not os.path.lexists(path):
        return HostInstallStatus(agent_key, scope, path, False)

    if os.path.islink(path):
        link_target = os.readlink(path)
        resolved = os.path.realpath(path)
        if not os.path.exists(path):
            return HostInstallStatus(agent_key, scope, path, True, "dangling_symlink", link_target, True)
        return HostInstallStatus(agent_key, scope, path, True, "symlink", resolved, False)

    if os.path.isdir(path):
        return HostInstallStatus(agent_key, scope, path, True, "directory", os.path.abspath(path), False)

    return HostInstallStatus(agent_key, scope, path, True, "unknown", path, False)


def install_skill_to_agent(
    source_skill_dir: str,
    skill_name: str,
    agent_key: str,
    scope: str = "global",
    project_root: Optional[str] = None,
    mode: str = "symlink",
    overwrite: bool = False
) -> Tuple[bool, str]:
    if agent_key not in SUPPORTED_AGENTS:
        return False, f"不支持的 Agent 类型: {agent_key}"

    agent_def = SUPPORTED_AGENTS[agent_key]
    parent_dir = agent_def.global_dir if scope == "global" else agent_def.get_project_dir(project_root or ".")
    target_path = os.path.join(parent_dir, skill_name)
    source_skill_dir = os.path.abspath(source_skill_dir)

    os.makedirs(parent_dir, exist_ok=True)

    if os.path.lexists(target_path):
        if not overwrite:
            return False, f"目标路径已存在: {target_path} (请使用覆盖选项)"
        if os.path.islink(target_path) or os.path.isfile(target_path):
            os.remove(target_path)
        elif os.path.isdir(target_path):
            shutil.rmtree(target_path)

    try:
        if mode == "symlink":
            os.symlink(source_skill_dir, target_path, target_is_directory=True)
            return True, f"已创建软链接: {target_path} -> {source_skill_dir}"
        elif mode == "copy":
            shutil.copytree(source_skill_dir, target_path)
            return True, f"已完成物理拷贝: {target_path}"
        return False, f"不支持的安装模式: {mode}"
    except Exception as e:
        return False, f"安装失败: {e}"


def uninstall_skill_from_agent(
    skill_name: str,
    agent_key: str,
    scope: str = "global",
    project_root: Optional[str] = None
) -> Tuple[bool, str]:
    if agent_key not in SUPPORTED_AGENTS:
        return False, f"不支持的 Agent 类型: {agent_key}"

    agent_def = SUPPORTED_AGENTS[agent_key]
    parent_dir = agent_def.global_dir if scope == "global" else agent_def.get_project_dir(project_root or ".")
    target_path = os.path.join(parent_dir, skill_name)

    if not os.path.lexists(target_path):
        return False, f"未在 {agent_def.display_name} ({scope}) 中发现已安装的技能"

    try:
        if os.path.islink(target_path) or os.path.isfile(target_path):
            os.remove(target_path)
            return True, f"已安全解除软链接: {target_path}"
        elif os.path.isdir(target_path):
            shutil.rmtree(target_path)
            return True, f"已删除物理安装目录: {target_path}"
        return False, f"未知文件类型，未做更改: {target_path}"
    except Exception as e:
        return False, f"卸载失败: {e}"


def get_all_agent_skill_dirs() -> List[str]:
    dirs = [agent.global_dir for agent in SUPPORTED_AGENTS.values()]
    if os.path.isdir(VENDOR_NEUTRAL_GLOBAL_PATH):
        dirs.append(VENDOR_NEUTRAL_GLOBAL_PATH)
    return dirs
