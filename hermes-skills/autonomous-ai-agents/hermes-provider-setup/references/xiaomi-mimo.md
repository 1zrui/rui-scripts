# 小米 MiMo 平台配置

## 基本参数

| 参数 | 值 |
|------|-----|
| Provider 名称 | `xiaomi` |
| Base URL | `https://api.xiaomimimo.com/v1` |
| 可用模型 | `xiaomi/mimo-v2.5`、`xiaomi/mimo-m2.7`、`xiaomi/mimo-mixture` |
| 认证方式 | API key |

## 作为备用提供商配置

```bash
hermes config set fallback_providers '["xiaomi"]'
```

当主模型不可用时自动切到小米，主模型恢复后自动切回。

## 双 Key 配置（实测方案）

```text
key1 → providers.xiaomi.api_key（config.yaml）
key2 → XIAOMI_API_KEY env var（.env）
```

### key1：config.yaml

```bash
hermes config set providers.xiaomi.api_key "sk-key1-full-string"
```

> ⚠️ 输出会截断显示（如 `sk-c6a...1w5c`），但实际存完整值。

### key2：.env 环境变量

`~/.hermes/.env` 中：

```env
XIAOMI_API_KEY=***
```

**写入时注意特殊字符**。API key 含 `$` `!` `` ` `` 等 bash 特殊字符时用 base64 编码绕过：

```bash
# 生成 base64
b64=$(python3 -c "import base64; print(base64.b64encode(b'sk-real-key').decode())")
# 写入 .env
python3 -c "
import os, base64
b64 = '$b64'
key = base64.b64decode(b64).decode()
env_path = os.path.expanduser('~/.hermes/.env')
with open(env_path, 'a') as f:
    f.write('XIAOMI_API_KEY=*** + key + chr(10))
"
```

### 验证

```bash
python3 -c "
import yaml
with open(r'D:\Hermes\config.yaml') as f:
    c = yaml.safe_load(f)
k1 = c['providers']['xiaomi']['api_key']
print(f'key1: {len(k1)} chars, end: {k1[-7:]}')
print(f'models: {c[\"providers\"][\"xiaomi\"][\"models\"]}')
print(f'fallback: {c.get(\"fallback_providers\", [])}')
"

grep XIAOMI_API_KEY ~/.hermes/.env | tail -1 | python3 -c "
import sys
l = sys.stdin.read().strip()
k, v = l.split('=', 1)
print(f'key2: {len(v)} chars, end: {v[-7:]}')
"
```

### auth.json 中的 Xiaomi cred pool（可选）

如果要在 credential pool 里追踪 Xiaomi key 状态，可以手动添加条目到 `D:\Hermes\auth.json`：

```python
import json, hashlib, random, string
key2 = "sk-real-key"
fp = "sha256:" + hashlib.sha256(key2.encode()).hexdigest()[:16]
uid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

with open("D:/Hermes/auth.json") as f:
    auth = json.load(f)

cred = {
    "id": uid, "label": "XIAOMI_API_KEY",
    "auth_type": "api_key", "priority": 0,
    "source": "env:XIAOMI_API_KEY",
    "last_status": None, "last_status_at": None,
    "last_error_code": None, "base_url": "https://api.xiaomimimo.com/v1",
    "request_count": 0, "secret_fingerprint": fp, "last_error_reason": None,
    "last_error_message": None, "last_error_reset_at": None
}
auth["credential_pool"].setdefault("xiaomi", []).append(cred)
auth["updated_at"] = "2026-06-15T00:00:00+00:00"

with open("D:/Hermes/auth.json", "w") as f:
    json.dump(auth, f, indent=2, ensure_ascii=False)
```

> 注意：credential pool 的 `source` 存的是环境变量名引用（`env:XIAOMI_API_KEY`），不是原始 key 值。
