# Render全栈部署详细步骤

## 📋 前置准备

### 1. 准备GitHub仓库

如果您的项目还没有推送到GitHub，执行以下操作：

```bash
# 在项目根目录
cd /Users/zhengsonghao/CodeBuddy/20260317162027

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Quantitative trading platform"

# 创建GitHub仓库后，连接远程仓库
git remote add origin https://github.com/你的用户名/quant-platform.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 2. 检查必需文件

确保以下文件存在：

**后端文件**：
- ✅ `backend/app.py`
- ✅ `backend/strategy_adapter.py`
- ✅ `backend/Procfile`
- ✅ `backend/runtime.txt`
- ✅ `requirements.txt`（包含gunicorn）

**前端文件**：
- ✅ `frontend/package.json`
- ✅ `frontend/vite.config.js`
- ✅ `frontend/render-build.sh`

**根目录文件**：
- ✅ `render.yaml`（可选，用于自动化部署）

---

## 🚀 方式一：手动部署（推荐首次使用）

### 步骤1：注册Render账号

1. 访问 https://dashboard.render.com
2. 点击 **"Sign Up"**
3. 选择使用GitHub账号注册（最简单）
4. 授权GitHub访问权限

### 步骤2：部署后端服务

#### 2.1 创建Web Service

1. 登录Render Dashboard
2. 点击右上角 **"New +"** 按钮
3. 选择 **"Web Service"**

#### 2.2 连接GitHub仓库

1. 在 "Connect a repository" 下找到您的仓库
2. 如果是私有仓库，需要点击 "Configure account" 授权
3. 点击 **"Connect"** 按钮连接仓库

#### 2.3 配置后端服务

**基本信息**
- **Name**: `quant-platform-backend`
- **Region**: `Singapore`（或选择离您最近的区域）
- **Branch**: `main`

**Build & Deploy**
- **Root Directory**: `backend`
- **Runtime**: `Python`
- **Build Command**: 留空（Render会自动识别）
- **Start Command**: 
  ```
  gunicorn app:app --host 0.0.0.0 --port $PORT --workers 2 --timeout 120
  ```

**Environment**（点击 "Advanced" 展开）
- **Instance Type**: `Free`
- **RAM**: `512 MB`
- **CPU**: `0.1 vCPU`
- **Max Instances**: `1`

**Health Check**
- **Health Check Path**: `/health`

4. 点击 **"Create Web Service"**

#### 2.4 等待部署

- 首次部署需要 **3-5分钟**
- 点击服务可以看到实时日志
- 部署成功后，会显示服务URL，例如：
  ```
  https://quant-platform-backend.onrender.com
  ```

#### 2.5 测试后端

在浏览器或终端测试：

```bash
# 测试健康检查
curl https://quant-platform-backend.onrender.com/health

# 测试ETF池接口
curl https://quant-platform-backend.onrender.com/api/etf_pool
```

应该返回JSON数据。

**记下后端URL，后面配置前端时需要使用！**

---

### 步骤3：部署前端服务

#### 3.1 创建Static Site

1. 点击右上角 **"New +"**
2. 选择 **"Static Site"**
3. 选择同一个GitHub仓库
4. 点击 **"Connect"**

#### 3.2 配置前端服务

**基本信息**
- **Name**: `quant-platform-frontend`
- **Region**: 与后端相同的区域
- **Branch**: `main`

**Build & Deploy**
- **Root Directory**: `frontend`
- **Build Command**: 
  ```
  npm install && npm run build
  ```
- **Publish Directory**: `dist`

**Environment**（点击 "Advanced" 展开）
- **Instance Type**: `Free`

**Environment Variables**（重要！）
点击 **"Advanced"** → **"Environment Variables"**，点击 **"Add Variable"**：

```
Key: VITE_API_BASE_URL
Value: https://quant-platform-backend.onrender.com
```

*将 `quant-platform-backend.onrender.com` 替换为您的实际后端URL*

5. 点击 **"Create Static Site"**

#### 3.3 等待部署

- 首次部署需要 **2-3分钟**
- 部署成功后，会显示前端URL，例如：
  ```
  https://quant-platform-frontend.onrender.com
  ```

#### 3.4 测试前端

访问前端URL，应该能看到您的量化策略回测平台界面。

---

### 步骤4：配置CORS（重要）

由于前端和后端是不同的子域名，需要配置CORS允许跨域请求。

#### 4.1 更新后端代码

编辑 `backend/app.py`：

```python
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# 允许所有来源（开发环境）
CORS(app)

# 或指定前端域名（生产环境推荐）
# CORS(app, origins=[
#     "https://quant-platform-frontend.onrender.com",
#     "http://localhost:5173"
# ])
```

#### 4.2 重新部署后端

1. 在Render Dashboard打开后端服务
2. 点击 **"Manual Deploy"** → **"Clear build cache & deploy"**
3. 等待重新部署完成

---

## 🎯 方式二：使用render.yaml（推荐自动化部署）

### 步骤1：创建render.yaml文件

项目根目录已有 `render.yaml` 文件，内容如下：

```yaml
services:
  # 后端服务
  - type: web
    name: quant-platform-backend
    env: python
    plan: free
    region: singapore
    rootDir: backend
    buildCommand: pip install -r ../requirements.txt
    startCommand: gunicorn app:app --host 0.0.0.0 --port $PORT --workers 2 --timeout 120
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
    healthCheckPath: /health

  # 前端服务
  - type: web
    name: quant-platform-frontend
    env: static
    plan: free
    region: singapore
    rootDir: frontend
    buildCommand: npm install && npm run build
    publishPath: ./dist
    envVars:
      - key: VITE_API_BASE_URL
        fromService:
          type: web
          name: quant-platform-backend
          property: url
