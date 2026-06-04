"""
币安行情查询工具
查询币安交易所加密货币的实时行情数据

使用方法：
    python binance_query.py BTC              # 查询单个币种
    python binance_query.py BTC ETH SOL      # 查询多个币种
    python binance_query.py BTC --format json  # JSON格式输出
    python binance_query.py BTC --proxy http://127.0.0.1:7890  # 使用代理
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from typing import Optional

BINANCE_API_URL = "https://api.binance.com/api/v3/ticker/24hr"


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="币安行情查询工具 - 查询加密货币实时行情",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python binance_query.py BTC
  python binance_query.py BTC ETH SOL
  python binance_query.py BTC --format json
  python binance_query.py BTC --proxy http://127.0.0.1:7890
"""
    )
    parser.add_argument("symbols", nargs="+", help="币种符号，如 BTC ETH SOL")
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="输出格式：text(默认) 或 json"
    )
    parser.add_argument(
        "--proxy",
        default=None,
        help="HTTP代理地址，如 http://127.0.0.1:7890"
    )
    return parser.parse_args()


def fetch_ticker(symbol: str, proxy: Optional[str] = None) -> Optional[dict]:
    """
    获取单个币种的行情数据

    Args:
        symbol: 币种符号，如 BTC
        proxy: 代理地址

    Returns:
        行情数据字典，失败返回 None
    """
    # 币安API使用USDT交易对，自动补全后缀
    sym = symbol.upper()
    ticker_sym = sym if sym.endswith("USDT") else sym + "USDT"

    url = f"{BINANCE_API_URL}?symbol={ticker_sym}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        # 设置代理
        if proxy:
            handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
            opener = urllib.request.build_opener(handler)
            response = opener.open(req, timeout=10)
        else:
            response = urllib.request.urlopen(req, timeout=10)

        data = json.loads(response.read().decode("utf-8"))
        return data

    except urllib.error.HTTPError as e:
        if e.code in (400, 404):
            print(f"错误：未找到币种 '{symbol}'，请确认币种符号是否正确", file=sys.stderr)
        else:
            print(f"错误：HTTP请求失败 ({e.code})", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"错误：网络连接失败 - {e.reason}，请检查网络或使用 --proxy 指定代理", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"错误：API返回数据解析失败", file=sys.stderr)
        return None
    except Exception as e:
        print(f"错误：{str(e)}", file=sys.stderr)
        return None


def format_price(price: str) -> str:
    """格式化价格，保留合理小数位"""
    try:
        p = float(price)
        if p >= 1000:
            return f"${p:,.2f}"
        elif p >= 1:
            return f"${p:,.4f}"
        else:
            return f"${p:,.8f}"
    except ValueError:
        return f"${price}"


def format_volume(volume: str) -> str:
    """格式化成交量"""
    try:
        v = float(volume)
        if v >= 1_000_000:
            return f"{v / 1_000_000:,.2f}M"
        elif v >= 1_000:
            return f"{v / 1_000:,.2f}K"
        else:
            return f"{v:,.2f}"
    except ValueError:
        return volume


def format_change_percent(percent: str) -> str:
    """格式化涨跌幅"""
    try:
        p = float(percent)
        sign = "+" if p >= 0 else ""
        color_indicator = "\033[92m" if p >= 0 else "\033[91m"  # 绿涨红跌
        reset = "\033[0m"
        return f"{color_indicator}{sign}{p:.2f}%{reset}"
    except ValueError:
        return percent


def print_text(ticker: dict):
    """格式化输出单个币种行情（文本格式）"""
    symbol = ticker.get("symbol", "")
    price = format_price(ticker.get("lastPrice", "0"))
    change = ticker.get("priceChangePercent", "0")
    high = format_price(ticker.get("highPrice", "0"))
    low = format_price(ticker.get("lowPrice", "0"))
    volume = format_volume(ticker.get("volume", "0"))

    print(f"\n币种: {symbol}")
    print(f"当前价格: {price}")
    print(f"24h涨跌: {format_change_percent(change)}")
    print(f"24h最高: {high}")
    print(f"24h最低: {low}")
    print(f"24h成交量: {volume} {symbol.replace('USDT', '')}")


def print_json(tickers: list):
    """输出JSON格式"""
    results = []
    for t in tickers:
        if t:
            results.append({
                "symbol": t.get("symbol"),
                "price": float(t.get("lastPrice", 0)),
                "change_24h": float(t.get("priceChangePercent", 0)),
                "high_24h": float(t.get("highPrice", 0)),
                "low_24h": float(t.get("lowPrice", 0)),
                "volume_24h": float(t.get("volume", 0)),
            })

    print(json.dumps(results, indent=2, ensure_ascii=False))


def main():
    args = parse_args()

    tickers = []
    for symbol in args.symbols:
        ticker = fetch_ticker(symbol, args.proxy)
        if ticker:
            tickers.append(ticker)

    if not tickers:
        sys.exit(1)

    if args.format == "json":
        print_json(tickers)
    else:
        for ticker in tickers:
            print_text(ticker)


if __name__ == "__main__":
    main()