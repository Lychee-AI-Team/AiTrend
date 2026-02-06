# 七牛云视频上传详细操作指南

**文档版本**: v1.0  
**适用对象**: AiTrend项目  
**目标**: 将视频上传到七牛云并获取访问链接

---

## 第一步：注册七牛云账号

### 1.1 访问官网
- 网址: https://www.qiniu.com/
- 点击右上角「免费注册」

### 1.2 填写注册信息
- 手机号/邮箱注册
- 完成实名认证（个人认证即可）

### 1.3 免费额度
- 存储空间: **10GB免费**
- 下载流量: **10GB/月免费**
- 请求次数: **100万次/月免费**
- **AiTrend项目完全够用！**

---

## 第二步：创建存储空间（Bucket）

### 2.1 进入对象存储控制台
1. 登录七牛云控制台: https://portal.qiniu.com/
2. 左侧菜单点击「对象存储」
3. 点击「空间管理」

### 2.2 创建空间
点击「新建存储空间」按钮，填写信息：

| 配置项 | 建议值 | 说明 |
|--------|--------|------|
| **空间名称** | `aitrend-videos` | 自定义，全局唯一 |
| **存储区域** | `华东-浙江` | 选择离用户最近的区域 |
| **访问控制** | **公开** | 允许外部访问视频 |

### 2.3 绑定域名（可选但推荐）
1. 进入空间详情
2. 点击「域名管理」
3. 可以使用七牛提供的测试域名（30天有效期）
4. 或绑定自己的域名（如 `videos.aitrend.com`）

**测试域名格式**: `https://<bucket-name>.qiniudn.com/`

---

## 第三步：获取AccessKey和SecretKey

### 3.1 进入密钥管理
1. 右上角头像 → 「密钥管理」
2. 或访问: https://portal.qiniu.com/user/key

### 3.2 创建密钥
点击「创建密钥」按钮，会生成：
- **AccessKey**: 类似 `xxxxxxxxxxxxxxxxxxxx`
- **SecretKey**: 类似 `yyyyyyyyyyyyyyyyyyyy`

⚠️ **重要**: SecretKey只显示一次，立即保存！

### 3.3 保存到.env文件
```bash
# 编辑 AiTrend/.env 文件，添加：

# ============================================
# 七牛云配置
# 获取地址: https://portal.qiniu.com/user/key
# ============================================
QINIU_ACCESS_KEY=你的AccessKey
QINIU_SECRET_KEY=你的SecretKey
QINIU_BUCKET_NAME=aitrend-videos
QINIU_BUCKET_DOMAIN=你的测试域名或自定义域名
```

---

## 第四步：安装Python SDK

### 4.1 安装七牛云SDK
```bash
cd /home/ubuntu/.openclaw/workspace/AiTrend

# 安装七牛云Python SDK
pip3 install qiniu --break-system-packages

# 验证安装
python3 -c "import qiniu; print(qiniu.__version__)"
```

---

## 第五步：编写上传脚本

### 5.1 创建上传脚本
创建文件: `video/scripts/upload_to_qiniu.py`

