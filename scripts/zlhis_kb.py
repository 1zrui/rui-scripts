#!/usr/bin/env python3
"""ZLHIS+ SQL 知识库 — 解析学习笔记，提取 SQL 片段，嵌入 ChromaDB，支持智能问答。

用法:
    python zlhis_kb.py --build                 # 构建/重建知识库
    python zlhis_kb.py --ask "住院药品发放怎么查"  # 智能问答
    python zlhis_kb.py --list                  # 列出所有知识条目
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field

# ── 配置 ──────────────────────────────────────────────────────────────────────
NOTES_DIR = Path(__file__).resolve().parent.parent / "SQL" / "学习笔记"
DB_DIR = Path(__file__).resolve().parent / ".zlhis_chromadb"
COLLECTION_NAME = "zlhis_sql"
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # 多语言，体积小，效果好


@dataclass
class KBEntry:
    """一条知识库条目。"""
    title: str
    category: str        # sql_snippet / field_ref / table_ref / join_ref / note
    content: str
    source_file: str
    metadata: dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        """基于内容生成稳定 ID。"""
        raw = f"{self.source_file}|{self.title}|{self.content[:200]}"
        return hashlib.md5(raw.encode()).hexdigest()


# ── Markdown 解析 ─────────────────────────────────────────────────────────────

def parse_md_file(path: Path) -> list[KBEntry]:
    """解析单个 .md 文件，提取各类知识条目。"""
    text = path.read_text(encoding="utf-8")
    source = path.name
    entries: list[KBEntry] = []

    # 1. 提取 SQL 代码块
    sql_blocks = re.findall(r"```sql\s*\n(.*?)```", text, re.DOTALL)
    for i, sql in enumerate(sql_blocks):
        sql = sql.strip()
        if not sql:
            continue
        # 尝试从 SQL 前面的标题获取描述
        title = _find_heading_for_sql(text, sql, i)
        entries.append(KBEntry(
            title=title or f"SQL片段 #{i+1}",
            category="sql_snippet",
            content=sql,
            source_file=source,
        ))

    # 2. 提取表定义（字段表格）
    table_defs = re.findall(
        r"###\s*(.+?)\n\n(?:.*?\n)*?\|.*?\|.*?\|\n\|[-|: ]+\|\n((?:\|.*?\n)+)",
        text,
    )
    for name, rows in table_defs:
        # 只保留看起来像字段表的（有多行表格数据）
        if rows.count("\n") < 2:
            continue
        content = f"### {name}\n{rows.strip()}"
        entries.append(KBEntry(
            title=name.strip(),
            category="table_ref",
            content=content,
            source_file=source,
        ))

    # 3. 提取字段值说明（表格：值 | 含义）
    field_values = re.findall(
        r"###\s*(\d+\.\s*.+?)(?:\n.*?)*?\|.*值.*含义.*\|\n\|[-|: ]+\|\n((?:\|.*?\n)+)",
        text,
    )
    for name, rows in field_values:
        entries.append(KBEntry(
            title=name.strip(),
            category="field_ref",
            content=f"{name.strip()}\n{rows.strip()}",
            source_file=source,
        ))

    # 4. 提取关联关系表格（含"关联字段"列标题）
    join_tables = re.findall(
        r"###\s*(.+?)\n\n\|(?:.*?表.*?字段.*?\|.*?\|)\n\|[-|: ]+\|\n((?:\|.*?\n)+)",
        text,
    )
    for name, rows in join_tables:
        entries.append(KBEntry(
            title=name.strip(),
            category="join_ref",
            content=f"{name.strip()}\n{rows.strip()}",
            source_file=source,
        ))

    # 5. 提取知识点/注意事项（带 emoji 标记或"知识点"的段落）
    notes = re.findall(
        r"###\s*(.+?)\n\n(.*?)(?=###|\Z)",
        text,
        re.DOTALL,
    )
    for title, body in notes:
        body = body.strip()
        # 跳过太短或已被上面规则捕获的内容
        if len(body) < 50:
            continue
        if "```sql" in body:
            continue  # SQL 块已在上面提取
        # 检查是否包含有价值的知识
        if any(kw in title for kw in ("要点", "区别", "关联", "规则", "公式", "知识点")):
            entries.append(KBEntry(
                title=title.strip(),
                category="note",
                content=body[:1000],
                source_file=source,
            ))

    # 6. 提取"文件学习进度"中的文件描述
    file_progress = re.findall(
        r"\|\s*\d+\s*\|\s*(.+?\.txt)\s*\|\s*✅.*?\|\s*(.+?)\s*\|",
        text,
    )
    for fname, desc in file_progress:
        entries.append(KBEntry(
            title=f"已学SQL文件: {fname}",
            category="note",
            content=f"文件: {fname}, 内容: {desc.strip()}",
            source_file=source,
        ))

    return entries


def _find_heading_for_sql(full_text: str, sql_block: str, index: int) -> str:
    """尝试为 SQL 代码块找到最近的标题。"""
    # 在原文中定位 SQL 块
    sql_preview = sql_block[:80]
    pos = full_text.find(sql_preview)
    if pos < 0:
        return ""

    # 向前搜索最近的 ### 标题
    before = full_text[:pos]
    headings = re.findall(r"###\s*(.+)", before)
    return headings[-1].strip() if headings else ""


def load_all_entries() -> list[KBEntry]:
    """加载所有 .md 文件的知识条目。"""
    all_entries: list[KBEntry] = []
    md_files = sorted(NOTES_DIR.glob("*.md"))
    if not md_files:
        print(f"❌ 未找到 .md 文件: {NOTES_DIR}")
        sys.exit(1)

    for md in md_files:
        print(f"  📖 解析 {md.name} ...")
        entries = parse_md_file(md)
        all_entries.extend(entries)
        print(f"     → 提取 {len(entries)} 条知识")

    # 去重（基于 ID）
    seen = set()
    unique: list[KBEntry] = []
    for e in all_entries:
        if e.id not in seen:
            seen.add(e.id)
            unique.append(e)

    return unique


# ── ChromaDB 操作 ─────────────────────────────────────────────────────────────

def get_collection():
    """获取或创建 ChromaDB 集合。"""
    import chromadb
    client = chromadb.PersistentClient(path=str(DB_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def build_kb():
    """构建知识库。"""
    print("🔨 开始构建 ZLHIS SQL 知识库...\n")

    entries = load_all_entries()
    print(f"\n📊 共提取 {len(entries)} 条知识（去重后）")

    # 加载模型
    print(f"\n🤖 加载嵌入模型: {EMBED_MODEL}")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBED_MODEL)

    # 准备文本（标题 + 内容 拼接用于嵌入）
    texts = [f"{e.title}\n{e.content}" for e in entries]
    print(f"📐 生成嵌入向量...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    # 写入 ChromaDB
    print(f"\n💾 写入 ChromaDB ({DB_DIR}) ...")
    collection = get_collection()

    # 清空旧数据
    existing = collection.count()
    if existing > 0:
        print(f"   清除旧数据 ({existing} 条)")
        # ChromaDB 不支持 clear，删除所有
        all_ids = collection.get()["ids"]
        if all_ids:
            collection.delete(ids=all_ids)

    # 批量插入
    BATCH = 100
    for i in range(0, len(entries), BATCH):
        batch_e = entries[i : i + BATCH]
        batch_emb = embeddings[i : i + BATCH].tolist()
        collection.add(
            ids=[e.id for e in batch_e],
            documents=[f"{e.title}\n{e.content}" for e in batch_e],
            embeddings=batch_emb,
            metadatas=[{
                "title": e.title,
                "category": e.category,
                "source_file": e.source_file,
            } for e in batch_e],
        )

    print(f"\n✅ 知识库构建完成！共 {len(entries)} 条知识")


def ask_question(question: str, top_k: int = 5):
    """智能问答。"""
    print(f"\n🔍 查询: {question}\n")

    collection = get_collection()
    if collection.count() == 0:
        print("❌ 知识库为空，请先运行 --build 构建")
        return

    # 加载模型
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBED_MODEL)

    # 查询嵌入
    q_embedding = model.encode([question], normalize_embeddings=True).tolist()

    # 检索
    results = collection.query(
        query_embeddings=q_embedding,
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    if not results["documents"][0]:
        print("⚠️  未找到相关知识")
        return

    print(f"📋 找到 {len(results['documents'][0])} 条相关知识：\n")
    print("=" * 80)

    for i, (doc, meta, dist) in enumerate(
        zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
    ):
        score = 1 - dist  # cosine distance → similarity
        cat_emoji = {
            "sql_snippet": "💻",
            "field_ref": "📊",
            "table_ref": "📋",
            "join_ref": "🔗",
            "note": "📝",
        }.get(meta["category"], "📄")

        print(f"\n{'─' * 80}")
        print(f"{cat_emoji} [{i+1}] {meta['title']}")
        print(f"   来源: {meta['source_file']} | 类型: {meta['category']} | 相似度: {score:.2%}")
        print(f"{'─' * 80}")
        print(doc)
        print()


def list_entries():
    """列出所有知识条目。"""
    collection = get_collection()
    total = collection.count()

    if total == 0:
        print("❌ 知识库为空，请先运行 --build 构建")
        return

    print(f"\n📚 ZLHIS SQL 知识库 — 共 {total} 条知识\n")

    # 按类别分组显示
    all_data = collection.get(include=["metadatas"])
    by_category: dict[str, list[dict]] = {}
    for meta in all_data["metadatas"]:
        cat = meta.get("category", "unknown")
        by_category.setdefault(cat, []).append(meta)

    cat_labels = {
        "sql_snippet": "💻 SQL 片段",
        "field_ref": "📊 字段值参考",
        "table_ref": "📋 表定义",
        "join_ref": "🔗 关联关系",
        "note": "📝 知识点/笔记",
    }

    for cat in ["sql_snippet", "field_ref", "table_ref", "join_ref", "note"]:
        items = by_category.get(cat, [])
        if not items:
            continue
        label = cat_labels.get(cat, cat)
        print(f"\n{label} ({len(items)} 条)")
        print("─" * 60)
        for item in items:
            src = item.get("source_file", "?")
            title = item.get("title", "?")[:50]
            print(f"  • {title}  [{src}]")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ZLHIS+ SQL 知识库 — 解析学习笔记，嵌入向量，智能问答",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python zlhis_kb.py --build                    构建/重建知识库
  python zlhis_kb.py --ask "住院药品发放怎么查"  智能问答
  python zlhis_kb.py --ask "LIS检验结果关联" --top 10
  python zlhis_kb.py --list                     列出所有知识条目
        """,
    )
    parser.add_argument("--build", action="store_true", help="构建/重建知识库（解析学习笔记 → 嵌入向量 → ChromaDB）")
    parser.add_argument("--ask", type=str, metavar="问题", help="智能问答（匹配相关SQL片段并返回）")
    parser.add_argument("--top", type=int, default=5, help="问答返回条数（默认 5）")
    parser.add_argument("--list", action="store_true", help="列出所有知识条目")

    args = parser.parse_args()

    if not any([args.build, args.ask, args.list]):
        parser.print_help()
        return

    if args.build:
        build_kb()

    if args.ask:
        ask_question(args.ask, top_k=args.top)

    if args.list:
        list_entries()


if __name__ == "__main__":
    main()
