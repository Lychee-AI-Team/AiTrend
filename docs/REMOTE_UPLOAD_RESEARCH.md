# 视频导出并发送到远程方案调研

**调研时间**: 2026-02-06  
**调研目标**: 找到将视频导出并发送到远程的最佳方案

---

## 📋 当前现状

### 视频导出（已完成）
```bash
# 本地导出命令
npx remotion render index-final.tsx DailyNewsFinal output.mp4
```
- 视频已生成到本地 `video/output/` 目录
- 需要发送到远程服务器/平台

---

## 方案一：上传到云存储（推荐）

### 1.1 AWS S3 / 阿里云OSS

**优势**:
- ✅ 稳定可靠，全球CDN加速
- ✅ 支持大文件上传
- ✅ 可直接生成URL分享
- ✅ 成本低（按量付费）

**实现方式**:
```python
import boto3

def upload_to_s3(local_file, bucket_name, s3_key):
    s3 = boto3.client('s3')
    s3.upload_file(local_file, bucket_name, s3_key)
    url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
    return url
```

**适用场景**:
- 需要长期存储视频
- 需要分享给他人下载
- 作为视频分发源

---

### 1.2 腾讯云COS / 七牛云

**优势**:
- ✅ 国内访问速度快
- ✅ 免费额度较高
- ✅ API简单易用

**七牛云免费额度**:
- 存储: 10GB免费
- 流量: 10GB/月免费
- 请求: 100万次/月免费

**适用场景**:
- 国内用户访问
- 预算有限的项目

---

## 方案二：上传到视频平台

### 2.1 YouTube Data API

**优势**:
- ✅ 全球最大视频平台
- ✅ 免费上传
- ✅ 自动转码多清晰度
- ✅ SEO友好

**劣势**:
- ❌ 需要Google账号
- ❌ API配额限制
- ❌ 国内访问受限

**实现方式**:
```python
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_youtube(video_file, title, description):
    youtube = build('youtube', 'v3', credentials=credentials)
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['AI', 'Tech'],
            'categoryId': '28'  # Tech
        },
        'status': {
            'privacyStatus': 'public'
        }
    }
    
    media = MediaFileUpload(video_file, mimetype='video/mp4')
    response = youtube.videos().insert(part='snippet,status', body=body, media_body=media).execute()
    return response['id']
```

---

### 2.2 Bilibili API

**优势**:
- ✅ 国内最大视频平台
- ✅ 开发者友好
- ✅ 国内用户基数大

**API文档**: https://openhome.bilibili.com/

---

### 2.3 TikTok / Douyin API

**优势**:
- ✅ 短视频平台，适合竖屏内容
- ✅ 算法推荐流量大

---

## 方案三：发送到消息平台

### 3.1 Discord Bot

**优势**:
- ✅ 实时推送
- ✅ 支持大文件（25MB免费，Boost后500MB）
- ✅ 已集成到当前系统

**实现方式**:
```python
import discord

async def send_video_to_discord(channel_id, video_path):
    channel = bot.get_channel(channel_id)
    with open(video_path, 'rb') as f:
        await channel.send(file=discord.File(f, 'video.mp4'))
```

**适用场景**:
- 团队内部通知
- 社区自动推送

---

### 3.2 Telegram Bot

**优势**:
- ✅ 支持2GB文件
- ✅ 速度快
- ✅ 免费

**实现方式**:
```python
import requests

def send_video_to_telegram(bot_token, chat_id, video_path):
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    with open(video_path, 'rb') as f:
        response = requests.post(url, files={'video': f}, data={'chat_id': chat_id})
    return response.json()
```

---

### 3.3 企业微信/钉钉/飞书

**优势**:
- ✅ 企业级应用
- ✅ 支持机器人推送
- ✅ 国内使用广泛

**飞书Bot**:
```python
def send_video_to_feishu(webhook_url, video_path):
    with open(video_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(webhook_url, files=files)
    return response.json()
```

---

## 方案四：SCP/SFTP传输到远程服务器

### 4.1 SCP命令

**优势**:
- ✅ 简单直接
- ✅ 无需第三方服务
- ✅ 安全加密

