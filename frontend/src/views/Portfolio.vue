<template>
  <div class="portfolio-container">
    <el-row :gutter="24">
      <!-- 资产概览 -->
      <el-col :span="24">
        <el-card class="overview-card fade-in-up">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Wallet /></el-icon>
                资产概览
              </span>
              <el-button
                type="primary"
                size="default"
                @click="refreshPortfolio"
                :loading="loading"
                plain
              >
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          
          <el-row :gutter="24">
            <el-col :span="6">
              <div class="asset-card gradient-1">
                <div class="asset-icon">
                  <el-icon><Wallet /></el-icon>
                </div>
                <div class="asset-content">
                  <div class="asset-label">总资产</div>
                  <div class="asset-value">{{ formatCurrency(portfolio.total_value) }}</div>
                  <div class="asset-change positive">
                    <el-icon><TrendCharts /></el-icon>
                    +2.34%
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="asset-card gradient-2">
                <div class="asset-icon">
                  <el-icon><Money /></el-icon>
                </div>
                <div class="asset-content">
                  <div class="asset-label">可用资金</div>
                  <div class="asset-value">{{ formatCurrency(portfolio.cash) }}</div>
                  <div class="asset-change">
                    <el-icon><Check /></el-icon>
                    可用
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="asset-card" :class="getProfitCardClass()">
                <div class="asset-icon">
                  <el-icon><TrendCharts /></el-icon>
                </div>
                <div class="asset-content">
                  <div class="asset-label">总盈亏</div>
                  <div class="asset-value" :class="getProfitClass()">
                    {{ portfolio.profit >= 0 ? '+' : '' }}{{ formatCurrency(portfolio.profit) }}
                  </div>
                  <div class="asset-change" :class="getProfitClass()">
                    <el-icon><TrendCharts /></el-icon>
                    {{ (portfolio.profit_rate * 100).toFixed(2) }}%
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="asset-card gradient-4">
                <div class="asset-icon">
                  <el-icon><ShoppingCart /></el-icon>
                </div>
                <div class="asset-content">
                  <div class="asset-label">持仓数量</div>
                  <div class="asset-value">{{ portfolio.positions.length }}</div>
                  <div class="asset-change">
                    <el-icon><Grid /></el-icon>
                    {{ portfolio.positions.length > 0 ? '已持仓' : '空仓' }}
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      
      <!-- 持仓列表 -->
      <el-col :span="24">
        <el-card class="positions-card fade-in-up" style="animation-delay: 0.1s">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><List /></el-icon>
                持仓明细
              </span>
              <div class="header-actions">
                <el-button
                  type="primary"
                  size="default"
                  @click="showTradeDialog = true"
                >
                  <el-icon><Plus /></el-icon>
                  下单交易
                </el-button>
                <el-button
                  type="danger"
                  size="default"
                  @click="clearAllPositions"
                  :disabled="portfolio.positions.length === 0"
                  plain
                >
                  <el-icon><Delete /></el-icon>
                  清空持仓
                </el-button>
              </div>
            </div>
          </template>
          
          <el-table
            :data="portfolio.positions"
            style="width: 100%"
            stripe
            v-loading="loading"
            :header-cell-style="{ background: 'linear-gradient(90deg, #f8f9fa 0%, #fff 100%)' }"
          >
            <el-table-column type="index" label="#" width="60" align="center" />
            <el-table-column prop="code" label="代码" width="120" />
            <el-table-column prop="name" label="名称" width="150" />
            <el-table-column prop="amount" label="持仓数量" width="120" align="right">
              <template #default="{ row }">
                <span class="amount-text">{{ row.amount.toLocaleString() }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="cost" label="成本价" width="100" align="right">
              <template #default="{ row }">
                {{ row.cost.toFixed(3) }}
              </template>
            </el-table-column>
            <el-table-column prop="current_price" label="当前价" width="100" align="right">
              <template #default="{ row }">
                <span :class="row.current_price >= row.cost ? 'price-up' : 'price-down'">
                  {{ row.current_price.toFixed(3) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="市值" width="140" align="right">
              <template #default="{ row }">
                {{ formatCurrency(row.amount * row.current_price) }}
              </template>
            </el-table-column>
            <el-table-column label="盈亏" width="140" align="right">
              <template #default="{ row }">
                <div class="profit-cell">
                  <span :class="getProfitClass(row.profit)">
                    {{ row.profit >= 0 ? '+' : '' }}{{ formatCurrency(row.profit) }}
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="盈亏比例" width="120" align="right">
              <template #default="{ row }">
                <el-tag :type="row.profit >= 0 ? 'success' : 'danger'" size="small" effect="plain">
                  {{ row.profit_rate >= 0 ? '+' : '' }}{{ (row.profit_rate * 100).toFixed(2) }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right" align="center">
              <template #default="{ row }">
                <el-button
                  type="primary"
                  size="small"
                  @click="sellPosition(row)"
                  plain
                >
                  <el-icon><Selling /></el-icon>
                  卖出
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <el-empty
            v-if="portfolio.positions.length === 0 && !loading"
            description="暂无持仓，点击上方按钮开始交易"
          >
            <template #image>
              <div class="empty-icon">
                <el-icon :size="80"><ShoppingCart /></el-icon>
              </div>
            </template>
            <el-button type="primary" size="large" @click="showTradeDialog = true">
              开始交易
            </el-button>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 交易对话框 -->
    <el-dialog v-model="showTradeDialog" title="下单交易" width="600px" class="trade-dialog">
      <el-form :model="tradeForm" label-width="100px" size="large">
        <el-form-item label="交易类型">
          <el-radio-group v-model="tradeForm.type" size="large">
            <el-radio-button label="buy">
              <el-icon><Plus /></el-icon>
              买入
            </el-radio-button>
            <el-radio-button label="sell">
              <el-icon><Minus /></el-icon>
              卖出
            </el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="证券代码">
          <el-input
            v-model="tradeForm.code"
            placeholder="输入ETF代码，如：518880.XSHG"
            size="large"
            clearable
          >
            <template #append>
              <el-button @click="searchSecurity">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="证券名称" v-if="tradeForm.securityInfo" class="security-info">
          <div class="security-details">
            <el-tag type="info" size="large">{{ tradeForm.securityInfo.name }}</el-tag>
            <el-tag type="success" size="large" style="margin-left: 12px">
              ¥{{ tradeForm.securityInfo.price }}
            </el-tag>
          </div>
        </el-form-item>
        
        <el-form-item label="交易数量">
          <el-input-number
            v-model="tradeForm.amount"
            :min="100"
            :step="100"
            :step-strictly="true"
            style="width: 100%"
            :disabled="!tradeForm.securityInfo"
            size="large"
          />
          <div class="help-text">（必须为100的整数倍）</div>
        </el-form-item>
        
        <el-form-item label="预计金额">
          <div class="amount-display">
            <span class="amount-value">
              {{ tradeForm.securityInfo ? formatCurrency(tradeForm.amount * tradeForm.securityInfo.price) : '---' }}
            </span>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button size="large" @click="showTradeDialog = false">取消</el-button>
        <el-button
          type="primary"
          size="large"
          @click="submitOrder"
          :loading="submitting"
        >
          <el-icon><Check /></el-icon>
          提交订单
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import {
  Wallet,
  Refresh,
  Money,
  TrendCharts,
  Check,
  ShoppingCart,
  List,
  Plus,
  Delete,
  Selling,
  Search,
  Grid
} from '@element-plus/icons-vue'

const loading = ref(false)
const showTradeDialog = ref(false)
const submitting = ref(false)

const portfolio = reactive({
  total_value: 1000000,
  cash: 1000000,
  profit: 0,
  profit_rate: 0,
  positions: []
})

const tradeForm = reactive({
  type: 'buy',
  code: '',
  amount: 100,
  securityInfo: null
})

let refreshInterval = null

const formatCurrency = (value) => {
  return '¥' + value.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const getProfitClass = (profit = portfolio.profit) => {
  return profit >= 0 ? 'positive' : 'negative'
}

const getProfitCardClass = () => {
  return portfolio.profit >= 0 ? 'gradient-3' : 'gradient-5'
}

const refreshPortfolio = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/portfolio')
    Object.assign(portfolio, response.data)
    ElMessage.success('持仓已刷新')
  } catch (error) {
    ElMessage.error('获取持仓失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const searchSecurity = async () => {
  if (!tradeForm.code) {
    ElMessage.warning('请输入证券代码')
    return
  }
  
  try {
    const response = await axios.get('/api/realtime', {
      params: { security: tradeForm.code }
    })
    
    if (response.data.paused) {
      ElMessage.warning('该证券已停牌')
      return
    }
    
    tradeForm.securityInfo = {
      name: response.data.name,
      price: response.data.price,
      high_limit: response.data.high_limit,
      low_limit: response.data.low_limit
    }
  } catch (error) {
    ElMessage.error('查询失败: ' + error.message)
  }
}

const submitOrder = async () => {
  if (!tradeForm.securityInfo) {
    ElMessage.warning('请先搜索证券')
    return
  }
  
  submitting.value = true
  try {
    // 模拟提交订单
    await new Promise(resolve => setTimeout(resolve, 1500))
    ElMessage.success('订单提交成功')
    showTradeDialog.value = false
    await refreshPortfolio()
  } catch (error) {
    ElMessage.error('提交失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}

const sellPosition = async (position) => {
  try {
    await ElMessageBox.confirm(
      `确定要卖出 ${position.name} (${position.code}) 的全部持仓吗？`,
      '确认卖出',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    // 模拟卖出
    ElMessage.success('卖出成功')
    await refreshPortfolio()
  } catch (error) {
    // 用户取消
  }
}

const clearAllPositions = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有持仓吗？此操作不可撤销！',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    ElMessage.success('已清空所有持仓')
    await refreshPortfolio()
  } catch (error) {
    // 用户取消
  }
}

onMounted(async () => {
  await refreshPortfolio()
  
  // 每30秒刷新一次持仓
  refreshInterval = setInterval(refreshPortfolio, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.portfolio-container {
  height: 100%;
}

.overview-card,
.positions-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.card-header .el-icon {
  margin-right: 8px;
  color: #667eea;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.asset-card {
  display: flex;
  align-items: center;
  padding: 24px;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e8ecf1 100%);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.asset-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.gradient-1::before {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.gradient-2::before {
  background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
}

.gradient-3::before {
  background: linear-gradient(90deg, #00b09b 0%, #96c93d 100%);
}

.gradient-4::before {
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
}

.gradient-5::before {
  background: linear-gradient(90deg, #ff416c 0%, #ff4b2b 100%);
}

.asset-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.asset-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 20px;
  font-size: 28px;
  flex-shrink: 0;
}

.gradient-1 .asset-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-2 .asset-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.gradient-3 .asset-icon {
  background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
}

.gradient-4 .asset-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.gradient-5 .asset-icon {
  background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
}

.asset-content {
  flex: 1;
}

.asset-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
  font-weight: 500;
}

.asset-value {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
  line-height: 1;
}

.asset-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 500;
  color: #909399;
}

.asset-change.positive {
  color: #67C23A;
}

.asset-change.negative {
  color: #F56C6C;
}

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}

.price-up {
  color: #F56C6C;
}

.price-down {
  color: #67C23A;
}

.amount-text {
  font-weight: 600;
  color: #2c3e50;
}

.profit-cell {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.security-info {
  margin-bottom: 8px;
}

.security-details {
  display: flex;
  align-items: center;
  padding: 12px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e8ecf1 100%);
  border-radius: 8px;
}

.help-text {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.amount-display {
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
}

.amount-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: white;
}

.empty-icon {
  color: #dcdfe6;
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* 对话框美化 */
.trade-dialog .el-dialog__header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 24px;
}

.trade-dialog .el-dialog__title {
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.trade-dialog .el-dialog__close {
  color: white;
  font-size: 20px;
}

.trade-dialog .el-dialog__close:hover {
  color: white;
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in-up {
  animation: fadeInUp 0.6s ease-out;
}
</style>
