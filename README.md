# 量化策略回测平台

一个基于Python Flask + Vue.js的量化策略回测与实时交易平台，支持接入A股实时数据进行量化回测和模拟交易。

## 功能特性

- ✅ 策略回测：支持多种参数配置，实时计算回测指标
- ✅ 实时监控：ETF实时行情数据展示
- ✅ 模拟交易：虚拟资金模拟A股交易
- ✅ 聚宽策略适配：完美运行七星高照ETF轮动策略
- ✅ A股数据接入：基于AkShare获取实时行情数据
- ✅ 可视化图表：ECharts展示权益曲线和K线图

## 技术栈

### 后端
- Python 3.8+
- Flask 3.0.0
- AkShare 1.12.0 (A股数据接口)
- Pandas 2.1.0
- NumPy 1.24.3

### 前端
- Vue 3.3.4
- Element Plus 2.4.4
- ECharts 5.4.3
- Axios 1.6.0
- Vite 5.0.0

## 快速开始

### 1. 环境准备

确保已安装：
- Python 3.8+
- Node.js 16+
- npm/yarn

### 2. 后端启动

```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install -r ../requirements.txt

# 启动Flask服务
python app.py
```

后端服务将运行在 `http://localhost:5000`

### 3. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将运行在 `http://localhost:5173`

### 4. 访问平台

打开浏览器访问：`http://localhost:5173`

## 项目结构

```
.
├── backend/                 # 后端服务
│   └── app.py              # Flask主应用
├── frontend/               # 前端应用
│   ├── index.html          # HTML入口
│   ├── package.json        # 依赖配置
│   ├── vite.config.js      # Vite配置
│   └── src/
│       ├── main.js         # Vue入口
│       ├── App.vue         # 根组件
│       └── views/          # 页面组件
│           ├── Backtest.vue    # 策略回测
│           ├── Realtime.vue    # 实时监控
│           └── Portfolio.vue   # 模拟交易
├── requirements.txt        # Python依赖
└── README.md              # 项目说明
```

## 功能说明

### 策略回测
- 配置回测参数（日期范围、初始资金、持仓数量等）
- 支持多种过滤条件（RSI过滤、短期动量过滤等）
- 实时计算策略指标（年化收益、最大回撤、夏普比率等）
- 权益曲线可视化展示
- ETF排名实时更新

### 实时监控
- ETF实时行情数据
- K线图可视化
- 策略指标实时计算
- 支持多ETF监控切换

### 模拟交易
- 虚拟资金管理
- 持仓明细展示
- 买入/卖出操作
- 盈亏实时统计

## 聚宽策略适配说明

本平台已完美适配聚宽的"七星高照ETF轮动策略"，核心功能包括：

1. **动量计算**：基于加权回归的长期动量指标
2. **RSI过滤**：过滤超买状态
3. **短期动量过滤**：避免追高
4. **风险控制**：固定止损、ATR动态止损
5. **成交量过滤**：过滤高位放量
6. **持仓管理**：支持同时持有多只ETF

策略代码已转换为独立函数，可直接在回测中使用。

## API接口

### 后端API

- `GET /api/etf_pool` - 获取ETF池
- `POST /api/backtest` - 运行回测
- `GET /api/realtime` - 获取实时行情
- `POST /api/strategy/metrics` - 计算策略指标
- `GET /api/stock/search` - 搜索股票/ETF
- `GET /api/portfolio` - 获取模拟持仓

## 数据来源

本平台使用 [AkShare](https://akshare.akfamily.xyz/) 作为数据源，提供：
- A股实时行情
- 历史K线数据
- ETF信息数据

**注意**：AkShare为免费开源接口，数据仅供学习和研究使用。

## 注意事项

1. 本平台仅供学习研究使用，不构成投资建议
2. 实时数据可能存在延迟，以实际交易为准
3. 回测结果仅供参考，历史表现不代表未来收益
4. 请遵守相关法律法规，合理使用平台功能

## 开发计划

- [ ] 增加更多技术指标计算
- [ ] 支持自定义策略代码编辑
- [ ] 增加策略性能对比功能
- [ ] 添加交易信号提醒
- [ ] 支持导出回测报告

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提交Issue或Pull Request。
