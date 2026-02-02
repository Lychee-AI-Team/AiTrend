#!/usr/bin/env python3
"""
发布模块测试脚本
测试 Discord 论坛发布模块
"""

import os
import sys
sys.path.insert(0, '.')

# 加载环境变量
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

print("="*60)
print("🧪 Discord 发布模块测试")
print("="*60)

# 导入发布模块
from publishers import create_publisher, list_publishers

print(f"\n📋 可用的发布模块:")
for name in list_publishers():
    print(f"  • {name}")

# 测试论坛发布模块
print("\n" + "="*60)
print("📤 测试论坛发布模块 (ForumPublisher)")
print("="*60)

# 从环境变量获取 Webhook URL
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

if not webhook_url:
    print("\n❌ 未配置 DISCORD_WEBHOOK_URL")
    print("请在 .env 文件中设置:")
    print("  DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...")
    sys.exit(1)

# 创建论坛发布模块实例
forum_config = {
    'webhook_url': webhook_url,
    'thread_name': '{name} – {source}',
    'username': 'AiTrend',
    'delay': 2,
    'max_length': 1900
}

forum_publisher = create_publisher('forum', forum_config)

if not forum_publisher:
    print("❌ 创建论坛发布模块失败")
    sys.exit(1)

print(f"\n✅ 论坛发布模块创建成功")
print(f"  配置:")
print(f"    - Webhook: {webhook_url[:50]}...")
print(f"    - 帖子标题模板: {forum_config['thread_name']}")
print(f"    - 用户名: {forum_config['username']}")

# 准备测试内容
print("\n" + "="*60)
print("📝 准备测试内容")
print("="*60)

test_contents = [
    {
        'name': 'nanobot',
        'content': '''nanobot 是一个超级轻量级的个人 AI 助手，整个项目才一千多星但已经能看出它的潜力。它是用 Python 写的，安装特别简单，一行 pip install nanobot-ai 就能搞定，而且只需要 Python 3.11 以上版本就能跑。

这个名字挺有意思的，带了个猫咪 emoji，感觉开发者是个有意思的人。它主打的就是"超轻量"，不像现在那些动不动就要几百 MB 甚至上 GB 的 AI 项目，nanobot 走的是精简路线，让你在自己的电脑上就能跑起一个个人 AI 助手，不用担心资源占用问题。

现在市面上很多 AI 工具要么太重，要么依赖各种云服务，nanobot 这种本地化、轻量化的思路其实挺实用的。如果你想拥有一个属于自己的、不依赖外部服务的 AI 助手，又不想折腾太复杂的配置，这个项目值得看一眼。''',
        'url': 'https://github.com/HKUDS/nanobot',
        'source': 'GitHub'
    },
    {
        'name': 'lingbot-world',
        'content': '''lingbot-world 是 Robbyant 团队刚开源的一个世界模型项目，GitHub 上已经拿到了近 2000 颗星。这个项目主打的是让 AI 真正"看懂"物理世界——不是简单地识别图片里的物体，而是理解物体之间的因果关系、运动规律，甚至能预测接下来会发生什么。

现在做世界模型的团队不少，但 lingbot-world 的亮点在于它是完全开源的。他们不仅把代码放出来了，训练好的模型也直接上传到了 HuggingFace，连论文 PDF 都能直接下载。这种开放程度在同类项目里还真不多见，对于想深入研究世界模型但又没有大厂资源的开发者来说，这简直是雪中送炭。

整个项目用 Python 写的，代码结构很干净，上手门槛不高。如果你对世界模型感兴趣，或者正在做机器人、自动驾驶这类需要空间推理的项目，这个项目值得花时间研究一下。''',
        'url': 'https://github.com/Robbyant/lingbot-world',
        'source': 'GitHub'
    }
]

print(f"  准备了 {len(test_contents)} 条测试内容")
for i, c in enumerate(test_contents, 1):
    print(f"    {i}. {c['name']} ({len(c['content'])} 字符)")

# 执行发布
print("\n" + "="*60)
print("🚀 开始发布到 Discord 论坛")
print("="*60)

published = forum_publisher.publish_batch(test_contents)

print("\n" + "="*60)
print(f"✅ 测试完成！成功发布 {published}/{len(test_contents)} 条")
print("="*60)

if published > 0:
    print("\n💡 提示:")
    print("  - 请到 Discord 论坛频道查看帖子")
    print("  - 每个项目会创建一个独立的论坛帖子")
    print("  - 帖子标题格式: 项目名称 – 来源")
