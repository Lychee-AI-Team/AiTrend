# 🤝 贡献指南

感谢您对 AiTrend 的兴趣！我们欢迎所有形式的贡献。

---

## 🚀 快速开始

### 1. Fork 本仓库

点击右上角的 "Fork" 按钮创建您的副本。

### 2. 克隆到本地

```bash
git clone https://github.com/YOUR_USERNAME/AiTrend.git
cd AiTrend
```

### 3. 设置开发环境

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp config/config.example.yaml config/config.yaml
cp .env.example .env
```

### 4. 创建分支

```bash
git checkout -b feature/你的特性名称
```

---

## 📝 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
类型(范围): 简短描述

详细描述（可选）

 fixes #123（关联 Issue）
```

### 类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加 Twitter 数据源` |
| `fix` | 修复 Bug | `fix: 修复 Reddit 403 错误` |
| `docs` | 文档更新 | `docs: 更新 README` |
| `style` | 代码格式 | `style: 格式化 Python 代码` |
| `refactor` | 重构 | `refactor: 优化数据源基类` |
| `test` | 测试相关 | `test: 添加单元测试` |
| `chore` | 构建/工具 | `chore: 更新依赖` |

---

## 🔍 开发流程

### 1. 寻找任务

查看 [Issues](https://github.com/Lychee-AI-Team/AiTrend/issues) 页面：
- `good first issue` - 适合新手
- `help wanted` - 需要帮助
- `bug` - 需要修复的 Bug

### 2. 编写代码

- 遵循 [PEP 8](https://pep8.org/) 编码规范
- 添加适当的注释
- 保持代码简洁

### 3. 测试

```bash
# 运行测试
python -m pytest tests/

# 检查代码格式
black src/
flake8 src/
```

### 4. 提交 PR

1. 推送到您的 Fork
```bash
git push origin feature/你的特性名称
```

2. 在 GitHub 上创建 Pull Request
3. 填写 PR 模板
4. 等待审核

---

## 📋 PR 检查清单

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 通过了所有 CI 检查
- [ ] 提交了清晰的提交信息

---

## 🐛 报告 Bug

发现 Bug？请创建 Issue 并提供：

1. **问题描述** - 清晰描述问题
2. **复现步骤** - 如何触发问题
3. **期望行为** - 应该发生什么
4. **实际行为** - 实际发生了什么
5. **环境信息** - Python 版本、操作系统等
6. **错误日志** - 相关日志输出

---

## 💡 建议新功能

有好主意？请创建 Issue 并说明：

1. **功能描述** - 这是什么功能？
2. **使用场景** - 谁会使用这个功能？
3. **实现思路** - 如何可能实现？
4. **替代方案** - 有其他解决方案吗？

---

## 📞 联系我们

- GitHub Issues: [创建 Issue](https://github.com/Lychee-AI-Team/AiTrend/issues)
- 邮件: ai-lychee@example.com

---

## 🙏 感谢

感谢所有贡献者！你们的贡献让 AiTrend 变得更好。

[查看所有贡献者](https://github.com/Lychee-AI-Team/AiTrend/graphs/contributors)
