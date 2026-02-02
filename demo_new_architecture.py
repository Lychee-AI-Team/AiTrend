#!/usr/bin/env python3
"""
AiTrend 新架构演示 - 基于真实数据抓取
"""

import sys
sys.path.insert(0, '.')

import os
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

print("="*60)
print("🎯 AiTrend 新架构演示")
print("基于真实数据抓取，不再凭空猜测")
print("="*60)

# 1. 获取数据源URL
print("\n📡 步骤1: 从数据源获取项目URL...")

from src.sources import create_sources
from src.core.config_loader import load_config
from src.core.webhook_sender import DiscordWebhookSender

config = load_config()
sources = create_sources(config.get("sources", {}))

# 收集项目URL
projects = []
for source in sources:
    if source.is_enabled() and len(projects) < 5:  # 只演示5个
        try:
            articles = source.fetch()
            for article in articles[:2]:  # 每个源取2个
                projects.append({
                    'title': article.title,
                    'url': article.url,
                    'source': source.name
                })
                if len(projects) >= 5:
                    break
        except Exception as e:
            print(f"  ✗ {source.name}: {e}")

print(f"  ✅ 获取到 {len(projects)} 个项目URL")
for p in projects:
    print(f"    • [{p['source']}] {p['title'][:50]}...")

# 2. 抓取真实数据
print("\n🔍 步骤2: 抓取项目真实数据...")

from src.scrapers import get_scraper

scraped_results = []
for project in projects:
    url = project['url']
    scraper = get_scraper(url)
    
    if scraper:
        print(f"\n  抓取: {project['title'][:40]}...")
        try:
            data = scraper.scrape(url)
            data['original_title'] = project['title']
            scraped_results.append(data)
            
            # 显示抓取到的数据
            print(f"    ✅ 成功")
            print(f"       名称: {data.get('name', 'N/A')}")
            if data.get('description'):
                print(f"       描述: {data['description'][:80]}...")
            if data.get('features'):
                print(f"       功能: {len(data['features'])} 个")
            if data.get('reviews'):
                print(f"       评论: {len(data['reviews'])} 条")
        except Exception as e:
            print(f"    ✗ 抓取失败: {e}")
    else:
        print(f"\n  跳过: {project['title'][:40]}... (无合适抓取器)")

print(f"\n  ✅ 成功抓取 {len(scraped_results)} 个项目")

# 3. 基于真实数据生成内容
print("\n📝 步骤3: 基于真实数据生成内容...")

from src.real_content_generator import generate_from_real_data, has_sufficient_data

contents = []
for data in scraped_results:
    print(f"\n  生成: {data.get('name', 'Unknown')}")
    
    # 检查数据是否充足
    if has_sufficient_data(data):
        content = generate_from_real_data(data)
        contents.append({
            'name': data.get('name', ''),
            'content': content,
            'source': data.get('source', '')
        })
        print(f"    ✅ 数据充足，生成详细内容 ({len(content)} 字符)")
        # 预览前100字
        preview = content[:100].replace('\n', ' ')
        print(f"       预览: {preview}...")
    else:
        print(f"    ⚠️ 数据不足，生成简短说明")
        content = f"{data.get('name', '')} 的详细信息还在收集中。\n\n{data.get('url', '')}"
        contents.append({
            'name': data.get('name', ''),
            'content': content,
            'source': data.get('source', '')
        })

# 4. 发布到Discord
print(f"\n📤 步骤4: 发布到Discord...")

webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
if not webhook_url:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('DISCORD_WEBHOOK_URL='):
                webhook_url = line.strip().split('=', 1)[1]
                break

sender = DiscordWebhookSender(webhook_url)

import time
for i, c in enumerate(contents, 1):
    print(f"  发布 {i}/{len(contents)}: {c['name'][:35]}...")
    sender.send_to_forum(
        f"{c['name']} – {c['source']}真实数据",
        c['content']
    )
    time.sleep(2)

print(f"\n✅ 发布完成！共 {len(contents)} 条基于真实数据的内容")

print("\n" + "="*60)
print("🎉 新架构演示完成")
print("="*60)
print("\n改进点:")
print("  ✓ 基于真实README生成内容")
print("  ✓ 基于真实用户评论生成内容")
print("  ✓ 基于真实GitHub数据生成内容")
print("  ✓ 数据不足时诚实说明，不编造")
print("  ✓ 每句话都有真实数据来源支撑")
