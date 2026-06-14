---
name: doubao-batch-download
description: 豆包（Doubao）Seedream 生图 → 批量下载原图 → NapCat 发 QQ 的完整工作流
version: 1.0.0
author: 豆子 (Hermes Agent)
tags: [doubao, image-generation, batch-download, seedream, napcat]
---

# 豆包批量下载原图工作流

通过 Chrome DevTools MCP 操控豆包（Doubao）网页版 → 用 Seedream 模型生成图片 → 用"更多"菜单中的"下载"打开批量下载界面 → 下载所有原图 → NapCat 发 QQ。

## 前置条件

1. Chrome 远程调试端口 9222 已开
2. 豆包网页已登录（https://www.doubao.com/chat）
3. NapCat HTTP API 在 18801 端口
4. 用户 QQ（大哥 = 2415317075，**不是 bot QQ**）

## 工作流

### Step 1: 定位或打开豆包页面

```python
list_pages()  # 查看所有页面
select_page(pageId=N)  # 切到豆包页面
```

如果豆包页面不存在，用 `mcp_chrome_devtools_new_page(url="https://www.doubao.com/chat")` 开新页。

### Step 2: 切到图像生成模式

点击工具栏的「图像生成」按钮进入生图模式。

### Step 3: 输入提示词并提交

```python
type_text(text="提示词...", submit_key="Enter")
```

提示词需要描述人物（长相/发型/服装/姿势）、场景、氛围、光线、画质等。

### Step 4: 等待图片生成完成

```python
wait_for(text=["image", "正在为您生成图片..."], timeout=180000)
```

注意：wait_for 可能会因为旧元素提前返回。需要继续等待真正的图片 element 出现。

### Step 5: 批量下载（核心流程）

```
1. 点「更多」按钮（图片下方 expandable haspopup="menu" 的 button）
2. 在弹出的菜单中点「下载」
3. 等待批量下载界面弹出（有「批量下载」标题、checkbox、已选择 N 项内容）
4. 确认所有图片已勾选
5. 点蓝色「下载」按钮（uid 为批量下载界面的下载 button）
```

### Step 6: 检查下载文件

```bash
ls -lat /c/Users/Administrator/Downloads/ | head -10
```

文件命名规则：豆包会自动以对话标题命名，多张时加 `(1)`, `(2)`, `(3)` 后缀。

### Step 7: 发送到 QQ

```python
import requests
src = r"C:\Users\Administrator\Downloads\文件名.png"
file_uri = "file:///" + src.replace("\\", "/")
payload = {"user_id": 2415317075, "message": [{"type": "image", "data": {"file": file_uri}}]}
r = requests.post("http://127.0.0.1:18801/send_private_msg", json=payload, timeout=30)
```

## 关键陷阱

### 🚨 「更多」菜单的「下载」只是打开批量下载界面

第一次点「更多」→「下载」只会弹出批量下载选择界面（带 checkbox），**不是直接下载**。还必须再点一次蓝色「下载」按钮才开始真正下载。

### 🚨 wait_for 可能被旧元素干扰

生图过程中不要只依赖 wait_for 的返回，要用 screenshot 二次确认图片是否真的出来了。

### 🚨 文件命名可能带序号

如果 Downloads 里已有同名文件，Chrome 会自动加 `(1)`, `(2)` 等后缀。发送时用最新的几个文件。

### 🚨 下载完成后批量下载界面不会自动关闭

需要手动点「取消」关闭，或者不管它直接发送给用户即可。

## 验证清单

- [ ] 图片已生成（通过 screenshot + vision_analyze 确认）
- [ ] 批量下载界面中所有图片已勾选
- [ ] 点击批量下载界面的「下载」后，Downloads 目录出现新文件
- [ ] 文件大小 3~5 MB（正常原图大小）
- [ ] 图片通过 NapCat 成功发送到 QQ

## 相关路径

- 下载目录：`C:\\Users\\Administrator\\Downloads`
- NapCat API：`http://127.0.0.1:18801`
- 用户 QQ：2415317075
