#!/usr/bin/env python3
"""
热点精选脚本
从24小时数据中精选5-10条热点
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

# 添加 AiTrend 路径
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/AiTrend')


class HotspotSelector:
    """热点精选器"""
    
    def __init__(self, max_items: int = 8, min_heat_score: int = 50):
        """
        初始化精选器
        
        Args:
            max_items: 最大精选数量（默认8条）
            min_heat_score: 最小热度分数阈值
        """
        self.max_items = max_items
        self.min_heat_score = min_heat_score
    
    def select(self, input_file: str, output_file: str = None) -> Dict[str, Any]:
        """
        从输入文件中精选热点
        
        Args:
            input_file: 输入数据文件路径（daily_raw_YYYY-MM-DD.json）
            output_file: 输出文件路径（可选）
            
        Returns:
            精选后的热点数据
        """
        # 加载数据
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取所有项目
        all_items = []
        for source in data.get('sources', []):
            source_name = source.get('source', 'unknown')
            for item in source.get('items', []):
                item['source_origin'] = source_name
                all_items.append(item)
        
        print(f"📊 原始数据: {len(all_items)} 条")
        
        # 筛选：热度分数达标
        filtered_items = [
            item for item in all_items 
            if item.get('heat_score', 0) >= self.min_heat_score
        ]
        
        print(f"🔥 热度达标(>{self.min_heat_score}): {len(filtered_items)} 条")
        
        # 去重：基于标题相似度
        deduplicated = self._deduplicate(filtered_items)
        print(f"🧹 去重后: {len(deduplicated)} 条")
        
        # 排序：按热度分数
        sorted_items = sorted(
            deduplicated, 
            key=lambda x: x.get('heat_score', 0), 
            reverse=True
        )
        
        # 多样性筛选：同类主题不超过2条
        selected = self._apply_diversity(sorted_items)
        
        print(f"✅ 最终精选: {len(selected)} 条")
        
        # 构建输出
        output = {
            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'selection_time': datetime.now().isoformat(),
            'selection_params': {
                'max_items': self.max_items,
                'min_heat_score': self.min_heat_score
            },
            'selected_count': len(selected),
            'hotspots': selected
        }
        
        # 保存到文件
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"💾 已保存: {output_file}")
        
        return output
    
    def _deduplicate(self, items: List[Dict]) -> List[Dict]:
        """基于标题相似度去重"""
        unique_items = []
        seen_titles = []
        
        for item in items:
            title = item.get('title', '').lower()
            
            # 检查是否与已有标题相似
            is_duplicate = False
            for seen in seen_titles:
                # 简单相似度检查：包含关系或编辑距离
                if self._is_similar(title, seen):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_items.append(item)
                seen_titles.append(title)
        
        return unique_items
    
    def _is_similar(self, title1: str, title2: str, threshold: float = 0.7) -> bool:
        """检查两个标题是否相似"""
        # 简单实现：包含检查
        if title1 in title2 or title2 in title1:
            return True
        
        # 计算简单相似度（共同字符比例）
        set1 = set(title1)
        set2 = set(title2)
        if not set1 or not set2:
            return False
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        similarity = intersection / union if union > 0 else 0
        
        return similarity > threshold
    
    def _apply_diversity(self, items: List[Dict]) -> List[Dict]:
        """应用多样性筛选：同类主题不超过2条"""
        selected = []
        category_count = {}
        
        for item in items:
            # 获取类别（如果没有则基于来源推断）
            category = item.get('category', '其他')
            if category == '其他':
                # 基于来源推断类别
                source = item.get('source_origin', '')
                category = self._infer_category(source)
            
            # 检查类别数量
            if category_count.get(category, 0) < 2:
                # 添加排名信息
                item['rank'] = len(selected) + 1
                selected.append(item)
                category_count[category] = category_count.get(category, 0) + 1
            
            if len(selected) >= self.max_items:
                break
        
        return selected
    
    def _infer_category(self, source: str) -> str:
        """基于来源推断类别"""
        category_map = {
            'hackernews': '技术开发',
            'producthunt': '产品发布',
            'github_trending': '开源项目',
            'reddit': '社区讨论',
            'twitter': '社交媒体',
            'moltbook': 'AI社区',
            'tavily': 'AI新闻'
        }
        return category_map.get(source.lower(), '其他')


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='热点精选脚本')
    parser.add_argument('--input', '-i', required=True, help='输入文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--max', '-m', type=int, default=8, help='最大精选数量')
    parser.add_argument('--min-heat', type=int, default=50, help='最小热度分数')
    
    args = parser.parse_args()
    
    selector = HotspotSelector(max_items=args.max, min_heat_score=args.min_heat)
    result = selector.select(args.input, args.output)
    
    print(f"\n📋 精选结果:")
    for item in result['hotspots']:
        print(f"  {item['rank']}. {item.get('title', 'N/A')[:50]}... (热度: {item.get('heat_score', 0)})")


if __name__ == '__main__':
    main()