**实现方式**:
```python
import paramiko

def scp_to_remote(local_file, remote_host, remote_path, username, key_file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(remote_host, username=username, key_filename=key_file)
    
    sftp = ssh.open_sftp()
    sftp.put(local_file, remote_path)
    sftp.close()
    ssh.close()
```

**适用场景**:
- 自有服务器
- 内部系统传输

---

### 4.2 Rsync

**优势**:
- ✅ 增量传输，支持断点续传
- ✅ 高效

```bash
rsync -avz --progress video.mp4 user@remote:/path/
```

---

## 方案五：HTTP API上传

### 5.1 自建上传API

**实现方式**:
```python
import requests

def upload_to_custom_api(video_path, api_url, api_key):
    with open(video_path, 'rb') as f:
        headers = {'Authorization': f'Bearer {api_key}'}
        files = {'video': f}
        response = requests.post(api_url, headers=headers, files=files)
    return response.json()
```

**适用场景**:
- 自有后端系统
- 需要自定义处理逻辑

---

## 方案六：Webhook回调

**流程**:
```
视频生成完成
    ↓
调用Webhook URL
    ↓
远程服务器接收并处理
```

**实现方式**:
```python
def notify_webhook(video_path, webhook_url):
    with open(video_path, 'rb') as f:
        response = requests.post(webhook_url, files={'video': f})
    return response.status_code == 200
```

---

## 📊 方案对比

| 方案 | 难度 | 成本 | 速度 | 容量 | 推荐 |
|------|------|------|------|------|------|
| **阿里云OSS** | 低 | 低 | 快 | 大 | ⭐⭐⭐⭐⭐ |
| **七牛云** | 低 | 免费 | 快 | 中 | ⭐⭐⭐⭐ |
| **YouTube** | 中 | 免费 | 慢 | 无限 | ⭐⭐⭐ |
| **Discord** | 低 | 免费 | 快 | 25MB | ⭐⭐⭐ |
| **Telegram** | 低 | 免费 | 快 | 2GB | ⭐⭐⭐⭐ |
| **SCP/SSH** | 中 | 免费 | 中 | 大 | ⭐⭐⭐ |
| **飞书Webhook** | 低 | 免费 | 快 | 中 | ⭐⭐⭐⭐ |

---

## 🎯 推荐方案

### 首选：阿里云OSS + 飞书通知

**理由**:
1. **OSS存储** - 国内访问快，成本低
2. **飞书通知** - 实时推送，团队可见
3. **自动生成URL** - 方便分享

**流程**:
```
视频渲染完成
    ↓
上传到阿里云OSS
    ↓
生成访问URL
    ↓
发送飞书通知（带链接）
```

**预估成本**:
- 存储: 0.12元/GB/月
- 流量: 0.24元/GB
- 每月成本: < 1元

---

### 备选：七牛云 + Discord

**理由**:
- 七牛云免费额度充足
- Discord已有集成

---

## 💡 实施建议

### 步骤1: 选择云存储
- 推荐阿里云OSS或七牛云
- 创建Bucket/空间
- 获取AccessKey

### 步骤2: 编写上传脚本
```python
# upload_video.py
import oss2

def upload_video(video_path):
    auth = oss2.Auth('access_key_id', 'access_key_secret')
    bucket = oss2.Bucket(auth, 'oss-cn-hangzhou.aliyuncs.com', 'aitrend-videos')
    
    bucket.put_object_from_file('videos/latest.mp4', video_path)
    url = bucket.sign_url('GET', 'videos/latest.mp4', 3600*24*7)  # 7天有效期
    return url
```

### 步骤3: 集成到视频生成流程
```bash
# render_and_upload.sh
npx remotion render index-final.tsx DailyNewsFinal output.mp4
python upload_video.py output.mp4
python notify_feishu.py "视频已生成: $URL"
```

---

## 📁 相关文件

- `scripts/upload_to_oss.py` - 上传脚本
- `scripts/notify_feishu.py` - 通知脚本
- `.env` - 存储AccessKey

---

**调研完成！推荐阿里云OSS + 飞书通知方案！** 🦞
