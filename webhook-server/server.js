#!/usr/bin/env node
// Webhook Server - 支持多种端点
import express from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';
import { writeFileSync, unlinkSync, readFileSync } from 'fs';

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
    // 创建临时文件避免 shell 转义问题
    const message = title ? `${title}\n\n${text}` : text;
    const tempFile = `/tmp/feishu-msg-${Date.now()}.txt`;
    writeFileSync(tempFile, message, 'utf8');

    // 使用环境变量方式传递消息
    const command = `MESSAGE=$(cat ${tempFile}) && clawdbot message send --channel feishu --target '${FEISHU_GROUP_ID}' --message "$MESSAGE"`;

    const { stdout, stderr } = await execAsync(command, { timeout: 30000 });

    // 删除临时文件
    try {
      unlinkSync(tempFile);
    } catch (e) {
      // 忽略删除失败
    }

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
    const { title, text, items, summary } = req.body;

    console.log(`[${new Date().toISOString()}] 📥 AI Hotspot webhook: 收到请求`);
    console.log(`   Body keys: ${Object.keys(req.body).join(', ')}`);
    console.log(`   Body:`, JSON.stringify(req.body, null, 2).substring(0, 500));

    let messageText = text;

    // 如果是 AI Hotspot 格式（items + summary）
    if (!messageText && items && summary) {
      console.log(`   使用 items + summary 格式，items 数量: ${items.length}`);
      messageText = `📊 **${summary}**\n\n`;
      items.forEach((item, index) => {
        messageText += `${index + 1}. **${item.title}**\n`;
        if (item.summary) messageText += `   ${item.summary.substring(0, 100)}\n`;
        if (item.url) messageText += `   🔗 ${item.url}\n`;
        if (item.source) messageText += `   来源: ${item.source}\n`;
        messageText += '\n';
      });
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

// /webhook/ai-news - AI News 端点
app.post('/webhook/ai-news', async (req, res) => {
  try {
    const { title, items, summary } = req.body;

    console.log(`[${new Date().toISOString()}] 📰 AI News webhook: 收到请求`);

    let messageText = title ? `📰 **${title}**\n\n` : '';
    messageText += `📊 **${summary || 'AI 行业资讯'}**\n\n`;

    if (items && Array.isArray(items)) {
      items.forEach((item, index) => {
        messageText += `${index + 1}. **${item.title}**\n`;
        if (item.summary || item.description) {
          messageText += `   ${item.summary || item.description}\n`;
        }
        if (item.url) messageText += `   🔗 ${item.url}\n`;
        if (item.source) messageText += `   来源: ${item.source}\n`;
        messageText += '\n';
      });
    } else if (typeof req.body === 'string') {
      messageText += req.body;
    }

    console.log(`📤 发送消息内容: ${messageText.substring(0, 200)}...`);

    await sendToFeishu('', messageText);

    res.status(202).json({ success: true });
  } catch (error) {
    console.error(`[${new Date().toISOString()}] ❌ AI News webhook 处理错误:`, error.message);
    res.status(500).json({ error: 'Internal server error', message: error.message });
  }
});

// /webhook/github - GitHub Issue 端点
app.post('/webhook/github', async (req, res) => {
  try {
    console.log(`[${new Date().toISOString()}] 📥 GitHub webhook: ${req.body.action || 'unknown'}`);
    const payload = req.body;

    let messageText = '🔔 **GitHub 事件**\n\n';
    if (payload.action) messageText += `操作: ${payload.action}\n`;
    if (payload.repository) messageText += `仓库: ${payload.repository.full_name}\n`;
    if (payload.sender) messageText += `触发者: ${payload.sender.login}\n`;
    if (payload.issue) {
      messageText += `\n问题: ${payload.issue.title}\n`;
      messageText += `链接: ${payload.issue.html_url}\n`;
    }

    await sendToFeishu('', messageText);

    res.status(202).json({ success: true });
  } catch (error) {
    console.error(`[${new Date().toISOString()}] ❌ GitHub webhook 处理错误:`, error.message);
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
  console.log(`   - /webhook/ai-news: AI News 端点`);
  console.log(`   - /webhook/github: GitHub Issue 端点`);
  console.log(`📱 飞书群聊 ID: ${FEISHU_GROUP_ID}`);
  console.log(`💡 健康检查: http://0.0.0.0:${PORT}/health`);
  console.log('---');
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
