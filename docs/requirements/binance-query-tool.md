# 币安行情查询工具 - 需求文档

## 项目概述
一个命令行工具，用于查询币安加密货币的实时行情信息。

## 功能需求

### 1. 查询单个币种
- 输入币种符号（如 BTC、ETH）
- 输出：当前价格、24h涨跌幅、24h最高价、24h最低价、24h成交量

### 2. 查询多个币种
- 支持同时查询多个币种（如 BTC ETH SOL）
- 表格形式输出，便于对比

### 3. 输出格式
```
币种: BTCUSDT
当前价格: $65,432.10
24h涨跌: +2.35%
24h最高: $66,000.00
24h最低: $64,500.00
24h成交量: 12,345.67 BTC
```

## 技术要求

### 输入
```bash
# 查询单个币种
python binance_query.py BTC

# 查询多个币种
python binance_query.py BTC ETH SOL

# 指定输出格式
python binance_query.py BTC --format json
```

### API
- 使用币安公开API：`https://api.binance.com/api/v3/ticker/24hr`
- 不需要API Key
- 需要代理支持（可选）

### 输出格式
- 默认：表格形式
- 可选：JSON格式

## 文件位置
- 输出脚本：`scripts/binance_query.py`

## 验收标准
1. 能正确查询币安API
2. 支持单个和多个币种查询
3. 输出格式清晰易读
4. 有错误处理（网络错误、无效币种等）
5. 代码有注释，易于维护
