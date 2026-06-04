# OpenClaw × 泡泡 协作流程

## 核心原理

泡泡（Claude Code）每次启动时会**自动读取**以下文件：
- `CLAUDE.md` — 项目说明和行为准则
- `memory/MEMORY.md` — 记忆索引
- `memory/` 目录下所有记忆文件

所以 OpenClaw 只需要**把信息写到这些文件里**，泡泡下次启动就能自动接收到所有上下文。

## 路径

```
D:\cc_workspace\rui-scripts\          # 仓库根目录
D:\cc_workspace\rui-scripts\.git\     # Git 仓库

# 泡泡的记忆（每次启动自动读取）
C:\Users\Administrator\.claude\projects\D--cc-workspace\memory\MEMORY.md
C:\Users\Administrator\.claude\projects\D--cc-workspace\memory\*.md

# 泡泡的项目指令（每次启动自动读取）
D:\cc_workspace\CLAUDE.md
```

## 协作流程

### 第一步：OpenClaw 创建任务

1. 在 GitHub 仓库 `1zrui/rui-scripts` 创建 Issue，标题和描述写清楚需求
2. 给 Issue 打标签 `todo`（泡泡认这个标签）

```bash
# OpenClaw 用这个命令创建 Issue
gh issue create --repo 1zrui/rui-scripts \
  --title "实现XXX功能" \
  --body "具体需求描述..." \
  --label "todo"
```

### 第二步：OpenClaw 写入当前任务文件

在泡泡的记忆目录写一个任务文件，告诉泡泡该干什么：

```bash
# 文件路径
# C:\Users\Administrator\.claude\projects\D--cc-workspace\memory\current-task.md

# 内容格式：
```

```markdown
---
name: current-task
description: 当前需要泡泡执行的任务，由 OpenClaw 写入
metadata:
  type: project
---

## 当前任务

**Issue**: #3（附上 Issue 链接）
**任务**: 实现 XXX 功能
**要求**:
- 第一点要求
- 第二点要求
**参考**: 某某文件可以参考
**状态**: 待执行
```

### 第三步：OpenClaw 启动泡泡

```bash
# 方式一：直接启动泡泡执行任务
claude "读 memory/current-task.md，按照要求完成 rui-scripts 仓库的开发任务"

# 方式二：更具体地指定
claude "rui-scripts 仓库 Issue #3 要实现 XXX，去读 Issue 内容然后实现它"

# 方式三：让泡泡自主查任务
claude "检查 rui-scripts 仓库有没有新的 todo Issue，有的话逐个实现"
```

### 第四步：泡泡执行

泡泡启动后会：
1. 读取 CLAUDE.md（知道自己是泡泡）
2. 读取 memory/ 目录（看到 current-task.md）
3. 读取 Issue 内容（`gh issue view #3 --repo 1zrui/rui-scripts`）
4. 在 `D:\cc_workspace\rui-scripts\` 目录下写代码
5. 提交并推送（`git commit` + `git push`）
6. 如果任务完成，可以关闭 Issue（`gh issue close #3 --repo 1zrui/rui-scripts`）

### 第五步：更新任务状态

泡泡完成后，更新任务文件状态：

```markdown
## 当前任务

**Issue**: #3
**状态**: ✅ 已完成
**提交**: bb18dd5
```

## 日常协作模式

### 模式一：OpenClaw 派任务，泡泡干活

```
OpenClaw: 创建 Issue → 写 current-task.md → 启动泡泡
泡泡:     读任务 → 写代码 → 提交 → 更新状态
大哥:     验收结果
```

### 模式二：大哥直接派任务

```
大哥: "泡泡，帮我实现 Issue #3"
泡泡: 读 Issue → 写代码 → 提交
```

### 模式三：泡泡自主找活

```
大哥: "看看有没有新任务"
泡泡: gh issue list --label todo → 逐个实现
```

## 注意事项

1. **记忆目录路径固定**：`C:\Users\Administrator\.claude\projects\D--cc-workspace\memory\`，不要改
2. **CLAUDE.md 路径固定**：`D:\cc_workspace\CLAUDE.md`，不要改
3. **仓库路径固定**：`D:\cc_workspace\rui-scripts\`，不要改
4. **泡泡不会主动运行**：必须有人或 OpenClaw 执行 `claude` 命令才会启动
5. **会话是独立的**：但记忆是持久的，每次启动都会读，所以通过文件传递信息没有问题
6. **提交代码不要用 --force**：泡泡有安全限制，不会执行破坏性操作

## 文件就是对话

OpenClaw 和泡泡之间不需要实时聊天，文件就是通信协议：
- OpenClaw 写文件 = 发消息给泡泡
- 泡泡读文件 = 收到消息
- 泡泡写文件 = 回复消息
- OpenClaw 读文件 = 看到回复

所有信息都持久化在磁盘上，任何一方重启都不会丢。