```

### 步骤2：推送到GitHub

```bash
git add render.yaml
git commit -m "Add Render deployment config"
git push
```

### 步骤3：在Render导入

1. 访问 https://dashboard.render.com
2. 点击 **"New +"** → **"Blueprint"**
3. 连接GitHub仓库
4. 选择 `render.yaml` 文件
5. 点击 **"Apply Blueprint"**

Render会自动创建并部署前后端服务！

---

## ✅ 部署后验证

### 1. 检查后端服务

访问以下URL确认后端正常：

```
https://quant-platform-backend.onrender.com/health
```

应该返回：
```json
{"status": "ok"}
```

### 2. 检查前端服务

访问前端URL：
```
https://quant-platform-frontend.onrender.com
```

应该能看到量化策略回测平台的界面。

### 3. 测试完整流程

1. 在前端界面点击"回测"标签
2. 选择ETF池，设置参数
3. 点击"开始回测"
4. 查看回测结果和图表

### 4. 检查日志

如果遇到问题，可以在Render Dashboard查看服务日志：
- 点击服务名称
- 点击 **"Logs"** 标签
- 查看实时日志输出

---

## 📊 免费额度说明

### Render免费实例限制

| 项目 | 限制 |
|------|------|
| CPU | 0.1 vCPU |
| RAM | 512 MB |
| 每月运行时间 | 750小时（约31天） |
| 带宽 | 100GB/月 |
| 构建时间 | 15分钟/次 |

### 休眠机制

- **15分钟无请求** → 实例休眠
- **首次唤醒时间**：30-60秒
- **唤醒后保持**：有请求时保持运行

### 适合使用场景

✅ 个人量化研究
✅ 策略回测
✅ 数据分析
✅ 偶尔查看行情

❌ 不适合：
- 高频交易
- 实时监控（需要保持唤醒）
- 高并发访问

---

## 🔧 常见问题

### Q1: 部署失败怎么办？

**检查日志**：
1. 在Render Dashboard点击服务
2. 查看"Logs"标签
3. 根据错误信息调整代码

**常见错误**：
- `ModuleNotFoundError`: 检查 `requirements.txt`
- `ImportError`: 检查Python版本和依赖
- `TimeoutError`: 增加构建超时时间或优化代码

### Q2: 前端无法连接后端？

**检查项**：
1. 后端服务是否正常运行
2. CORS是否配置正确
3. 前端的 `VITE_API_BASE_URL` 环境变量是否正确
4. 查看浏览器控制台是否有CORS错误

**解决方案**：
```python
# backend/app.py
CORS(app, origins=["*"])  # 允许所有来源（仅用于测试）
```

### Q3: 如何防止实例休眠？

**方法1**：使用Keep-Alive服务
- 使用第三方服务（如UptimeRobot）定期ping您的URL
- 设置每10分钟访问一次

**方法2**：使用Render的付费计划
- $7/月起，不休眠

**方法3**：接受休眠机制
- 量化策略回测不需要实时运行
- 首次访问等待30-60秒可以接受

### Q4: 如何更新代码？

**自动部署**：
```bash
# 修改代码后
git add .
git commit -m "Update strategy"
git push
```

Render会自动检测到推送并重新部署。

**手动触发**：
1. 在Render Dashboard点击服务
2. 点击 **"Manual Deploy"** → **"Deploy latest commit"**

---

## 📝 部署清单

部署前确认：

- [ ] 代码已推送到GitHub
- [ ] `backend/Procfile` 存在
- [ ] `backend/runtime.txt` 存在
- [ ] `requirements.txt` 包含所有依赖
- [ ] `frontend/package.json` 配置正确
- [ ] 后端健康检查接口 `/health` 正常
- [ ] CORS配置正确

部署后验证：

- [ ] 后端服务可访问
- [ ] 前端服务可访问
- [ ] 前端能正常调用后端API
- [ ] 回测功能正常
- [ ] 实时行情功能正常

---

## 🎉 完成！

恭喜！您的量化策略回测平台已成功部署到Render！

**访问地址**：
- 前端：`https://quant-platform-frontend.onrender.com`
- 后端：`https://quant-platform-backend.onrender.com`

现在您可以随时随地访问您的量化平台，进行策略回测和分析！

---

## 📚 参考资源

- [Render官方文档](https://render.com/docs)
- [Render免费额度说明](https://render.com/docs/free)
- [Flask部署指南](https://render.com/docs/deploy-flask)
- [Static Site部署](https://render.com/docs/deploy-static-sites)

需要帮助？查看日志或联系Render支持。
