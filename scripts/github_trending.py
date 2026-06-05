#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Trending 热门项目日报工具
抓取 GitHub Trending 页面，输出热门项目信息

使用方法:
    python github_trending.py                      # 默认获取当日热门前10
    python github_trending.py --limit 20           # 获取前20个
    python github_trending.py --language python     # 只看 Python 项目
    python github_trending.py --daily               # 今日热门（默认）
    python github_trending.py --weekly              # 本周热门
    python github_trending.py --monthly             # 本月热门
    python github_trending.py --format json         # JSON 格式输出
"""

import argparse
import json
import sys
import re
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timedelta

import requests

GITHUB_SEARCH_API = "https://api.github.com/search/repositories"


def build_url(language=None, date_range="daily"):
    """构建 GitHub API 查询 URL"""
    # 使用 trending 的核心逻辑：按最近创建时间+高 star 排序
    # daily: 最近 7 天内创建的高 star 项目（更宽松）
    # weekly: 最近 30 天内创建的高 star 项目
    # monthly: 最近 90 天内创建的高 star 项目
    now = datetime.now()
    if date_range == "monthly":
        date_from = now - timedelta(days=90)
    elif date_range == "weekly":
        date_from = now - timedelta(days=30)
    else:  # daily
        date_from = now - timedelta(days=7)

    date_str = date_from.strftime("%Y-%m-%d")

    # 构建查询字符串：最近创建 + 高 star
    query_parts = [f"created:>{date_str}", "stars:>50"]
    if language:
        query_parts.append(f"language:{language}")

    # 按星标数排序
    query = " ".join(query_parts)
    return f"{GITHUB_SEARCH_API}?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page=100"


def fetch_trending(limit=10, language=None, date_range="daily", proxy=None):
    """获取 GitHub Trending 项目"""
    url = build_url(language, date_range)

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Trending-Tool/1.0"
    }

    proxies = {}
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy
        }

    req = urllib.request.Request(url, headers=headers)

    try:
        if proxy:
            handler = urllib.request.ProxyHandler(proxies)
            opener = urllib.request.build_opener(handler)
            response = opener.open(req, timeout=30)
        else:
            response = urllib.request.urlopen(req, timeout=30)

        data = json.loads(response.read().decode("utf-8"))
        return data.get("items", [])[:limit]

    except urllib.error.URLError as e:
        print(f"错误: 无法连接 GitHub - {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"错误: 解析响应失败 - {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return None


def format_text(projects):
    """格式化输出为表格"""
    if not projects:
        return "没有找到热门项目"

    # 表头
    header = f"{'项目名':<40} {'语言':<10} {'星标':>8} {'今日新增':>8} {'描述'}"
    separator = "-" * len(header)

    lines = [f"GitHub Trending 热门项目 (共 {len(projects)} 个)", ""]
    lines.append(header)
    lines.append(separator)

    for p in projects:
        name = p.get("full_name", "")[:40]
        lang = p.get("language") or "-"
        stars = p.get("stargazers_count", 0)
        desc = p.get("description") or "-"
        # 截断描述
        if len(desc) > 50:
            desc = desc[:47] + "..."

        lines.append(f"{name:<40} {lang:<10} {stars:>8,} {'':>8} {desc}")

    return "\n".join(lines)


def format_json(projects):
    """格式化输出为 JSON"""
    output = []
    for p in projects:
        output.append({
            "name": p.get("full_name"),
            "description": p.get("description"),
            "language": p.get("language"),
            "stars": p.get("stargazers_count"),
            "forks": p.get("forks_count"),
            "url": p.get("html_url"),
            "created_at": p.get("created_at"),
        })
    return json.dumps(output, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Trending 热门项目日报工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python github_trending.py
  python github_trending.py --limit 20
  python github_trending.py --language python
  python github_trending.py --weekly --limit 5
  python github_trending.py --format json
        """
    )

    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=10,
        help="限制返回数量 (默认: 10)"
    )

    parser.add_argument(
        "--language", "-l",
        type=str,
        help="按语言筛选 (如: python, javascript, go)"
    )

    parser.add_argument(
        "--daily",
        action="store_true",
        help="今日热门"
    )

    parser.add_argument(
        "--weekly",
        action="store_true",
        help="本周热门"
    )

    parser.add_argument(
        "--monthly",
        action="store_true",
        help="本月热门"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="输出格式 (默认: text)"
    )

    parser.add_argument(
        "--proxy",
        type=str,
        help="代理地址 (如: http://127.0.0.1:7890)"
    )

    args = parser.parse_args()

    # 确定时间范围
    if args.monthly:
        date_range = "monthly"
    elif args.weekly:
        date_range = "weekly"
    else:
        date_range = "daily"

    # 获取数据
    projects = fetch_trending(
        limit=args.limit,
        language=args.language,
        date_range=date_range,
        proxy=args.proxy
    )

    if projects is None:
        sys.exit(1)

    # 输出
    if args.format == "json":
        print(format_json(projects))
    else:
        print(format_text(projects))


if __name__ == "__main__":
    main()