#!/usr/bin/env python3
# 发送消息到飞书

import json
import os
import sys
import subprocess

def get_token(app_id, secret_key):
    """获取飞书访问令牌"""
    resp = subprocess.run([
        'curl', '-s', '-X', 'POST',
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({'app_id': app_id, 'app_secret': secret_key})
    ], capture_output=True, text=True)

    data = json.loads(resp.stdout)
    if data.get('code') != 0:
        print(f"获取 token 失败: {data.get('msg')}")
        return None
    return data.get('tenant_access_token')

def send_message(token, receive_id, message):
    """发送消息"""
    content = json.dumps({'text': message})
    resp = subprocess.run([
        'curl', '-s', '-w', '\nHTTP_CODE:%{http_code}', '-X', 'POST',
        'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id',
        '-H', f'Authorization: Bearer {token}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps({
            'receive_id': receive_id,
            'msg_type': 'text',
            'content': content
        })
    ], capture_output=True, text=True)

    lines = resp.stdout.strip().split('\n')
    http_code = lines[-1].split(':')[1] if 'HTTP_CODE:' in lines[-1] else '0'
    body = '\n'.join(lines[:-1]) if 'HTTP_CODE:' in lines[-1] else resp.stdout

    data = json.loads(body) if body else {}
    if http_code == '200' or data.get('code') == 0:
        print("✅ 发送成功！")
        return True
    else:
        print(f"❌ 发送失败: {data.get('msg', '未知错误')}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("用法: send-feishu.py <app_id> <secret_key> <receive_id> <message>")
        sys.exit(1)

    app_id = sys.argv[1]
    secret_key = sys.argv[2]
    receive_id = sys.argv[3]
    message = sys.argv[4]

    token = get_token(app_id, secret_key)
    if token:
        send_message(token, receive_id, message)
