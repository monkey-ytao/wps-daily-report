"""

WPS 社区 AI 日报生成与推送模块
对抓取的帖子进行分类整理，生成日报并推送到微信

分类体系（5 类）：
  🔥 新功能发布：新功能、重大更新、内测招募、上线发布
  🧪 内测/Beta：抢先体验、公测、内测资格、Beta版本
  ⭐ 案例/技巧：优质使用案例、实用技巧教程、实战攻略
  🐛 问题反馈：Bug报告、功能请求、吐槽、求助
  📌 社区动态：社区活动、话题讨论、一般性分享

输出增强：
  - 关键词高亮（行业相关术语自动加标记）
  - 来源标注（区分话题页 vs 板块页）
  - 简要统计摘要
"""
__version__ = "1.1.0"


import os
import re
import requests
from datetime import datetime, timedelta, timezone
from typing import Optional

# ---- 行业关键词高亮 ----
# 行业热门术语关键词
INDUSTRY_KEYWORDS = {
    # WPS 产品线
    "WPS AI": "WPS AI", "WPS灵犀": "灵犀", "灵犀Claw": "灵犀Claw", "Claw": "Claw",
    "WPS 365": "WPS 365", "WPS Office": "WPS Office",
    # AI/大模型
    "AI": "AI", "AIGC": "AIGC", "大模型": "大模型", "LLM": "LLM",
    "Agent": "Agent", "MCP": "MCP", "智能体": "智能体",
    # 文档类型
    "PPT": "PPT", "Word": "Word", "Excel": "Excel", "PDF": "PDF",
# 实用工具
    "Python": "Python", "API": "API", "自动化": "自动化",
    "Skill": "Skill", "技能": "技能",
}

# ---- 分类规则 ----

# 🔥 新功能发布
NEW_FEATURE_KEYWORDS = [
    "新功能", "更新", "升级", "上线", "发布",
    "新版本", "重磅", "全新", "新增",
    "正式版", "正式上线", "全面开放",
]

# 🧪 内测/Beta
BETA_KEYWORDS = [
    "内测", "测试", "公测", "招募", "抢先体验", "首发",
    "Beta", "beta", "体验资格", "灰度", "预览版",
    "候补", "名额", "报名",
]

# ⭐ 案例/技巧
CASE_TIPS_KEYWORDS = [
    "教程", "技巧", "实战", "案例", "使用心得", "用法", "攻略",
    "指南", "方法", "提效", "效率", "自动化", "操作", "场景",
    "怎么用", "如何", "一键", "搞定", "保姆级", "入门",
    "基础", "进阶", "课件", "教学", "从零", "搭建",
    "分享", "模板", "批量", "插件", "脚本",
]

# 🐛 问题反馈
BUG_KEYWORDS = [
    "bug", "BUG", "Bug", "崩溃", "闪退", "卡顿", "报错",
    "问题", "故障", "异常", "失效", "无法", "不能",
    "希望增加", "建议", "功能请求", "优化建议",
    "求助", "求助", "问答", "怎么解决", "修复",
    "吐槽", "差评", "不满", "失望",
]

# 📌 社区动态
COMMUNITY_KEYWORDS = [
    "社区", "活动", "话题", "讨论", "签到",
    "反馈", "意见", "BB机", "打卡",
]


def classify_post(post: dict) -> str:
    """对帖子进行分类（5类优先级：新功能 > 内测 > 技巧 > 问题 > 社区）"""
    title = post.get("title", "")
    summary = post.get("summary", "") or ""
    source_name = post.get("source_name", "")
    text = f"{title} {summary} {source_name}"

    # 🧪 内测/Beta（优先级高，单独标记）
    for kw in BETA_KEYWORDS:
        if kw in text:
            return "beta"

    # 🔥 新功能发布
    for kw in NEW_FEATURE_KEYWORDS:
        if kw in text:
            return "new_feature"

    # 🐛 问题反馈
    for kw in BUG_KEYWORDS:
        if kw in text:
            return "bug"

    # ⭐ 案例/技巧
    for kw in CASE_TIPS_KEYWORDS:
        if kw in text:
            return "tips"

    # 📌 社区动态（默认）
    for kw in COMMUNITY_KEYWORDS:
        if kw in text:
            return "community"

    return "community"


