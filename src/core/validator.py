"""
自验证器 - 纯标准库版本
"""
import re
from typing import List, Tuple, Dict, Any
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

class SelfValidator:
    """自验证器：自动验证数据质量和格式"""
    
    def __init__(self, auto_fix: bool = True):
        self.auto_fix = auto_fix
    
    def validate_articles(self, articles: List[Dict[str, Any]]) -> Tuple[bool, str, List[Dict]]:
        """验证文章数据"""
        if not articles:
            return False, "文章列表为空", []
        
        valid_articles = []
        issues = []
        
        for i, article in enumerate(articles):
            errors = []
            
            if not article.get('title') or len(str(article.get('title', ''))) < 5:
                errors.append(f"标题过短或缺失")
            
            url = article.get('url', '')
            if not url or not url.startswith(('http://', 'https://')):
                errors.append(f"URL 无效: {url}")
            
            if errors:
                issues.append(f"文章 {i+1}: {', '.join(errors)}")
                if self.auto_fix:
                    fixed = self._fix_article(article)
                    if fixed:
                        valid_articles.append(fixed)
                continue
            
            valid_articles.append(article)
        
        if issues:
            msg = f"验证发现 {len(issues)} 个问题"
            if valid_articles:
                msg += f"，已修复并保留 {len(valid_articles)} 条"
            return len(valid_articles) > 0, msg, valid_articles
        
        return True, f"全部 {len(valid_articles)} 条验证通过", valid_articles
    
    def _fix_article(self, article: Dict) -> Dict:
        """尝试修复文章数据"""
        fixed = article.copy()
        
        if not fixed.get('title'):
            fixed['title'] = '未命名文章'
        
        url = fixed.get('url', '')
        if not url.startswith(('http://', 'https://')):
            if url.startswith('www.'):
                fixed['url'] = f"https://{url}"
            else:
                return None
        
        if not fixed.get('summary'):
            fixed['summary'] = '暂无摘要'
        
        return fixed
    
    def validate_summary(self, summary: str, original_articles: List[Dict]) -> Tuple[bool, str, str]:
        """验证总结质量"""
        issues = []
        fixed_summary = summary
        
        original_length = sum(len(str(a.get('title', ''))) + len(str(a.get('summary', ''))) 
                             for a in original_articles)
        
        if len(summary) < original_length * 0.05:
            issues.append("总结内容过短，可能丢失重要信息")
        
        if len(summary) > 4000:
            issues.append(f"总结过长 ({len(summary)} 字符)，超过飞书限制")
            if self.auto_fix:
                fixed_summary = summary[:3997] + "..."
        
        if not re.search(r'[\u4e00-\u9fff]', summary):
            issues.append("总结不包含中文字符，可能翻译失败")
        
        if '**' in summary or '__' in summary:
            issues.append("总结包含 markdown 格式标记")
            if self.auto_fix:
                fixed_summary = re.sub(r'\*\*|__', '', fixed_summary)
        
        if '<' in summary and '>' in summary:
            issues.append("总结可能包含 HTML 标签")
            if self.auto_fix:
                fixed_summary = re.sub(r'<[^>]+>', '', fixed_summary)
        
        if issues:
            return len(issues) <= 2, f"发现 {len(issues)} 个问题: {'; '.join(issues[:3])}", fixed_summary
        
        return True, "总结质量良好", fixed_summary
    
    def validate_send_format(self, content: str, channel: str = "feishu") -> Tuple[bool, str, str]:
        """验证发送格式"""
        issues = []
        fixed = content
        
        if channel == "feishu":
            if len(content) > 4000:
                issues.append(f"内容长度 {len(content)} 超过飞书限制 4000")
                if self.auto_fix:
                    fixed = content[:3997] + "..."
            
            if '\x00' in content or '\x01' in content:
                issues.append("包含非法字符")
                if self.auto_fix:
                    fixed = content.replace('\x00', '').replace('\x01', '')
        
        if issues:
            return self.auto_fix, f"格式问题: {'; '.join(issues)}", fixed
        
        return True, "格式符合要求", fixed
    
    def full_validate(self, articles: List[Dict], summary: str, channel: str = "feishu") -> Tuple[bool, Dict[str, Any]]:
        """执行完整验证流程"""
        result = {
            "data_valid": False,
            "summary_valid": False,
            "format_valid": False,
            "data_count": 0,
            "issues": [],
            "fixed_articles": [],
            "fixed_summary": summary,
            "fixed_content": summary
        }
        
        data_ok, msg, fixed_articles = self.validate_articles(articles)
        result["data_valid"] = data_ok
        result["data_count"] = len(fixed_articles)
        result["fixed_articles"] = fixed_articles
        if not data_ok:
            result["issues"].append(f"数据验证: {msg}")
        
        if data_ok:
            summary_ok, msg, fixed_summary = self.validate_summary(summary, fixed_articles)
            result["summary_valid"] = summary_ok
            result["fixed_summary"] = fixed_summary
            if not summary_ok:
                result["issues"].append(f"总结验证: {msg}")
        
        content = result["fixed_summary"]
        format_ok, msg, fixed_content = self.validate_send_format(content, channel)
        result["format_valid"] = format_ok
        result["fixed_content"] = fixed_content
        if not format_ok:
            result["issues"].append(f"格式验证: {msg}")
        
        all_passed = result["data_valid"] and result["summary_valid"] and result["format_valid"]
        
        if all_passed:
            logger.info("✅ 完整验证通过")
        else:
            logger.warning(f"⚠️ 验证未通过: {'; '.join(result['issues'])}")
        
        return all_passed, result
