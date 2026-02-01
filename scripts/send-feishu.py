#!/usr/bin/env python3
# 发送消息到飞书

import json
import sys

def send_message(app_id, secret_key, receive_id, message):
    """发送消息到飞书"""
    import subprocess

    # 获取 token
    resp = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({'app_id': app_id, 'app_secret': secret_key})
    ], capture_output=True, text=True)

    data = json.loads(resp.stdout)
    if data.get('code') != 0:
        print(f"获取 token 失败: {data.get('msg')}")
        return False

    token = data.get('tenant_access_token')

    # 发送消息 - content 需要是 JSON 字符串（不是嵌套 JSON）
    # message 中的换行符会正确保留
    resp = subprocess.run([
        'curl', '-s', '-w', '\nHTTP_CODE:%{http_code}', '-X', 'POST',
        f'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({
            'receive_id': receive_id,
            'msg_type': 'text',
            'content': json.dumps({'text': message})  # 嵌套 JSON 需要转成字符串
        })
    ], capture_output=True, text=True)

    lines = resp.stdout.strip().split('\n')
    http_code = '0'
    body = resp.stdout
    for line in lines:
        if 'HTTP_CODE:' in line:
            http_code = line.split(':')[1]
            body = '\n'.join([l for l in lines if 'HTTP_CODE:' not in l])
            break

    try:
        data = json.loads(body) if body else {}
    except:
        data = {}

    if http_code == '200' or data.get('code') == 0:
        print("✅ 发送成功！")
        return True
    else:
        print(f"❌ 发送失败: {data.get('msg', '未知错误')}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("用法: send-feishu.py <app_id> <secret_key> <receive_id> <message>")
        sys.exit(1)

    app_id = sys.argv[1]
    secret_key = sys.argv[2]
    receive_id = sys.argv[3]
    message = sys.argv[4]

    send_message(app_id, secret_key, receive_id, message)
