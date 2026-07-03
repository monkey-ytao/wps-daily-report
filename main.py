#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WPS 社区 AI 日报 - 主入口
抓取 WPS 社区最新 AI 相关内容，分类整理后推送到微信
支持本地运行和 GitHub Actions 自动运行
"""

__version__ = "1.1.0"

import os
import sys
from datetime import datetime, timedelta, timezone

from fetch_posts import collect_all_posts
from report import generate_report, push_to_wechat

# PushPlus Token（从环境变量读取）
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

def main():
    print("=" * 50)
    print(f"WPS AI 社区日报生成器 (v{__version__})")
    now_beijing = datetime.now(timezone(timedelta(hours=8)))
    print(f"当前时间: {now_beijing.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 1. 抓取帖子
    print("\n[步骤1] 抓取社区帖子...")
    posts = collect_all_posts()

    if not posts:
        print("[INFO] 最近24小时内没有新帖子")

    # 2. 生成日报（无论有无帖子都生成）
    print(f"\n[步骤2] 生成日报（共 {len(posts)} 条帖子）...")
    report_text = generate_report(posts, enrich=False)
    print(report_text)

    # 3. 推送到微信（无论有无内容都推送）
    if PUSHPLUS_TOKEN:
        print("\n[步骤3] 推送到微信...")
        date_str = now_beijing.strftime("%Y年%m月%d日")
        title = f"WPS AI 社区日报 - {date_str}"
        success = push_to_wechat(title, report_text, PUSHPLUS_TOKEN)
        if success:
            print("[DONE] 日报推送成功！")
        else:
            print("[FAIL] 日报推送失败，请检查 PushPlus Token")
            sys.exit(1)
    else:
        print("\n[SKIP] 未配置 PUSHPLUS_TOKEN，跳过微信推送")
        print("如需推送，请设置环境变量: export PUSHPLUS_TOKEN=你的token")

    print("\n[DONE] 日报流程完成")

if __name__ == "__main__":
    main()
