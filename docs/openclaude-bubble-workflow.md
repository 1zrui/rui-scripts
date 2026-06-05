# OpenClaw × 泡泡 协作流程

## 核心分工

- **布丁（OpenClaw）**：项目规划、需求分析、创建 Issue
- **泡泡（Claude Code）**：读 Issue、写代码、提交
- **大哥**：通知泡泡看 Issue

## 路径

```
D:\git_scripts\                        # 主仓库（布丁使用）
D:\cc_workspace\rui-scripts\           # Claude Code 仓库（泡泡使用）

# 泡泡的记忆（每次启动自动读取）
C:\Users\Administrator\.claude\projects\D--cc-workspace\memory\

# 泡泡的项目指令（每次启动自动读取）
D:\cc_workspace\rui-scripts\CLAUDE.md
```

## 协作流程

### 布丁只做这三步

1. **写需求文档** → `D:\git_scripts\docs\requirements\xxx.md`
2. **创建 Issue** → GitHub 仓库 `1zrui/rui-scripts`
3. **提交到 GitHub** → `git push`

**布丁到此为止，不再做任何事。**

### 大哥通知泡泡

大哥自己通知泡泡去看 Issue，方式：
- 直接告诉泡泡："看看 Issue #N"
- 或者："有没有新任务"

### 泡泡执行

泡泡收到通知后：
1. 读 Issue 内容
2. 在 `D:\cc_workspace\rui-scripts\` 写代码
3. `git commit` + `git push`
4. 关闭 Issue

## 布丁创建 Issue 的格式

```bash
gh issue create --repo 1zrui/rui-scripts \
  --title "实现XXX功能" \
  --body "具体需求描述..." \
  --label "todo"
```

## 注意事项

1. **布丁不写 current-task.md** — 泡泡直接读 Issue
2. **布丁不启动泡泡** — 大哥通知
3. **布丁不验收** — 大哥自己看
4. **布丁不帮泡泡同步代码** — 泡泡自己 commit + push

## 日常流程

```
大哥: "做一个XXX功能"
布丁: 写需求文档 → 创建 Issue → push 到 GitHub → 告诉大哥"搞定了"
大哥: "泡泡，看看 Issue #N"
泡泡: 读 Issue → 写代码 → commit → push → 关闭 Issue
大哥: 验收结果
```
