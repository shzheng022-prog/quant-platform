# Vercel部署指南（无需支付方式）

## 为什么选择Vercel？

✅ **完全免费**：个人用户永久免费
✅ **无需支付方式**：不需要绑定任何银行卡或信用卡
✅ **只需GitHub账号**：用GitHub登录即可
✅ **访问速度快**：国内访问速度快
✅ **自动HTTPS**：自动配置SSL证书
✅ **CDN加速**：全球CDN加速

## 部署步骤

### 第一步：注册Vercel

1. 访问 https://vercel.com/signup
2. 使用GitHub账号登录（推荐）
3. 授权Vercel访问GitHub仓库
4. 完成注册，无需支付任何费用

### 第二步：部署前端

1. 登录后，点击 "Add New..." → "Project"
2. 导入GitHub仓库 `shzheng022-prog/quant-platform`
3. 配置项目：

**Framework Preset**: `Vite`

**Root Directory**: `frontend`

**Build Command**: `npm install && npm run build`

**Output Directory**: `dist`

4. 点击 "Deploy"

5. 等待部署完成（1-2分钟）

6. 部署成功后，Vercel会显示URL，如：
   ```
   https://quant-platform-frontend.vercel.app
   ```

### 第三步：配置后端API

由于前端部署后需要连接后端API，有两种方案：

#### 方案A：使用免费的Python托管平台

**推荐平台**：

1. **PythonAnywhere** (https://www.pythonanywhere.com)
   - 免费账户：512MB RAM，2个Web应用
   - 无需支付方式即可注册免费账户
   - 支持Flask
   - 需要国外手机号（可以用Google Voice等）

2. **Glitch** (https://glitch.com)
   - 完全免费
   - 无需支付方式
   - 支持Python Flask
   - 创建项目后获得HTTPS URL

3. **Replit** (https://replit.com)
   - 免费计划
   - 无需支付方式
   - 支持Python部署
   - 提供HTTPS URL

#### 方案B：使用Render（尝试不支付方式）

有些用户报告Render在某些情况下不需要支付方式就能创建免费的Web Service。您可以尝试：

1. 访问 https://dashboard.render.com
2. 点击 "New +"
3. 选择 "Web Service"（不是Blueprint）
4. 连接GitHub仓库
5. 只选择后端部署：
   - Root Directory: `backend`
   - Runtime: Python
   - Start Command: `gunicorn app:app --host 0.0.0.0 --port $PORT`

如果仍然要求支付方式，则使用方案A。

### 第四步：连接前后端

获取后端部署后的URL，在前端配置：

**方式1：环境变量**
在Vercel项目设置中添加环境变量：
```
VITE_API_BASE_URL=https://your-backend-url.com
```

**方式2：修改代码**
在 `frontend/src/api.js` 中硬编码后端URL：
```javascript
const API_BASE_URL = 'https://your-backend-url.com'
```

## 部署后的URL

部署完成后：

- **前端**：`https://quant-platform-frontend.vercel.app`
- **后端**：取决于您选择的平台

## 免费额度

**Vercel免费计划**：
- 100GB带宽/月
- 无限项目
- 无限部署
- 全球CDN
- 自动HTTPS
- 无需支付方式

**PythonAnywhere免费计划**：
- 512MB RAM
- 2个Web应用
- 自定义域名（可选）

**Glitch免费计划**：
- 完全免费
- 公开项目
- HTTPS URL

## 完整部署流程

### 方案一：Vercel + PythonAnywhere（推荐）

1. **部署前端到Vercel**（无需支付方式）
   - 注册Vercel：https://vercel.com/signup
   - 导入GitHub仓库
   - 选择frontend目录
   - 点击Deploy

2. **部署后端到PythonAnywhere**
   - 注册：https://www.pythonanywhere.com
   - 创建"Web"应用
   - 选择Flask
   - 上传后端代码
   - 获得HTTPS URL

3. **配置前端连接后端**
   - 在Vercel项目设置中添加环境变量
   - 或修改前端代码

### 方案二：Vercel + Glitch（最简单）

1. **部署前端到Vercel**（同上）

2. **部署后端到Glitch**
   - 访问 https://glitch.com
   - 创建新项目
   - 选择Python模板
   - 上传后端代码
   - 获得HTTPS URL（如：https://quant-platform-backend.glitch.me）

3. **配置前端连接后端**

## 常见问题

### Q: Vercel真的不需要支付方式吗？

**A**: 是的！Vercel的免费计划完全不需要任何支付方式。只需GitHub账号即可注册和使用。

### Q: PythonAnywhere需要国外手机号怎么办？

**A**:
- 使用Google Voice（免费）
- 或使用其他免费虚拟号码
- 或选择Glitch/Replit（不需要手机号）

### Q: Glitch稳定吗？

**A**:
- Glitch适合学习和个人项目
- 免费，但性能有限
- 如果不稳定可以随时迁移到其他平台

### Q: 如何更新代码？

**Vercel前端**：
```bash
git push
# Vercel自动检测并重新部署
```

**PythonAnywhere后端**：
- 上传新代码
- 在控制台重启Web应用

**Glitch后端**：
- 在Glitch界面修改代码
- 自动保存和部署

## 下一步

1. 先注册并部署前端到Vercel（最简单）
2. 然后选择一个后端平台部署
3. 配置前后端连接
4. 测试完整功能

需要帮助选择后端平台吗？或者您想先部署前端看看效果？