def fetch_post_content(url: str) -> Optional[dict]:
    """
    抓取帖子详情（供分类时参考）
    如果摘要不够，可以访问详情页获取更多信息
    """
    try:
        from fetch_posts import fetch_html
        html = fetch_html(url)
        if not html:
            return None

        desc = re.search(r'name="description"[^>]*content="([^"]+)"', html)
        summary = desc.group(1).strip() if desc else ""

        content = re.search(
            r'class="topic-content[^"]*"[^>]*>([\s\S]*?)</div>\s*<div class="topic-vote"',
            html
        )
        body = ""
        if content:
            body = re.sub(r'<[^>]+>', '', content.group(1))
            body = re.sub(r'\s+', ' ', body).strip()

        tags = re.findall(r'href="/topics/tag/\d+"[^>]*>#([^<]+)', html)

        return {
            "url": url,
            "summary": summary,
            "body": body[:1000],
            "tags": tags,
        }
    except Exception as e:
        print(f"[WARN] Failed to fetch detail {url}: {e}")
        return None


def classify_with_detail(post: dict) -> str:
    """带详情的分类（用于摘要不足时）"""
    title = post.get("title", "")
    summary = post.get("summary", "") or ""

    # 先用已有信息分类
    initial = classify_post(post)

    # 如果摘要较长（>30字），信任初始分类
    if len(summary) > 30:
        return initial

    # 摘要太短，尝试抓详情
    detail = fetch_post_content(post["url"])
    if detail:
        enriched = {
            "title": title,
            "summary": (detail.get("summary", "") or "") + " " + (detail.get("body", "") or ""),
        }
        return classify_post(enriched)

    return initial


def highlight_keywords(text: str) -> str:
    """对文本中的行业关键词进行高亮标记（使用【】包裹）"""
    result = text
    for kw, label in INDUSTRY_KEYWORDS.items():
        # 只替换标题/摘要中独立出现的关键词，避免重复标记
        pattern = re.compile(re.escape(kw))
        # 检查是否已经被标记过
        if f"【{label}】" in result:
            continue
        result = pattern.sub(f"【{label}】", result)
    return result


def detect_industry_tags(title: str, summary: str) -> list[str]:
    """检测帖子涉及的应用行业/场景标签"""
    tags = []
    text = f"{title} {summary}"

    industry_map = {
        "教育": ["教师", "学生", "课堂", "课件", "教学", "学习", "考试", "作业", "课件", "校园"],
        "政务": ["政务", "政府", "审批", "公文", "办公", "公共服务"],
        "财务/金融": ["财务", "报表", "预算", "审计", "金融", "银行", "会计"],
        "人力资源": ["HR", "人事", "招聘", "薪酬", "绩效考核", "考勤"],
        "项目管理": ["项目", "进度", "甘特图", "里程碑", "排期"],
        "营销/电商": ["营销", "电商", "运营", "推广", "活动策划", "带货"],
    }

    for industry, keywords in industry_map.items():
        for kw in keywords:
            if kw in text:
                tags.append(industry)
                break

    return tags


def generate_report(posts: list[dict], enrich: bool = False) -> str:
    """
    生成日报文本
    :param posts: 帖子列表
    :param enrich: 是否抓取详情来补充分类（较慢）
    :return: 日报纯文本
    """
    now_beijing = datetime.now(timezone(timedelta(hours=8)))
    date_str = now_beijing.strftime("%Y年%m月%d日")

    new_features = []  # 🔥 新功能
    betas = []         # 🧪 内测/Beta
    tips = []          # ⭐ 案例/技巧
    bugs = []          # 🐛 问题反馈
    community = []     # 📌 社区动态

    for post in posts:
        cat = classify_with_detail(post) if enrich else classify_post(post)
        item = _format_post_item(post, cat)

        if cat == "new_feature":
            new_features.append(item)
        elif cat == "beta":
            betas.append(item)
        elif cat == "tips":
            tips.append(item)
        elif cat == "bug":
            bugs.append(item)
        else:
            community.append(item)

    lines = []
    lines.append("═══ WPS AI 社区日报 ═══")
    lines.append(f"📅 {date_str}")
    lines.append("")

    # 数据源统计
    source_names = set()
    for p in posts:
        source_names.add(p.get("source_name", ""))
    lines.append(f"📊 本次覆盖 {len(source_names)} 个数据源，共 {len(posts)} 条内容")
    lines.append("")

    # 🔥 今日新功能
    lines.append(f"🔥 新功能发布（{len(new_features)}条）")
    if new_features:
        for item in new_features:
            lines.append(item)
            lines.append("")
    else:
        lines.append("暂无")
        lines.append("")

    # 🧪 内测/Beta
    lines.append(f"🧪 内测/Beta（{len(betas)}条）")
    if betas:
        for item in betas:
            lines.append(item)
            lines.append("")
    else:
        lines.append("暂无")
        lines.append("")

    # ⭐ 推荐案例/技巧
    lines.append(f"⭐ 案例/技巧（{len(tips)}条）")
    if tips:
        for item in tips:
            lines.append(item)
            lines.append("")
    else:
        lines.append("暂无")
        lines.append("")

    # 🐛 问题反馈
    lines.append(f"🐛 问题反馈（{len(bugs)}条）")
    if bugs:
        for item in bugs:
            lines.append(item)
            lines.append("")
    else:
        lines.append("暂无")
        lines.append("")

    # 📌 社区动态
    lines.append(f"📌 社区动态（{len(community)}条）")
    if community:
        for item in community:
            lines.append(item)
            lines.append("")
    else:
        lines.append("暂无")
        lines.append("")

    # 💡 一句话总结
    summary_line = _generate_summary(new_features, betas, tips, bugs, community)
    lines.append("💡 灵犀一句话总结")
    lines.append(summary_line)

    return "\n".join(lines)


