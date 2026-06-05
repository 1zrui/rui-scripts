---
name: current-task
description: 当前需要泡泡执行的任务
metadata: 
  node_type: memory
  type: project
---

## 当前任务

**Issue**: #3
**链接**: https://github.com/1zrui/rui-scripts/issues/3
**任务**: 实现 GitHub Trending 热门项目日报工具
**输出脚本**: `scripts/github_trending.py`

**要求**:
1. 抓取 GitHub Trending 页面
2. 支持按语言筛选：`--language python`
3. 支持按时间范围：`--daily` / `--weekly` / `--monthly`
4. 输出：项目名、描述、星标数、今日新增、语言
5. 支持 `--format json` 输出
6. 支持 `--limit N` 限制数量（默认 10）
7. 错误处理（网络错误等）
8. 代码有中文注释

**注意**: 测试阶段，不要推送到远程仓库，只本地提交！

**状态**: 待执行
