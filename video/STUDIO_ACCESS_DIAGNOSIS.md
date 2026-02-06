# Remotion Studio 无法访问问题诊断报告

**时间**: 2026-02-06 15:47  
**问题**: Studio启动成功但浏览器无法访问

---

## 服务器端状态 (✅ 正常)

```
进程状态: ✅ 运行中 (PID: 20544, 20556)
端口监听: ✅ 3005端口 LISTEN
HTTP状态: ✅ 200 OK
内容返回: ✅ HTML正常
构建状态: ✅ Built in 314ms
```

**验证命令**:
```bash
curl -s http://localhost:3005/ | head -5
# 返回: <!DOCTYPE html>... (正常)
```

---

## 可能原因分析

### 原因1: WSL网络转发问题 (最可能)
**现象**: WSL内部可访问，Windows浏览器无法访问
**原因**: WSL2使用虚拟网络，需要端口转发

**解决方案**:
在Windows PowerShell (管理员) 中执行:
```powershell
# 查看WSL IP
wsl hostname -I

# 添加端口转发 (将WSL的3005转发到Windows的3005)
netsh interface portproxy add v4tov4 listenport=3005 listenaddress=0.0.0.0 connectport=3005 connectaddress=172.27.221.245

# 防火墙允许
netsh advfirewall firewall add rule name="Remotion Studio 3005" dir=in action=allow protocol=tcp localport=3005
```

然后访问: http://localhost:3005

---

### 原因2: Windows防火墙阻止
**检查方法**:
1. 打开 Windows 安全中心
2. 检查"应用和浏览器控制"
3. 允许 Node.js 通过防火墙

---

### 原因3: 浏览器缓存或扩展
**尝试**:
1. 清除浏览器缓存 (Ctrl+Shift+Delete)
2. 无痕模式访问 (Ctrl+Shift+N)
3. 禁用浏览器扩展

---

### 原因4: 浏览器控制台JavaScript错误
**检查方法**:
1. 打开浏览器开发者工具 (F12)
2. 查看 Console 标签
3. 查看是否有红色错误信息

---

## 快速解决方案

### 方案A: 直接在WSL中访问 (推荐)
在WSL中启动浏览器:
```bash
# 安装wslu (如果未安装)
sudo apt install wslu

# 用Windows浏览器打开
wslview http://localhost:3005
```

### 方案B: 使用IP直接访问
尝试以下地址:
- http://172.27.221.245:3005
- http://127.0.0.1:3005
- http://[::1]:3005

### 方案C: 使用VS Code端口转发
1. 在VS Code中打开项目
2. 点击底部状态栏的"端口"标签
3. 添加端口转发: 3005 -> 3005
4. 点击转发后的链接

---

## 备用方案: 生成静态预览图

如果Studio始终无法访问，可以直接渲染视频:
```bash
cd AiTrend/video/src
npx remotion render index-60s.tsx DailyNews60s ../data/output/preview_60s.mp4 --browser-executable=$(find ~/.cache/ms-playwright -name "chrome" -type f | head -1) --concurrency=2
```

---

## 当前可用地址汇总

| 地址 | 状态 | 适用场景 |
|------|------|----------|
| http://localhost:3005 | ✅ WSL内正常 | WSL内部curl访问 |
| http://172.27.221.245:3005 | ⚠️ 需转发 | Windows浏览器 |
| http://127.0.0.1:3005 | ❓ 待测试 | 回环地址 |

---

## 推荐下一步

1. **在WSL中测试**:
   ```bash
   curl -s http://localhost:3005/ > /dev/null && echo "✅ WSL内可访问" || echo "❌ WSL内也无法访问"
   ```

2. **在Windows中测试**:
   PowerShell中执行:
   ```powershell
   Invoke-WebRequest -Uri "http://172.27.221.245:3005" -Method HEAD
   ```

3. **如果WSL内可访问但Windows不可**:
   - 执行方案A的端口转发命令
   - 或直接使用渲染命令生成视频

---

**请尝试上述方案并反馈结果！** 🦞
