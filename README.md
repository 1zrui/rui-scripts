# rui-scripts

个人脚本和工具集

## 目录结构

```
rui-scripts/
├── SQL/                    # ZLHIS SQL 脚本和学习笔记
│   ├── 学习笔记/           # SQL 学习笔记（通用 + ZLHIS）
│   ├── 查询脚本/           # 各类查询 SQL（会诊、骨密度、中药颗粒等）
│   └── 报表脚本/           # 门诊/住院报表 SQL
├── scripts/                # Python 脚本和自动化工具
│   ├── binance_query.py    # 币安行情查询工具
│   ├── dict_query.py       # ZLHIS 数据字典查询工具
│   ├── github_trending.py  # GitHub Trending 热门项目日报工具
│   ├── fb_video_downloader.py  # Facebook 博主视频自动下载工具
│   └── zlhis_kb.py         # ZLHIS SQL 知识库（ChromaDB + 智能问答）
├── docs/                   # 文档和说明
│   └── requirements/       # 需求文档
├── AGENTS.md               # Hermes（豆子）工作区配置
└── README.md               # 本文件
```

## 内容说明

### SQL/
- **学习笔记/**：SQL 基础、ZLHIS 表结构、查询技巧
- **查询脚本/**：会诊查询、骨密度患者查询、中药颗粒查询等
- **报表脚本/**：门诊中医工作报表、治疗报表、检查设备排序等

### scripts/
- **binance_query.py** — 币安行情查询（支持多币种、代理、JSON 输出）
- **dict_query.py** — ZLHIS 数据字典查询（按表名/字段名模糊搜索）
- **github_trending.py** — GitHub Trending 热门项目抓取（支持语言/时间筛选）
- **fb_video_downloader.py** — Facebook 博主短视频自动下载（yt-dlp）
- **zlhis_kb.py** — ZLHIS SQL 知识库（ChromaDB 嵌入 + 智能问答）

### docs/
- **requirements/**：各脚本的需求文档

## 协作方式

- **Hermes（豆子🍡）**：日常开发、脚本维护、仓库整理
- **OpenClaw（布丁）**：需求分析、代码审查、方案讨论
- **Claude Code（泡泡）**：辅助开发（按需调用）

## 使用方法

```bash
# 克隆仓库
git clone https://github.com/1zrui/rui-scripts.git

# 更新代码
git pull

# 添加文件
git add .
git commit -m "说明"
git push
```