def _format_post_item(post: dict, category: str) -> str:
    """格式化单个帖子条目（带关键词高亮和行业标签）"""
    title = post.get("title", "未知标题")
    url = post.get("url", "")
    summary = post.get("summary", "") or ""
    source_name = post.get("source_name", "")

    # 关键词高亮标题
    highlighted_title = highlight_keywords(title)

    # 检测行业标签
    industry_tags = detect_industry_tags(title, summary)

    lines = []
    lines.append(f"【{highlighted_title}】")

    if category == "new_feature":
        lines.append(f"▸ 功能亮点：{summary[:150]}")
        lines.append(f"▸ 使用入口：详见原帖")
    elif category == "beta":
        lines.append(f"▸ 内测信息：{summary[:150]}")
    elif category == "tips":
        lines.append(f"▸ 方法要点：{summary[:150]}")
        lines.append(f"▸ 效果/收益：提升办公效率")
    elif category == "bug":
        lines.append(f"▸ 问题描述：{summary[:120]}")
    else:
        lines.append(f"▸ {summary[:100]}")

    # 来源标注
    lines.append(f"▸ 来源：{source_name} | {url}")

    # 行业标签
    if industry_tags:
        lines.append(f"▸ 场景：{'、'.join(industry_tags)}")

    return "\n".join(lines)


def _generate_summary(features, betas, tips, bugs, community) -> str:
    """生成一句话总结"""
    total = len(features) + len(betas) + len(tips) + len(bugs) + len(community)
    if total == 0:
        return "今日社区暂无新动态，明天继续关注！"

    parts = []
    if features:
        parts.append(f"有{len(features)}个新功能发布")
    if betas:
        parts.append(f"{len(betas)}个内测机会")
    if tips:
        parts.append(f"{len(tips)}篇实用技巧")
    if bugs:
        parts.append(f"{len(bugs)}条问题反馈")
    if community:
        parts.append(f"{len(community)}条社区讨论")

    return f"今日社区共{total}条内容，{'，'.join(parts)}，值得关注！"


def push_to_wechat(title: str, content: str, token: str) -> bool:
    """通过 PushPlus 推送到微信"""
    # 逐行处理，保留特殊符号，URL 可点击
    html_lines = []
    for line in content.split("\n"):
        line = line.replace("&", "&amp;")
        # 将 URL 转为可点击链接
        url_pattern = r'(https?://[^\s<]+)'
        line = re.sub(url_pattern, r'<a href="\1">\1</a>', line)
        html_lines.append(line)
    html_content = "<br>".join(html_lines)

    # 加粗标题行
    html_content = re.sub(
        r'(【[^】]+】)',
        r'<b>\1</b>',
        html_content
    )

    payload = {
        "token": token,
        "title": title,
        "content": html_content,
        "template": "html",
    }

    try:
        resp = requests.post(
            "https://www.pushplus.plus/send",
            json=payload,
            timeout=30,
        )
        result = resp.json()
        if result.get("code") == 200:
            print(f"[INFO] 推送成功: {title}")
            return True
        else:
            print(f"[ERROR] 推送失败: {result}")
            return False
    except Exception as e:
        print(f"[ERROR] 推送异常: {e}")
        return False
