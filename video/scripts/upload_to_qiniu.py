#!/usr/bin/env python3
"""
七牛云视频上传脚本
使用: python upload_to_qiniu.py <视频文件路径> [远程文件名]
"""

import os
import sys
import json
import time

# 尝试导入qiniu，如果失败给出友好提示
try:
    from qiniu import Auth, put_file, etag
except ImportError:
    print("❌ 错误: 未安装七牛云SDK")
    print("请运行: pip3 install qiniu --break-system-packages")
    sys.exit(1)

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
    """上传视频到七牛云"""
    
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
