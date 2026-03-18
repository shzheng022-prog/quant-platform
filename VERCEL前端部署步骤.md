# Vercel 快速部署指南

## 📋 部署前检查

- ✅ 已注册Vercel账号
- ✅ 代码已推送到GitHub: https://github.com/shzheng022-prog/quant-platform

## 🚀 三步部署前端到Vercel

### 第一步：导入项目

1. 访问 https://vercel.com/dashboard
2. 点击右上角 **"Add New..."** → **"Project"**
3. 在仓库列表中找到并点击 **`quant-platform`**
4. 点击 **"Import"**

### 第二步：配置项目

在项目配置页面，填写以下信息：

**框架设置：**
- Framework Preset: `Vite`
- Root Directory: `frontend`

**环境变量（重要）：**
- Name: `VITE_API_BASE_URL`
- Value: `https://quant-platform-backend.glitch.me` (先填这个，部署后端后再更新)

**构建设置：**
- Build Command: `npm install && npm run build`
- Output Directory: `dist`

### 第三步：部署

1. 点击底部 **"Deploy"** 按钮
2. 等待 2-3 分钟
3. 部署成功后，点击 **"Visit"** 查看您的网站

---

## 📦 部署后URL示例

部署成功后，您会得到一个类似这样的URL：
```
https://quant-platform.vercel.app
```

## 🔧 常见问题

### Q: 部署失败怎么办？
A: 检查以下几点：
1. `frontend/package.json` 是否存在
2. Node.js 版本是否兼容（建议使用16+）
3. 查看Vercel的部署日志

### Q: 如何更新代码？
A: 推送代码到GitHub后，Vercel会自动重新部署

### Q: 如何添加自定义域名？
A: 在项目设置 → Domains 中添加您的域名

---

## 🎯 下一步

前端部署成功后，继续部署后端到Glitch：
1. 访问 https://glitch.com
2. 创建新项目
3. 上传后端代码
