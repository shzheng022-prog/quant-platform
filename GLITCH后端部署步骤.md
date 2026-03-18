# Glitch 后端部署指南

## 📋 准备工作

- ✅ 前端已部署到Vercel
- ✅ 拥有Glitch账号

## 🚀 五步部署后端到Glitch

### 第一步：创建项目

1. 访问 https://glitch.com
2. 点击 **"New Project"**
3. 选择 **"glitch-hello-python"** 模板

### 第二步：上传代码

在Glitch编辑器中：

1. 打开 `server.py`（或 `main.py`），删除所有内容
2. 将以下代码复制进去：

```python
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import pandas as pd
import numpy as np
import akshare as ak
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# 健康检查
@app.route('/health')
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

# ETF池查询
@app.route('/api/etf_pool')
def etf_pool():
    try:
        etf_list = ak.fund_etf_category_sina(symbol="ETF基金")
        if isinstance(etf_list, pd.DataFrame):
            etf_list = etf_list.head(50).to_dict('records')
        return jsonify({"success": True, "data": etf_list})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 股票实时行情
@app.route('/api/stock_quote', methods=['POST'])
def stock_quote():
    try:
        data = request.json
        code = data.get('code', '000001')
        quote = ak.stock_zh_a_spot_em()
        if isinstance(quote, pd.DataFrame):
            result = quote[quote['代码'] == code].to_dict('records')
            if result:
                return jsonify({"success": True, "data": result[0]})
        return jsonify({"success": False, "error": "未找到股票数据"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
```

3. 打开 `requirements.txt`，替换为：

```
flask==2.3.3
flask-cors==4.0.0
pandas==2.0.3
numpy==1.24.3
akshare>=1.10.0
python-dateutil==2.8.2
```

### 第三步：自动部署

- Glitch会自动检测到文件更改并重新部署
- 点击页面顶部的 **"Show"** 按钮预览您的应用
- 记录下后端URL，例如：`https://quant-platform-backend.glitch.me`

### 第四步：连接前端

1. 访问 https://vercel.com/dashboard
2. 找到您的 `quant-platform` 项目
3. 点击 **Settings** → **Environment Variables**
4. 更新环境变量：
   - Name: `VITE_API_BASE_URL`
   - Value: 您的Glitch后端URL（如 `https://quant-platform-backend.glitch.me`）
5. 点击 **Redeploy** 重新部署前端

### 第五步：测试

1. 访问您的前端URL（如：https://quant-platform.vercel.app）
2. 测试各项功能是否正常

---

## 🔧 常见问题

### Q: Glitch项目一直显示启动中怎么办？
A: 检查 `requirements.txt` 中的依赖版本，某些依赖可能需要调整

### Q: 后端API调用失败？
A: 
1. 检查Glitch日志（Logs标签页）
2. 确认CORS配置正确
3. 检查前端的环境变量设置

### Q: Glitch有免费限制吗？
A: 免费版有限制：
- 每天最多1000小时运行时间
- 休眠15分钟后会自动休眠
- 重新访问会唤醒

---

## 📝 总结

部署完成后，您将拥有：

✅ 前端: `https://quant-platform.vercel.app`
✅ 后端: `https://quant-platform-backend.glitch.me`

**完全免费，无需任何支付方式！** 🎉
