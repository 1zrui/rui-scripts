# GitHub Trending 热门项目日报工具

## 需求概述
每天自动抓取 GitHub Trending 热门项目，生成中文日报，推送到指定渠道。

## 功能要求

### 核心功能
1. **抓取 GitHub Trending 页面**
   - 获取当日热门项目（Top 15-20）
   - 支持按语言筛选（可选）
   - 提取：项目名、描述、Star 数、今日新增 Star、主要语言

2. **AI 摘要生成**
   - 用 AI 将英文描述翻译成中文
   - 生成项目简介（1-2句话）
   - 标注项目类型（AI Agent、开发工具、CLI 工具等）

3. **日报格式**
   - Markdown 格式
   - 按类别分组（AI/Agent、开发工具、实用工具等）
   - 包含项目链接、Star 数、简介

4. **输出**
   - 保存到文件：`D:\布丁工作区\github-trending\daily\YYYY-MM-DD.md`
   - 可选推送到 Telegram/微信

### 技术要求
- Python 脚本
- 使用 GitHub Trending 页面抓取（或 API）
- AI 摘要使用 OpenRouter API（或本地模型）
- 定时执行（cron 或 Windows 任务计划）

### 输入参数
- `--date YYYY-MM-DD`：指定日期（默认今天）
- `--lang python`：按语言筛选（可选）
- `--output md|json`：输出格式（默认 md）
- `--push telegram|wechat`：推送渠道（可选）

### 输出示例
```markdown
# GitHub Trending 日报 - 2026-06-05

## AI / Agent
1. **chopratejas/headroom** ⭐ 13,847 (+3,142 today)
   > AI Agent 上下文压缩层，减少 60-95% token 消耗

2. **NousResearch/hermes-agent** ⭐ 8,421
   > 自我进化的 AI Agent 框架

## 开发工具
3. **CopilotKit/CopilotKit** ⭐ 32,328 (+350 today)
   > 前端 Agent & 生成式 UI 框架
...
```

## 验收标准
1. 能成功抓取 GitHub Trending 页面
2. 生成的日报格式正确、内容准确
3. AI 摘要质量可读（不是机翻）
4. 支持保存到文件
5. 支持定时执行

## 参考
- GitHub Trending 页面：https://github.com/trendshift.io
- Issue #3
