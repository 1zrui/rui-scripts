---
name: web-ai-imagegen
description: 通过 Chrome DevTools MCP 控制网页版 AI 图像生成服务（Gemini、ChatGPT、豆包等），生成图片 → 下载高清原图 → 通过 NapCat HTTP API 发送给用户。平台无关的通用工作流，每个平台的具体差异通过 reference 文件覆盖。
version: 1.4.0
author: 豆子 (Hermes Agent)
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: image-gen, chrome-devtools, napcat, creative, gemini, chatgpt, doubao
---

# Web AI 生图 → 下载原图 → NapCat 发送

通过 **Chrome DevTools MCP** 操控网页版 AI 图像服务（Gemini、ChatGPT 等），生成图片并下载**高清原图**（不是浏览器截图），再通过 **NapCat HTTP API** 发给用户。零官方 API Key 依赖，复用浏览器登录态。

## 前置条件

1. Chrome 远程调试端口 9222 已开（大哥环境默认常开）
2. 目标 AI 服务页面已登录好（Gemini / ChatGPT 任意对话页）
3. NapCat HTTP API 在 18801 端口（`http://127.0.0.1:18801`）
4. 用户 QQ（大哥 = 2415317075，**不是 bot QQ**）

## 通用工作流（5 步）

### Step 0: 选页面

```python
list_pages()  # 看看有哪些 tab
select_page(pageId=N)  # 切到目标页面
```

### Step 1: 判断要不要新建对话

- 当前对话有污染上下文（分析视频、吃播、旧讨论等）→ 点"New Chat"按钮
- 当前对话是空页面或无关紧要的历史 → **直接在当前对话下发提示词**，无需开新对话

### Step 2: 输入提示词

```python
click(uid="<输入框的uid>")              # 聚焦输入
type_text(text="<提示词>", submit_key="Enter")  # 输入并回车
```

提示词语言：**中英文都行**，重点是把人物/场景/光线/画质写细致，加上摄影参数和"8K超高清超写实"等画质词。

### Step 3: 等图生成（关键陷阱）

#### 🚨 `wait_for` 会匹配旧对话的残留元素

`wait_for` 扫描整个页面的 DOM，包括**前一次对话**的按钮元素（"Good response"、"Copy"、", AI generated"等）。
如果旧对话的按钮还在 DOM 里，`wait_for` 会**立即返回**，你以为图好了，实际上还在"Creating your image"。

**具体表现**：每次生图 `wait_for` 都秒回，但截图发现还在生成中。这是因为 Gemini 聊天模式下，历史消息的按钮不会被销毁。

**正确做法（两步确认）：**

```python
# 3a: 先 wait_for 等一段时间
wait_for(text=["Download full size", "Good response"], timeout=120000)

# 3b: 必须用 screenshot + vision_analyze 二次确认！
screenshot = take_screenshot()
vision_analyze(image_url=screenshot, question="图片生成出来了吗？页面上显示图片了吗？")
```

#### ⏱ 长时间等待时保持沟通

Gemini/ChatGPT 出图可能 **30s~2min+**。如果只 silent wait 不吭声，用户会问"死了吗"。

**原则**：wait_for 后截图发现还在生成 → 每 30 秒截图确认一次，同时给用户发一句状态（如"还在画，再等一下～"）。
1. 提交提示词后**先说一句**（如"发出去了，等生成中～"），让用户知道已提交
2. `wait_for` 后截图发现还在生成 → 每 30 秒截图确认一次，同时招呼一声（如"还在画，再等一下～"）
3. 图出来后说一句（如"出来了！点下载原图"），然后继续走流程
4. 全程避免 30 秒以上无任何消息的静默期

### Step 4: 下载原图

**Gemini/ChatGPT 方式**：snapshot 里找 description="Download full size image"/"Download full size"/"Save" 的 button，click 它。

**豆包方式**（完全不同，注意区分）：

**先批量下载（推荐）**：
1. 在图片下方点「...」（更多）→「下载」
2. 批量下载界面默认全选，点底部蓝色「下载」按钮
3. 所有图片同时下载为独立文件

**备选：单张预览灯箱下载**：
1. 先点击图片（evaluate_script 用 `img.click()` 或 snapshot uid click）
2. 打开预览灯箱模式
3. 灯箱右上角找到蓝色下载按钮，点击

文件下载到 `$USERPROFILE\\Downloads\\`，命名格式为 `{对话标题}.png`

文件下载到 `$USERPROFILE\\Downloads\\`，常见命名格式：
- Gemini：`Gemini_Generated_Image_{hash}.png`
- ChatGPT：`ChatGPT Image {日期}.png`
- 豆包：`{对话标题}.png`（如`拥挤地铁惊艳女子.png`）

```bash
ls -lat "$USERPROFILE/Downloads/" | head -5
# 找最新那个生成的文件
```

#### 🚫 不要从 blob 导出

