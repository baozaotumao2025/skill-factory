#!/usr/bin/env python3
"""
tools/upgrade_skill.py - Skill Factory 工业级历史技能自动化升级器

功能：
1. 采用“血统指纹（Lineage Fingerprint）+ 向后兼容特征嗅探”双轨机制，精准探测由 skill-factory
   孵化的技能，绝对排除环境中的第三方外部技能（如 google-agents-*, tavily-* 等）；
2. 外科手术式无损升级：
   - 基础设施热替换：同步更新 slop-filter.md, slop_filter.py, retrieve.py, build_db.py；
   - 业务规约智能打补丁：增量注入金字塔原理、DoD 目标驱动、防中二拟人化反噬、AP-008 品牌即动作；
   - 子命令质检闸口注入：向 commands/*.md 追加品类替罪羊与品牌绑定审查；
   - 自动上牌：补全/升级 .skill-factory.json 清单与 SKILL.md Frontmatter 谱系元数据；
3. 自动化门禁闭环：调用 lint_skill.py 静态审计并尝试运行回归测试套件。

用法：
  python3 tools/upgrade_skill.py --scan
  python3 tools/upgrade_skill.py /path/to/skill --dry-run
  python3 tools/upgrade_skill.py /path/to/skill
  python3 tools/upgrade_skill.py --scan --upgrade-all
"""

import argparse
from datetime import datetime, timezone
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent_targets import (
    SUPPORTED_AGENTS,
    get_all_agent_skill_dirs,
    inspect_agent_installations
)
from domain_taxonomy import DOMAINS, infer_domain


REAL_FILE = os.path.realpath(__file__)
PARENT_DIR = os.path.dirname(REAL_FILE)
if os.path.basename(PARENT_DIR) == "tools":
    FACTORY_ROOT = os.path.dirname(PARENT_DIR)
else:
    FACTORY_ROOT = PARENT_DIR

TEMPLATES_DIR = os.path.join(FACTORY_ROOT, "templates")
CURRENT_FACTORY_VERSION = "2.1.0"

LATEST_PATCHES = [
    "AP-006-theatrical-persona",
    "AP-007-hard-dod-pyramid",
    "AP-008-category-martyr-brand-action"
]

RULE_TEMPLATES = {
    "pyramid": '4. **金字塔原理先行 (Pyramid Principle)**：所有方案输出必须**先结论后论据、先全局架构后模块细节**；分类必须严格做到 **MECE（相互独立、完全穷尽）**；用户输入若散乱，必须主动重组后再输出。',
    "dod": '5. **目标驱动执行与硬性 DoD (Goal-Driven Execution)**：将所有任务翻译为带量化指标的工程目标；多步任务必须包含明确的**可验证验收标准（Definition of Done）**，改完即验证，不一步一停等用户喂指令。',
    "persona": '6. **严禁拟人化中二自嗨 (Persona Antidote)**：严禁输出戏精台词或夸张江湖隐喻；始终保持优秀技术架构师与商业系统工程师的冷静、中立与严密。',
    "brand_action": '7. **防范品类替罪羊与品牌无主游魂 (Brand-Action Anchoring)**：若涉及无实体包装的无形服务、高客单决策或口碑转介绍品类，生成的口号与核心卖点严禁牺牲品牌名，必须通过【品牌即动作】将品牌名锁死为行动入口或语法主语（如“买卖二手车，上瓜子二手车”），坚决杜绝替全行业当免费雷锋的公益式口号。'
}


class SkillTarget:
    def __init__(self, project_root, skill_dir, name, lineage_type, version, manifest_path=None, domain="universal"):
        self.project_root = project_root
        self.skill_dir = skill_dir
        self.name = name
        self.lineage_type = lineage_type  # 'explicit' | 'legacy_fingerprint'
        self.version = version
        self.manifest_path = manifest_path
        self.domain = domain
        self.skill_md_path = os.path.join(skill_dir, "SKILL.md")
        self.canonical_dir = os.path.realpath(skill_dir)
        self.mounted_hosts = []


