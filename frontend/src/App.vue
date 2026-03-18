<template>
  <el-container class="app-container">
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <h2>🚀 量化回测平台</h2>
      </div>
      <el-menu
        :default-active="currentRoute"
        class="menu"
        router
        background-color="transparent"
        text-color="#fff"
        active-text-color="#fff"
      >
        <el-menu-item index="/backtest">
          <el-icon><DataAnalysis /></el-icon>
          <span>策略回测</span>
        </el-menu-item>
        <el-menu-item index="/realtime">
          <el-icon><Monitor /></el-icon>
          <span>实时监控</span>
        </el-menu-item>
        <el-menu-item index="/portfolio">
          <el-icon><Wallet /></el-icon>
          <span>模拟交易</span>
        </el-menu-item>
      </el-menu>
      
      <div class="sidebar-footer">
        <div class="user-info">
          <el-avatar :size="40" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-details">
            <div class="user-name">量化交易员</div>
            <div class="user-role">VIP用户</div>
          </div>
        </div>
      </div>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <div class="header-left">
            <h1>{{ pageTitle }}</h1>
            <el-tag type="info" size="large" effect="plain">v2.0 专业版</el-tag>
          </div>
          <div class="header-right">
            <el-button :icon="Bell" circle size="large" />
            <el-button :icon="Setting" circle size="large" />
            <el-dropdown>
              <el-button :icon="MoreFilled" circle size="large" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item>
                    <el-icon><Setting /></el-icon>
                    系统设置
                  </el-dropdown-item>
                  <el-dropdown-item divided>
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  DataAnalysis,
  Monitor,
  Wallet,
  User,
  Bell,
  Setting,
  MoreFilled,
  SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()

const currentRoute = computed(() => route.path)
const pageTitle = computed(() => {
  const titles = {
    '/backtest': '策略回测',
    '/realtime': '实时监控',
    '/portfolio': '模拟交易'
  }
  return titles[route.path] || '量化回测平台'
})
</script>

<style scoped>
@import '@/assets/global.css';

.sidebar-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.2) 100%);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.user-role {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h1 {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 按钮渐变效果 */
.el-button:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: white;
}

/* 头部按钮悬停效果 */
.header-right .el-button {
  transition: all 0.3s ease;
}

.header-right .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}
</style>
