// AI News Collector Script
// 收集多来源 AI 资讯并发送到 Webhook

import axios from 'axios';
import * as cheerio from 'cheerio';
import fs from 'fs';

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;

console.log('🔍 开始收集 AI 资讯...\n');

const newsItems = [];

// 1. GitHub Trending - AI Agent 相关
async function fetchGitHubTrending() {
  try {
    console.log('[1/4] 正在获取 GitHub Trending (AI Agent)...');
    const response = await axios.get(
      'https://api.github.com/search/repositories?q=topic:agent+language:python&sort=updated&order=desc&per_page=5',
      {
        headers: GITHUB_TOKEN ? { Authorization: `token ${GITHUB_TOKEN}` } : {}
      }
    );
    
    response.data.items.forEach((repo, index) => {
      newsItems.push({
        source: 'GitHub Trending',
        title: repo.full_name,
        summary: repo.description || 'No description',
        url: repo.html_url,
        stars: repo.stargazers_count
      });
    });
    
    console.log(`   ✅ 获取到 ${response.data.items.length} 个仓库\n`);
  } catch (error) {
    console.log(`   ❌ 获取失败: ${error.message}\n`);
  }
}

// 2. 中国大模型相关
async function fetchChineseModels() {
  try {
    console.log('[2/4] 正在获取中国大模型相关...');
    const response = await axios.get(
      'https://api.github.com/search/repositories?q=DeepSeek+OR+Qwen+OR+ChatGLM&sort=updated&order=desc&per_page=5',
      {
        headers: GITHUB_TOKEN ? { Authorization: `token ${GITHUB_TOKEN}` } : {}
      }
    );
    
    response.data.items.forEach((repo, index) => {
      newsItems.push({
        source: '中国大模型',
        title: repo.full_name,
        summary: repo.description || 'No description',
        url: repo.html_url,
        stars: repo.stargazers_count
      });
    });
    
    console.log(`   ✅ 获取到 ${response.data.items.length} 个仓库\n`);
  } catch (error) {
    console.log(`   ❌ 获取失败: ${error.message}\n`);
  }
}

// 3. Zread Trending
async function fetchZreadTrending() {
  try {
    console.log('[3/4] 正在获取 Zread Trending...');
    const response = await axios.get('https://zread.ai/trending', {
      timeout: 10000
    });
    
    const $ = cheerio.load(response.data);
    let count = 0;
    
    $('h3, h4').slice(0, 5).each((i, el) => {
      const title = $(el).text().trim();
      if (title && title.length > 10) {
        newsItems.push({
          source: 'Zread Trending',
          title: title,
          summary: '来自 Zread 趋势',
          url: 'https://zread.ai/trending'
        });
        count++;
      }
    });
    
    console.log(`   ✅ 获取到 ${count} 条资讯\n`);
  } catch (error) {
    console.log(`   ⚠️  Zread 获取失败\n`);
  }
}

// 4. AI Hot Today
async function fetchAIHotToday() {
  try {
    console.log('[4/4] 正在获取 AI Hot Today...');
    const response = await axios.get('https://aihot.today/', {
      timeout: 10000
    });
    
    const $ = cheerio.load(response.data);
    let count = 0;
    
    $('h2, h3, article').slice(0, 3).each((i, el) => {
      const title = $(el).find('h2, h3').first().text().trim() || $(el).text().trim();
      const link = $(el).find('a').first().attr('href');
      if (title && title.length > 5) {
        newsItems.push({
          source: 'AI Hot Today',
          title: title.substring(0, 100),
          summary: '来自 AI Hot Today',
          url: link || 'https://aihot.today/'
        });
        count++;
      }
    });
    
    console.log(`   ✅ 获取到 ${count} 条资讯\n`);
  } catch (error) {
    console.log(`   ⚠️  AI Hot Today 获取失败\n`);
  }
}

// 主函数
async function main() {
  await Promise.all([
    fetchGitHubTrending(),
    fetchChineseModels(),
    fetchZreadTrending(),
    fetchAIHotToday()
  ]);
  
  const summary = `共收集到 ${newsItems.length} 条 AI 资讯`;
  
  const result = {
    timestamp: new Date().toISOString(),
    summary,
    items: newsItems.slice(0, 10)
  };
  
  fs.writeFileSync('result.json', JSON.stringify(result, null, 2));
  
  console.log(`\n📊 ${summary}`);
  console.log(`📝 结果已保存到 result.json\n`);
}

main().catch(console.error);
