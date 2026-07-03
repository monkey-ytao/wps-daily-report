# WPS AI 社区日报

自动抓取 WPS 官方社区（forum.wps.cn）最新内容，分类整理后通过 PushPlus 推送到微信。

## 功能

- 每日自动抓取 WPS 社区 **20 个数据源**的最新帖子
- 按内容类型分 **5 类**：新功能、内测/Beta、案例/技巧、问题反馈、社区动态
- **关键词高亮**：自动标记 AI、Agent、Skill 等行业术语
- **行业标签**：自动检测教育、政务、财务/金融等应用场景
- **来源标注**：区分话题页和板块页，方便追溯
- 通过 PushPlus 推送日报到微信

## 数据源

| # | 来源 | 类型 | 说明 |
|---|------|------|------|
| 1 | [WPS AI 话题](https://forum.wps.cn/topics/tag/277) | 话题 | #WPS AI 标签下最新帖子 |
| 2 | [AI办公话题](https://forum.wps.cn/topics/tag/424) | 话题 | #AI办公 标签下最新帖子 |
| 3 | [灵犀板块](https://forum.wps.cn/topics/node/23?child=96) | 板块 | 灵犀技巧教程区最新帖子 |
| 4 | [WPS AI 板块](https://forum.wps.cn/topics/node/8) | 板块 | WPS AI 综合讨论区 |
| 5 | [WPS产品体验](https://forum.wps.cn/topics/node/5) | 板块 | 产品反馈与体验分享 |
| 6 | [活动赛事](https://forum.wps.cn/topics/node/1) | 板块 | 官方社区活动 |
| 7 | [灵犀Claw](https://forum.wps.cn/topics/tag/16497) | 话题 | 灵犀 Claw 桌面客户端相关 |
| 8 | [Skills技能](https://forum.wps.cn/topics/tag/15880) | 话题 | 灵犀技能开发与分享 |
| 9 | [WPS表格](https://forum.wps.cn/topics/node/2) | 板块 | 表格产品讨论与技巧 |
| 10 | [WPS文字](https://forum.wps.cn/topics/node/3) | 板块 | 文字处理讨论与技巧 |
| 11 | [WPS演示](https://forum.wps.cn/topics/node/4) | 板块 | 演示文稿讨论与技巧 |
| 12 | [WPS学堂](https://forum.wps.cn/topics/node/6) | 板块 | 学习教程与课程分享 |
| 13 | [WPS云文档](https://forum.wps.cn/topics/node/9) | 板块 | 云文档协作与使用 |
| 14 | [WPS多维表格](https://forum.wps.cn/topics/node/10) | 板块 | 多维表格/智能表格讨论 |
| 15 | [WPS PDF](https://forum.wps.cn/topics/node/11) | 板块 | PDF 功能讨论与反馈 |
| 16 | [WPS 365魔法社](https://forum.wps.cn/topics/node/12) | 板块 | WPS 365 综合讨论 |
| 17 | [综合杂谈圈](https://forum.wps.cn/topics/node/13) | 板块 | 社区杂谈与互动 |
| 18 | [反馈直通车](https://forum.wps.cn/topics/node/18) | 板块 | 用户问题反馈直达官方 |
| 19 | [WPS移动办公](https://forum.wps.cn/topics/node/22) | 板块 | 移动端使用讨论 |
| 20 | [WPS图片](https://forum.wps.cn/topics/node/24) | 板块 | 图片处理功能讨论 |

## 分类体系

| 类别 | 标记 | 触发关键词示例 |
|------|------|---------------|
| 新功能发布 | 🔥 | 新功能、更新、升级、上线、发布、正式版 |
| 内测/Beta | 🧪 | 内测、公测、招募、抢先体验、灰度、Beta |
| 案例/技巧 | ⭐ | 教程、技巧、实战、案例、攻略、提效 |
| 问题反馈 | 🐛 | bug、崩溃、闪退、求助、建议、吐槽 |
| 社区动态 | 📌 | 社区、活动、话题、讨论、签到 |

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/monkey-ytao/wps-daily-report.git
cd wps-daily-report
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 创建 .env 文件
echo 'PUSHPLUS_TOKEN=你的token' > .env
```

> PushPlus Token 从 [pushplus.plus](https://www.pushplus.plus) 免费获取，用于推送到微信。

### 4. 运行

```bash
python main.py
```

## 部署到 GitHub Actions

### 1. 创建 GitHub 仓库

在 GitHub 上创建仓库（公开或私有均可），将本目录所有文件上传：

```
wps-daily-report/
├── .github/
│   └── workflows/
│       └── daily-report.yml    # GitHub Actions 配置
├── fetch_posts.py               # 抓取模块（20个数据源）
├── report.py                    # 分类（5类）、高亮、推送模块
├── main.py                      # 主入口
├── requirements.txt             # Python 依赖
├── LICENSE                       # MIT 许可证
└── README.md                    # 本文件
```

### 2. 配置 Secret

进入仓库 **Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|------|-------|
| `PUSHPLUS_TOKEN` | 你的 PushPlus Token |

### 3. 启用 Actions

推送代码后，进入 **Actions** 页面确认 workflow 已启用。

- **自动执行**：每天北京时间 08:00 自动运行
- **手动触发**：Actions → "WPS AI 社区日报" → Run workflow

## 部署到云服务器

支持部署到任意 Linux 服务器（Ubuntu/CentOS/Debian），配合 cron 定时运行：

```bash
# 安装依赖
pip3 install -r requirements.txt

# 配置环境变量
echo 'PUSHPLUS_TOKEN=你的token' > .env

# 设置定时任务（每天北京时间 08:00 = UTC 00:00）
(crontab -l 2>/dev/null; echo '0 0 * * * cd /opt/wps-daily-report && . .env && export PUSHPLUS_TOKEN && /usr/bin/python3 main.py >> /opt/wps-daily-report/logs/daily.log 2>&1') | crontab -
```

## 注意事项

- GitHub Actions 使用 UTC 时区，cron `0 0 * * *` 对应北京时间 08:00
- GitHub Actions 的 cron 可能有几分钟延迟，属于正常现象
- 抓取请求支持 3 次重试，网络波动不影响整体运行
- 关键词高亮使用 【】标记，在微信推送中会加粗显示
- 行业标签自动检测，覆盖教育、政务、财务/金融、人力资源等场景

## 免责声明

### 1. 项目性质

本项目是一个个人开源项目，仅供学习、研究和技术交流使用。本项目与金山办公软件有限公司（以下简称"金山办公"）、WPS 品牌及其关联方无任何隶属、合作或代理关系，未获得金山办公的官方授权或背书。

### 2. 数据来源与版权

- 本工具抓取的内容均来源于 [WPS 官方社区](https://forum.wps.cn)（forum.wps.cn）的公开页面
- 上述内容的版权归原作者、帖子发布者及金山办公所有
- 本工具仅对公开信息进行采集和整理，不对原始内容进行任何修改
- 如内容原作者认为抓取行为侵犯了其权益，请联系开发者，将在收到通知后第一时间删除相关内容

### 3. 准确性与时效性

- 本工具通过自动化方式抓取和分类社区内容，**不对内容的准确性、完整性、时效性和可靠性做任何明示或暗示的保证**
- 分类结果基于关键词匹配算法，可能存在误分类或遗漏
- 摘要内容为自动截取，可能无法完整反映原帖含义
- 用户应以 WPS 社区原始帖子为准，本工具的整理结果仅供参考

### 4. 服务可用性

- 本工具依赖 WPS 社区网站的结构稳定性运行，若 WPS 社区改版、升级或关闭，本工具可能无法正常工作
- 本工具依赖 PushPlus 推送服务，该服务可能存在不可用、延迟或功能变更的情况
- 本工具通过网络请求抓取数据，可能因网络波动、IP 限制等原因导致抓取失败
- **开发者不保证本工具能够持续、稳定、无中断地运行**

### 5. 使用限制

- 本工具基于 MIT 许可证开源，允许商业和非商业使用，但需保留版权声明
- 本工具抓取的内容版权归原作者及金山办公所有，使用者不得将抓取内容直接转售或打包销售
- 本工具不得用于任何非法用途，包括但不限于批量爬取、恶意攻击、数据倒卖
- 使用者应遵守 WPS 社区的用户协议和相关服务条款
- 使用者应遵守所在地关于数据采集和使用的法律法规

### 6. 责任限制

在适用法律允许的最大范围内，对于因使用或无法使用本工具而导致的任何直接、间接、附带、特殊或后果性损害（包括但不限于数据丢失、业务中断、利润损失），开发者不承担任何赔偿责任。

### 7. 知识产权

- 本项目的源代码采用 [MIT 许可证](LICENSE) 开源
- 项目中的分类算法、关键词列表、行业标签等均为开发者原创设计
- WPS、WPS AI、WPS灵犀、灵犀Claw、PushPlus 等名称和商标归各自权利人所有

### 8. 接受声明

使用本工具即表示您已阅读、理解并同意上述全部条款。如果您不同意其中任何条款，请立即停止使用本工具。

### 9. 联系方式

如对本声明或本工具有任何疑问，可通过 [GitHub Issues](https://github.com/monkey-ytao/wps-daily-report/issues) 联系开发者。

## 许可证

[MIT License](LICENSE)
