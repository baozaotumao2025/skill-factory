#!/usr/bin/env python3
"""
{{SKILL_TITLE}} 全系统回归测试套件 (System Regression Test Suite)
覆盖：
1. 密态知识库检索引擎边界测试 (Database & Retrieval Engine Boundary Tests)
2. No AI Slop 规则合规性质检 (Slop Filter Compliance Tests)
3. 子命令契约完整性 (Commands Schema & 3-State Engine Integrity)
"""

import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(BASE_DIR, "skills", "{{SKILL_NAME}}")
RETRIEVE_PY = os.path.join(SKILL_DIR, "retrieve.py")
DB_PATH = os.path.join(SKILL_DIR, "knowledge.db")
SLOP_PY = os.path.join(SKILL_DIR, "slop_filter.py")
SLOP_MD = os.path.join(SKILL_DIR, "slop-filter.md")

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def test_retriever():
    print("▶ 1. 测试密态知识库与检索引擎边界...")
    assert os.path.exists(DB_PATH), "knowledge.db 文件不存在！"

    code, out, err = run_cmd(f"python3 {RETRIEVE_PY} --list")
    assert code == 0 and "Total" in out, f"列表检索失败: {err}"
    print("  [PASS] 知识库索引列表查询正常")

    code, out, err = run_cmd(f"python3 {RETRIEVE_PY} ch01")
    assert code == 0 and len(out.strip()) > 0, f"单章检索失败: {err}"
    print("  [PASS] 核心章节流式解压正常")

    code, out, err = run_cmd(f"python3 {RETRIEVE_PY} --search '###@@@$$$%'")
    assert "No matching" in err or out == "", "特殊字符搜索容错未生效"
    print("  [PASS] 极端特殊字符/空查询容错表现正常")

def test_slop_filter():
    print("\n▶ 2. 测试 No-AI-Slop 规则与自检合规性...")
    assert os.path.exists(SLOP_MD), "slop-filter.md 丢失！"
    assert os.path.exists(SLOP_PY), "slop_filter.py 丢失！"

    code, out, _ = run_cmd(f'python3 {SLOP_PY} "这不是一款产品，而是赋能未来"')
    assert "二元对立句式" in out and "赋能" in out, "静态去AI味脚本排雷失败"
    print("  [PASS] slop_filter.py 自动化静态拦截排雷运行正常")

def test_commands_integrity():
    print("\n▶ 3. 测试子命令契约完整性...")
    cmd_dir = os.path.join(BASE_DIR, ".claude", "commands")
    if os.path.exists(cmd_dir):
        for cmd_file in os.listdir(cmd_dir):
            if not cmd_file.endswith(".md"):
                continue
            fpath = os.path.join(cmd_dir, cmd_file)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            assert "State 1" in content and "State 2" in content and "State 3" in content, f"{cmd_file} 缺少三态引擎！"
            assert "retrieve.py" in content, f"{cmd_file} 未绑定密态检索引擎！"
            assert "slop-filter.md" in content, f"{cmd_file} 未绑定去AI味质检闸口！"
            print(f"  [PASS] {cmd_file} 强契约与三态引擎检验通过")

def main():
    print("==================================================")
    print("   {{SKILL_TITLE}} 自动化全套回归测试   ")
    print("==================================================")
    try:
        test_retriever()
        test_slop_filter()
        test_commands_integrity()
        print("\n==================================================")
        print(" 🎉 全部测试通过！系统处于 100% 工业级可用状态！  ")
        print("==================================================")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
