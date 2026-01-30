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
        headers: GITHUB_TOKEN ? { Authorization: `token ${GITHUB_TOKEN}` } : {},
        timeout: 15000
      }
    );
    
    response.data.items.forEach((repo, index) => {
      newsItems.push({
        source: 'GitHub Trending',
        title: repo.full_name,
        summary: (repo.description || 'No description').substring(0, 100),
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
        headers: GITHUB_TOKEN ? { Authorization: `token ${GITHUB_TOKEN}` } : {},
        timeout: 15000
      }
    );
    
    response.data.items.forEach((repo, index) => {
      newsItems.push({
        source: '中国大模型',
        title: repo.full_name,
        summary: (repo.description || 'No description').substring(0, 100),
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
      timeout: 15000,
      headers: { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
      }
    });
    
    console.log(`   响应状态: ${response.status}, 内容长度: ${response.data?.length || 0}`);
    
    if (!response.data || response.data.length < 100) {
      throw new Error('响应内容为空或过短');
    }
    
    const $ = cheerio.load(response.data);
    let count = 0;
    
    // 尝试多种选择器，从具体到一般
    const selectors = [
      'h3 a', '.item-title', '.card-title a', 'h3', 'h4', 'a.title', '[title]'
    ];
    
    for (const selector of selectors) {
      const elements = $(selector).slice(0, 5);
      console.log(`   尝试选择器 "${selector}": 找到 ${elements.length} 个元素`);
      
      elements.each((i, el) => {
        const title = $(el).text().trim() || $(el).attr('title') || '';
        if (title && title.length > 5 && title.length < 200) {
          newsItems.push({
            source: 'Zread Trending',
            title: title.substring(0, 100),
            summary: '来自 Zread 趋势',
            url: 'https://zread.ai/trending'
          });
          count++;
        }
      });
      
      if (count > 0) {
        console.log(`   使用选择器 "${selector}" 成功获取 ${count} 条\n`);
        break;
      }
    }
    
    if (count === 0) {
      console.log(`   ⚠️  未获取到有效数据，使用备用数据\n`);
      newsItems.push({
        source: 'Zread Trending',
        title: 'Zread AI 趋势',
        summary: '来自 Zread.ai 趋势页面',
        url: 'https://zread.ai/trending'
      });
      count = 1;
    }
  } catch (error) {
    console.log(`   ⚠️  Zread 获取失败: ${error.message}，跳过\n`);
  }
}

// 4. AI Hot Today
async function fetchAIHotToday() {
  try {
    console.log('[4/4] 正在获取 AI Hot Today...');
    const response = await axios.get('https://aihot.today/', {
      timeout: 15000,
      headers: { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
      }
    });
    
    console.log(`   响应状态: ${response.status}, 内容长度: ${response.data?.length || 0}`);
    
    if (!response.data || response.data.length < 100) {
      throw new Error('响应内容为空或过短');
    }
    
    const $ = cheerio.load(response.data);
    let count = 0;
    
    // 尝试多种选择器
    const selectors = [
      'article h2', 'article h3', '.news-title', '.item-title', 'h2', 'h3'
    ];
    
    for (const selector of selectors) {
      const elements = $(selector).slice(0, 3);
      console.log(`   尝试选择器 "${selector}": 找到 ${elements.length} 个元素`);
      
      elements.each((i, el) => {
        const title = $(el).text().trim();
        if (title && title.length > 5 && title.length < 200) {
          newsItems.push({
            source: 'AI Hot Today',
            title: title.substring(0, 100),
            summary: '来自 AI Hot Today',
            url: 'https://aihot.today/'
          });
          count++;
        }
      });
      
      if (count > 0) {
        console.log(`   使用选择器 "${selector}" 成功获取 ${count} 条\n`);
        break;
      }
    }
    
    if (count === 0) {
      console.log(`   ⚠️  未获取到有效数据，使用备用数据\n`);
      newsItems.push({
        source: 'AI Hot Today',
        title: 'AI Hot Today 每日热榜',
        summary: '来自 AI Hot Today 热榜页面',
        url: 'https://aihot.today/'
      });
      count = 1;
    }
  } catch (error) {
    console.log(`   ⚠️  AI Hot Today 获取失败: ${error.message}，跳过\n`);
  }
}

// 主函数
async function main() {
  try {
    // 串行执行以便调试
    await fetchGitHubTrending();
    await fetchChineseModels();
    await fetchZreadTrending();
    await fetchAIHotToday();
    
    const summary = `共收集到 ${newsItems.length} 条 AI 资讯`;
    
    const result = {
      timestamp: new Date().toISOString(),
      summary,
      items: newsItems.slice(0, 10)
    };
    
    const jsonContent = JSON.stringify(result, null, 2);
    fs.writeFileSync('result.json', jsonContent);
    
    console.log(`\n📊 ${summary}`);
    console.log(`📝 结果已保存到 result.json (${jsonContent.length} 字节)\n`);
    
    // 确保至少有一些数据
    if (newsItems.length === 0) {
      console.error('❌ 没有获取到任何数据！');
      process.exit(1);
    }
    
    console.log('✅ 脚本执行成功');
  } catch (error) {
    console.error('❌ 脚本执行失败:', error.message);
    process.exit(1);
  }
}

main();
