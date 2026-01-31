// AI News Collector - 飞书 Action 版（带本地翻译）

const https = require('https');

const TRANSLATE_DICT = {
  'AI': '人工智能',
  'artificial intelligence': '人工智能',
  'agent': '智能体',
  'agents': '智能体',
  'Agent': '智能体',
  'LLM': '大语言模型',
  'Large Language Model': '大语言模型',
  'model': '模型',
  'training': '训练',
  'fine-tuning': '微调',
  'inference': '推理',
  'RAG': 'RAG',
  'Retrieval-Augmented Generation': '检索增强生成',
  'API': 'API',
  'webhook': 'Webhook',
  'deployment': '部署',
  'pipeline': '流水线',
  'repository': '代码仓库',
  'Repository': '代码仓库',
  'workflow': '工作流',
  'automation': '自动化',
  'development': '开发',
  'trending': '热门',
  'GitHub Trending': 'GitHub 热门',
  'Chinese Models': '中国大模型',
  'open-source': '开源',
  'production': '生产环境',
  'framework': '框架',
  'chat': '聊天',
  'bot': '机器人',
  'assistant': '助手',
  'plugin': '插件',
  'extension': '扩展',
  'tool': '工具',
  'tools': '工具',
  'app': '应用',
  'application': '应用',
  'web': '网页',
  'mobile': '移动端',
  'desktop': '桌面端',
  'cross-platform': '跨平台',
  'data': '数据',
  'database': '数据库',
  'vector database': '向量数据库',
  'knowledge': '知识',
  'context': '上下文',
  'embedding': '嵌入',
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

function simpleTranslate(text) {
  if (!text) return text;
  var result = text;
  for (var key in TRANSLATE_DICT) {
    var regex = new RegExp('\\b' + key + '\\b', 'gi');
    result = result.replace(regex, TRANSLATE_DICT[key]);
  }
  return result;
}

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

async function main() {
  var trending = await fetchData(
    'https://api.github.com/search/repositories?q=topic:agent+language:python&sort=updated&order=desc&per_page=5'
  );
  
  var models = await fetchData(
    'https://api.github.com/search/repositories?q=DeepSeek+OR+Qwen+OR+ChatGLM&sort=updated&order=desc&per_page=5'
  );
  
  var allItems = trending.items.concat(models.items);
  
  var message = '🤖 AI 行业资讯 (' + new Date().toLocaleDateString('zh-CN') + ')\n\n';
  
  allItems.forEach(function(item, index) {
    var desc = (item.description || '无描述');
    desc = simpleTranslate(desc);
    
    message += (index + 1) + '. ' + item.full_name + '\n';
    message += '   ' + desc.substring(0, 80) + '\n';
    message += '   链接: ' + item.html_url + '\n\n';
  });
  
  console.log(message);
}

main().catch(function(error) {
  console.log('错误: ' + error.message);
});
