"""

WPS 社区 AI 内容抓取模块
从 WPS 官方社区多个话题页、板块页抓取最近24小时内的帖子
"""
__version__ = "1.1.0"


import os
import re
import requests
from datetime import datetime, timedelta, timezone
from typing import Optional


def fetch_html(url: str, timeout: int = 30) -> Optional[str]:
    """抓取页面 HTML（带重试）"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"  [WARN] 第{attempt+1}次请求失败 {url}: {e}")
            if attempt < 2:
                import time
                time.sleep(2)
    print(f"  [ERROR] 放弃抓取 {url}")
    return None


def parse_list_page(html: str, base_url: str = "https://forum.wps.cn") -> list[dict]:
    """
    从列表页 HTML 中解析帖子信息
    返回列表: [{"url": "...", "title": "...", "datetime": "...", "summary": "..."}]
    """
    posts = []
    if not html:
        return posts

    # 匹配所有 topic-title 中的链接和标题
    title_links = re.findall(
        r'<h1\s+class="topic-title[^"]*"[^>]*>\s*<a\s+href="(/topic/\d+)"[^>]*>([^<]+)</a>',
        html, re.DOTALL
    )

    # 匹配 datetime
    datetimes = re.findall(r'<time\s+datetime="([^"]+)"', html)

    # 匹配摘要
    summaries = re.findall(
        r'class="topic-summary"[^>]*>([^<]{10,500})',
        html, re.DOTALL
    )

    for i, (href, title) in enumerate(title_links):
        post = {
            "url": f"{base_url}{href}",
            "title": title.strip(),
            "datetime": datetimes[i] if i < len(datetimes) else None,
            "summary": summaries[i].strip() if i < len(summaries) else "",
        }
        posts.append(post)

    return posts


def fetch_post_detail(url: str) -> Optional[dict]:
    """抓取帖子详情页，提取完整内容"""
    html = fetch_html(url)
    if not html:
        return None

    # 标题
    meta_title = re.search(r'<title>([^<]+)', html)
    title = meta_title.group(1).strip() if meta_title else ""

    # 描述/内容摘要
    desc = re.search(r'name="description"[^>]*content="([^"]+)"', html)
    summary = desc.group(1).strip() if desc else ""

    # 正文内容（取 topic-content 区域）
    content = re.search(
        r'class="topic-content[^"]*"[^>]*>([\s\S]*?)</div>\s*<div class="topic-vote"',
        html
    )
    body = ""
    if content:
        # 清理 HTML 标签
        body = re.sub(r'<[^>]+>', '', content.group(1))
        body = re.sub(r'\s+', ' ', body).strip()

    # 时间
    times = re.findall(r'datetime="([^"]+)"', html)
    dt = times[0] if times else ""

    # 标签
    tags = re.findall(r'href="/topics/tag/\d+"[^>]*>#([^<]+)', html)

    return {
        "url": url,
        "title": title,
        "datetime": dt,
        "summary": summary,
        "body": body[:800],
        "tags": tags,
    }


def is_within_24h(dt_str: str, hours: int = 24) -> bool:
    """判断时间是否在指定小时数内（默认24小时）"""
    if not dt_str:
        return True  # 无法解析时间的默认保留
    try:
        post_time = datetime.fromisoformat(dt_str)
        # 如果解析出来是 naive datetime，视为北京时间
        if post_time.tzinfo is None:
            post_time = post_time.replace(tzinfo=timezone(timedelta(hours=8)))
        # 计算 cutoff（北京时间）
        cutoff = datetime.now(timezone(timedelta(hours=8))) - timedelta(hours=hours)
        return post_time >= cutoff
    except Exception:
        return True


def deduplicate(posts: list[dict]) -> list[dict]:
    """按 URL 去重"""
    seen = set()
    result = []
    for p in posts:
        if p["url"] not in seen:
            seen.add(p["url"])
            result.append(p)
    return result


def collect_all_posts() -> list[dict]:
    """
    从多个话题页和板块页采集最近24小时的帖子
    数据源（共 8 个）：
      ---- 原有 3 个 ----
      1. WPS AI 话题页: forum.wps.cn/topics/tag/277
      2. AI办公话题页: forum.wps.cn/topics/tag/424
      3. 灵犀板块技巧教程: forum.wps.cn/topics/node/23?child=96
      ---- 新增 5 个 ----
      4. WPS AI 板块: forum.wps.cn/topics/node/8
      5. WPS产品体验板块（反馈/内测）: forum.wps.cn/topics/node/5
      6. 活动赛事板块: forum.wps.cn/topics/node/1
      7. 灵犀Claw话题: forum.wps.cn/topics/tag/16497
      8. Skills话题: forum.wps.cn/topics/tag/15880
    """
    sources = [
    # ---- 原有数据源（8个）----
    {
        "name": "WPS AI话题",
        "url": "https://forum.wps.cn/topics/tag/277?sort=newest",
        "type": "tag",
    },
    {
        "name": "AI办公话题",
        "url": "https://forum.wps.cn/topics/tag/424?sort=newest",
        "type": "tag",
    },
    {
        "name": "灵犀板块",
        "url": "https://forum.wps.cn/topics/node/23?child=96&sort=newest",
        "type": "node",
    },
    {
        "name": "WPS AI板块",
        "url": "https://forum.wps.cn/topics/node/8?sort=newest",
        "type": "node",
    },
    {
        "name": "WPS产品体验",
        "url": "https://forum.wps.cn/topics/node/5?sort=newest",
        "type": "node",
    },
    {
        "name": "活动赛事",
        "url": "https://forum.wps.cn/topics/node/1?sort=newest",
        "type": "node",
    },
    {
        "name": "灵犀Claw",
        "url": "https://forum.wps.cn/topics/tag/16497?sort=newest",
        "type": "tag",
    },
    {
        "name": "Skills技能",
        "url": "https://forum.wps.cn/topics/tag/15880?sort=newest",
        "type": "tag",
    },
    # ---- 新增数据源（12个）----
    {
        "name": "WPS表格",
        "url": "https://forum.wps.cn/topics/node/2?sort=newest",
        "type": "node",
    },
    {
        "name": "WPS文字",
        "url": "https://forum.wps.cn/topics/node/3?sort=newest",
        "type": "node",
    },
    {
        "name": "WPS演示",
        "url": "https://forum.wps.cn/topics/node/4?sort=newest",
        "type": "node",
    },
    {
        "name": "WPS学堂",
        "url": "https://forum.wps.cn/topics/node/6?sort=newest",
        "type": "node",
    },
    {
        "name": "WPS云文档",
        "url": "https://forum.wps.cn/topics/node/9?sort=newest",
        "type": "node",
    },
    {
        "name": "WPS多维表格",
        "url": "https://forum.wps.cn/topics/node/10?sort=newest",
        "type": "node",
    },
    {
        "name": "WPS PDF",
        "url": "https://forum.wps.cn/topics/node/11?sort=newest",
        "type": "node",
    },
    {
        "name": "WPS 365魔法社",
        "url": "https://forum.wps.cn/topics/node/12?sort=newest",
        "type": "node",
    },
    {
        "name": "综合杂谈圈",
        "url": "https://forum.wps.cn/topics/node/13?sort=newest",
        "type": "node",
    },
    {
        "name": "反馈直通车",
        "url": "https://forum.wps.cn/topics/node/18?sort=newest",
        "type": "node",
    },
    {
        "name": "WPS移动办公",
        "url": "https://forum.wps.cn/topics/node/22?sort=newest",
        "type": "node",
    },
    {
        "name": "WPS图片",
        "url": "https://forum.wps.cn/topics/node/24?sort=newest",
        "type": "node",
    },
]
    all_posts = []
    for source in sources:
        print(f"[INFO] 抓取 {source['name']}: {source['url']}")
        html = fetch_html(source["url"])
        posts = parse_list_page(html)
        print(f"  -> 获取到 {len(posts)} 条帖子")
        for p in posts:
            p["source_name"] = source["name"]
            p["source_type"] = source["type"]
        all_posts.extend(posts)

    # 去重
    all_posts = deduplicate(all_posts)
    print(f"[INFO] 去重后共 {len(all_posts)} 条帖子")

    # 过滤：支持通过环境变量 FILTER_HOURS 调整（默认24小时）
    filter_hours = int(os.environ.get("FILTER_HOURS", "24"))
    recent = [p for p in all_posts if is_within_24h(p["datetime"], hours=filter_hours)]
    print(f"[INFO] 最近{filter_hours}小时内共 {len(recent)} 条帖子")

    return recent
