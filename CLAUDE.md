# CLAUDE.md - 项目说明

## 项目概述
rui-scripts 是个人脚本和工具集，主要用于：
- ZLHIS SQL 查询和报表
- Python 自动化脚本
- 工作工具和 utilities

## 目录结构
```
rui-scripts/
├── SQL/              # ZLHIS SQL 脚本和学习笔记
│   ├── 学习笔记/     # SQL 学习笔记（通用 + ZLHIS）
│   ├── 查询脚本/     # 各类查询 SQL
│   └── 报表脚本/     # 门诊/住院报表 SQL
├── scripts/          # Python 脚本和自动化工具
├── docs/             # 文档和说明
│   └── requirements/ # 需求文档（布丁写，泡泡读）
├── memory/           # 记忆文件
├── CLAUDE.md         # 本文件，给 Claude Code 看
└── README.md
```

## 协作方式
- **布丁（OpenClaw）**：项目规划、需求分析、创建 Issue
- **泡泡（Claude Code）**：读 Issue、写代码、commit + push

## 工作流程
1. 布丁写需求文档 → `docs/requirements/xxx.md`
2. 布丁创建 Issue → GitHub 仓库 `1zrui/rui-scripts`
3. 大哥通知泡泡看 Issue
4. 泡泡读 Issue → 写代码 → commit → push → 关闭 Issue

## 开发规范
1. 代码提交前先 pull 最新版本
2. 中文注释，清晰明了
3. 新功能放在对应目录，不要散落
4. 测试通过再推送

## ZLHIS 相关
- 数据字典：`D:\布丁工作区\字典\ZLHIS+_数据字典.xlsx`
- SQL 知识库：`memory/knowledge/tech/zlhis-sql.md`
- 写 SQL 前先查字典，不确定的问大哥

## 记忆系统
- @.claude/claude-memory-bank.md
