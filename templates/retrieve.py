#!/usr/bin/env python3
"""
卖点铸造局 · 零依赖密态知识库检索引擎 (Core Forge Vault Retriever)
基于 Python 内置 sqlite3 与 zlib 标准库，毫秒级流式解压召回，人类无法肉眼直视。
"""

import argparse
import os
import re
import sqlite3
import sys
import zlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "knowledge.db")


def get_db():
    if not os.path.exists(DB_PATH):
        sys.stderr.write(f"Error: knowledge vault not found at {DB_PATH}\n")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)


def list_chapters():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, chapter_num, title, tag FROM knowledge_vault ORDER BY chapter_num ASC")
    rows = cur.fetchall()
    conn.close()
    print(f"Total {len(rows)} chapters in vault:")
    for r in rows:
        print(f"  [{r[0]}] {r[2]} ({r[3]})")


def get_by_ids(cids):
    conn = get_db()
    cur = conn.cursor()
    results = []
    for cid in cids:
        # Normalize: e.g. 'ch19-slogan' or '19' or 'ch19'
        m = re.search(r"(\d+)", cid)
        target_id = f"ch{int(m.group(1)):02d}" if m else cid
        cur.execute("SELECT id, title, payload FROM knowledge_vault WHERE id = ? OR id = ?", (target_id, cid))
        row = cur.fetchone()
        if row:
            raw_text = zlib.decompress(row[2]).decode("utf-8")
            results.append(raw_text)
        else:
            # Fallback search by tag/title
            cur.execute("SELECT id, title, payload FROM knowledge_vault WHERE tag LIKE ? OR title LIKE ?", (f"%{cid}%", f"%{cid}%"))
            for r in cur.fetchall():
                raw_text = zlib.decompress(r[2]).decode("utf-8")
                results.append(raw_text)
    conn.close()
    return results


def search_keywords(query, top_k=2):
    conn = get_db()
    cur = conn.cursor()
    terms = re.findall(r"[\u4e00-\u9fa5a-zA-Z0-9]+", query)
    if not terms:
        return []

    cur.execute("SELECT id, keywords FROM knowledge_index")
    rows = cur.fetchall()

    scored = []
    for cid, kws in rows:
        score = 0
        for term in terms:
            score += kws.count(term)
        if score > 0:
            scored.append((score, cid))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_cids = [item[1] for item in scored[:top_k]]
    conn.close()
    return get_by_ids(top_cids)


def main():
    parser = argparse.ArgumentParser(description="Core Forge Knowledge Vault Retriever")
    parser.add_argument("chapters", nargs="*", help="Chapter IDs to retrieve (e.g. ch19 ch20)")
    parser.add_argument("-s", "--search", type=str, help="Search vault by natural language query")
    parser.add_argument("-l", "--list", action="store_true", help="List all indexed chapters")
    parser.add_argument("-k", "--top-k", type=int, default=2, help="Number of search matches to return")

    args = parser.parse_args()

    if args.list:
        list_chapters()
        return

    if args.search:
        texts = search_keywords(args.search, top_k=args.top_k)
        if texts:
            print("\n\n---\n\n".join(texts))
        else:
            sys.stderr.write("No matching knowledge found in vault.\n")
        return

    if args.chapters:
        texts = get_by_ids(args.chapters)
        if texts:
            print("\n\n---\n\n".join(texts))
        else:
            sys.stderr.write(f"Chapters {args.chapters} not found in vault.\n")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
