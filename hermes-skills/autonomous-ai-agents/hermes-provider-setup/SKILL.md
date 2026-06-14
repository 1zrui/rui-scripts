---
name: hermes-provider-setup
description: 在 Hermes Agent 中配置自定义模型提供商/备用提供商，管理 API 密钥和 credential pool，以及常见配置陷阱。补充 bundled `hermes-agent` skill 中未覆盖的特定提供商细节。
version: 1.0.0
author: 豆子 (Hermes Agent)
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: hermes, config, provider, credential, api-key
---

# Hermes 提供商配置 & 凭据池

在 `hermes-agent`（bundled skill）的通用配置流程之外，记录本环境中实测过的特定提供商配置、credential pool 设置，以及配置命令的陷阱。

## 核心约束

- 不要直接用 `patch`/`write_file` 修改 `config.yaml` — 用 `hermes config set`
- 但也有例外：嵌套配置（如 `auxiliary.vision.extra_body`）用 Python yaml 编辑
- 任何 provider 配置变更后，**重启网关**生效（`hermes gateway restart`）

## 文件位置（重要）

```
config.yaml: D:\Hermes\config.yaml（$HERMES_HOME 目录）
.env:        C:\Users\Administrator\.hermes\.env（标准路径，不受 config.yaml 位置影响）
auth.json:   D:\Hermes\auth.json（$HERMES_HOME 下，不在 ~/.hermes/）
```

`.env` 在 C 盘是**完全正常且生效的**。Hermes 的标准 `~/.hermes/.env` 路径就在 C 盘用户目录下，不管 config.yaml 放 D 盘还是其他地方，`.env` 路径不变。`XIAOMI_API_KEY` 等环境变量从这里自动读取。

## 🚨 大坑：`hermes auth add` 是交互式命令

`hermes auth add xiaomi` 会启动交互式提示要求输入 API key，**不能通过 piped input 或 echo 管道**传入：

```bash
# ❌ 都会超时
echo "sk-xxx" | hermes auth add xiaomi
python3 -c "..." | hermes auth add xiaomi
```

**正确做法**：手动直接编辑 `auth.json`（Python 方式），或在 PTY 模式下运行 `hermes auth add`。

`hermes config set providers.xiaomi.api_key "sk-xxx"` 在终端输出中会截断 API key 显示：

```text
输出：api_key: sk-c6a...1w5c
```

这**不**意味着存储的是截断版！实际存储的是完整 key。但反过来说：你**没法通过终端输出来验证** key 是否存对了。

**正确验证姿势：用 Python yaml 直接读文件**

```python
import yaml
with open(r"D:\Hermes\config.yaml", encoding='utf-8') as f:
    config = yaml.safe_load(f)
k = config['providers']['xiaomi']['api_key']
print(f"len={len(k)}, last_7={k[-7:]}")
```

同理，`auth.json` 里的 credential pool key 也要直接 `cat` 或 `json.load` 验证，不能信 `hermes auth list` 的显示。

**惨痛教训**：本会话中因为这个坑，两个 key 各写错过两次截断版 😅

## 🚨 大坑：API Key 含特殊字符导致写入失败

很多 API key 包含 `$`、`!`、`` ` ``、`&` 等 bash/Python 特殊字符，直接 echo 写入 .env 会翻车：

```bash
# ❌ $ 被当作变量
echo "XIAOMI_API_KEY=*** > ~/.hermes/.env
# ❌ ! 被解释为历史命令
sed -i "s/KEY=/KEY=sk-xxx/" .env
```

### 安全方案：Base64 编码绕开 shell 解析

```bash
# 1. 生成 base64（纯字母数字，安全可复制）
b64=$(python3 -c "import base64; print(base64.b64encode(b'sk-xxx').decode())")
echo $b64