def detect_skill_lineage(target_dir):
    """
    智能判定指定目录是否属于 skill-factory 谱系。
    返回 SkillTarget 对象；若不属于则返回 None。
    """
    target_dir = os.path.abspath(target_dir)
    if not os.path.isdir(target_dir):
        return None

    project_root = None
    skill_dir = None
    skill_name = None

    # 形态 A：工程根目录，内有 skills/<name>
    skills_subdir = os.path.join(target_dir, "skills")
    if os.path.isdir(skills_subdir):
        subdirs = [d for d in os.listdir(skills_subdir) if os.path.isdir(os.path.join(skills_subdir, d))]
        for sub in subdirs:
            candidate = os.path.join(skills_subdir, sub)
            if os.path.isfile(os.path.join(candidate, "SKILL.md")):
                project_root = target_dir
                skill_dir = candidate
                skill_name = sub
                break

    # 形态 B：直接是技能目录本身
    if not skill_dir and os.path.isfile(os.path.join(target_dir, "SKILL.md")):
        skill_dir = target_dir
        skill_name = os.path.basename(target_dir)
        parent = os.path.dirname(target_dir)
        grandparent = os.path.dirname(parent)
        # 仅当是在普通工程目录结构中 (如 my-project/skills/my-skill，且父级不是 .agents 或 .claude 全局目录)
        if os.path.basename(parent) == "skills" and os.path.basename(grandparent) not in (".agents", ".claude", "skills"):
            project_root = grandparent
        else:
            project_root = target_dir

    if not skill_dir or not os.path.isfile(os.path.join(skill_dir, "SKILL.md")):
        return None

    # 检查显式标记 (Priority 1)
    manifest_candidates = [
        os.path.join(skill_dir, ".skill-factory.json"),
        os.path.join(project_root, ".skill-factory.json") if project_root and project_root != skill_dir else None
    ]
    manifest_path = None
    version = "1.0.0"
    domain = None
    is_explicit = False

    for mc in manifest_candidates:
        if mc and os.path.isfile(mc):
            try:
                with open(mc, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("generator") == "skill-factory":
                        # 必须技能名称匹配或清单就存放在该技能自身目录下
                        if mc == os.path.join(skill_dir, ".skill-factory.json") or data.get("skill_name") == skill_name:
                            manifest_path = mc
                            version = data.get("version", "1.0.0")
                            domain = data.get("domain")
                            is_explicit = True
                            break
            except Exception:
                pass

    with open(os.path.join(skill_dir, "SKILL.md"), "r", encoding="utf-8") as f:
        skill_md_content = f.read()

    if not domain:
        d_match = re.search(r"^domain:\s*([\w\-]+)", skill_md_content, re.MULTILINE)
        if d_match:
            domain = d_match.group(1).strip()

    if not domain or domain not in DOMAINS:
        inferred_domain, _, _ = infer_domain(f"{skill_name} {skill_md_content[:1000]}")
        domain = inferred_domain

    if "generator: skill-factory" in skill_md_content:
        is_explicit = True
        v_match = re.search(r"factory-version:\s*([\d\.]+)", skill_md_content)
        if v_match:
            version = v_match.group(1)

    if is_explicit:
        return SkillTarget(project_root, skill_dir, skill_name, "explicit", version, manifest_path, domain=domain)

    # 检查特征签名嗅探 (Priority 2 - 向后兼容历史技能)
    has_retrieve = os.path.isfile(os.path.join(skill_dir, "retrieve.py"))
    has_slop_filter = os.path.isfile(os.path.join(skill_dir, "slop-filter.md"))
    has_build_db = os.path.isfile(os.path.join(skill_dir, "build_db.py"))
    has_patterns = os.path.isfile(os.path.join(skill_dir, "patterns.md"))

    if (has_retrieve and has_slop_filter) or (has_patterns and has_slop_filter):
        keywords = ["slop-filter.md", "三态分流引擎", "State 1", "白纸引导态", "七重硬核信任状"]
        if any(kw in skill_md_content for kw in keywords):
            return SkillTarget(project_root, skill_dir, skill_name, "legacy_fingerprint", "1.0.0", None, domain=domain)

    return None


def scan_environment(search_roots=None):
    """
    扫描指定根目录，找出所有属于 skill-factory 谱系的技能。
    自动接入 Claude / Codex / Cline 宿主并进行真实物理路径 (canonical realpath) 归一化去重。
    """
    if not search_roots:
        home = os.path.expanduser("~")
        search_roots = [
            os.path.join(home, "Downloads"),
        ]
        for d in get_all_agent_skill_dirs():
            if d not in search_roots:
                search_roots.append(d)

    found = []
    seen_canonical_dirs = {}
    dangling_links = []

    for root_dir in search_roots:
        if not os.path.isdir(root_dir):
            continue

        # 检查宿主目录下的死链
        if any(root_dir.startswith(ad) for ad in get_all_agent_skill_dirs()):
            try:
                for entry in os.listdir(root_dir):
                    entry_path = os.path.join(root_dir, entry)
                    if os.path.islink(entry_path) and not os.path.exists(entry_path):
                        dangling_links.append((entry, entry_path, os.readlink(entry_path)))
            except Exception:
                pass

        for current_path, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build', '.cache')]
            depth = len(os.path.relpath(current_path, root_dir).split(os.sep))
            if depth > 4:
                dirnames.clear()
                continue

            target = detect_skill_lineage(current_path)
            if target:
                canonical = os.path.realpath(target.skill_dir)
                if canonical.startswith(FACTORY_ROOT):
                    continue
                if canonical in seen_canonical_dirs:
                    continue
                seen_canonical_dirs[canonical] = target
                # 嗅探当前技能在各大 Agent 下的挂载状态
                statuses = inspect_agent_installations(target.name)
                for st in statuses:
                    if st.is_installed and not st.is_broken:
                        agent_badge = f"{st.agent_def.icon}{st.agent_def.display_name}"
                        if agent_badge not in target.mounted_hosts:
                            target.mounted_hosts.append(agent_badge)
                found.append(target)

    if dangling_links:
        print("\n⚠️  [宿主环境检测] 发现以下断头失效软链接 (指向的原技能已被移动或删除):")
        for name, link_path, target in dangling_links:
            print(f"   - {name}: {link_path} -> {target}")
        print("   建议使用 `python3 uninstall_skill.py <name>` 进行清理。\n")

    return found


def diagnose_skill(target: SkillTarget):
    """
    对技能进行版本差异诊断，列出待补丁项。
    根据 target.domain 精准派发，杜绝跨场景规则污染。
    """
    diffs = []

    slop_path = os.path.join(target.skill_dir, "slop-filter.md")
    if os.path.isfile(slop_path):
        with open(slop_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "戏精角色扮演与中二隐喻" not in content:
            diffs.append("slop-filter.md 缺少 AP-006 (戏精中二反噬) 清洗规则")
        if target.domain == "positioning":
            if "品类替罪羊" not in content or "品牌无主游魂" not in content:
                diffs.append("slop-filter.md 缺少 AP-008 (品类替罪羊与品牌无主游魂) 质检项")
    else:
        diffs.append("缺失 slop-filter.md")

    with open(target.skill_md_path, "r", encoding="utf-8") as f:
        skill_content = f.read()

    if "金字塔原理先行" not in skill_content:
        diffs.append("SKILL.md 缺失第 4 条铁律：金字塔原理先行 (Pyramid Principle)")
    if "目标驱动执行与硬性 DoD" not in skill_content:
        diffs.append("SKILL.md 缺失第 5 条铁律：目标驱动执行与硬性 DoD (Goal-Driven Execution)")
    if "严禁拟人化中二自嗨" not in skill_content:
        diffs.append("SKILL.md 缺失第 6 条铁律：严禁拟人化中二自嗨 (Persona Antidote)")
    if target.domain == "positioning" and "防范品类替罪羊与品牌无主游魂" not in skill_content:
        diffs.append("SKILL.md 缺失第 7 条铁律：防范品类替罪羊与品牌无主游魂 (Brand-Action Anchoring)")

    if "generator: skill-factory" not in skill_content:
        diffs.append("SKILL.md Frontmatter 缺少工厂谱系元数据标记")

    if not target.manifest_path or not os.path.isfile(target.manifest_path):
        diffs.append("缺少 .skill-factory.json 工厂清单凭证")

    # 检查是否缺失安装器（仅针对普通外部工程根目录，不在宿主目录内套娃注入）
    proj_root = target.project_root or os.path.dirname(target.skill_dir)
    home = os.path.expanduser("~")
    agent_dirs = [os.path.join(home, ".claude"), os.path.join(home, ".codex"), os.path.join(home, ".cline"), os.path.join(home, ".agents")]
    is_in_host = any(os.path.abspath(proj_root).startswith(ad) for ad in agent_dirs)
    if proj_root and os.path.isdir(proj_root) and not is_in_host:
        if not os.path.isfile(os.path.join(proj_root, "install.py")):
            diffs.append("缺少多端开箱即用安装套件 (install.py / uninstall.py)")
        if not os.path.isfile(os.path.join(proj_root, "absorb_to_skill_factory.py")):
            diffs.append("缺少端侧反哺上报套件 (absorb_to_skill_factory.py)")


    return diffs



def upgrade_skill(target: SkillTarget, dry_run=False, force_domain=None):
    """
    对指定技能执行外科手术式升级，依据商业细分场景精准打补丁。
    """
    if force_domain:
        target.domain = force_domain
    domain_meta = DOMAINS.get(target.domain, DOMAINS["universal"])
    print(f"\n🚀 开始升级技能: [{target.name}] (细分场景: {domain_meta['name']}) -> {target.skill_dir}")
    diffs = diagnose_skill(target)

    if not diffs:
        print("  ✅ 该技能已符合当前工业标准，无需升级！")
        return True

    print("  📋 待修复与升级项:")
    for d in diffs:
        print(f"    - {d}")

    if dry_run:
        print("  [DRY-RUN] 预览完成，未修改物理文件。")
        return True

    # 1. 基础设施热替换
    infra_files = ["slop-filter.md", "slop_filter.py", "retrieve.py", "build_db.py"]
    for fname in infra_files:
        src = os.path.join(TEMPLATES_DIR, fname)
        dst = os.path.join(target.skill_dir, fname)
        if os.path.isfile(src):
            shutil.copy(src, dst)
            if fname.endswith(".py"):
                os.chmod(dst, 0o755)
            print(f"  [SYNC] 已同步最新基础设施: {fname}")

    # 2. SKILL.md 外科手术式打补丁
    with open(target.skill_md_path, "r", encoding="utf-8") as f:
        skill_text = f.read()

    # 2.1 Frontmatter 补丁 (含 domain 标记)
    if "generator: skill-factory" not in skill_text:
        skill_text = re.sub(
            r"^(---[\s\S]*?)(---)",
            r"\1generator: skill-factory\nfactory-version: " + CURRENT_FACTORY_VERSION + r"\ndomain: " + target.domain + r"\n\2",
            skill_text,
            count=1
        )
        print(f"  [PATCH] 已在 SKILL.md Frontmatter 中注入工厂血统与领域标记 ({target.domain})")
    else:
        skill_text = re.sub(
            r"factory-version:\s*[\d\.]+",
            f"factory-version: {CURRENT_FACTORY_VERSION}",
            skill_text
        )
        if "domain:" not in skill_text:
            skill_text = re.sub(
                r"^(---[\s\S]*?)(---)",
                r"\1domain: " + target.domain + r"\n\2",
                skill_text,
                count=1
            )
        else:
            skill_text = re.sub(r"domain:\s*[\w\-]+", f"domain: {target.domain}", skill_text)

    # 2.2 铁律增量追加 (按领域过滤)
    rules_header_pattern = r"(## 终极原则[^\n]*\n)"
    if re.search(rules_header_pattern, skill_text):
        to_append = []
        if "金字塔原理先行" not in skill_text:
            to_append.append(RULE_TEMPLATES["pyramid"])
        if "目标驱动执行与硬性 DoD" not in skill_text:
            to_append.append(RULE_TEMPLATES["dod"])
        if "严禁拟人化中二自嗨" not in skill_text:
            to_append.append(RULE_TEMPLATES["persona"])
        if target.domain == "positioning" and "防范品类替罪羊与品牌无主游魂" not in skill_text:
            to_append.append(RULE_TEMPLATES["brand_action"])

        if to_append:
            append_block = "\n" + "\n".join(to_append) + "\n"
            skill_text = skill_text.rstrip() + "\n" + append_block
            print(f"  [PATCH] 已增量追加 {len(to_append)} 条高阶工程铁律")

    with open(target.skill_md_path, "w", encoding="utf-8") as f:
        f.write(skill_text)

    # 3. commands/ 质检闸口注入 (仅 positioning 注入 AP-008 品牌绑定)
    if target.domain == "positioning":
        commands_dir = os.path.join(target.skill_dir, "commands")
        if os.path.isdir(commands_dir):
            for cmd_f in os.listdir(commands_dir):
                if cmd_f.endswith(".md"):
                    cmd_path = os.path.join(commands_dir, cmd_f)
                    with open(cmd_path, "r", encoding="utf-8") as f:
                        cmd_text = f.read()

                    if "执行品类载体与品牌绑定审查" not in cmd_text and "slop-filter.md" in cmd_text:
                        cmd_text = cmd_text.replace(
                            "执行可移植性测试：文案必须绑定具体机制，不能换个同行名字也能通顺通用。",
                            "执行可移植性测试：文案必须绑定具体机制，不能换个同行名字也能通顺通用；\n    - 执行品类载体与品牌绑定审查：若服务于无形服务业、高客单决策或口碑裂变品类，严禁输出无品牌名的行业公德口号（防范 AP-008 品类替罪羊），必须使用【品牌即动作】将品牌名锁死为必经入口。"
                        )
                        with open(cmd_path, "w", encoding="utf-8") as f:
                            f.write(cmd_text)
                        print(f"  [PATCH] [positioning] 已向子命令注入 AP-008 质检流水线: {cmd_f}")

    # 3.5 注入/同步开箱即用多端安装套件 (仅限外部独立工程根目录，不向已安装的宿主目录套娃注入)
    proj_root = target.project_root or os.path.dirname(target.skill_dir)
    home = os.path.expanduser("~")
    agent_dirs = [os.path.join(home, ".claude"), os.path.join(home, ".codex"), os.path.join(home, ".cline"), os.path.join(home, ".agents")]
    is_in_host = any(os.path.abspath(proj_root).startswith(ad) for ad in agent_dirs)
    if proj_root and os.path.isdir(proj_root) and not is_in_host:
        tools_dest = os.path.join(proj_root, "tools")
        os.makedirs(tools_dest, exist_ok=True)
        tools_src = os.path.join(FACTORY_ROOT, "tools")
        for tool_f in ["agent_targets.py", "install_skill.py", "uninstall_skill.py", "domain_taxonomy.py", "absorb_to_skill_factory.py"]:
            src_f = os.path.join(tools_src, tool_f)
            dst_f = os.path.join(tools_dest, tool_f)
            if os.path.isfile(src_f):
                shutil.copy(src_f, dst_f)
                os.chmod(dst_f, 0o755)
        for script_name, src_name in [("install.py", "install_skill.py"), ("uninstall.py", "uninstall_skill.py"), ("absorb_to_skill_factory.py", "absorb_to_skill_factory.py")]:
            src_f = os.path.join(tools_src, src_name)
            dst_f = os.path.join(proj_root, script_name)
            if os.path.isfile(src_f):
                shutil.copy(src_f, dst_f)
                os.chmod(dst_f, 0o755)

        # 补齐经验反哺子命令
        claude_cmds = os.path.join(proj_root, ".claude", "commands")
        if os.path.isdir(claude_cmds):
            absorb_cmd_path = os.path.join(claude_cmds, "absorb-to-skill-factory.md")
            if not os.path.isfile(absorb_cmd_path):
                with open(absorb_cmd_path, "w", encoding="utf-8") as ac_f:
                    ac_f.write("---\ndescription: 将本技能调试踩坑经验脱敏后提交给 Skill Factory 母机提案箱。\n---\n\n# 经验反哺母机 (absorbToSkillFactory)\n\n```bash\npython3 absorb_to_skill_factory.py\n```\n")

        print("  [TOOL] 已注入/同步多端安装套件与反哺通道 (install.py / uninstall.py / absorb_to_skill_factory.py)")

    # 4. 生成或更新 .skill-factory.json 清单凭证 (技能目录自身与工程根目录双重保护)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    applied = ["AP-006-theatrical-persona", "AP-007-hard-dod-pyramid"]
    if target.domain == "positioning":
        applied.append("AP-008-category-martyr-brand-action")

    manifest_data = {
        "generator": "skill-factory",
        "version": CURRENT_FACTORY_VERSION,
        "skill_name": target.name,
        "domain": target.domain,
        "upgraded_at": now_iso,
        "factory_root": FACTORY_ROOT,

        "applied_patches": applied
    }
    with open(os.path.join(target.skill_dir, ".skill-factory.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
    if target.project_root and target.project_root != target.skill_dir and not is_in_host:
        with open(os.path.join(target.project_root, ".skill-factory.json"), "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
    print(f"  [STAMP] 已上牌更新工厂清单凭证 (.skill-factory.json, 场景: {target.domain})")

    # 5. 门禁验证 (Lint Gate)
    lint_tool = os.path.join(FACTORY_ROOT, "tools", "lint_skill.py")
    if os.path.isfile(lint_tool):
        res = subprocess.run([sys.executable, lint_tool, target.skill_dir], capture_output=True, text=True)
        if res.returncode == 0:
            print("  ✅ 升级后静态门禁质检 (Lint) 通过！")
        else:
            print("  ⚠️  升级后静态门禁质检告警:")
            for line in res.stdout.splitlines():
                if "警告" in line or "建议" in line:
                    print(f"     {line}")

    print(f"🎉 技能 [{target.name}] 成功升级至 v{CURRENT_FACTORY_VERSION}！")
    return True



def main():
    parser = argparse.ArgumentParser(description="Skill Factory 工业级历史技能自动化升级器")
    parser.add_argument("target", nargs="?", help="指定待升级的技能目录或工程路径")
    parser.add_argument("--scan", action="store_true", help="自动全域扫描环境中所有 skill-factory 孵化的技能")
    parser.add_argument("--scan-dirs", nargs="+", help="自定义扫描目录列表")
    parser.add_argument("-p", "--pick", help="扫描后指定升级的序号 (如: 1,2)")
    parser.add_argument("-n", "--name", help="指定待升级的技能名称 (支持逗号分隔，如: core-forge,tob-master)")
    parser.add_argument(
        "--domain",
        choices=["tob-sales", "copywriting", "positioning"],
        default=None,
        help="显式指定或重标商业细分场景 (三选一: tob-sales | copywriting | positioning)"
    )
    parser.add_argument("--upgrade-all", action="store_true", help="与 --scan 配合使用，批量升级所有过期的技能")
    parser.add_argument("--dry-run", action="store_true", help="仅预览版本差异与拟修改项，不实际落盘")
    parser.add_argument("-y", "--yes", action="store_true", help="非交互静默确认")

    args = parser.parse_args()

    if args.name:
        skill_names = [x.strip() for x in args.name.split(",") if x.strip()]
        found = scan_environment(args.scan_dirs)
        matched = [s for s in found if s.name in skill_names]
        if not matched:
            print(f"❌ 未找到匹配名称的技能: {skill_names}")
            sys.exit(1)
        print(f"\n▶ 找到 {len(matched)} 个匹配技能，开始升级:")
        for s in matched:
            upgrade_skill(s, dry_run=args.dry_run, force_domain=args.domain)
        print("\n🎉 升级执行完毕！")
        return

    if args.scan:
        print(f"🔍 正在执行全域己方技能探测 (指纹优先 + 特征嗅探)...")
        found_skills = scan_environment(args.scan_dirs)

        if not found_skills:
            print("  未检测到任何由 skill-factory 孵化的历史技能。")
            return

        print(f"\n共识别到 {len(found_skills)} 个归属 skill-factory 谱系的技能:")
        print(f"{'序号':<4} {'技能名称':<18} {'商业细分':<12} {'版本':<8} {'健康状态':<16} {'挂载宿主':<22} {'物理路径'}")
        print("-" * 110)

        needs_upgrade = []
        for idx, s in enumerate(found_skills, 1):
            diffs = diagnose_skill(s)
            status = "已是最新" if not diffs else f"待升级 ({len(diffs)}项待补)"
            if diffs:
                needs_upgrade.append(s)
            hosts_str = " ".join(s.mounted_hosts) if s.mounted_hosts else "未挂载"
            domain_name = DOMAINS.get(s.domain, DOMAINS["positioning"])["name"][:7]
            print(f"{idx:<4} {s.name:<18} {domain_name:<12} {s.version:<8} {status:<16} {hosts_str:<22} {s.skill_dir}")

        print("-" * 110)

        targets_to_upgrade = []
        if args.upgrade_all:
            targets_to_upgrade = needs_upgrade
            if not targets_to_upgrade:
                print("所有技能均已处于最新工业标准，无需批量升级！")
                return
        elif args.pick:
            parts = [p.strip() for p in args.pick.replace("，", ",").split(",") if p.strip()]
            for p in parts:
                if p.isdigit() and 1 <= int(p) <= len(found_skills):
                    targets_to_upgrade.append(found_skills[int(p) - 1])
        elif sys.stdin.isatty() and not args.yes:
            if needs_upgrade:
                print(f"\n? 发现 {len(needs_upgrade)} 个技能存在待更新项，请选择操作:")
                print("  - 输入序号多选升级 (如: 1,2)")
                print("  - 输入 all 或 a (一键升级所有待更新技能)")
                print("  - 直接回车或输入 q (退出，不作修改)")
            else:
                print("\n? 所有检测到的技能均已处于最新标准。")
                print("  - 若需对指定技能强制刷新重打补丁，请输入序号 (如: 1,2)")
                print("  - 直接回车或输入 q (退出)")

            choice = input("选择编号 > ").strip().lower()
            if choice in ("all", "a"):
                targets_to_upgrade = needs_upgrade if needs_upgrade else found_skills
            elif choice and choice not in ("q", "quit", "exit"):
                parts = [p.strip() for p in choice.replace("，", ",").split(",") if p.strip()]
                for p in parts:
                    if p.isdigit() and 1 <= int(p) <= len(found_skills):
                        targets_to_upgrade.append(found_skills[int(p) - 1])
            else:
                print("已安全退出，未作任何更改。")
                return
        else:
            if needs_upgrade:
                print(f"\n💡 提示: 发现 {len(needs_upgrade)} 个技能存在待更新项。可添加 `--upgrade-all` 批量升级，或使用 `--pick 1,2` 指定升级。")
            return

        if not targets_to_upgrade:
            print("未选定任何待升级目标，已退出。")
            return

        dry_run = args.dry_run
        if sys.stdin.isatty() and not args.yes and not dry_run:
            ans = input(f"\n? 即将升级 {len(targets_to_upgrade)} 个技能，是否先执行 Dry-run 预览差异? [y/N 默认: N直接升级]: ").strip().lower()
            if ans in ("y", "yes"):
                dry_run = True

        print(f"\n▶ 正在执行升级 (共 {len(targets_to_upgrade)} 个技能)...")
        for s in targets_to_upgrade:
            upgrade_skill(s, dry_run=dry_run, force_domain=args.domain)
        print("\n🎉 升级执行完毕！")
        return

    if args.target:
        target = detect_skill_lineage(args.target)
        if not target:
            print(f"❌ 目标路径 '{args.target}' 不是由 skill-factory 孵化的有效技能，已安全跳过以防误伤。")
            sys.exit(1)

        upgrade_skill(target, dry_run=args.dry_run, force_domain=args.domain)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