这些姿势都是**死路**，不要走：
- ❌ `evaluate_script` 用 `fetch(blob_url)` → `Failed to fetch`，blob 受同源保护
- ❌ `evaluate_script` 用 canvas `toDataURL` → 大文件卡死
- ❌ `take_screenshot` 当原图发给用户 → 带浏览器 UI 的缩略图，不是原图

### Step 5: 用 NapCat HTTP API 发送

#### 🚫 不要用 curl

MSYS bash 下 `curl -X POST` 时 Windows 反斜杠 `\` 会被 bash 吃掉（`D:\path` 变成 `D:path`），报"识别URL失败"。

#### ✅ 正确姿势：Python requests

```python
import requests

src = r"C:\Users\Administrator\Downloads\Gemini_Generated_Image_xxxxx.png"
file_uri = "file:///" + src.replace("\\", "/")

payload = {
    "user_id": 2415317075,  # ⚠️ 用户 QQ，不是 bot QQ！
    "message": [{
        "type": "image",
        "data": {"file": file_uri}
    }]
}

r = requests.post("http://127.0.0.1:18801/send_private_msg", json=payload, timeout=30)
print(r.json())
```

## 验证清单

发到 QQ 后确认：
- ✅ 收到的是**清晰无浏览器 UI**的图片（不是截图）
- ✅ Gemini 文件大小 **~1.5~2.5 MB**，GPT **~1.5~1.8 MB**，豆包 **~3.8~4.6 MB**
- ✅ 分辨率通常是：Gemini 1024×559、GPT 1024×1024、豆包 **1773×2364**（原图更大）

## 提示词模板

实战验证过的模板见 `references/prompt-templates.md`，包含：
- 韩系清新女友
- 夏日超短裤少女
- 国漫仙气少女
- 国风仙侠角色三视图
- 通勤地铁惊艳女子（纪实街拍风）

模板要点：
- 人物：长相特征 + 身材 + 表情 + 发型/发色 + 服装（颜色/材质/纹路）
- 场景：什么地方 + 什么光线 + 氛围
- 风格：摄影参数 + 画质词（8K超高清超写实）
- **中英文都可以**，描述越细效果越好

> 进阶三视图和角色设计提示词 → 参见 `ai-comic-drama` skill（AI漫剧全流程，含五要素公式、一致性控制等）

## 跨平台生图：用户可能在 A/B 对比

当用户说"用 Gemini 试一下"时，**用户很可能同时在对比 GPT-Image2 的结果**。这是常见场景——用户手上已经有另一个平台的图，让你在另一個平台跑同样的提示词，看哪个效果好。

### 质量预期参考

各平台图像生成质量有显著差异，提前知道可以帮助管理用户预期：

| 平台 | 人像质量 | 场景把控 | 面部精致度 | 光影细节 | 典型分辨率 |
|------|---------|---------|-----------|---------|-----------|
| **GPT-Image2 (DALL·E)** | ⭐⭐⭐⭐⭐ 极高 | 极好 | 极高，五官精致分明 | 丰富自然的光影层次 | 1024×1024 |
| **豆包 (Seedream 4.5)** | ⭐⭐⭐⭐ 高 | 好 | 高，三张不同角度 | 较好 | **1773×2364** |
| **Gemini Flash** | ⭐⭐⭐ 中等 | 一般 | 中等，偏柔和/模糊 | 平淡，缺乏层次 | 1024×559 |

### 重要提示

- **不要盲目选择 Gemini**：如果用户没有明确指定平台，优先推荐 GPT-Image2（质量明显更高）
- **用户说"试试"往往在 A/B 对比**：当用户让你用 Gemini 跑一段提示词时，大概率他已经有 GPT 的图在手，正在比较效果
- **Gemini 适合的场景**：快速出图预览提示词效果、非写实风格（插画/动画类）、不追求极致细节的场合
- **GPT-Image2 适合的场景**：高质量写实人像、精致场景、任何需要发给用户展示的成品图
- **对比结果如实反馈**：如果用户问"你觉得哪个好"，直接说 GPT-Image2 更好

## 平台参考

各平台的具体差异（DOM 结构、按钮文本、下载格式等）在独立的 reference 文件中：

| 平台 | 参考文件 | 状态 |
|------|---------|------|
| Gemini | `references/gemini-platform.md` | ✅ 已验证 |
| ChatGPT | `references/chatgpt-platform.md` | ✅ 已实测 |
| 豆包 | `references/doubao-platform.md` | ✅ 已实测 |
| 平台对比 | `references/platform-comparison.md` | ✅ 已验证 |

## 相关路径

- Chrome DevTools MCP：默认端口 9222，工具前缀 `mcp_chrome_devtools_`
- NapCat HTTP API：`http://127.0.0.1:18801`
- 下载目录：`C:\\Users\\Administrator\\Downloads`
- 图片缓存：`D:\\Hermes\\image_cache`

## 关联 skill

| Skill | 用途 |
|-------|------|
| `hermes-provider-setup` | Hermes 模型提供商配置、API Key credential pool、备用 provider |
| `ai-comic-drama` | 进阶三视图、角色定妆、AI漫剧提示词全流程 |