```python
#!/usr/bin/env python3
"""
七牛云视频上传脚本
"""

import os
import sys
import json
from qiniu import Auth, put_file, etag

# 读取环境变量
env_path = '/home/ubuntu/.openclaw/workspace/AiTrend/.env'
env_vars = {}
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#') and not line.strip().startswith('TWITTER'):
                try:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
                except:
                    pass

# 七牛云配置
ACCESS_KEY = env_vars.get('QINIU_ACCESS_KEY', '')
SECRET_KEY = env_vars.get('QINIU_SECRET_KEY', '')
BUCKET_NAME = env_vars.get('QINIU_BUCKET_NAME', 'aitrend-videos')
BUCKET_DOMAIN = env_vars.get('QINIU_BUCKET_DOMAIN', '')

def upload_video(local_file_path, remote_filename=None):
    """
    上传视频到七牛云
    
    Args:
        local_file_path: 本地视频文件路径
        remote_filename: 远程文件名（可选，默认使用本地文件名）
    
    Returns:
        dict: 包含url、hash、key等信息
    """
    if not ACCESS_KEY or not SECRET_KEY:
        print("❌ 错误: 未配置七牛云AccessKey或SecretKey")
        print("请检查 .env 文件中的 QINIU_ACCESS_KEY 和 QINIU_SECRET_KEY")
        return None
    
    if not os.path.exists(local_file_path):
        print(f"❌ 错误: 文件不存在: {local_file_path}")
        return None
    
    # 构建鉴权对象
    q = Auth(ACCESS_KEY, SECRET_KEY)
    
    # 生成上传凭证（有效期1小时）
    token = q.upload_token(BUCKET_NAME, expires=3600)
    
    # 远程文件名
    if remote_filename is None:
        remote_filename = os.path.basename(local_file_path)
    
    # 添加时间戳避免重名
    import time
    timestamp = int(time.time())
    remote_key = f"videos/{timestamp}_{remote_filename}"
    
    print(f"📤 开始上传...")
    print(f"   本地文件: {local_file_path}")
    print(f"   远程路径: {remote_key}")
    
    try:
        # 上传文件
        ret, info = put_file(token, remote_key, local_file_path, version='v2')
        
        if info.status_code == 200:
            print(f"✅ 上传成功!")
            print(f"   Hash: {ret['hash']}")
            print(f"   Key: {ret['key']}")
            
            # 构建访问URL
            if BUCKET_DOMAIN:
                url = f"{BUCKET_DOMAIN}/{remote_key}"
            else:
                # 使用七牛默认域名
                url = f"https://{BUCKET_NAME}.qiniudn.com/{remote_key}"
            
            print(f"   URL: {url}")
            
            return {
                'success': True,
                'url': url,
                'hash': ret['hash'],
                'key': ret['key'],
                'size': os.path.getsize(local_file_path)
            }
        else:
            print(f"❌ 上传失败: {info}")
            return None
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return None


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python upload_to_qiniu.py <视频文件路径> [远程文件名]")
        print("示例: python upload_to_qiniu.py ../output/video.mp4")
        sys.exit(1)
    
    local_file = sys.argv[1]
    remote_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = upload_video(local_file, remote_name)
    
    if result:
        # 保存结果到JSON
        result_path = local_file + '.upload.json'
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 上传信息已保存: {result_path}")
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

---

## 第六步：测试上传

### 6.1 准备测试视频
```bash
# 创建一个测试文件（如果没有视频）
echo "测试视频内容" > /tmp/test_video.txt
```

### 6.2 运行上传脚本
```bash
cd /home/ubuntu/.openclaw/workspace/AiTrend/video/scripts

# 上传视频
python3 upload_to_qiniu.py ../output/video.mp4

# 或使用测试文件
python3 upload_to_qiniu.py /tmp/test_video.txt
```

### 6.3 预期输出
```
📤 开始上传...
   本地文件: ../output/video.mp4
   远程路径: videos/1707225600_video.mp4
✅ 上传成功!
   Hash: FrU-NS4fLDu5jTDp5e5rT7j5Q0zV
   Key: videos/1707225600_video.mp4
   URL: https://aitrend-videos.qiniudn.com/videos/1707225600_video.mp4

✅ 上传信息已保存: ../output/video.mp4.upload.json
```

### 6.4 验证访问
复制输出的URL，在浏览器中打开，应该能直接播放或下载视频。

---

## 第七步：集成到视频生成流程

### 7.1 创建自动化脚本
创建文件: `video/scripts/render_and_upload.sh`

```bash
#!/bin/bash
# 渲染视频并上传到七牛云

set -e  # 遇到错误立即退出

echo "🎬 AiTrend 视频渲染上传脚本"
echo "=============================="

# 配置
TEMPLATE="index-final.tsx"
COMPOSITION="DailyNewsFinal"
OUTPUT_DIR="../output"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="${OUTPUT_DIR}/aitrend_${TIMESTAMP}.mp4"

# 确保输出目录存在
mkdir -p ${OUTPUT_DIR}

echo ""
echo "📹 步骤1: 渲染视频"
echo "------------------------------"
cd /home/ubuntu/.openclaw/workspace/AiTrend/video/src

