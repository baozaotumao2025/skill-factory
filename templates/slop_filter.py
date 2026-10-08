#!/usr/bin/env python3
"""
卖点铸造局 · 去 AI 味静态质检脚本 (Core Forge Slop Linter & Filter)
移植自 petergyang/no-ai-slop 规则，针对中文商业文案、口号、定位语进行硬规则静态排雷。
零外部依赖（纯 Python 标准库），支持独立命令行运行、文件检查或被子命令调用。
"""

import argparse
import re
import sys

# 1. 典型 AI 腔调黑话词库 (Buzzwords & Puffery)
BUZZWORDS = [
    "赋能", "闭环", "链路", "抓手", "矩阵", "沉淀", "打法", "重构",
    "颠覆认知", "降维打击", "全方位", "深层次", "重新定义", "全新时代",
    "见证了", "见证每一次", "匠心铸就", "尊享", "非凡", "智享",
    "品质之选", "不忘初心", "为了更好的你", "让美好发生", "时代的眼泪"
]

# 2. 伪深刻假升华词组 (Fake-profound kickers)
FAKE_PROFOUND = [
    "未来的列车早已启程", "时间会给出最好的答案", "这就是最好的证明",
    "一切都是最好的安排", "写在最后", "划重点", "很多人不知道的是",
    "其实真相是", "必须承认的是", "毋庸置疑"
]

# 3. 典型二元对立正则模式 (Binary contrast regex)
BINARY_PATTERNS = [
    r"不是[^，。！？]+，?而是[^，。！？]+",
    r"不仅是?[^，。！？]+，?更是[^，。！？]+",
    r"不只是?[^，。！？]+，?更是[^，。！？]+",
    r"重要的不是[^，。！？]+，?而是[^，。！？]+",
]

# 4. 冒号揭秘式装腔 (Colon reveals)
COLON_PATTERNS = [
    r"(秘密|答案|真相|关键|核心|原因)(只有|就是|在于)?\s*[:：]",
]

# 5. 武侠玄学化用词 (Martial/theatrical drama)
THEATRICAL_WORDS = [
    "重锤诛心", "破甲反杀", "残酷认知反差", "一剑封喉", "绝杀招式"
]


def audit_text(text: str):
    issues = []
    
    # 检查 1: 二元对立
    for pat in BINARY_PATTERNS:
        matches = re.findall(pat, text)
        for m in matches:
            issues.append({
                "type": "二元对立句式 (Binary Contrast)",
                "match": m,
                "suggestion": "删去虚假衬托，直接陈述产品客观物理功效或参数"
            })

    # 检查 2: 冒号揭秘
    for pat in COLON_PATTERNS:
        matches = re.finditer(pat, text)
        for m in matches:
            issues.append({
                "type": "冒号揭秘式装腔 (Colon Reveal)",
                "match": m.group(0),
                "suggestion": "去掉悬疑铺垫，合并为平实的大白话陈述句"
            })

    # 检查 3: 虚浮黑话词
    for w in BUZZWORDS:
        if w in text:
            issues.append({
                "type": "空洞黑话与浮夸修饰 (Buzzword Puffery)",
                "match": w,
                "suggestion": "替换为具体的秒数、克重、金额账或物理事实"
            })

    # 检查 4: 伪深刻结语
    for w in FAKE_PROFOUND:
        if w in text:
            issues.append({
                "type": "伪深刻感叹结语 (Fake-profound Kicker)",
                "match": w,
                "suggestion": "删去煽情升华，结尾收敛在具体动作指令或算账结果上"
            })

    # 检查 5: 戏剧性玄学词
    for w in THEATRICAL_WORDS:
        if w in text:
            issues.append({
                "type": "戏剧玄学夸大词 (Theatrical Metaphor)",
                "match": w,
                "suggestion": "替换为客观商业词汇（如：购买理由、事实依据、直接指令）"
            })

    # 检查 6: 长破折号滥用
    dash_count = text.count("——") + text.count("—")
    if dash_count >= 2:
        issues.append({
            "type": "长破折号滥用 (Em Dash Clutter)",
            "match": f"出现 {dash_count} 处破折号",
            "suggestion": "在短文案中删去破折号，改用逗号、句号或自然分句"
        })

    return issues


def clean_text_suggestions(text: str):
    """给出快速去 AI 味的处理报告"""
    issues = audit_text(text)
    score = max(0, 100 - len(issues) * 15)
    return issues, score


def main():
    parser = argparse.ArgumentParser(description="Core Forge No-AI-Slop Linter (去 AI 味静态排雷脚本)")
    parser.add_argument("input", nargs="?", help="待检测的文本字符串，或使用 --file")
    parser.add_argument("-f", "--file", type=str, help="待检测的文本文件路径")
    parser.add_argument("--strict", action="store_true", help="严格模式：存在任一 AI 腔调即返回非零退出码")

    args = parser.parse_args()

    content = ""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    elif args.input:
        content = args.input
    else:
        if not sys.stdin.isatty():
            content = sys.stdin.read()
        else:
            parser.print_help()
            sys.exit(0)

    issues, score = clean_text_suggestions(content)

    print(f"==================================================")
    print(f"      No-AI-Slop 去 AI 味质检报告 (得分: {score}/100)")
    print(f"==================================================")

    if not issues:
        print("  ✅ 恭喜！未检出明显 AI 腔调套路。")
        print("  文案具备大白话、重事实、无空洞煽情的高人味特征。")
    else:
        print(f"  ⚠️ 共发现 {len(issues)} 处高频 AI 腔调死穴：\n")
        for i, item in enumerate(issues, 1):
            print(f"  {i}. [{item['type']}]")
            print(f"     命中内容: \"{item['match']}\"")
            print(f"     手术建议: {item['suggestion']}\n")

    if args.strict and issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
