#!/usr/bin/env python3
"""
tools/domain_taxonomy.py - 商业操盘与实战转化领域细分模型 (Domain Taxonomy)

唯一主类别：商业操盘与实战转化 (Commercial Operations & Strategy)
细分子领域（三选一，强制收敛，禁止实例化 universal，防止经验反哺时毒化系统底座）：
  - tob-sales:    ToB大客户采购与复杂决策链销售 (对齐客户CFO/决策链)
  - copywriting:  公私域内容与爆款转化文案 (对齐大众消费者/点击转化)
  - positioning:  品牌战略与心智定位 (对齐创始人/公司战略心智)
"""

from typing import Dict, List, Optional, Tuple

DOMAINS: Dict[str, dict] = {
    "tob-sales": {
        "key": "tob-sales",
        "name": "ToB大客户与组织销售",
        "audience": "最终方案给客户老板 / 采购 / CFO 看",
        "display": "搞定客户签单：教销售谈单、攻破采购决策链、做财务算账报价",
        "keywords": [
            "tob", "to-b", "b端", "大客户", "采购", "决策链", "dmu", "销售", "签单",
            "商机", "线索", "回本", "mql", "sql", "谈判", "续约", "增购", "标杆案例"
        ]
    },
    "copywriting": {
        "key": "copywriting",
        "name": "公私域内容与爆款文案",
        "audience": "最终内容发给大众消费者 / 读者看",
        "display": "搞流量与卖货：写爆款短视频脚本、小红书种草、私域高转化文案",
        "keywords": [
            "文案", "脚本", "短视频", "小红书", "朋友圈", "种草", "标题", "爆款",
            "投放", "信息流", "转化率", "点击率", "完播率", "卖点提炼", "痛点共鸣"
        ]
    },
    "positioning": {
        "key": "positioning",
        "name": "战略定位与品牌心智",
        "audience": "最终战略给公司创始人 / 高管层看",
        "display": "搞品牌与战略：提炼第一购买理由、起超级口号、找差异化卖点",
        "keywords": [
            "定位", "心智", "购买理由", "超级口号", "口号", "品牌", "差异化",
            "品类", "避险因果", "认知", "护城河", "战略", "公德心"
        ]
    }
}

VALID_DOMAINS = list(DOMAINS.keys())


def infer_domain(text: str) -> Tuple[str, float, str]:
    """
    根据标题、一句话定位或语料片段进行轻量级语义特征打分，强制在 3 个垂直子领域中收敛。
    绝不返回 universal，防止污染系统公共底座。
    返回: (domain_key, 置信度 0.0~1.0, 命中理由)
    """
    if not text:
        return "positioning", 0.5, "未提供文本，依据主干战略强制收敛至定位基准 (positioning)"

    lower_text = text.lower()
    scores: Dict[str, int] = {"tob-sales": 0, "copywriting": 0, "positioning": 0}
    matched_words: Dict[str, List[str]] = {"tob-sales": [], "copywriting": [], "positioning": []}

    for d_key in VALID_DOMAINS:
        for kw in DOMAINS[d_key]["keywords"]:
            if kw in lower_text:
                scores[d_key] += 1
                matched_words[d_key].append(kw)

    max_score = max(scores.values())
    if max_score == 0:
        return "positioning", 0.5, "特征较为泛化，强制收敛至商业主干战略 (positioning)，禁止虚化为通用模式"

    best_domain = max(scores, key=lambda k: scores[k])
    confidence = min(0.6 + max_score * 0.1, 0.95)
    reason = f"命中核心特征词: {', '.join(matched_words[best_domain][:3])}"
    return best_domain, confidence, reason


def prompt_user_domain(default_domain: Optional[str] = None, text_for_inference: str = "") -> str:
    """
    在终端向用户呈现以“最终交付物给谁看”为准绳的强制三选一探针界面。
    杜绝第四个逃避选项，彻底保护系统底座。
    """
    inferred_domain, conf, reason = infer_domain(text_for_inference)
    recommended = default_domain if (default_domain in DOMAINS) else inferred_domain

    print("\n" + "=" * 65)
    print("🎯 请确认该技能最终成果【对谁负责 / 主要给谁看】 (必须三选一):")
    print(f"💡 系统已自动分析，智能推荐: \033[1;32m{DOMAINS[recommended]['name']} ({recommended})\033[0m")
    if text_for_inference:
        print(f"   推断依据: {reason} (置信度: {int(conf * 100)}%)")
    print("=" * 65)

    options = ["tob-sales", "copywriting", "positioning"]
    for idx, opt in enumerate(options, 1):
        rec_tag = " \033[1;33m[推荐方案]\033[0m" if opt == recommended else ""
        print(f"  [{idx}] 【{DOMAINS[opt]['name']}】 ({DOMAINS[opt]['audience']})")
        print(f"      业务场景: {DOMAINS[opt]['display']}{rec_tag}")

    def_idx = options.index(recommended) + 1
    choice = input(f"\n请选择编号 [直接回车采纳推荐: {def_idx}] > ").strip()

    if not choice:
        return recommended
    if choice.isdigit() and 1 <= int(choice) <= len(options):
        return options[int(choice) - 1]
    if choice.lower() in DOMAINS:
        return choice.lower()

    return recommended


    if not choice:
        return recommended
    if choice.isdigit() and 1 <= int(choice) <= len(options):
        return options[int(choice) - 1]
    if choice.lower() in DOMAINS:
        return choice.lower()

    return recommended
