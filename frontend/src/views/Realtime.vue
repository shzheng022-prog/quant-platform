<template>
  <div class="realtime-container">
    <el-row :gutter="24">
      <!-- 左侧：ETF监控列表 -->
      <el-col :span="6">
        <el-card class="etf-list-card fade-in-up">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Monitor /></el-icon>
                ETF监控
              </span>
              <el-tag type="success" effect="plain">实时</el-tag>
            </div>
          </template>
          
          <el-input
            v-model="searchKeyword"
            placeholder="搜索ETF..."
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <div class="etf-list">
            <div
              v-for="(etf, index) in filteredEtfs"
              :key="etf.code"
              class="etf-item"
              :class="{ active: selectedEtf === etf.code }"
              @click="selectEtf(etf.code)"
              :style="{ animationDelay: `${index * 0.05}s` }"
            >
              <div class="etf-info">
                <div class="etf-code">{{ etf.code }}</div>
                <div class="etf-name">{{ etf.name }}</div>
              </div>
              <div class="etf-price" :class="getPriceClass(etf)">
                <el-icon v-if="etf.price > 0"><Top /></el-icon>
                <el-icon v-else><Bottom /></el-icon>
                <span>{{ formatPrice(etf.price) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：详情和图表 -->
      <el-col :span="18">
        <!-- ETF基本信息 -->
        <el-card class="info-card fade-in-up" style="animation-delay: 0.1s" v-if="selectedEtfData">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><InfoFilled /></el-icon>
                {{ selectedEtfData.name }}
              </span>
              <div class="header-actions">
                <el-tag type="info" effect="plain">{{ selectedEtfData.security }}</el-tag>
              </div>
            </div>
          </template>
          
          <el-row :gutter="24">
            <el-col :span="6">
              <div class="info-card-item gradient-1">
                <div class="info-icon">
                  <el-icon><PriceTag /></el-icon>
                </div>
                <div class="info-content">
                  <div class="info-label">当前价</div>
                  <div class="info-value" :class="priceClass">
                    {{ selectedEtfData.price }}
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-card-item gradient-2">
                <div class="info-icon">
                  <el-icon><Top /></el-icon>
                </div>
                <div class="info-content">
                  <div class="info-label">涨停价</div>
                  <div class="info-value positive">
                    {{ selectedEtfData.high_limit }}
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-card-item gradient-3">
                <div class="info-icon">
                  <el-icon><Bottom /></el-icon>
                </div>
                <div class="info-content">
                  <div class="info-label">跌停价</div>
                  <div class="info-value negative">
                    {{ selectedEtfData.low_limit }}
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="info-card-item gradient-4">
                <div class="info-icon">
                  <el-icon><Clock /></el-icon>
                </div>
                <div class="info-content">
                  <div class="info-label">更新时间</div>
                  <div class="info-value">
                    {{ updateTime }}
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
          
          <el-alert
            v-if="selectedEtfData.paused"
            title="该ETF已停牌"
            type="warning"
            :closable="false"
            show-icon
            style="margin-top: 20px"
          />
        </el-card>
        
        <!-- 实时图表 -->
        <el-card class="chart-card fade-in-up" style="animation-delay: 0.2s">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><TrendCharts /></el-icon>
                实时行情
              </span>
              <div class="header-actions">
                <el-tag type="info" effect="plain">AkShare</el-tag>
                <el-button
                  :icon="Refresh"
                  @click="refreshData"
                  :loading="loading"
                  size="default"
                  type="primary"
                  plain
                >
                  刷新
                </el-button>
              </div>
            </div>
          </template>
          
          <div ref="chartRef" style="width: 100%; height: 480px"></div>
        </el-card>
        
        <!-- 策略指标 -->
        <el-card class="metrics-card fade-in-up" style="animation-delay: 0.3s">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><DataAnalysis /></el-icon>
                策略指标
              </span>
              <el-button
                :icon="VideoPlay"
                @click="calculateMetrics"
                size="default"
                type="primary"
              >
                计算
              </el-button>
            </div>
          </template>
          
          <el-table
            :data="strategyMetrics"
            style="width: 100%"
            stripe
            v-loading="metricsLoading"
            :header-cell-style="{ background: 'linear-gradient(90deg, #f8f9fa 0%, #fff 100%)' }"
          >
            <el-table-column type="index" label="排名" width="80" align="center">
              <template #default="{ $index }">
                <el-tag v-if="$index < 3" :type="getRankTagType($index)" size="large">
                  {{ $index + 1 }}
                </el-tag>
                <span v-else class="rank-number">{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="etf" label="代码" width="120" />
            <el-table-column prop="etfName" label="名称" width="120" />
            <el-table-column label="年化收益率" align="right">
              <template #default="{ row }">
                <el-tag :type="row.annualizedReturns >= 0 ? 'success' : 'danger'" effect="plain">
                  {{ (row.annualizedReturns * 100).toFixed(2) }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="R²" align="center">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.rSquared * 100"
                  :color="getR2Color(row.rSquared)"
                  :show-text="true"
                  :format="() => row.rSquared.toFixed(4)"
                  :stroke-width="8"
                />
              </template>
            </el-table-column>
            <el-table-column label="综合得分" align="right">
              <template #default="{ row }">
                <span class="score-text" :style="{ color: getScoreColor(row.score) }">
                  {{ row.score.toFixed(4) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="短期年化" align="right">
              <template #default="{ row }">
                <el-tag :type="row.shortAnnualized >= 0 ? 'success' : 'danger'" size="small">
                  {{ (row.shortAnnualized * 100).toFixed(2) }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="row.score > 0 ? 'success' : 'danger'"
                  effect="plain"
                >
                  {{ row.score > 0 ? '通过' : '过滤' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'
import {
  Monitor,
  Search,
  Top,
  Bottom,
  InfoFilled,
  PriceTag,
  Clock,
  TrendCharts,
  Refresh,
  DataAnalysis,
  VideoPlay
} from '@element-plus/icons-vue'

const searchKeyword = ref('')
const selectedEtf = ref('518880.XSHG')
const selectedEtfData = ref(null)
const loading = ref(false)
const metricsLoading = ref(false)
const chartRef = ref(null)
const updateTime = ref('--')
let chartInstance = null
let refreshInterval = null

const etfList = ref([
  { code: '518880.XSHG', name: '黄金ETF', price: 4.567 },
  { code: '159985.XSHE', name: '豆粕ETF', price: 2.345 },
  { code: '501018.XSHG', name: '南方原油', price: 1.234 },
  { code: '161226.XSHE', name: '白银LOF', price: 3.456 },
  { code: '513100.XSHG', name: '纳指ETF', price: 6.789 },
  { code: '159915.XSHE', name: '创业板ETF', price: 2.567 },
  { code: '511220.XSHG', name: '城投债ETF', price: 100.234 }
])

const strategyMetrics = ref([])

const filteredEtfs = computed(() => {
  if (!searchKeyword.value) return etfList.value
  return etfList.value.filter(etf =>
    etf.code.includes(searchKeyword.value) ||
    etf.name.includes(searchKeyword.value)
  )
})

const priceClass = computed(() => {
  if (!selectedEtfData.value) return ''
  return selectedEtfData.price > 0 ? 'price-up' : 'price-down'
})

const getPriceClass = (etf) => {
  if (etf.price > 0) return 'price-up'
  if (etf.price < 0) return 'price-down'
  return ''
}

const formatPrice = (price) => {
  if (price === 0) return '---'
  return price.toFixed(3)
}

const getRankTagType = (index) => {
  const types = ['warning', 'success', 'info']
  return types[index] || ''
}

const getR2Color = (value) => {
  if (value >= 0.8) return '#67C23A'
  if (value >= 0.5) return '#409EFF'
  return '#E6A23C'
}

const getScoreColor = (score) => {
  if (score > 0.5) return '#67C23A'
  if (score > 0.2) return '#409EFF'
  if (score > 0) return '#E6A23C'
  return '#F56C6C'
}

const selectEtf = async (code) => {
  selectedEtf.value = code
  await fetchRealtimeData(code)
  await renderChart()
}

const fetchRealtimeData = async (code) => {
  loading.value = true
  try {
    const response = await axios.get('/api/realtime', {
      params: { security: code }
    })
    
    selectedEtfData.value = response.data
    updateTime.value = new Date().toLocaleTimeString('zh-CN')
    
    // 更新列表中的价格
    const etfIndex = etfList.value.findIndex(e => e.code === code)
    if (etfIndex >= 0) {
      etfList.value[etfIndex].price = response.data.price
    }
  } catch (error) {
    ElMessage.error('获取实时数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  await fetchRealtimeData(selectedEtf.value)
  ElMessage.success('数据已刷新')
}

const renderChart = async () => {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  // 生成模拟K线数据
  const dates = []
  const data = []
  let basePrice = selectedEtfData.value?.price || 4.5
  
  for (let i = 100; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(date.toISOString().split('T')[0])
    
    const open = basePrice * (0.995 + Math.random() * 0.01)
    const close = basePrice * (0.995 + Math.random() * 0.01)
    const low = Math.min(open, close) * (0.99 + Math.random() * 0.01)
    const high = Math.max(open, close) * (1 + Math.random() * 0.01)
    
    data.push([open.toFixed(3), close.toFixed(3), low.toFixed(3), high.toFixed(3)])
    basePrice = close
  }
  
  const option = {
    title: {
      text: `${selectedEtfData.value?.name || 'ETF'} - 实时行情`,
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 18,
        fontWeight: 600,
        color: '#2c3e50'
      }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e8e8e8',
      borderWidth: 1,
      textStyle: {
        color: '#2c3e50'
      },
      formatter: function(params) {
        const date = params[0].name
        const values = params[0].value
        return `
          <div style="padding: 12px;">
            <div style="font-weight: 600; margin-bottom: 8px;">${date}</div>
            <div>开盘: ${values[0]}</div>
            <div>收盘: ${values[1]}</div>
            <div>最低: ${values[2]}</div>
            <div>最高: ${values[3]}</div>
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#e8e8e8'
        }
      },
      axisLabel: {
        color: '#909399'
      }
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLine: {
        lineStyle: {
          color: '#e8e8e8'
        }
      },
      axisLabel: {
        color: '#909399'
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0',
          type: 'dashed'
        }
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 70,
        end: 100
      },
      {
        start: 70,
        end: 100,
        height: 30,
        bottom: 30,
        borderColor: '#e8e8e8',
        fillerColor: 'rgba(102, 126, 234, 0.1)',
        handleStyle: {
          color: '#667eea'
        }
      }
    ],
    series: [{
      name: 'K线',
      type: 'candlestick',
      data: data,
      itemStyle: {
        color: '#F56C6C',
        color0: '#67C23A',
        borderColor: '#F56C6C',
        borderColor0: '#67C23A',
        borderWidth: 2
      }
    }]
  }
  
  chartInstance.setOption(option)
}

const calculateMetrics = async () => {
  metricsLoading.value = true
  try {
    const response = await axios.post('/api/strategy/metrics', {
      etf_pool: etfList.value.map(e => e.code),
      lookback_days: 25,
      use_rsi_filter: true,
      use_short_momentum_filter: true
    })
    
    strategyMetrics.value = response.data.metrics || []
    ElMessage.success('指标计算完成')
  } catch (error) {
    ElMessage.error('计算失败: ' + (error.response?.data?.message || error.message))
  } finally {
    metricsLoading.value = false
  }
}

onMounted(async () => {
  await selectEtf(selectedEtf.value)
  await calculateMetrics()
  
  // 每10秒刷新一次数据
  refreshInterval = setInterval(() => {
    refreshData()
  }, 10000)
  
  window.addEventListener('resize', () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style scoped>
.realtime-container {
  height: 100%;
}

.etf-list-card,
.info-card,
.chart-card,
.metrics-card {
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

.search-input {
  margin-bottom: 20px;
}

.etf-list {
  max-height: calc(100vh - 350px);
  overflow-y: auto;
  padding-right: 8px;
}

.etf-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  margin-bottom: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  animation: slideIn 0.4s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.etf-item:hover {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.etf-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.etf-item.active .etf-code,
.etf-item.active .etf-name,
.etf-item.active .etf-price {
  color: white;
}

.etf-info {
  flex: 1;
}

.etf-code {
  font-weight: 600;
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 4px;
}

.etf-name {
  font-size: 12px;
  color: #909399;
}

.etf-price {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: bold;
  font-size: 16px;
}

.etf-price .el-icon {
  font-size: 18px;
}

.price-up {
  color: #F56C6C;
}

.price-down {
  color: #67C23A;
}

.info-card-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.info-card-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.info-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  flex-shrink: 0;
}

.gradient-1 .info-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-2 .info-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.gradient-3 .info-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.gradient-4 .info-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.info-content {
  flex: 1;
}

.info-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
  font-weight: 500;
}

.info-value {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
}

.info-value.positive {
  color: #67C23A;
}

.info-value.negative {
  color: #F56C6C;
}

.rank-number {
  font-size: 16px;
  font-weight: 600;
  color: #909399;
}

.score-text {
  font-weight: 600;
  font-size: 16px;
}

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
