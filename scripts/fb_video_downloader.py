#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook 博主视频自动下载工具

自动下载 Facebook 博主近一天发布的短视频（<60秒）
"""

import os
import re
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import requests

# ============== 配置 ==============
PROXY = "http://127.0.0.1:10808"
PROXIES = {
    "http": PROXY,
    "https": PROXY,
}

# 博主信息
PAGE_ID = "61560682054555"
PAGE_URL = "https://www.facebook.com/share/18og5yecYJ/?mibextid=wwXIfr"

# 下载配置
OUTPUT_DIR = Path("D:/布丁工作区/facebook_download/")
DOWNLOADED_LOG = Path(__file__).parent / "fb_downloaded.json"
MAX_DURATION = 60  # 秒

# Cookie（需要手动填入Facebook登录后的cookie）
COOKIES = ""  # TODO: 填入你的Facebook Cookie


class FBDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.proxies = PROXIES
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        if COOKIES:
            self.session.headers["Cookie"] = COOKIES

    def load_downloaded(self) -> set:
        """加载已下载视频ID"""
        if DOWNLOADED_LOG.exists():
            with open(DOWNLOADED_LOG, "r", encoding="utf-8") as f:
                return set(json.load(f))
        return set()

    def save_downloaded(self, video_ids: list):
        """保存已下载视频ID"""
        downloaded = self.load_downloaded()
        downloaded.update(video_ids)
        with open(DOWNLOADED_LOG, "w", encoding="utf-8") as f:
            json.dump(list(downloaded), f, ensure_ascii=False, indent=2)

    def get_video_list(self) -> list:
        """
        获取博主视频列表
        使用 Facebook GraphQL API
        """
        # Facebook GraphQL endpoint
        url = "https://www.facebook.com/api/graphql/"

        # 构建查询
        query = {
            "av": PAGE_ID,
            "__user": "0",
            "__a": "1",
            "__req": "1d",
            "__ccg": "EXCELLENT",
            "__hs": "19765.HB:facebook_combout_pkg.2.0..0.0",
            "dpr": "1",
            "__csr": "",
            "__crg": "",
            "server_timestamps": "true",
            "doc_id": "5817908061808667",
            "variables": json.dumps({
                "pageID": PAGE_ID,
                "scale": "1",
            })
        }

        try:
            response = self.session.get(url, params=query, timeout=30)
            data = response.json()
            # 解析返回数据
            videos = self._parse_videos(data)
            return videos
        except Exception as e:
            print(f"获取视频列表失败: {e}")
            return []

    def _parse_videos(self, data: dict) -> list:
        """解析视频数据"""
        videos = []
        try:
            # 遍历数据找视频节点
            nodes = data.get("data", {}).get("node", {}).get("video_chaining_unit", {}).get("videos", {}).get("nodes", [])
            for node in nodes:
                video = {
                    "id": node.get("id"),
                    "url": node.get("playable_url") or node.get("video_view_url"),
                    "duration": node.get("original_spherical_video_fallback_url", {}).get("duration", 0),
                    "created_at": node.get("creation_time", 0),
                    "title": node.get("title", ""),
                }
                if video["url"]:
                    videos.append(video)
        except Exception as e:
            print(f"解析视频数据失败: {e}")
        return videos

    def get_video_duration(self, video_url: str) -> int:
        """使用 yt-dlp 获取视频时长（秒）"""
        try:
            result = subprocess.run(
                ["yt-dlp", "--dump-json", "--no-download", video_url],
                capture_output=True,
                text=True,
                timeout=30,
                proxies={"http": PROXY, "https": PROXY}
            )
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return int(info.get("duration", 0) or 0)
        except Exception as e:
            print(f"获取时长失败: {e}")
        return 0

    def is_recent(self, timestamp: int) -> bool:
        """检查是否是近一天发布的"""
        if not timestamp:
            return True  # 无法判断时默认下载
        video_time = datetime.fromtimestamp(timestamp)
        one_day_ago = datetime.now() - timedelta(days=1)
        return video_time > one_day_ago

    def download_video(self, video_url: str, filename: str) -> bool:
        """使用 yt-dlp 下载视频"""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / f"{filename}.mp4"

        try:
            result = subprocess.run(
                [
                    "yt-dlp",
                    "-f", "best[height<=720]",
                    "--no-playlist",
                    "-o", str(output_path),
                    "--proxy", PROXY,
                    video_url
                ],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                print(f"✅ 下载成功: {filename}.mp4")
                return True
            else:
                print(f"❌ 下载失败: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"❌ 下载超时: {filename}")
            return False
        except Exception as e:
            print(f"❌ 下载异常: {e}")
            return False

    def run(self):
        """主流程"""
        print(f"📺 开始获取 Facebook 博主视频...")
        print(f"   博主ID: {PAGE_ID}")
        print(f"   代理: {PROXY}")
        print(f"   输出目录: {OUTPUT_DIR}")
        print()

        # 加载已下载列表
        downloaded = self.load_downloaded()
        print(f"📋 已有 {len(downloaded)} 个视频已下载")

        # 获取视频列表
        videos = self.get_video_list()
        print(f"📋 获取到 {len(videos)} 个视频")

        if not videos:
            print("⚠️ 未获取到视频，可能需要更新 Cookie")
            self._try_alternative_method()
            return

        # 筛选并下载
        new_downloads = []
        for video in videos:
            video_id = video["id"]

            # 跳过已下载
            if video_id in downloaded:
                print(f"⏭️ 跳过已下载: {video_id}")
                continue

            # 检查时长
            duration = video.get("duration", 0)
            if not duration:
                duration = self.get_video_duration(video["url"])

            if duration > MAX_DURATION:
                print(f"⏭️ 跳过过长视频 ({duration}s): {video_id}")
                continue

            # 下载
            print(f"⬇️ 下载中 ({duration}s): {video_id}")
            if self.download_video(video["url"], f"{video_id}_{int(time.time())}"):
                new_downloads.append(video_id)

        # 保存下载记录
        if new_downloads:
            self.save_downloaded(new_downloads)
            print(f"\n✅ 本次新增 {len(new_downloads)} 个视频")

    def _try_alternative_method(self):
        """备选方案：尝试直接用 yt-dlp 解析博主主页"""
        print("\n🔄 尝试备选方案...")

        # yt-dlp 支持直接解析 Facebook 页面
        # 尝试用 yt-dlp 获取视频信息
        try:
            result = subprocess.run(
                ["yt-dlp", "--flat-playlist", "--print", "%(id)s %(duration)s %(title)s",
                 "--proxy", PROXY, PAGE_URL],
                capture_output=True,
                text=True,
                timeout=60,
                proxies=PROXIES
            )
            if result.returncode == 0:
                print("📋 备选方案可用（需进一步实现）")
                print(result.stdout)
        except Exception as e:
            print(f"备选方案也失败了: {e}")


def main():
    downloader = FBDownloader()
    downloader.run()


if __name__ == "__main__":
    main()