#!/usr/bin/env python3
"""
tools/absorb_proposal.py - 工厂母机端提案审核与吸收中心 (Factory Center Proposal Receiver)
运行环境：仅在 skill-factory 工厂根目录下运行
职责边界：审核端侧上报的反哺提案，正式收录入库 (生成 AP 编号、写入 rules、归档提案)。
"""

import argparse
from datetime import datetime, timezone
import json
import os
import re
import sys

REAL_FILE = os.path.realpath(__file__)
PARENT_DIR = os.path.dirname(REAL_FILE)
FACTORY_ROOT = os.path.dirname(PARENT_DIR) if os.path.basename(PARENT_DIR) == "tools" else PARENT_DIR
PROPOSALS_DIR = os.path.join(FACTORY_ROOT, "rules", "proposals")
ACCEPTED_DIR = os.path.join(PROPOSALS_DIR, "accepted")
REJECTED_DIR = os.path.join(PROPOSALS_DIR, "rejected")
ANTI_PATTERNS_FILE = os.path.join(FACTORY_ROOT, "rules", "anti_patterns.md")

os.makedirs(PROPOSALS_DIR, exist_ok=True)
os.makedirs(ACCEPTED_DIR, exist_ok=True)
os.makedirs(REJECTED_DIR, exist_ok=True)


def list_pending_proposals() -> list[dict]:
    proposals = []
    for fname in os.listdir(PROPOSALS_DIR):
        if fname.endswith(".json") and not fname.startswith("."):
            fpath = os.path.join(PROPOSALS_DIR, fname)
            if os.path.isfile(fpath):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        data["_filepath"] = fpath
                        proposals.append(data)
                except Exception:
                    pass
    proposals.sort(key=lambda x: x.get("submitted_at", ""), reverse=True)
    return proposals


