"""
ZLHIS 数据字典查询工具
用法:
  python dict_query.py --table "门诊费用记录"    # 按表名查询
  python dict_query.py --field "病人id"          # 按字段名查询
  python dict_query.py --table "%费用%"           # 模糊搜索
  python dict_query.py --table "门诊" --field "id"  # 组合查询
"""
import argparse
import sys
import os

try:
    import openpyxl
except ImportError:
    print("需要安装 openpyxl: pip install openpyxl")
    sys.exit(1)

# 默认数据字典路径
DEFAULT_DICT_PATH = r"D:\布丁工作区\字典\ZLHIS+_数据字典.xlsx"


def load_dict(path: str) -> list[dict]:
    """加载数据字典，返回字典列表"""
    if not os.path.exists(path):
        print(f"文件不存在: {path}")
        sys.exit(1)

    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.active
    rows = []
    header = None

    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            header = [str(c).strip() if c else "" for c in row]
            continue
        record = {}
        for j, val in enumerate(row):
            key = header[j] if j < len(header) else f"col{j}"
            record[key] = str(val).strip() if val is not None else ""
        rows.append(record)

    wb.close()
    return rows


def match_pattern(text: str, pattern: str) -> bool:
    """支持 SQL LIKE 风格的 % 通配符匹配"""
    if not pattern:
        return True
    # 如果没有 %，默认做包含匹配
    if "%" not in pattern:
        return pattern.lower() in text.lower()
    # 转换 % 为正则
    import re
    regex = pattern.replace("%", ".*")
    return bool(re.search(regex, text, re.IGNORECASE))


def query(data: list[dict], table: str = None, field: str = None) -> list[dict]:
    """查询数据字典"""
    results = []
    for row in data:
        t = match_pattern(row.get("表名", ""), table or "")
        f = match_pattern(row.get("字段名", ""), field or "")
        if t and f:
            results.append(row)
    return results


def print_table(results: list[dict]):
    """表格形式输出"""
    if not results:
        print("未找到匹配结果")
        return

    # 按表名分组
    groups = {}
    for row in results:
        tname = row.get("表名", "")
        groups.setdefault(tname, []).append(row)

    for tname, rows in groups.items():
        print(f"\n表名: {tname}  (共 {len(rows)} 个字段)")
        print("-" * 70)
        print(f"{'字段名':<20} {'字段类型':<12} {'字段大小':<10} {'字段说明'}")
        print("-" * 70)
        for r in rows:
            fname = r.get("字段名", "")
            ftype = r.get("字段类型", "")
            fsize = r.get("字段大小", "")
            fdesc = r.get("字段说明", "")
            print(f"{fname:<20} {ftype:<12} {fsize:<10} {fdesc}")
        print()


def main():
    parser = argparse.ArgumentParser(description="ZLHIS 数据字典查询工具")
    parser.add_argument("--table", "-t", help="表名（支持 % 通配符）")
    parser.add_argument("--field", "-f", help="字段名（支持 % 通配符）")
    parser.add_argument("--path", "-p", default=DEFAULT_DICT_PATH, help="数据字典文件路径")
    args = parser.parse_args()

    if not args.table and not args.field:
        parser.print_help()
        sys.exit(1)

    data = load_dict(args.path)
    results = query(data, table=args.table, field=args.field)
    print_table(results)
    print(f"共 {len(results)} 条结果")


if __name__ == "__main__":
    main()
