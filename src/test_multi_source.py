#!/usr/bin/env python3
"""
AiTrend 多源覆盖测试系统
确保内容来源分布均衡、质量达标
"""

import json
import os
import sys
from datetime import datetime
from collections import Counter
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEST_LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'memory', 'test_log.json')

class MultiSourceTester:
    """多源覆盖测试器"""
    
    def __init__(self):
        self.requirements = {
            'min_sources': 3,           # 至少3个不同源
            'max_source_percentage': 0.4,  # 单源最多40%
            'must_include_realtime': True,   # 必须有实时源
            'must_include_deep': True,       # 必须有深度源
        }
        self.realtime_sources = ['twitter', 'producthunt']
        self.deep_sources = ['hackernews', 'reddit']
    
    def test_source_distribution(self, articles: List[Dict]) -> Dict:
        """测试来源分布是否均衡"""
        results = {
            'passed': True,
            'score': 0,
            'issues': [],
            'details': {}
        }
        
        # 统计来源
        sources = [a.get('source', 'unknown') for a in articles]
        source_counts = Counter(sources)
        total = len(articles)
        
        results['details']['source_distribution'] = dict(source_counts)
        results['details']['total_articles'] = total
        results['details']['unique_sources'] = len(source_counts)
        
        # 测试1：至少3个不同源
        if len(source_counts) < self.requirements['min_sources']:
            results['passed'] = False
            results['issues'].append(
                f"来源不足: 只有{len(source_counts)}个源，需要至少{self.requirements['min_sources']}个"
            )
        else:
            results['score'] += 30
        
        # 测试2：单源不超过40%
        for source, count in source_counts.items():
            percentage = count / total
            if percentage > self.requirements['max_source_percentage']:
                results['passed'] = False
                results['issues'].append(
                    f"来源不均衡: {source}占比{percentage:.1%}，超过{self.requirements['max_source_percentage']:.0%}"
                )
            else:
                results['score'] += 20
        
        # 测试3：必须包含实时源
        has_realtime = any(s in self.realtime_sources for s in source_counts.keys())
        if self.requirements['must_include_realtime'] and not has_realtime:
            results['passed'] = False
            results['issues'].append("缺少实时源：需要包含Twitter或Product Hunt")
        else:
            results['score'] += 25
        
        # 测试4：必须包含深度源
        has_deep = any(s in self.deep_sources for s in source_counts.keys())
        if self.requirements['must_include_deep'] and not has_deep:
            results['passed'] = False
            results['issues'].append("缺少深度源：需要包含HN或Reddit")
        else:
            results['score'] += 25
        
        return results
    
    def test_content_diversity(self, articles: List[Dict]) -> Dict:
        """测试内容类型多样性"""
        results = {
            'passed': True,
            'score': 0,
            'issues': [],
            'details': {}
        }
        
        # 检测内容关键词
        type_keywords = {
            'ai_model': ['model', 'llm', 'gpt', 'ai', 'claude', 'gemini', 'openai'],
            'dev_tool': ['tool', 'cli', 'api', 'library', 'sdk', 'framework'],
            'product': ['app', 'product', 'platform', 'service'],
            'open_source': ['github', 'open source', '开源'],
            'research': ['paper', 'research', 'study', 'novel']
        }
        
        type_counts = Counter()
        for article in articles:
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            text = title + ' ' + summary
            
            detected_types = []
            for type_name, keywords in type_keywords.items():
                if any(kw in text for kw in keywords):
                    detected_types.append(type_name)
            
            if detected_types:
                type_counts[detected_types[0]] += 1
            else:
                type_counts['other'] += 1
        
        results['details']['type_distribution'] = dict(type_counts)
        
        # 测试：至少3种不同类型
        if len(type_counts) >= 3:
            results['score'] = 100
        elif len(type_counts) >= 2:
            results['score'] = 70
            results['issues'].append(f"类型单一：只有{len(type_counts)}种类型")
        else:
            results['passed'] = False
            results['score'] = 40
            results['issues'].append(f"类型严重不足：只有{len(type_counts)}种类型")
        
        return results
    
    def test_information_density(self, articles: List[Dict]) -> Dict:
        """测试信息密度"""
        results = {
            'passed': True,
            'score': 0,
            'issues': [],
            'details': {}
        }
        
        empty_phrases = [
            '针对痛点', '解决需求', '功能设计', '务实', '专注',
            '讨论的焦点', '关注点主要', '从...来看', '整体来说',
            '第一', '第二', '第三', '首先', '其次', '最后'
        ]
        
        scores = []
        for article in articles:
            content = article.get('content', '')
            word_count = len(content.replace(' ', '').replace('\n', ''))
            
            # 检查空话数量
            empty_count = sum(1 for phrase in empty_phrases if phrase in content)
            
            # 检查具体信息
            has_numbers = any(char.isdigit() for char in content)
            has_tech_detail = any(kw in content.lower() for kw in ['使用', '基于', '采用', '代码', '架构'])
            has_usage = any(kw in content.lower() for kw in ['安装', '使用', '运行', '配置'])
            
            # 计算单篇得分
            score = 0
            if word_count >= 200: score += 20
            if word_count >= 400: score += 20
            if has_numbers: score += 20
            if has_tech_detail: score += 20
            if has_usage: score += 20
            score -= empty_count * 10  # 空话扣分
            
            scores.append(max(0, score))
        
        avg_score = sum(scores) / len(scores) if scores else 0
        results['score'] = avg_score
        results['details']['individual_scores'] = scores
        results['details']['average_score'] = avg_score
        
        if avg_score < 60:
            results['passed'] = False
            results['issues'].append(f"信息密度不足：平均分{avg_score:.1f}，需要≥60")
        
        return results
    
    def run_full_test(self, articles: List[Dict]) -> Dict:
        """运行完整测试"""
        print("\n" + "="*60)
        print("🧪 AiTrend 多源覆盖测试")
        print("="*60)
        
        # 测试1：来源分布
        print("\n📊 测试1: 来源分布...")
        source_test = self.test_source_distribution(articles)
        print(f"  结果: {'✅ 通过' if source_test['passed'] else '❌ 失败'}")
        print(f"  得分: {source_test['score']}/100")
        print(f"  来源: {source_test['details']['unique_sources']}个")
        for issue in source_test['issues'][:2]:
            print(f"  ⚠️ {issue}")
        
        # 测试2：内容多样性
        print("\n📊 测试2: 内容类型多样性...")
        diversity_test = self.test_content_diversity(articles)
        print(f"  结果: {'✅ 通过' if diversity_test['passed'] else '❌ 失败'}")
        print(f"  得分: {diversity_test['score']}/100")
        print(f"  类型: {list(diversity_test['details']['type_distribution'].keys())}")
        
        # 测试3：信息密度
        print("\n📊 测试3: 信息密度...")
        density_test = self.test_information_density(articles)
        print(f"  结果: {'✅ 通过' if density_test['passed'] else '❌ 失败'}")
        print(f"  得分: {density_test['score']:.1f}/100")
        
        # 汇总
        total_score = (source_test['score'] + diversity_test['score'] + density_test['score']) / 3
        all_passed = source_test['passed'] and diversity_test['passed'] and density_test['passed']
        
        print("\n" + "="*60)
        print("📈 测试结果汇总")
        print("="*60)
        print(f"来源分布: {source_test['score']}/100")
        print(f"类型多样: {diversity_test['score']}/100")
        print(f"信息密度: {density_test['score']:.1f}/100")
        print(f"总平均分: {total_score:.1f}/100")
        print(f"整体状态: {'✅ 通过' if all_passed else '❌ 未通过'}")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_score': total_score,
            'passed': all_passed,
            'source_test': source_test,
            'diversity_test': diversity_test,
            'density_test': density_test
        }

def main():
    """测试入口"""
    # 示例：测试一批内容
    test_articles = [
        {'source': 'hackernews', 'title': 'Test', 'content': '...'},
        # 更多测试数据...
    ]
    
    tester = MultiSourceTester()
    results = tester.run_full_test(test_articles)
    
    # 保存测试结果
    with open(TEST_LOG_PATH, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
