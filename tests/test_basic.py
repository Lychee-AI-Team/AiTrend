"""
基础测试
验证核心功能
"""
import pytest
from src.core.validator import SelfValidator
from src.sources.base import Article

class TestValidator:
    """测试自验证器"""
    
    def test_validate_articles_valid(self):
        """测试有效文章验证"""
        validator = SelfValidator()
        
        articles = [
            {"title": "Test Article", "url": "https://example.com", "summary": "Test"},
            {"title": "Another Article", "url": "https://test.com", "summary": "Another"}
        ]
        
        is_valid, msg, fixed = validator.validate_articles(articles)
        assert is_valid is True
        assert len(fixed) == 2
    
    def test_validate_articles_invalid_url(self):
        """测试无效 URL 自动修复"""
        validator = SelfValidator(auto_fix=True)
        
        articles = [
            {"title": "Test", "url": "www.example.com", "summary": "Test"}
        ]
        
        is_valid, msg, fixed = validator.validate_articles(articles)
        assert len(fixed) == 1
        assert fixed[0]["url"].startswith("https://")
    
    def test_validate_summary_format(self):
        """测试总结格式验证"""
        validator = SelfValidator()
        
        summary = "🔥 AI 热点\n\n1. Test（来源）- 摘要"
        articles = [{"title": "Test", "summary": "Original summary"}]
        
        is_valid, msg, fixed = validator.validate_summary(summary, articles)
        assert is_valid is True
    
    def test_validate_summary_no_chinese(self):
        """测试无中文检测"""
        validator = SelfValidator()
        
        summary = "No Chinese characters here"
        articles = [{"title": "Test", "summary": "Original"}]
        
        is_valid, msg, fixed = validator.validate_summary(summary, articles)
        assert is_valid is False
        assert "不包含中文字符" in msg

class TestArticleModel:
    """测试文章模型"""
    
    def test_article_creation(self):
        """测试创建文章"""
        article = Article(
            title="Test Title",
            url="https://example.com",
            summary="Test summary",
            source="test"
        )
        
        assert article.title == "Test Title"
        assert article.url == "https://example.com"
        assert article.source == "test"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
