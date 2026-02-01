# 飞书卡片消息格式示例

## 示例卡片 1：单列产品展示

```json
{
  "config": {
    "wide_screen_mode": true
  },
  "header": {
    "template": "blue",
    "title": {
      "tag": "plain_text",
      "content": "🔥 本周 AI 热点"
    }
  },
  "elements": [
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "**1. OpenClaw**\n@GitHub_Daily 发现的 AI Agent 应用商店"
      }
    },
    {
      "tag": "div",
      "text": {
        "tag": "plain_text",
        "content": "一个命令行工具，像 brew 安装软件一样给你的 AI 助手安装 700+ 插件。"
      }
    },
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": {
            "tag": "plain_text",
            "content": "查看详情"
          },
          "type": "primary",
          "url": "https://x.com/GitHub_Daily/status/..."
        }
      ]
    },
    {
      "tag": "hr"
    },
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "**2. Dottie**\nProduct Hunt 热门产品"
      }
    },
    {
      "tag": "div",
      "text": {
        "tag": "plain_text",
        "content": "主打隐私的 AI 私人日记，所有数据本地存储。"
      }
    },
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": {
            "tag": "plain_text",
            "content": "查看详情"
          },
          "type": "primary",
          "url": "https://www.producthunt.com/products/dottie"
        }
      ]
    },
    {
      "tag": "hr"
    },
    {
      "tag": "note",
      "elements": [
        {
          "tag": "plain_text",
          "content": "📊 数据来源：Twitter、Product Hunt、HackerNews、GitHub"
        }
      ]
    }
  ]
}
```

## 示例卡片 2：多列布局（产品对比）

```json
{
  "config": {
    "wide_screen_mode": true
  },
  "header": {
    "template": "orange",
    "title": {
      "tag": "plain_text",
      "content": "🛠️ 本周精选工具"
    }
  },
  "elements": [
    {
      "tag": "column_set",
      "flex_mode": "bisect",
      "background_style": "grey",
      "columns": [
        {
          "tag": "column",
          "width": "weighted",
          "weight": 1,
          "elements": [
            {
              "tag": "div",
              "text": {
                "tag": "lark_md",
                "content": "**OpenClaw**\n🤖 AI Agent 商店"
              }
            },
            {
              "tag": "div",
              "text": {
                "tag": "plain_text",
                "content": "700+ 插件一键安装"
              }
            }
          ]
        },
        {
          "tag": "column",
          "width": "weighted",
          "weight": 1,
          "elements": [
            {
              "tag": "div",
              "text": {
                "tag": "lark_md",
                "content": "**Dottie**\n📝 AI 日记"
              }
            },
            {
              "tag": "div",
              "text": {
                "tag": "plain_text",
                "content": "本地隐私保护"
              }
            }
          ]
        }
      ]
    },
    {
      "tag": "hr"
    },
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": {
            "tag": "plain_text",
            "content": "查看全部"
          },
          "type": "primary",
          "url": "https://github.com/Lychee-AI-Team/AiTrend"
        }
      ]
    }
  ]
}
```

## 示例卡片 3：带图片的富文本卡片

```json
{
  "config": {
    "wide_screen_mode": true
  },
  "header": {
    "template": "red",
    "title": {
      "tag": "plain_text",
      "content": "🔥 DeepSeek-R1 登上 Nature 封面"
    }
  },
  "elements": [
    {
      "tag": "img",
      "img_key": "img_v2_xxx",  // 需要上传到飞书获取
      "alt": {
        "tag": "plain_text",
        "content": "DeepSeek"
      },
      "preview": true
    },
    {
      "tag": "div",
      "text": {
        "tag": "lark_md",
        "content": "**国产大模型的历史性突破**\n\n仅用 30 万美元训练成本，达到 OpenAI 千万美元级别效果。"
      }
    },
    {
      "tag": "action",
      "actions": [
        {
          "tag": "button",
          "text": {
            "tag": "plain_text",
            "content": "阅读全文"
          },
          "type": "primary",
          "url": "https://36kr.com/p/..."
        },
        {
          "tag": "button",
          "text": {
            "tag": "plain_text",
            "content": "分享"
          },
          "type": "default"
        }
      ]
    }
  ]
}
```

## 在 AiTrend 中使用

修改 `src/channels/feishu_sender.py`：

```python
def send_card_message(content: dict, webhook_url: str):
    """发送飞书卡片消息"""
    import http.client
    import json
    
    conn = http.client.HTTPSConnection("open.feishu.cn")
    
    payload = json.dumps({
        "msg_type": "interactive",
        "card": content  # 上面示例的 JSON
    })
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    conn.request("POST", webhook_url, payload, headers)
    response = conn.getresponse()
    return response.status == 200
```

## 优势对比

| 特性 | 纯文本 | 卡片消息 |
|------|--------|----------|
| 视觉效果 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 移动端体验 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 按钮交互 | ❌ | ✅ |
| 图片展示 | ❌ | ✅ |
| 折叠面板 | ❌ | ✅ |
| 实现复杂度 | 低 | 中 |

## 推荐方案

**方案 A：渐进式**
- 保持当前纯文本格式
- 添加简单的按钮链接

**方案 B：卡片化**
- 每个产品一张卡片
- 包含标题、简介、按钮
- 更适合移动端阅读

**方案 C：混合式**
- 产品列表用卡片
- 趋势洞察用文本
- 平衡效果与复杂度

---

大师倾向哪种方案？🦞
