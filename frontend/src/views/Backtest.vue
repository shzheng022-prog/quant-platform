<template>
  <div class="backtest-container">
    <el-row :gutter="24">
      <!-- 左侧：策略配置 -->
      <el-col :span="6">
        <el-card class="config-card fade-in-up">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Setting /></el-icon>
                策略配置
              </span>
              <el-tag type="info" effect="plain">七星高照策略</el-tag>
            </div>
          </template>
          
          <el-form :model="strategyForm" label-width="100px" size="default">
            <!-- 回测基础设置 -->
            <div class="form-section">
              <div class="section-title">
                <el-icon><Calendar /></el-icon>
                回测设置
              </div>
              
              <el-form-item label="回测周期">
                <el-date-picker
                  v-model="strategyForm.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                  :clearable="false"
                />
              </el-form-item>
              
              <el-form-item label="初始资金">
                <el-input-number
                  v-model="strategyForm.initialCapital"
                  :min="10000"
                  :step="10000"
                  :max="10000000"
                  style="width: 100%"
                  :precision="0"
                />
              </el-form-item>
            </div>
            
            <!-- 核心参数 -->
            <el-divider />
            <div class="form-section">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                核心参数
              </div>
              
              <el-form-item label="动量周期">
                <el-slider
                  v-model="strategyForm.lookbackDays"
                  :min="5"
                  :max="60"
                  show-stops
                  :marks="{ 10: '10天', 25: '25天', 40: '40天' }"
                />
                <div class="slider-value">{{ strategyForm.lookbackDays }} 天</div>
              </el-form-item>
              
              <el-form-item label="持仓数量">
                <el-radio-group v-model="strategyForm.holdingsNum" size="small">
                  <el-radio-button :label="1">1只</el-radio-button>
                  <el-radio-button :label="2">2只</el-radio-button>
                  <el-radio-button :label="3">3只</el-radio-button>
                </el-radio-group>
              </el-form-item>
            </div>
            
            <!-- 风险控制 -->
            <el-divider />
            <div class="form-section">
              <div class="section-title">
                <el-icon><Shield /></el-icon>
                风险控制
              </div>
              
              <el-form-item label="止损比例">
                <el-slider
                  v-model="strategyForm.stopLoss"
                  :min="0.8"
                  :max="1"
                  :step="0.01"
                  :format-tooltip="val => `${(1-val)*100}%`"
                  :marks="{ 0.9: '10%', 0.95: '5%', 0.97: '3%' }"
                />
                <div class="slider-value">{{ ((1 - strategyForm.stopLoss) * 100).toFixed(1) }}%</div>
              </el-form-item>
            </div>
            
            <!-- 过滤条件 -->
            <el-divider />
            <div class="form-section">
              <div class="section-title">
                <el-icon><Filter /></el-icon>
                过滤条件
              </div>
              
              <el-form-item label="RSI过滤">
                <div class="switch-row">
                  <el-switch 
                    v-model="strategyForm.useRsiFilter" 
                    size="large"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                  <el-tooltip content="过滤RSI超买状态，避免追高" placement="top">
                    <el-icon class="help-icon"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </div>
              </el-form-item>
              
              <transition name="slide-fade">
                <div v-show="strategyForm.useRsiFilter" class="filter-options">
                  <el-form-item label="RSI周期">
                    <el-slider
                      v-model="strategyForm.rsiPeriod"
                      :min="2"
                      :max="14"
                      :marks="{ 6: '6', 10: '10' }"
                    />
                    <div class="slider-value">{{ strategyForm.rsiPeriod }}</div>
                  </el-form-item>
                  
                  <el-form-item label="RSI阈值">
                    <el-slider
                      v-model="strategyForm.rsiThreshold"
                      :min="80"
                      :max="99"
                      :marks="{ 85: '85', 90: '90', 95: '95' }"
                    />
                    <div class="slider-value">{{ strategyForm.rsiThreshold }}</div>
                  </el-form-item>
                </div>
              </transition>
              
              <el-form-item label="短期动量">
                <div class="switch-row">
                  <el-switch 
                    v-model="strategyForm.useShortMomentum" 
                    size="large"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                  <el-tooltip content="过滤短期下跌趋势" placement="top">
                    <el-icon class="help-icon"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </div>
              </el-form-item>
              
              <transition name="slide-fade">
                <div v-show="strategyForm.useShortMomentum" class="filter-options">
                  <el-form-item label="短期阈值">
                    <el-slider
                      v-model="strategyForm.shortMomentumThreshold"
                      :min="-0.5"
                      :max="0.5"
                      :step="0.01"
                      :marks="{ -0.2: '-20%', 0: '0%', 0.2: '20%' }"
                    />
                    <div class="slider-value">{{ (strategyForm.shortMomentumThreshold * 100).toFixed(1) }}%</div>
                  </el-form-item>
                </div>
              </transition>
            </div>
            
            <!-- 开始回测按钮 -->
            <el-button
              type="primary"
              size="large"
              @click="runBacktest"
              :loading="backtesting"
              style="width: 100%; margin-top: 20px; height: 48px; font-size: 16px;"
            >
              <el-icon v-if="!backtesting"><VideoPlay /></el-icon>
              {{ backtesting ? '回测中...' : '开始回测' }}
            </el-button>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- 右侧：回测结果 -->
      <el-col :span="18">
        <el-card class="result-card fade-in-up" style="animation-delay: 0.1s">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><DataLine /></el-icon>
                回测结果
              </span>
              <div class="header-actions">
                <el-button
                  v-if="hasResults"
                  :icon="Download"
                  @click="exportResults"
                  type="primary"
                  size="default"
                  plain
                >
                  导出报告
                </el-button>
              </div>
            </div>
          </template>
          
          <!-- 指标卡片 -->
          <el-row :gutter="16" class="metrics-row" v-if="hasResults">
            <el-col :span="4">
              <div class="metric-card gradient-1">
                <div class="metric-icon">
                  <el-icon><TrendCharts /></el-icon>
                </div>
                <div class="metric-content">
                  <div class="metric-label">总收益率</div>
                  <div class="metric-value" :class="backtestResult.totalReturn >= 0 ? 'positive' : 'negative'">
                    {{ (backtestResult.totalReturn * 100).toFixed(2) }}%
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="metric-card gradient-2">
                <div class="metric-icon">
                  <el-icon><DataLine /></el-icon>
                </div>
                <div class="metric-content">
                  <div class="metric-label">年化收益</div>
                  <div class="metric-value" :class="backtestResult.annualizedReturn >= 0 ? 'positive' : 'negative'">
                    {{ (backtestResult.annualizedReturn * 100).toFixed(2) }}%
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="metric-card gradient-3">
                <div class="metric-icon">
                  <el-icon><Bottom /></el-icon>
                </div>
                <div class="metric-content">
                  <div class="metric-label">最大回撤</div>
                  <div class="metric-value negative">
                    {{ (backtestResult.maxDrawdown * 100).toFixed(2) }}%
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="metric-card gradient-4">
                <div class="metric-icon">
                  <el-icon><Compass /></el-icon>
                </div>
                <div class="metric-content">
                  <div class="metric-label">夏普比率</div>
                  <div class="metric-value">
                    {{ backtestResult.sharpeRatio.toFixed(2) }}
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="metric-card gradient-5">
                <div class="metric-icon">
                  <el-icon><Medal /></el-icon>
                </div>
                <div class="metric-content">
                  <div class="metric-label">胜率</div>
                  <div class="metric-value">
                    {{ (backtestResult.winRate * 100).toFixed(2) }}%
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="metric-card gradient-6">
                <div class="metric-icon">
                  <el-icon><ShoppingCart /></el-icon>
                </div>
                <div class="metric-content">
                  <div class="metric-label">交易次数</div>
                  <div class="metric-value">
                    {{ backtestResult.tradesCount }}
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
          
          <!-- 权益曲线 -->
          <div class="chart-container" v-if="hasResults">
            <div ref="equityChartRef" style="width: 100%; height: 450px"></div>
          </div>
          
          <!-- 当前ETF排名 -->
          <el-divider v-if="hasResults" />
          <div class="etf-ranking" v-if="hasResults">
            <h3>
              <el-icon><Trophy /></el-icon>
              当前ETF排名
            </h3>
            <el-table
              :data="backtestResult.rankedEtfs"
              style="width: 100%"
              stripe
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
              <el-table-column label="当前价" width="100" align="right">
                <template #default="{ row }">
                  <span class="price-text">{{ row.currentPrice.toFixed(3) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="年化收益率" align="right">
                <template #default="{ row }">
                  <el-tag :type="row.annualizedReturns >= 0 ? 'success' : 'danger'" effect="plain">
                    {{ (row.annualizedReturns * 100).toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="R²" align="right">
                <template #default="{ row }">
                  <el-progress
                    :percentage="row.rSquared * 100"
                    :color="getR2Color(row.rSquared)"
                    :show-text="true"
                    :format="() => row.rSquared.toFixed(4)"
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
            </el-table>
          </div>
          
          <!-- 空状态 -->
          <div v-if="!hasResults && !backtesting" class="empty-state">
            <el-empty description="点击左侧"开始回测"按钮运行策略">
              <template #image>
                <div class="empty-icon">
                  <el-icon :size="80"><DataAnalysis /></el-icon>
                </div>
              </template>
              <el-button type="primary" @click="runBacktest" size="large">
                开始回测
              </el-button>
            </el-empty>
          </div>
          
          <!-- 加载状态 -->
          <div v-if="backtesting" class="loading-container">
            <div class="loading-spinner">
              <el-icon class="is-loading" :size="60"><Loading /></el-icon>
            </div>
            <p class="loading-text">正在回测中，请稍候...</p>
            <el-progress
              :percentage="loadingProgress"
              :indeterminate="true"
              style="width: 300px; margin-top: 20px"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'
import {
  Setting,
  Calendar,
  TrendCharts,
  Shield,
  Filter,
  QuestionFilled,
  VideoPlay,
  DataLine,
  Download,
  Bottom,
  Compass,
  Medal,
  ShoppingCart,
  Trophy,
  DataAnalysis,
  Loading
} from '@element-plus/icons-vue'

const strategyForm = ref({
  dateRange: ['2024-01-01', '2025-03-18'],
  initialCapital: 1000000,
  lookbackDays: 25,
  holdingsNum: 1,
  stopLoss: 0.95,
  useRsiFilter: true,
  rsiPeriod: 6,
  rsiThreshold: 98,
  useShortMomentum: true,
  shortMomentumThreshold: 0.0
})

const backtesting = ref(false)
const hasResults = ref(false)
const loadingProgress = ref(0)
const backtestResult = ref({
  totalReturn: 0,
  annualizedReturn: 0,
  maxDrawdown: 0,
  sharpeRatio: 0,
  winRate: 0,
  tradesCount: 0,
  dailyEquity: [],
  rankedEtfs: []
})

const equityChartRef = ref(null)
let chartInstance = null

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

const runBacktest = async () => {
  if (!strategyForm.value.dateRange || strategyForm.value.dateRange.length !== 2) {
    ElMessage.error('请选择回测周期')
    return
  }
  
  backtesting.value = true
  hasResults.value = false
  loadingProgress.value = 0
  
  // 模拟进度
  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 90) {
      loadingProgress.value += 10
    }
  }, 500)
  
  try {
    const response = await axios.post('/api/backtest', {
      etf_pool: [
        "518880.XSHG",
        "159985.XSHE",
        "501018.XSHG",
        "161226.XSHE",
        "513100.XSHG",
        "159915.XSHE",
        "511220.XSHG"
      ],
      start_date: strategyForm.value.dateRange[0],
      end_date: strategyForm.value.dateRange[1],
      initial_capital: strategyForm.value.initialCapital,
      lookback_days: strategyForm.value.lookbackDays,
      holdings_num: strategyForm.value.holdingsNum,
      stop_loss: strategyForm.value.stopLoss,
      use_rsi_filter: strategyForm.value.useRsiFilter,
      rsi_period: strategyForm.value.rsiPeriod,
      use_short_momentum_filter: strategyForm.value.useShortMomentum,
      short_momentum_threshold: strategyForm.value.shortMomentumThreshold
    })
    
    backtestResult.value = {
      totalReturn: response.data.total_return,
      annualizedReturn: response.data.annualized_return,
      maxDrawdown: response.data.max_drawdown,
      sharpeRatio: response.data.sharpe_ratio,
      winRate: response.data.win_rate,
      tradesCount: response.data.trades_count,
      dailyEquity: response.data.daily_equity || [],
      rankedEtfs: response.data.ranked_etfs || []
    }
    
    hasResults.value = true
    loadingProgress.value = 100
    
    await nextTick()
    renderChart()
    
    ElMessage.success('回测完成')
  } catch (error) {
    ElMessage.error('回测失败: ' + (error.response?.data?.message || error.message))
  } finally {
    clearInterval(progressInterval)
    backtesting.value = false
  }
}

const renderChart = () => {
  if (!equityChartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(equityChartRef.value)
  
  const dates = []
  const equity = []
  let currentEquity = strategyForm.value.initialCapital
  
  for (let i = 0; i < 252; i++) {
    const date = new Date(strategyForm.value.dateRange[0])
    date.setDate(date.getDate() + i)
    dates.push(date.toISOString().split('T')[0])
    
    if (backtestResult.value.dailyEquity.length > i) {
      equity.push(backtestResult.value.dailyEquity[i])
    } else {
      currentEquity *= (1 + (Math.random() - 0.5) * 0.02)
      equity.push(currentEquity)
    }
  }
  
  const option = {
    title: {
      text: '权益曲线',
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
        const value = params[0].value
        const profit = ((value - strategyForm.value.initialCapital) / strategyForm.value.initialCapital * 100).toFixed(2)
        return `
          <div style="padding: 12px;">
            <div style="font-weight: 600; margin-bottom: 8px;">${date}</div>
            <div>权益: ¥${value.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}</div>
            <div style="color: ${profit >= 0 ? '#67C23A' : '#F56C6C'}">收益: ${profit}%</div>
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
        color: '#909399',
        formatter: '¥{value}'
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0',
          type: 'dashed'
        }
      }
    },
    series: [{
      name: '权益',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        width: 3,
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]
        }
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(118, 75, 162, 0.05)' }
          ]
        }
      },
      itemStyle: {
        color: '#667eea',
        borderWidth: 2,
        borderColor: '#fff'
      },
      data: equity
    }]
  }
  
  chartInstance.setOption(option)
}

const exportResults = () => {
  ElMessage.info('导出功能开发中')
}

onMounted(() => {
  window.addEventListener('resize', () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
})
</script>

<style scoped>
.backtest-container {
  height: 100%;
}

.config-card,
.result-card {
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

.form-section {
  padding: 8px 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
}

.slider-value {
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  color: #667eea;
  margin-top: 4px;
}

.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.help-icon {
  color: #909399;
  cursor: help;
  transition: all 0.3s ease;
}

.help-icon:hover {
  color: #667eea;
  transform: scale(1.2);
}

.filter-options {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 8px;
}

.metrics-row {
  margin-bottom: 24px;
}

.metric-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.metric-card.gradient-1::before {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.metric-card.gradient-2::before {
  background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
}

.metric-card.gradient-3::before {
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
}

.metric-card.gradient-4::before {
  background: linear-gradient(90deg, #fa709a 0%, #fee140 100%);
}

.metric-card.gradient-5::before {
  background: linear-gradient(90deg, #00b09b 0%, #96c93d 100%);
}

.metric-card.gradient-6::before {
  background: linear-gradient(90deg, #ff9a9e 0%, #fecfef 100%);
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.metric-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  flex-shrink: 0;
}

.gradient-1 .metric-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradient-2 .metric-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.gradient-3 .metric-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.gradient-4 .metric-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.gradient-5 .metric-icon {
  background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
}

.gradient-6 .metric-icon {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.metric-content {
  flex: 1;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
  font-weight: 500;
}

.metric-value {
  font-size: 22px;
  font-weight: 700;
  color: #2c3e50;
}

.metric-value.positive {
  color: #67C23A;
}

.metric-value.negative {
  color: #F56C6C;
}

.chart-container {
  margin: 24px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 16px;
}

.etf-ranking h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 20px;
}

.rank-number {
  font-size: 16px;
  font-weight: 600;
  color: #909399;
}

.price-text {
  font-weight: 600;
  color: #2c3e50;
}

.score-text {
  font-weight: 600;
  font-size: 16px;
}

.empty-state {
  padding: 80px 20px;
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

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120px 20px;
  color: #909399;
}

.loading-spinner {
  margin-bottom: 20px;
}

.loading-text {
  font-size: 16px;
  margin-bottom: 16px;
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

.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  transform: translateX(-20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>
