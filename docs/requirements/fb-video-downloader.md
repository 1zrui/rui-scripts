# 需求：Facebook博主视频下载工具

## 目标
创建一个脚本/工具，能够自动下载指定Facebook博主主页上"近一天"发布的短视频（时长 < 60秒），并保存到本地。

## 输入
- Facebook博主主页链接：`https://www.facebook.com/share/18og5yecYJ/?mibextid=wwXIfr`
- 博主ID：`61560682054555`（泰语吃播博主"ตั้งใจกิน"）
- 时间范围：近24小时内发布的视频
- 时长过滤：< 60秒

## 输出
- 下载的视频文件保存到 `D:\布丁工作区\facebook_download\`
- 每个视频文件名包含发布日期和视频ID

## 技术约束
- 使用 yt-dlp 下载（已安装）
- 需要走代理 `http://127.0.0.1:10808`（Facebook在国内无法直连）
- Facebook需要登录才能访问视频列表，需要解决认证问题
- 已知 yt-dlp 的 `--cookies-from-browser chrome` 在Windows上会报 DPAPI 错误

## 已验证可用的方法
- yt-dlp 可以下载单个Facebook视频（需要代理）
- 直接用Facebook视频URL：`https://www.facebook.com/61560682054555/videos/{video_id}`

## 难点
1. **列出博主所有视频**：Facebook需要登录才能查看视频列表
2. **获取视频元数据**：需要知道视频ID才能用yt-dlp获取时长和发布日期
3. **近一天过滤**：需要从视频列表中筛选出近24小时内发布的

## 可能的解决方案
1. 使用Facebook Graph API（需要access token）
2. 使用浏览器自动化（Selenium/Playwright）登录后抓取视频列表
3. 使用Facebook Cookie文件访问
4. 使用Facebook公开的RSS/Feed页面

## 验收标准
1. 能自动获取博主主页上近一天发布的所有视频
2. 只下载时长 < 60秒的视频
3. 视频文件保存到指定目录
4. 输出下载结果摘要（视频标题、时长、发布日期）
