# 📋 更新日志

所有显著变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [0.3.0] - 2026-02-03

### ✨ 新增

- 🔥 全新架构 - 模块化设计，支持自由组合数据源和输出渠道
- 🐳 Docker 支持 - 提供 Dockerfile 和 docker-compose.yml
- 📦 OpenClaw Skill 支持 - 可作为 OpenClaw 插件安装
- 🛡️ 密钥保护机制 - 多层保护防止 API Key 泄露
- 🌐 多语言 README - 支持简体中文、英语、日语、韩语、西班牙语

### 🔧 改进

- ⚡ 性能优化 - 数据源获取超时机制
- 🔒 安全增强 - 启动时自动检查密钥保护状态
- 📝 文档完善 - 新增 API Key 设置指南、故障排查文档

### 🐛 修复

- 修复硬编码路径问题
- 修复配置文件混乱问题
- 修复 requirements.txt 依赖声明

### 🗑️ 移除

- 移除废弃的 GitHub Actions workflows
- 移除旧版本残留的脚本文件

---

## [0.2.0] - 2026-01-XX

### ✨ 新增

- 多数据源支持（GitHub、Product Hunt、HackerNews）
- Discord 发布功能
- 基础去重机制

### 🔧 改进

- 优化内容生成质量
- 改进错误处理

---

## [0.1.0] - 2026-01-XX

### ✨ 新增

- 初始版本发布
- 基础数据源采集
- 控制台输出

---

## 版本说明

- **MAJOR**: 不兼容的 API 更改
- **MINOR**: 向后兼容的功能添加
- **PATCH**: 向后兼容的问题修复
