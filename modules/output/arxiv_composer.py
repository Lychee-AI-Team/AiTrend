"""
arXiv 论文内容生成器

生成中文介绍文本：
- 论文核心贡献
- 方法概述
- 实验结果亮点
- 适用场景

最终输出：中文
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class ArxivContentComposer:
    """arXiv 论文中文内容生成器"""
    
    # 分类中文映射
    CATEGORY_NAMES = {
        'cs.AI': '人工智能',
        'cs.CL': '计算语言学',
        'cs.LG': '机器学习',
        'cs.CV': '计算机视觉',
        'cs.IR': '信息检索',
        'cs.RO': '机器人学',
        'cs.CR': '密码学与安全',
        'cs.DB': '数据库',
        'cs.DC': '分布式计算',
        'cs.HC': '人机交互',
        'cs.NE': '神经与进化计算',
        'cs.SE': '软件工程',
        'stat.ML': '统计机器学习'
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
    def _get_category_name(self, category: str) -> str:
        """获取分类中文名称"""
        return self.CATEGORY_NAMES.get(category, category)
    
    def _extract_first_sentence(self, text: str, max_length: int = 200) -> str:
        """提取第一句话作为概述"""
        # 按句号分割，取第一句
        sentences = text.split('.')
        if sentences:
            first = sentences[0].strip()
            if len(first) > max_length:
                first = first[:max_length] + "..."
            return first
        return text[:max_length]
    
    def compose(self, paper: Dict[str, Any]) -> str:
        """
        生成论文的中文介绍
        
        Args:
            paper: 论文信息字典
            
        Returns:
            中文介绍文本
        """
        title = paper.get('title', '')
        summary = paper.get('summary', '')
        authors = paper.get('authors', [])
        categories = paper.get('categories', [])
        primary_cat = paper.get('primary_category', '')
        published = paper.get('published_str', '')
        abs_url = paper.get('abs_url', '')
        pdf_url = paper.get('pdf_url', '')
        
        # 获取分类中文名
        cat_names = [self._get_category_name(cat) for cat in categories[:3]]
        primary_cat_name = self._get_category_name(primary_cat)
        
        # 作者信息（最多3位）
        author_str = ', '.join(authors[:3])
        if len(authors) > 3:
            author_str += f" 等 {len(authors)} 位作者"
        
        # 提取核心摘要（简化）
        # 去除 LaTeX 符号
        clean_summary = summary.replace('$', '').replace('\\', '')
        # 取前200字
        brief_summary = clean_summary[:200].strip()
        if len(clean_summary) > 200:
            brief_summary += "..."
        
        # 构建内容
        parts = []
        
        # 标题和基本信息
        parts.append(f"**{title}**")
        parts.append("")
        
        # 元信息
        parts.append(f"📚 {primary_cat_name} | {published} | {author_str}")
        parts.append("")
        
        # 论文概述
        parts.append("**研究概述**")
        parts.append(brief_summary)
        parts.append("")
        
        # 核心贡献（从摘要推断）
        parts.append("**核心贡献**")
        # 简单启发式提取
        if 'propose' in summary.lower() or 'introduce' in summary.lower():
            parts.append("本文提出了一种新方法，旨在解决现有技术的局限性。")
        elif 'improve' in summary.lower() or 'better' in summary.lower():
            parts.append("本研究在性能上实现了显著提升，超越了现有基准。")
        elif 'benchmark' in summary.lower() or 'dataset' in summary.lower():
            parts.append("本文构建了新的基准测试或数据集，推动了领域发展。")
        elif 'survey' in summary.lower() or 'review' in summary.lower():
            parts.append("这是一篇综述性论文，系统梳理了该领域的研究进展。")
        else:
            parts.append("本文针对该领域的核心问题提出了创新性解决方案。")
        
        parts.append("")
        
        # 适用场景
        parts.append("**适用场景**")
        if 'cs.CV' in categories:
            parts.append("适用于图像识别、视觉理解等计算机视觉任务。")
        elif 'cs.CL' in categories:
            parts.append("适用于自然语言处理、文本理解、机器翻译等任务。")
        elif 'cs.LG' in categories:
            parts.append("适用于机器学习理论研究、算法优化、模型改进等。")
        elif 'cs.AI' in categories:
            parts.append("适用于人工智能系统设计与应用、智能决策等场景。")
        else:
            parts.append("适用于相关领域的研究和工程实践。")
        
        parts.append("")
        
        # 链接
        parts.append("**获取论文**")
        parts.append(f"📄 论文页面: {abs_url}")
        if pdf_url:
            parts.append(f"📥 PDF下载: {pdf_url}")
        
        return '\n'.join(parts)
    
    def compose_narrative(self, paper: Dict[str, Any]) -> str:
        """
        生成叙述式中文介绍（更自然的文本）
        
        Args:
            paper: 论文信息
            
        Returns:
            自然叙述式中文文本
        """
        title = paper.get('title', '')
        summary = paper.get('summary', '')
        authors = paper.get('authors', [])
        categories = paper.get('categories', [])
        primary_cat = paper.get('primary_category', '')
        published = paper.get('published_str', '')
        abs_url = paper.get('abs_url', '')
        
        # 分类名
        cat_names = [self._get_category_name(cat) for cat in categories[:2]]
        primary_cat_name = self._get_category_name(primary_cat)
        
        # 作者（最多2位）
        author_display = ', '.join(authors[:2])
        if len(authors) > 2:
            author_display += " 等"
        
        # 提取核心主题和方法
        topic = self._extract_topic(summary)
        method_desc = self._extract_method_description(summary)
        
        # 生成内容（叙述式）
        lines = []
        
        # 开头：直接介绍论文（简洁）
        lines.append(f"这篇 {primary_cat_name} 论文由 {author_display} 提出，聚焦 {topic}。")
        
        # 方法/贡献（中文描述）
        contribution = self._generate_contribution_text(summary, categories)
        lines.append(contribution)
        
        # 实验/结果（如有）
        if self._has_experiments(summary):
            lines.append("实验验证表明该方法具有良好性能。")
        
        # 价值/意义
        value = self._generate_value_text(primary_cat_name, categories)
        lines.append(value)
        
        # 链接
        lines.append("")
        lines.append(f"📄 论文: {abs_url}")
        
        return '\n'.join(lines)
    
    def _extract_topic(self, summary: str) -> str:
        """从摘要提取研究主题"""
        summary_lower = summary.lower()
        
        # 关键词到中文的映射
        topics = [
            ('large language model', '大语言模型'),
            ('llm', '大语言模型'),
            ('transformer', 'Transformer架构'),
            ('diffusion model', '扩散模型'),
            ('neural network', '神经网络'),
            ('deep learning', '深度学习'),
            ('reinforcement learning', '强化学习'),
            ('computer vision', '计算机视觉'),
            ('video generation', '视频生成'),
            ('image generation', '图像生成'),
            ('natural language processing', '自然语言处理'),
            ('nlp', '自然语言处理'),
            ('machine learning', '机器学习'),
            ('artificial intelligence', '人工智能'),
            ('generative', '生成式AI'),
            ('multimodal', '多模态学习'),
            ('optimization', '优化方法'),
            ('robotics', '机器人学'),
            ('prompt', '提示工程'),
        ]
        
        for eng, chn in topics:
            if eng in summary_lower:
                return chn
        
        return "该领域前沿问题"
    
    def _extract_method_description(self, summary: str) -> str:
        """提取方法描述"""
        # 清理并简化摘要
        clean = summary.replace('$', '').replace('\\', '').replace('\n', ' ')
        
        # 识别方法类型
        if 'propose' in summary.lower() or 'introduce' in summary.lower():
            return "提出新方法"
        elif 'improve' in summary.lower() or 'enhance' in summary.lower():
            return "改进现有方案"
        elif 'survey' in summary.lower() or 'review' in summary.lower():
            return "系统性综述"
        else:
            return "深入研究"
    
    def _generate_contribution_text(self, summary: str, categories: List[str]) -> str:
        """生成贡献描述"""
        summary_lower = summary.lower()
        
        # 根据摘要内容选择描述
        if 'propose' in summary_lower or 'present' in summary_lower:
            if 'cs.CV' in categories:
                return "提出了一种视觉处理方法，旨在提升生成质量与一致性。"
            elif 'cs.CL' in categories:
                return "提出了一种语言处理方法，在理解和生成任务上有所创新。"
            elif 'cs.LG' in categories:
                return "提出了一种学习框架，改进了模型训练效率和效果。"
            else:
                return "提出了一种新的方法框架，针对现有挑战给出了解决方案。"
        
        elif 'improve' in summary_lower or 'better' in summary_lower:
            return "在现有方法基础上进行了改进，提升了性能和稳定性。"
        
        elif 'survey' in summary_lower or 'review' in summary_lower:
            return "对该领域进行了系统性梳理，总结了当前进展和未来方向。"
        
        else:
            return "针对核心问题展开研究，给出了有价值的理论或实践贡献。"
    
    def _has_experiments(self, summary: str) -> bool:
        """检查是否有实验部分"""
        keywords = ['experiment', 'result', 'benchmark', 'evaluate', 'dataset']
        return any(kw in summary.lower() for kw in keywords)
    
    def _generate_value_text(self, primary_cat: str, categories: List[str]) -> str:
        """生成价值描述"""
        if '计算机视觉' in primary_cat:
            return "对视觉理解和生成领域具有参考价值，适合关注图像视频技术的研究者。"
        elif '计算语言学' in primary_cat or '自然语言处理' in primary_cat:
            return "对语言技术领域有所贡献，适合从事文本理解和生成的研究人员。"
        elif '机器学习' in primary_cat:
            return "为机器学习理论和实践提供了新思路，适合算法研究者关注。"
        elif '人工智能' in primary_cat:
            return "推动了AI技术发展，对研究和应用均有参考意义。"
        else:
            return "为该领域的发展提供了有价值的参考，值得关注。"


if __name__ == "__main__":
    # 测试
    test_paper = {
        'title': 'Attention Is All You Need',
        'summary': 'We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.',
        'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar'],
        'categories': ['cs.CL', 'cs.LG'],
        'primary_category': 'cs.CL',
        'published_str': '2024-01-15',
        'abs_url': 'https://arxiv.org/abs/1706.03762',
        'pdf_url': 'https://arxiv.org/pdf/1706.03762.pdf'
    }
    
    composer = ArxivContentComposer()
    
    print("=== 结构化格式 ===")
    print(composer.compose(test_paper))
    print("\n=== 叙述式格式 ===")
    print(composer.compose_narrative(test_paper))
