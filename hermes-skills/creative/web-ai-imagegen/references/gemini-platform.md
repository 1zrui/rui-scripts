# Gemini Web 平台参考

## 页面选择
- URL: `https://gemini.google.com/app` 或 `https://gemini.google.com/app/<unique_id>`
- `list_pages()` 中找标题含 "Google Gemini" 的页面

## 新建对话
- 按钮文本: "New Chat", 或 description="New chat"
- uid 每次不同，先 snapshot 找 `button "New Chat"` 或 `generic description="New chat"` 下的 button

## 输入框
- textbox: `"Enter a prompt for Gemini"` / `"与 Gemini 聊天"`
- 点一下聚焦，然后用 `type_text(text="<prompt>", submit_key="Enter")` 输入并提交

## 等待生成
- 生成中显示: `StaticText "Creating your image"` / `"正在生成图片"`
- 生成完成标志: 出现 `button ", AI generated"`、`"Download full size image"`、`"Good response"`
- **注意**: 如果没用 New Chat，旧对话的按钮（", AI generated"等）会留存在 DOM 中，导致 `wait_for` 提前返回
- **检查步骤见主 SKILL.md Step 3**：wait_for 后必须用 screenshot + vision_analyze 二次确认

## 下载按钮
- 按钮文本: `"Download full size image"`
- description=`"Download full size"`
- point: snapshot 中找 uid，click 即可

## 下载文件
- 下载到: `C:\Users\Administrator\Downloads\`
- 命名格式: `Gemini_Generated_Image_<hash>.png`（hash 含字母数字）
- 典型大小: ~1.5~2.4 MB
- 典型分辨率: 1024×559

## 已知限制
- Gemini Flash 模式下出图快（~30s），Flash Extended 稍慢（~60s）
- Gemini Pro 被限时可能降级模型（见页面提示 "Pro is in high demand, another model was used"）
- 不支持批量生图（一次只能一张）
