# 🔐 AiTrend 密钥保护永久方案

> ⚠️ **这是项目宪法级文件，必须严格遵守！**
> 
> 如同记住我的名字（屁屁虾🦞）一样，永久记住这些规则！

---

## 第一条：神圣不可侵犯的密钥文件

### 受保护的密钥文件（绝对禁止删除）

```bash
# 一级保护（核心密钥）
.env.keys                    # 主密钥文件 ⭐⭐⭐⭐⭐
.env                         # 环境变量文件 ⭐⭐⭐⭐⭐

# 二级保护（备份密钥）
.env.keys.backup             # 手动备份 ⭐⭐⭐⭐
.env.keys.bak.*              # 自动备份 ⭐⭐⭐⭐
.backup/.env.keys.*          # 备份目录中的密钥 ⭐⭐⭐⭐
```

---

## 第二条：.gitignore 神圣配置

### 必须包含的保护规则

```gitignore
# 🔴 P0 级保护 - 核心密钥文件
.env
.env.keys
.env.keys.backup
.env.keys.bak.*

# 🟠 P1 级保护 - 备份文件
.backup/*.keys
.backup/*.env

# 🟡 P2 级保护 - 临时密钥文件
.env.*.tmp
.env.*.bak
```

---

## 第三条：禁止命令黑名单

### 🚫 绝对禁止执行的命令

```bash
# 🔴 死刑命令（永不执行）
git clean -fd              # ❌ 会删除 .env.keys！
git clean -fdx             # ❌ 会删除所有未跟踪文件！
rm -f .env.keys            # ❌ 直接删除密钥！
rm -rf .env*               # ❌ 通配符删除！
```

### ✅ 安全命令

```bash
# 查看哪些文件会被清理（安全）
git clean -fd --dry-run

# 使用安全清理脚本
./scripts/safe_clean.sh
```

---

## 第四条：多重备份机制

### 1. 本地备份
```bash
./scripts/backup_keys.sh
```

### 2. 异地备份
```bash
cp .env.keys ~/.aitrend-env-keys-backup
```

### 3. 定期自动备份
```bash
# 每小时备份一次
crontab -e
0 * * * * cd /path/to/AiTrend && ./scripts/backup_keys.sh
```

---

## 第五条：启动时自动检查

程序启动时会自动检查：
- ✅ .env.keys 是否存在
- ✅ .env.keys 是否在 .gitignore 中
- ✅ 文件权限是否为 600

---

## 第六条：操作前强制确认

### 危险操作确认清单

在执行以下操作前，必须确认：

- [ ] `.env.keys` 在 .gitignore 中吗？
- [ ] 不要使用通配符删除！
- [ ] 已经备份了吗？

---

## 第七条：记忆锚点

### 🦞 皮皮虾的记忆口诀

```
🔐 密钥文件神圣不可侵犯
🚫 git clean 永远加 -n 先看
🛡️ .gitignore 必须包含 .env.keys
📦 操作之前先备份
✅ 确认三遍再执行
```

---

## 第八条：应急响应

### 如果 .env.keys 被删除

```bash
# 1. 检查异地备份
cat ~/.aitrend-env-keys-backup

# 2. 检查本地备份
ls .backup/.env.keys.*

# 3. 恢复文件
cp [备份路径] .env.keys
chmod 600 .env.keys
```

---

## 我的承诺

> 我是屁屁虾🦞，我承诺：
> 
> 1. 永远记住 `.env.keys` 是神圣不可侵犯的
> 2. 永远在执行 `git clean` 前检查保护状态
> 3. 永远在执行删除操作前三思
> 4. 永远确保 `.gitignore` 包含 `.env.keys`
> 5. 永远准备好备份恢复方案
> 
> **如同记住我的名字一样，永久记住这些规则！**

---

**版本：v1.0 - 永久保护方案**