# 2. 用 Python 写入 .env
python3 -c "
import os, base64
b64 = '$b64'
key = base64.b64decode(b64).decode()
env_path = os.path.expanduser('~/.hermes/.env')
with open(env_path, 'a') as f:
    f.write('XIAOMI_API_KEY=*** + key + chr(10))
"
```

> `chr(10)` 代替 `\\n` 防止字符串转义破坏。也可用 `os.linesep`。

### 如果 .env 已存在该变量（sed 替换）

不要用 `sed` 替换已有行（key 含特殊字符会爆炸），正确做法是 Python 读入全部行→过滤→追加：

```python
import os
env_path = os.path.expanduser('~/.hermes/.env')
key2 = "sk-real-key"

with open(env_path, 'r') as f:
    lines = f.readlines()

# 删掉旧 XIAOMI 行
lines = [l for l in lines if not l.startswith('XIAOMI')]

# 追加新行
lines.append('XIAOMI_API_KEY=*** + key2 + chr(10))

with open(env_path, 'w') as f:
    f.writelines(lines)
```

## Credential Pool 轮换机制（双 Key 自动切换）

### auth.json 真实格式

`auth.json` 位于 **`$HERMES_HOME/auth.json`**（本机 = `D:\Hermes\auth.json`），**不是** `~/.hermes/auth.json`。

```json
{
  "version": 1,
  "providers": {},
  "credential_pool": {
    "nvidia": [
      {
        "id": "19c27c",
        "label": "NVIDIA_API_KEY",
        "auth_type": "api_key",
        "priority": 0,
        "source": "env:NVIDIA_API_KEY",
        "last_status": "exhausted",
        "last_status_at": 1781451172,
        "base_url": "https://integrate.api.nvidia.com/v1",
        "request_count": 0,
        "secret_fingerprint": "sha256:..."
      }
    ]
  },
  "updated_at": "ISO_TIMESTAMP"
}
```

关键发现：
- `source` 存的是**引用**（如 `env:NVIDIA_API_KEY`），不是原始 key 值
- 实际 key 值来自环境变量或 `.env` 文件
- `id` = 随机 6 位 hex、`secret_fingerprint` = `sha256:` + key hash 前 16 位
- `priority` 决定尝试顺序（0 优先）

### 轮换流程（从主 key 到备用 key）

```
请求发起
  → 先用 providers.xiaomi.api_key（config.yaml，主 key）
  → 如果收到 429（额度用尽），系统标记该 key 为 exhausted
  → 自动切换到 credential pool 中 priority 最高的活跃条目
  → 从 source 指定的位置（env:XIAOMI_API_KEY）读取备用 key
  → 用备用 key 重试请求
  → 所有 key 都 exhaust → 返回错误
```

这个切换对用户透明，不需要手动干预。

### 双 Key 推荐模式

```text
config.yaml: providers.xiaomi.api_key = sk-key1（主 key，完整值）
.env:         XIAOMI_API_KEY=*** key，完整值）
auth.json:    credential_pool.xiaomi[0] = {source: "env:XIAOMI_API_KEY", ...}
```

主 key 从 config 读取，备用 key 走 env var，credential pool 仅做路由追踪。

### 验证双 Key

```bash
# key1（config.yaml）
python3 -c "
import yaml, json
with open('D:/Hermes/config.yaml') as f:
    c = yaml.safe_load(f)
k1 = c['providers']['xiaomi']['api_key']
print(f'key1: {len(k1)} chars, end: {k1[-7:]}')
"

# key2（.env）
grep XIAOMI_API_KEY ~/.hermes/.env | tail -1 | python3 -c "
import sys
l = sys.stdin.read().strip()
k, v = l.split('=', 1)
print(f'key2: {len(v)} chars, end: {v[-7:]}')
"
```

## 提供商配置参考

各平台的具体配置参数（base_url、可用模型、API key 获取方式等）见 `references/`：

| 提供商 | 参考文件 | 状态 |
|--------|---------|------|
| 小米 MiMo | `references/xiaomi-mimo.md` | ✅ 已实测 |

## 相关路径

- config.yaml: `D:\Hermes\config.yaml`（`$HERMES_HOME` 目录下）
- auth.json: `D:\Hermes\auth.json`（**不是** `~/.hermes/auth.json`）
- .env: `C:\Users\Administrator\.hermes\.env`
- Heremes Home: `D:\Hermes`（`echo $HERMES_HOME`）
