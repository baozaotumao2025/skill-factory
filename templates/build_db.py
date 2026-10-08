#!/usr/bin/env python3
import os
import re
import sqlite3
import zlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")
DB_PATH = os.path.join(BASE_DIR, "knowledge.db")

def build_vault():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE knowledge_vault (
        id TEXT PRIMARY KEY,
        chapter_num INTEGER,
        title TEXT,
        tag TEXT,
        payload BLOB
    )
    """)

    cur.execute("""
    CREATE TABLE knowledge_index (
        id TEXT PRIMARY KEY,
        keywords TEXT
    )
    """)

    count = 0
    for fname in sorted(os.listdir(CHAPTERS_DIR)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(CHAPTERS_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        cid_match = re.search(r"(ch\d+)", fname)
        cid = cid_match.group(1) if cid_match else fname.replace(".md", "")
        num_match = re.search(r"ch(\d+)", cid)
        cnum = int(num_match.group(1)) if num_match else 0

        lines = [line.strip() for line in content.split("\n") if line.strip()]
        title = lines[0].lstrip("#").strip() if lines else fname

        clean_words = " ".join(re.findall(r"[\u4e00-\u9fa5a-zA-Z0-9]+", content))

        compressed_payload = zlib.compress(content.encode("utf-8"), level=9)

        cur.execute(
            "INSERT INTO knowledge_vault (id, chapter_num, title, tag, payload) VALUES (?, ?, ?, ?, ?)",
            (cid, cnum, title, fname, compressed_payload)
        )
        cur.execute(
            "INSERT INTO knowledge_index (id, keywords) VALUES (?, ?)",
            (cid, clean_words)
        )
        count += 1

    conn.commit()
    conn.close()
    print(f"Successfully compiled {count} chapters into {DB_PATH}")

if __name__ == "__main__":
    build_vault()
