#!/usr/bin/env python3
"""
tools/absorb_to_skill_factory.py - 端侧技能经验反哺上报工具 (Client-Side Feedback Submitter)

运行环境：在具体的业务技能工程内部运行 (如 ~/Desktop/tob-master/)
职责边界：仅从当前技能提炼新坑与防御对策，脱敏后提交给工厂母机提案箱。
坚决不执行越权的全网扫描与跨技能广播。
"""

import argparse
from datetime import datetime, timezone
import json
import os
import re
import sys

DEFAULT_FACTORY_ROOT = "/Users/cherubines/Downloads/skill-factory"


def find_factory_root(skill_dir: str, project_root: str) -> str:
    env_root = os.environ.get("SKILL_FACTORY_ROOT")
    if env_root and os.path.isdir(env_root) and os.path.isfile(os.path.join(env_root, "make_skill.py")):
        return os.path.abspath(env_root)

    for p in [os.path.join(skill_dir, ".skill-factory.json"), os.path.join(project_root, ".skill-factory.json")]:
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    fr = json.load(f).get("factory_root")
                    if fr and os.path.isdir(fr):
                        return os.path.abspath(fr)
            except Exception:
                pass

    candidate_parent = os.path.abspath(os.path.join(project_root, "..", ".."))
    if os.path.isfile(os.path.join(candidate_parent, "make_skill.py")):
        return candidate_parent

    if os.path.isdir(DEFAULT_FACTORY_ROOT) and os.path.isfile(os.path.join(DEFAULT_FACTORY_ROOT, "make_skill.py")):
        return os.path.abspath(DEFAULT_FACTORY_ROOT)

    print("❌ 错误: 无法定位 Skill Factory 母机路径！")
    print("   请设置环境变量: export SKILL_FACTORY_ROOT=/path/to/skill-factory")
    sys.exit(1)


def detect_current_skill_info() -> tuple[str, str, str, str]:
    cur_dir = os.path.abspath(".")
    skill_dir, project_root = cur_dir, cur_dir
    skill_name = os.path.basename(cur_dir)
    domain = "positioning"

    skills_sub = os.path.join(cur_dir, "skills")
    if os.path.isdir(skills_sub):
        for sub in os.listdir(skills_sub):
            cand = os.path.join(skills_sub, sub)
            if os.path.isdir(cand) and os.path.isfile(os.path.join(cand, "SKILL.md")):
                skill_dir, skill_name, project_root = cand, sub, cur_dir
                break

    for mc in [os.path.join(skill_dir, ".skill-factory.json"), os.path.join(project_root, ".skill-factory.json")]:
        if os.path.isfile(mc):
            try:
                with open(mc, "r", encoding="utf-8") as f:
                    m = json.load(f)
                    if m.get("skill_name"):
                        skill_name = m["skill_name"]
                    if m.get("domain") in ("tob-sales", "copywriting", "positioning"):
                        domain = m["domain"]
            except Exception:
                pass

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if os.path.isfile(skill_md):
        with open(skill_md, "r", encoding="utf-8") as f:
            dm = re.search(r"^domain:\s*([\w\-]+)", f.read(), re.MULTILINE)
            if dm and dm.group(1).strip() in ("tob-sales", "copywriting", "positioning"):
                domain = dm.group(1).strip()

    return skill_name, domain, skill_dir, project_root


