#!/usr/bin/env node
// Webhook Server - 支持 AI Hotspot 端点
import express from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';
import { writeFileSync, unlinkSync } from 'fs';

const execAsync = promisify(exec);
const app = express();
const PORT = process.env.PORT || 3000;

// 飞书群聊 ID
const FEISHU_GROUP_ID = 'oc_9a3c218325fd2cfa42f2a8f6fe03ac02';

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

// 通用消息发送函数
async function sendToFeishu(title, text) {
  try {
    // 移除 markdown 格式（**粗体**），保留 emoji
    let message = text
      .replace(/\*\*(.*?)\*\*/g, '$1')  // 移除 **粗体**
      .replace(/`(.*?)`/g, '$1')        // 移除 `行内代码`
      .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1') // 移除 [链接](url)

    if (title) {
      title = title.replace(/\*\*(.*?)\*\*/g, '$1')
      message = `${title}\n\n${message}`
    }

    const tempFile = `/tmp/feishu-msg-${Date.now()}.txt`;
    writeFileSync(tempFile, message, 'utf8');

    const command = `MESSAGE=$(cat ${tempFile}) && clawdbot message send --channel feishu --target '${FEISHU_GROUP_ID}' --message "$MESSAGE"`;

    const { stdout, stderr } = await execAsync(command, { timeout: 30000 });

    try {
      unlinkSync(tempFile);
    } catch (e) {}

    if (stderr && !stderr.includes('NO_REPLY')) {
      console.error(`发送警告: ${stderr}`);
    }
    console.log(`✅ 消息已发送到飞书群聊 ${FEISHU_GROUP_ID} (${message.length} 字符)`);
    return true;
  } catch (execError) {
    console.error(`❌ clawdbot message 执行失败:`, execError.message);
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

    await sendToFeishu(title, messageText);

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
