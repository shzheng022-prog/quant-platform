# Render部署快速开始

## 🚀 一键部署到Render

### 前置要求

1. **GitHub账号**：用于存储代码
2. **Render账号**：用于部署服务（免费）
   - 注册地址：https://dashboard.render.com

### 部署步骤

#### 步骤1：准备代码

在项目根目录运行：

```bash
./deploy-to-render.sh
```

这个脚本会：
- ✅ 检查所有必需文件
- ✅ 初始化Git仓库（如果需要）
- ✅ 提交代码
- ✅ 推送到GitHub

如果脚本运行成功，会显示推送完成的信息。

#### 步骤2：在Render上部署

**方式A：使用Blueprint（推荐，自动化部署）**

1. 访问 https://dashboard.render.com
2. 登录后，点击右上角 **"New +"**
3. 选择 **"Blueprint"**
4. 连接您的GitHub仓库
5. 选择 `render.yaml` 文件
6. 点击 **"Apply Blueprint"**

Render会自动创建并部署前后端服务！

**方式B：手动部署**

详细步骤请查看：[Render部署指南.md](./Render部署指南.md)

#### 步骤3：等待部署完成

- 后端部署：3-5分钟
- 前端部署：2-3分钟

部署完成后，Render会显示您的服务URL：
- 前端：`https://quant-platform-frontend.onrender.com`
- 后端：`https://quant-platform-backend.onrender.com`

### 验证部署

1. 访问前端URL，确认页面正常显示
2. 测试回测功能
3. 测试实时行情功能

## 📋 项目结构

```
quant-platform/
├── backend/               # 后端服务
│   ├── app.py            # Flask应用
│   ├── strategy_adapter.py # 策略适配器
│   ├── Procfile          # Render启动配置 ✅
│   └── runtime.txt       # Python版本配置 ✅
├── frontend/             # 前端服务
│   ├── package.json
│   ├── vite.config.js
│   └── render-build.sh  # 构建脚本 ✅
├── requirements.txt      # Python依赖 ✅
├── render.yaml          # Render配置文件 ✅
└── deploy-to-render.sh  # 部署准备脚本 ✅
```

## 🔧 配置文件说明

### backend/Procfile
```
web: gunicorn app:app --host 0.0.0.0 --port $PORT --workers 2 --timeout 120
```

### backend/runtime.txt
```
python-3.9.16
```

### render.yaml
自动化部署配置，同时部署前后端服务。

## 💰 免费额度

Render提供永久免费实例：
- **后端**：512MB RAM, 0.1 CPU
- **前端**：静态站点托管
- **每月**：750小时运行时间
- **限制**：15分钟无请求会休眠

## ❓ 常见问题

### Q: 如何更新代码？

```bash
# 修改代码后
git add .
git commit -m "Update"
git push
```

Render会自动检测到推送并重新部署。

### Q: 实例休眠了怎么办？

首次访问需要30-60秒唤醒，之后会保持运行（有请求时）。

### Q: 如何查看部署日志？

在Render Dashboard：
1. 点击服务名称
2. 点击"Logs"标签
3. 查看实时日志

## 📚 详细文档

- [Render部署指南.md](./Render部署指南.md) - 详细的手动部署步骤
- [免费部署方案.md](./免费部署方案.md) - 其他部署方案对比
- [README.md](./README.md) - 项目说明文档

## 🎉 开始部署

准备好了吗？运行部署脚本开始吧！

```bash
./deploy-to-render.sh
```

然后按照步骤2在Render上部署您的量化平台。