npx remotion render ${TEMPLATE} ${COMPOSITION} ${OUTPUT_FILE} \
  --browser-executable=$(find ~/.cache/ms-playwright -name "chrome" -type f | head -1) \
  --concurrency=2

if [ ! -f "${OUTPUT_FILE}" ]; then
    echo "❌ 视频渲染失败"
    exit 1
fi

echo "✅ 视频渲染完成: ${OUTPUT_FILE}"

# 获取文件大小
FILE_SIZE=$(du -h ${OUTPUT_FILE} | cut -f1)
echo "   文件大小: ${FILE_SIZE}"

echo ""
echo "☁️  步骤2: 上传到七牛云"
echo "------------------------------"
cd /home/ubuntu/.openclaw/workspace/AiTrend/video/scripts

python3 upload_to_qiniu.py ${OUTPUT_FILE}

echo ""
echo "🎉 全部完成!"
echo "=============================="
```

### 7.2 添加执行权限
```bash
chmod +x /home/ubuntu/.openclaw/workspace/AiTrend/video/scripts/render_and_upload.sh
```

### 7.3 使用方法
```bash
# 一键渲染并上传
./render_and_upload.sh
```

---

## 第八步：添加飞书通知（可选）

### 8.1 创建飞书通知脚本
创建文件: `video/scripts/notify_feishu.py`

```python
#!/usr/bin/env python3
"""
飞书通知脚本 - 视频上传完成通知
"""

import requests
import json
import sys
import os

def send_notification(video_url, video_title="AiTrend每日AI热点"):
    """发送飞书通知"""
    
    # 从环境变量读取Webhook URL
    webhook_url = os.getenv('FEISHU_WEBHOOK_URL', '')
    
    if not webhook_url:
        print("❌ 未配置飞书Webhook URL")
        return False
    
    # 构建消息卡片
    message = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🎬 AiTrend视频已生成"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**{video_title}**\n\n[点击观看视频]({video_url})"
                    }
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "观看视频"
                            },
                            "type": "primary",
                            "url": video_url
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(webhook_url, json=message, timeout=30)
        if response.status_code == 200:
            print("✅ 飞书通知发送成功")
            return True
        else:
            print(f"❌ 通知发送失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python notify_feishu.py <视频URL>")
        sys.exit(1)
    
    video_url = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else "AiTrend每日AI热点"
    
    send_notification(video_url, title)
```

### 8.2 完整自动化流程
修改 `render_and_upload.sh`:

```bash
# 在文件末尾添加:

echo ""
echo "📢 步骤3: 发送飞书通知"
echo "------------------------------"

# 读取上传结果
UPLOAD_INFO="${OUTPUT_FILE}.upload.json"
if [ -f "${UPLOAD_INFO}" ]; then
    VIDEO_URL=$(python3 -c "import json; print(json.load(open('${UPLOAD_INFO}'))['url'])")
    python3 notify_feishu.py "${VIDEO_URL}" "AiTrend ${TIMESTAMP}"
fi
```

---

## 常见问题

### Q1: 上传失败，提示"bad token"
- **原因**: AccessKey或SecretKey错误
- **解决**: 检查.env文件中的密钥是否正确

### Q2: 上传成功但无法访问
- **原因**: Bucket访问控制设置为「私有」
- **解决**: 在七牛云控制台将Bucket改为「公开」

### Q3: 域名过期
- **原因**: 七牛测试域名只有30天有效期
- **解决**: 绑定自己的域名（推荐）或定期更新

### Q4: 上传速度慢
- **解决**: 选择离服务器最近的存储区域（华东/华北/华南）

---

## 总结

**七牛云操作流程**:
1. ✅ 注册账号（免费）
2. ✅ 创建Bucket（aitrend-videos）
3. ✅ 获取密钥（AccessKey/SecretKey）
4. ✅ 安装SDK（pip install qiniu）
5. ✅ 编写脚本（upload_to_qiniu.py）
6. ✅ 测试上传
7. ✅ 集成到视频流程

**费用**: 基本免费（10GB存储+10GB流量）

---

**文档完成！按步骤操作即可！** 🦞