def sanitize_text(text: str) -> tuple[bool, str]:
    patterns = [
        (r"(sk-[a-zA-Z0-9]{20,})", "API Key"),
        (r"(ghp_[a-zA-Z0-9]{20,})", "Token"),
        (r"(1[3-9]\d{9})", "手机号"),
        (r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", "邮箱地址")
    ]
    for p, desc in patterns:
        if re.search(p, text):
            return False, f"检测到可能包含私密敏感信息 ({desc})，请脱敏后再提交！"
    return True, ""


def submit_proposal(factory_root: str, skill_name: str, domain: str, title: str,
                    issue: str, consequence: str, solution: str, trigger_example: str):
    print("\n▶ 正在向技能工厂母机提交反哺提案...")
    print("-" * 60)

    full_text = f"{title}\n{issue}\n{consequence}\n{solution}\n{trigger_example}"
    ok, err = sanitize_text(full_text)
    if not ok:
        print(f"  ❌ 脱敏拦截: {err}")
        sys.exit(1)
    print("  ✅ 1. 本地脱敏安全审计通过 (无私有凭证与联系方式)")

    if domain not in ("tob-sales", "copywriting", "positioning"):
        domain = "positioning"
    print(f"  ✅ 2. 商业细分场景锁定: [{domain}] (绝不泛化为 universal)")

    now_utc = datetime.now(timezone.utc)
    now_iso = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    slug = re.sub(r"[^\w\-]+", "-", title.lower()).strip("-")[:30] or "new-lesson"
    proposal_id = f"{now_utc.strftime('%Y%m%d_%H%M%S')}_{skill_name}_{slug}"

    proposal_dir = os.path.join(factory_root, "rules", "proposals")
    os.makedirs(proposal_dir, exist_ok=True)
    proposal_file = os.path.join(proposal_dir, f"{proposal_id}.json")

    payload = {
        "proposal_id": proposal_id,
        "submitted_at": now_iso,
        "source_skill": skill_name,
        "domain": domain,
        "title": title,
        "issue": issue,
        "consequence": consequence,
        "solution": solution,
        "trigger_example": trigger_example,
        "status": "pending_review"
    }

    with open(proposal_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"  ✅ 3. 已生成结构化提案: rules/proposals/{os.path.basename(proposal_file)}")
    print("-" * 60)
    print("🎉 反哺提案已成功交付母机提案箱！")
    print("💡 当前端侧技能任务已闭环退出。母机管理员可在工厂统筹审核并适时发版。\n")


def prompt_user_input(skill_name: str, domain: str, factory_root: str):
    print("\n" + "=" * 60)
    print("🏭 Skill Factory · 经验反哺上报通道 (absorbToSkillFactory)")
    print(f"来源技能: \033[1;36m{skill_name}\033[0m")
    print(f"所属场景: \033[1;32m{domain}\033[0m")
    print(f"目标母机: {factory_root}")
    print("=" * 60)

    print("\n请提供本次调试实战中沉淀的经验教训 (大白话填写即可):")
    title = input("? 1. 这次踩坑的简短【标题/主题】 (如: ToB方案缺少CFO回本测算): ").strip()
    while not title:
        title = input("  标题不能为空，请重新输入: ").strip()

    issue = input("? 2. 踩坑的典型【错误现象】 (如: 销售给大客户出方案时只讲产品功能，没有算账): ").strip()
    consequence = input("? 3. 导致的【严重后果】 (如: 客户业务认可但CFO一票否决): ").strip()
    solution = input("? 4. 验证有效的【防御规约/正确做法】 (如: 强制输出3列财务算账卡): ").strip()
    trigger_example = input("? 5. 典型排雷语句/自检提示 (直接回车可留空): ").strip()

    return title, issue, consequence, solution, trigger_example


def main():
    parser = argparse.ArgumentParser(description="Skill Factory 端侧技能经验反哺上报工具 (absorbToSkillFactory)")
    parser.add_argument("-t", "--title", help="经验教训简短标题")
    parser.add_argument("-i", "--issue", help="错误现象描述")
    parser.add_argument("-c", "--consequence", help="导致的严重后果")
    parser.add_argument("-s", "--solution", help="验证有效的正确解法/规约")
    parser.add_argument("-e", "--example", default="", help="典型排雷自检短语")
    parser.add_argument("--factory-root", help="自定义母机路径")
    parser.add_argument("-y", "--yes", action="store_true", help="非交互自动提交")

    args = parser.parse_args()
    skill_name, domain, skill_dir, project_root = detect_current_skill_info()
    factory_root = os.path.abspath(args.factory_root) if args.factory_root else find_factory_root(skill_dir, project_root)

    is_interactive = sys.stdin.isatty() and not args.yes and (not args.title or not args.issue or not args.solution)

    if is_interactive:
        title, issue, consequence, solution, trigger_example = prompt_user_input(skill_name, domain, factory_root)
    else:
        title = args.title or "实践经验沉淀"
        issue = args.issue or "未详细说明错误现象"
        consequence = args.consequence or "方案交付效果未达预期"
        solution = args.solution or "按规范执行质检与约束"
        trigger_example = args.example

    submit_proposal(factory_root, skill_name, domain, title, issue, consequence, solution, trigger_example)


if __name__ == "__main__":
    main()