def list_history_proposals() -> list[dict]:
    history = []
    # 1. 扫描已同意归档 (accepted)
    if os.path.isdir(ACCEPTED_DIR):
        for fname in os.listdir(ACCEPTED_DIR):
            if fname.endswith(".json") and not fname.startswith("."):
                fpath = os.path.join(ACCEPTED_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        data["_filepath"] = fpath
                        data["_type"] = "accepted"
                        history.append(data)
                except Exception:
                    pass

    # 2. 扫描已拒绝归档 (rejected)
    if os.path.isdir(REJECTED_DIR):
        for fname in os.listdir(REJECTED_DIR):
            if fname.endswith(".json") and not fname.startswith("."):
                fpath = os.path.join(REJECTED_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        data["_filepath"] = fpath
                        data["_type"] = "rejected"
                        history.append(data)
                except Exception:
                    pass

    history.sort(key=lambda x: x.get("accepted_at") or x.get("rejected_at") or x.get("submitted_at", ""), reverse=True)
    return history


def display_proposal_card(prop: dict):
    print("\n" + "=" * 70)
    print(f"📄 提案详情审查: \033[1;36m{prop.get('title')}\033[0m")
    print("-" * 70)
    print(f"  • 来源技能: {prop.get('source_skill')}")
    print(f"  • 商业场景: {prop.get('domain')} (强制场景隔离)")
    print(f"  • 提交时间: {prop.get('submitted_at', '')[:19].replace('T', ' ')}")
    print(f"  • 错误现象: {prop.get('issue', '无')}")
    print(f"  • 严重后果: {prop.get('consequence', '无')}")
    print(f"  • 正确解法: {prop.get('solution', '无')}")
    if prop.get("trigger_example"):
        print(f"  • 质检自检: {prop.get('trigger_example')}")
    if prop.get("status") == "accepted":
        print(f"  • 处理状态: \033[1;32m✅ 已同意入库 [{prop.get('assigned_ap', '')}]\033[0m ({prop.get('accepted_at', '')[:19].replace('T', ' ')})")
    elif prop.get("status") == "rejected":
        print(f"  • 处理状态: \033[1;31m❌ 已驳回归档\033[0m ({prop.get('rejected_at', '')[:19].replace('T', ' ')})")
        print(f"  • 驳回原因: {prop.get('reject_reason', '无')}")
    print("=" * 70)


def get_next_ap_number() -> tuple[str, int]:
    if not os.path.isfile(ANTI_PATTERNS_FILE):
        return "AP-001", 1
    with open(ANTI_PATTERNS_FILE, "r", encoding="utf-8") as f:
        matches = re.findall(r"AP-(\d{3})", f.read())
    nums = [int(m) for m in matches]
    next_num = max(nums) + 1 if nums else 1
    return f"AP-{next_num:03d}", next_num


def accept_proposal(prop: dict):
    ap_id, _ = get_next_ap_number()
    title = prop.get("title", "未命名教训")
    domain = prop.get("domain", "positioning")

    print(f"\n▶ 正在审核入库提案: [{prop.get('proposal_id')}]...")
    print(f"  分配编号: \033[1;32m{ap_id}\033[0m")
    print(f"  商业场景: \033[1;36m{domain}\033[0m")

    # 1. 写入 rules/anti_patterns.md
    with open(ANTI_PATTERNS_FILE, "r", encoding="utf-8") as f:
        md_text = f.read()

    new_section = f"""

### {ap_id}: {title} (Domain: {domain})
- **来源技能**：`{prop.get('source_skill')}`
- **现象**：{prop.get('issue', '')}
- **后果**：{prop.get('consequence', '')}
- **正解**：{prop.get('solution', '')}
"""
    if prop.get("trigger_example"):
        new_section += f"- **自检提示**：{prop['trigger_example']}\n"

    toc_entry = f"\n- [{ap_id}: {title}](#{ap_id.lower()}-{re.sub(r'[^\\w\\-]+', '-', title.lower()).strip('-')})"
    if "## 目录" in md_text:
        md_text = md_text.replace("## 目录", f"## 目录{toc_entry}")
    md_text = md_text.rstrip() + new_section

    with open(ANTI_PATTERNS_FILE, "w", encoding="utf-8") as f:
        f.write(md_text)
    print(f"  ✅ 1. 已成功收录入库: rules/anti_patterns.md ({ap_id})")

    # 2. 归档提案至 accepted/
    prop["status"] = "accepted"
    prop["assigned_ap"] = ap_id
    prop["accepted_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    target_file = os.path.join(ACCEPTED_DIR, os.path.basename(prop["_filepath"]))
    with open(target_file, "w", encoding="utf-8") as f:
        p_copy = dict(prop)
        p_copy.pop("_filepath", None)
        p_copy.pop("_type", None)
        json.dump(p_copy, f, indent=2, ensure_ascii=False)

    if os.path.isfile(prop["_filepath"]):
        os.remove(prop["_filepath"])
    print(f"  ✅ 2. 提案已归档至: rules/proposals/accepted/ (待处理箱中已清除)")
    print("-" * 70)
    print(f"🎉 提案已正式晋升为工厂核心基因 [{ap_id}]！")
    print("💡 统筹提醒: 若需发版推送到同类存量技能，可在工厂根目录下执行: python3 upgrade_skill.py --scan\n")


def reject_proposal(prop: dict, reason: str = ""):
    title = prop.get("title", "未命名提案")
    default_reason = "不符合通用化标准或包含私有业务细节"
    final_reason = reason.strip() if reason and reason.strip() else default_reason

    print(f"\n▶ 正在驳回提案: [{title}]...")
    prop["status"] = "rejected"
    prop["reject_reason"] = final_reason
    prop["rejected_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    target_file = os.path.join(REJECTED_DIR, os.path.basename(prop["_filepath"]))
    with open(target_file, "w", encoding="utf-8") as f:
        p_copy = dict(prop)
        p_copy.pop("_filepath", None)
        p_copy.pop("_type", None)
        json.dump(p_copy, f, indent=2, ensure_ascii=False)

    if os.path.isfile(prop["_filepath"]):
        os.remove(prop["_filepath"])
    print(f"  ❌ 提案已驳回并归档至: rules/proposals/rejected/ (待处理箱中已清除)")
    print(f"  📝 驳回原因: {final_reason}\n")


def prompt_proposal_action(prop: dict):
    display_proposal_card(prop)

    print("? 请选择对此提案的处理操作:")
    print("  [1] ✅ 同意入库 (Accept)   - 分配 AP 编号、写入 rules 规范库，并归档至 accepted/")
    print("  [2] ❌ 拒绝提案 (Reject)   - 输入驳回原因并归档至 rejected/，不入母机规范库")
    print("  [3] ⏳ 暂不处理 (Skip)     - 保持待处理状态留在待办箱，下次依然可见 [默认]")

    try:
        action = input("\n请选择操作 [1/2/3 默认: 3] > ").strip()
    except (EOFError, KeyboardInterrupt):
        action = "3"

    if action == "1":
        accept_proposal(prop)
    elif action == "2":
        try:
            r = input("请输入驳回原因 (直接回车使用默认: 不符合通用化标准或包含私有细节): ").strip()
        except (EOFError, KeyboardInterrupt):
            r = ""
        reject_proposal(prop, r)
    else:
        print(f"⏳ 提案 [{prop.get('title')}] 暂不处理，已保留在待处理箱中，下次可见。\n")


def show_history_view():
    history = list_history_proposals()
    print("\n" + "=" * 80)
    print(f"📜 Skill Factory · 反哺提案历史审计台账 (共 {len(history)} 条已归档)")
    print("=" * 80)

    if not history:
        print("  暂无任何历史处理记录。")
        return

    print(f"{'序号':<4} {'状态':<14} {'编号/原因':<20} {'来源技能':<16} {'场景':<12} {'处理时间':<20} {'提案标题'}")
    print("-" * 80)
    for idx, h in enumerate(history, 1):
        if h.get("_type") == "accepted":
            st_badge = "\033[1;32m✅ 已同意\033[0m"
            mark = h.get("assigned_ap", "")
            proc_time = h.get("accepted_at", "")[:19].replace("T", " ")
        else:
            st_badge = "\033[1;31m❌ 已驳回\033[0m"
            mark = h.get("reject_reason", "无原因")[:16]
            proc_time = h.get("rejected_at", "")[:19].replace("T", " ")

        print(f"{idx:<4} {st_badge:<22} {mark:<20} {h.get('source_skill',''):<16} {h.get('domain',''):<12} {proc_time:<20} {h.get('title','')}")
    print("-" * 80)

    if sys.stdin.isatty():
        try:
            choice = input("\n输入序号可查看该条历史提案的完整详情卡片 (直接回车退出) > ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(history):
                display_proposal_card(history[int(choice) - 1])
        except (EOFError, KeyboardInterrupt):
            pass


def main():
    parser = argparse.ArgumentParser(description="Skill Factory 母机提案审核吸收中心")
    parser.add_argument("-l", "--list", action="store_true", help="列出待审核提案")
    parser.add_argument("-H", "--history", action="store_true", help="查看所有历史处理记录 (已同意/已驳回)")
    parser.add_argument("-a", "--accept", help="通过并收录指定提案 (输入提案ID或待办序号)")
    parser.add_argument("-r", "--reject", help="驳回指定提案 (输入提案ID或待办序号)")
    parser.add_argument("--reason", default="", help="驳回原因")

    args = parser.parse_args()

    if args.history:
        show_history_view()
        return

    pending = list_pending_proposals()

    # 非交互命令行执行
    if args.accept:
        target = None
        for p in pending:
            if p.get("proposal_id") == args.accept:
                target = p
                break
        if not target and args.accept.isdigit() and 1 <= int(args.accept) <= len(pending):
            target = pending[int(args.accept) - 1]
        if target:
            accept_proposal(target)
        else:
            print(f"❌ 未找到待处理提案: {args.accept}")
        return

    if args.reject:
        target = None
        for p in pending:
            if p.get("proposal_id") == args.reject:
                target = p
                break
        if not target and args.reject.isdigit() and 1 <= int(args.reject) <= len(pending):
            target = pending[int(args.reject) - 1]
        if target:
            reject_proposal(target, args.reason)
        else:
            print(f"❌ 未找到待处理提案: {args.reject}")
        return

    # 默认/交互模式
    print("\n" + "=" * 70)
    print(f"📥 Skill Factory · 待审核反哺提案箱 (共 {len(pending)} 个待处理)")
    print("=" * 70)
    if not pending:
        print("  暂无待审核的端侧反哺提案。")
        print("  提示: 可使用 `python3 absorb_proposal.py --history` 查看历史归档台账。")
        return

    print(f"{'序号':<4} {'来源技能':<16} {'场景':<12} {'提交时间':<20} {'提案标题'}")
    print("-" * 70)
    for idx, p in enumerate(pending, 1):
        sub_time = p.get("submitted_at", "")[:19].replace("T", " ")
        print(f"{idx:<4} {p.get('source_skill',''):<16} {p.get('domain',''):<12} {sub_time:<20} {p.get('title','')}")
    print("-" * 70)

    if sys.stdin.isatty() and not args.list:
        try:
            choice = input("\n提示: 输入序号进行审核 (1/2/3态) | 输入 h 查看历史归档 | 直接回车退出 > ").strip().lower()
            if choice in ("h", "history"):
                show_history_view()
            elif choice.isdigit() and 1 <= int(choice) <= len(pending):
                prompt_proposal_action(pending[int(choice) - 1])
        except (EOFError, KeyboardInterrupt):
            pass


if __name__ == "__main__":
    main()
