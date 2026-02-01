#!/usr/bin/env node
// Webhook Server - 支持 AI Hotspot 端点，直接调用飞书 API

import express from 'express';
import axios from 'axios';
import { writeFileSync, unlinkSync } from 'fs';

const app = express();
const PORT = process.env.PORT || 3000;

// 飞书配置（从环境变量读取）
const FEISHU_APP_ID = process.env.FEISHU_APP_ID || '';
const FEISHU_SECRET_KEY = process.env.FEISHU_SECRET_KEY || '';
const FEISHU_GROUP_ID = process.env.FEISHU_GROUP_ID || 'oc_9a3c218325fd2cfa42f2a8f6fe03ac02';

// Token 缓存
let tokenCache = { token: null, expireTime: 0 };

// 解析 JSON body
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// CORS 支持
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
});

// 获取飞书访问令牌
async function getFeishuToken() {
  const now = Date.now();
  if (tokenCache.token && now < tokenCache.expireTime - 60000) {
    return tokenCache.token;
  }

  try {
    const response = await axios.post(
      'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
      { app_id: FEISHU_APP_ID, app_secret: FEISHU_SECRET_KEY },
      { headers: { 'Content-Type': 'application/json' } }
    );

    if (response.data.code === 0) {
      tokenCache = {
        token: response.data.tenant_access_token,
        expireTime: now + (response.data.expire - 60) * 1000
      };
      return tokenCache.token;
    }
    throw new Error(response.data.msg);
  } catch (error) {
    console.error('获取飞书 token 失败:', error.message);
    throw error;
  }
}

// 发送消息到飞书
async function sendToFeishu(text) {
  try {
    const token = await getFeishuToken();

    // 移除 markdown 格式，保留 emoji
    let message = text
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/`(.*?)`/g, '$1')
      .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1');

    const response = await axios.post(
      `https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id`,
      {
        receive_id: FEISHU_GROUP_ID,
        msg_type: 'text',
        content: JSON.stringify({ text: message })
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (response.data.code === 0) {
      console.log(`✅ 消息已发送到飞书群聊 ${FEISHU_GROUP_ID} (${message.length} 字符)`);
      return true;
    }
    console.error('发送失败:', response.data.msg);
    return false;
  } catch (error) {
    console.error('发送失败:', error.response?.data || error.message);
    return false;
  }
}

// /webhook/ai-hotspot - AI Hotspot 专用端点
app.post('/webhook/ai-hotspot', async (req, res) => {
  try {
    const { title, text, items, summary, timestamp } = req.body;

    console.log(`[${new Date().toISOString()}] 📥 AI Hotspot webhook 收到请求`);
    console.log(`   items 数量: ${items ? items.length : 0}`);

    let messageText = text;

    // 如果是 items 格式
    if (!messageText && items && Array.isArray(items)) {
      console.log(`   使用 items + summary 格式`);

      // 按分类组织
      const categoryMap = new Map();
      items.forEach(item => {
        const cat = item.category || '其他';
        if (!categoryMap.has(cat)) {
          categoryMap.set(cat, []);
        }
        categoryMap.get(cat).push(item);
      });

      messageText = `🔥 AI 热点资讯\n`;
      messageText += `📅 ${timestamp || new Date().toLocaleString('zh-CN')}\n\n`;

      categoryMap.forEach((catItems, catName) => {
        messageText += `${catName}\n`;
        catItems.forEach((item, idx) => {
          messageText += `${idx + 1}. ${item.title}\n`;
          if (item.summary) {
            const summaryText = item.summary.length > 80 ? item.summary.substring(0, 80) + '...' : item.summary;
            messageText += `   ${summaryText}\n`;
          }
          if (item.url) messageText += `   🔗 ${item.url}\n`;
          messageText += '\n';
        });
      });

      if (summary) {
        messageText += `📊 ${summary}`;
      }
    }

    if (!messageText) {
      console.error(`   ❌ 缺少 text 或 items 字段`);
      return res.status(400).json({ error: 'Missing text or items field' });
    }

    console.log(`内容长度: ${messageText.length} 字符`);

    await sendToFeishu(messageText);

    res.status(202).json({ success: true, message: 'Message queued for delivery' });
  } catch (error) {
    console.error(`[${new Date().toISOString()}] ❌ AI Hotspot webhook 处理错误:`, error.message);
    res.status(500).json({ error: 'Internal server error', message: error.message });
  }
});

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 404 处理
app.use((req, res) => {
  res.status(404).json({ error: 'Not found', path: req.path });
});

// 启动服务器
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Webhook 服务器启动成功，监听端口 ${PORT}`);
  console.log(`   - /webhook/ai-hotspot: AI Hotspot 端点`);
  console.log(`📱 飞书群聊 ID: ${FEISHU_GROUP_ID}`);
});

// 优雅关闭
process.on('SIGTERM', () => {
  console.log('收到 SIGTERM 信号，正在关闭...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\n收到 SIGINT 信号，正在关闭...');
  process.exit(0);
});
