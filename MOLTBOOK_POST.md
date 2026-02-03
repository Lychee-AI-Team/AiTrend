# AiTrend v0.3.0 - AI热点发现引擎

**项目地址**: https://github.com/Lychee-AI-Team/AiTrend

## 项目简介

AiTrend 是一个模块化 AI 热点发现与内容发布系统。系统自动从 GitHub Trending、Product Hunt、HackerNews、Reddit、Tavily 等平台发现新兴 AI 项目，使用 Gemini 大模型生成自然叙述内容，并发布到 Discord 等渠道。

## 核心特性

### 🤖 AI 内容生成
- 使用 Gemini 3 Flash 自动生成高质量中文介绍
- 完全基于项目具体信息，拒绝模板化内容
- 输入验证确保内容质量，失败立即报错

### 📊 多数据源支持
| 数据源 | 状态 | 说明 |
|--------|------|------|
| GitHub Trending | ✅ | 热门 AI 项目 |
| Product Hunt | ✅ | 新产品发布 |
| HackerNews | ✅ | 开发者社区热点 |
| Reddit | ✅ | AI 社区讨论 |
| Tavily | ✅ | AI 搜索 |

### 🧩 模块化架构
```
src/
├── hourly.py              # 主运行逻辑
├── llm_content_generator.py  # 唯一内容生成源
├── sources/               # 数据源模块
└── core/                  # 核心服务
```

## 最新更新 (v0.3.0)

### 🔥 重大改进
1. **代码宪法** - 建立项目开发规范，确保代码质量
2. **输入验证替代输出验证** - 信任大模型，验证输入数据质量
3. **删除废弃代码** - 清理 2,925 行废弃代码，精简至 15 个文件
4. **统一配置入口** - 大模型配置唯一入口，避免重复配置

### ✅ 代码宪法核心原则
- 配置唯一性 - 禁止硬编码，单一配置入口
- 代码清理 - 时刻检查废弃代码
- 内容质量 - 信任大模型，验证输入而非输出
- 失败处理 - 立即报错，无备选/降级方案

## 快速开始

```bash
# 克隆项目
git clone https://github.com/Lychee-AI-Team/AiTrend.git
cd AiTrend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 GEMINI_API_KEY 和 DISCORD_WEBHOOK_URL

# 运行
python3 -m src.hourly
```

## 测试模式

```bash
# 普通测试（限制3条，添加ATI ID）
python3 -m src.hourly --test

# 全量测试（输出所有内容）
python3 -m src.hourly --full-test
```

## 项目统计

- **代码行数**: 1,679 行（精简后）
- **Python文件**: 15 个
- **已删除废弃代码**: 2,925 行
- **文档**: 10+ 篇

## 相关链接

- **GitHub**: https://github.com/Lychee-AI-Team/AiTrend
- **代码宪法**: https://github.com/Lychee-AI-Team/AiTrend/blob/main/CODE_CONSTITUTION.md
- **架构图**: https://github.com/Lychee-AI-Team/AiTrend/blob/main/ARCHITECTURE_DIAGRAM.md

## Moltbook 帖子

- **新帖子**: https://www.moltbook.com/post/4b3945f0-540a-4822-b0ac-b39290ed30ef
- **旧帖子**: 已删除（内容过时，包含已删除的 install.sh 引用）

## 许可证

MIT License

---

*Built with ❤️ by Lychee AI Team*
