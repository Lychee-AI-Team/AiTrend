// AI News Collector - 飞书 Action 版（带本地翻译）
// 收集多来源 AI 资讯并简单翻译

const https = require('https');

// 简易翻译字典（常见技术词汇）
const TRANSLATE_DICT = {
  // 通用
  'AI': 'AI',
  'artificial intelligence': '人工智能',
  'agent': '智能体',
  'agents': '智能体',
  'Agent': '智能体',
  
  // 模型相关
  'LLM': '大语言模型',
  'Large Language Model': '大语言模型',
  'model': '模型',
  'training': '训练',
  'fine-tuning': '微调',
  'inference': '推理',
  
  // 技术相关
  'RAG': 'RAG',
  'Retrieval-Augmented Generation': '检索增强生成',
  'API': 'API',
  'webhook': 'Webhook',
  'deployment': '部署',
  'pipeline': '流水线',
  
  // 开发相关
  'repository': '代码仓库',
  'Repository': '代码仓库',
  'workflow': '工作流',
  'automation': '自动化',
  'development': '开发',
  
  // 其他
  'trending': '热门',
  'GitHub Trending': 'GitHub 热门',
  'Chinese Models': '中国大模型',
  'open-source': '开源',
  'production': '生产环境',
  'framework': '框架',
  
  // 功能相关
  'chat': '聊天',
  'bot': '机器人',
  'assistant': '助手',
  'plugin': '插件',
  'extension': '扩展',
  'tool': '工具',
  'tools': '工具',
  
  // 应用相关
  'app': '应用',
  'application': '应用',
  'web': '网页',
  'mobile': '移动端',
  'desktop': '桌面端',
  'cross-platform': '跨平台',
  
  // 数据相关
  'data': '数据',
  'database': '数据库',
  'vector database': '向量数据库',
  'knowledge': '知识',
  'context': '上下文',
  'embedding': '嵌入',
  
  // 其他常见词
  'integration': '集成',
  'interface': '接口',
  'endpoint': '端点',
  'service': '服务',
  'platform': '平台',
  'architecture': '架构',
  'performance': '性能',
  'scalability': '可扩展性',
  'security': '安全',
  'authentication': '认证',
  'authorization': '授权'
};

// 简易翻译函数
function simpleTranslate(text) {
  if (!text) return text;
  var result = text;
  
  // 遍历字典进行替换
  for (var key in TRANSLATE_DICT) {
    var regex = new RegExp('\\b' + key + '\\b', 'gi');
    result = result.replace(regex, TRANSLATE_DICT[key]);
  }
  
  return result;
}

// 请求函数
function fetchData(url) {
  return new Promise(function(resolve, reject) {
    https.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/vnd.github.v3+json'
      }
    }, function(res) {
      var data = '';
      res.on('data', function(chunk) {
        data += chunk;
      });
      res.on('end', function() {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

// 主函数
async function main() {
  console.log('[1/2] 获取 GitHub 热门...');
  var trending = await fetchData(
    'https://api.github.com/search/repositories?q=topic:agent+language:python&sort=updated&order=desc&per_page=5'
  );
  
  console.log('   获取到 ' + trending.items.length + ' 个仓库');

  console.log('[2/2] 获取中国大模型...');
  var models = await fetchData(
    'https://api.github.com/search/repositories?q=DeepSeek+OR+Qwen+OR+ChatGLM&sort=updated&order=desc&per_page=5'
  );
  
  console.log('   获取到 ' + models.items.length + ' 个仓库');
  
  // 合并数据
  var allItems = trending.items.concat(models.items);
  
  // 生成消息
  console.log('\n🤖 AI 行业资讯 (' + new Date().toLocaleDateString('zh-CN') + ')\n');
  
  allItems.forEach(function(item, index) {
    var title = item.full_name;
    var desc = (item.description || '无描述');
    var source = item.source || 'GitHub';
    
    // 简易翻译
    desc = simpleTranslate(desc);
    source = simpleTranslate(source);
    
    console.log((index + 1) + '. ' + title);
    console.log('   ' + desc.substring(0, 80));
    console.log('   来源: ' + source);
    console.log('   链接: ' + item.html_url);
    console.log('');
  });
}

main().catch(function(error) {
  console.log('错误: ' + error.message);
});
