<template>
  <div class="dashboard-container">
    <el-container>
      <el-aside width="250px">
        <div class="logo">
          <h2>WALLET</h2>
        </div>
        <el-menu
          router
          :default-active="$route.path"
          class="dashboard-menu"
        >
          <el-menu-item index="/dashboard">
            <el-icon><Monitor /></el-icon>
            <span>Dashboard</span>
          </el-menu-item>
          <el-menu-item index="/dashboard/transfer">
            <el-icon><Money /></el-icon>
            <span>Transfer Money</span>
          </el-menu-item>
          <el-menu-item index="/dashboard/request">
            <el-icon><Document /></el-icon>
            <span>Request Money</span>
          </el-menu-item>
          <el-menu-item index="/dashboard/accounts">
            <el-icon><CreditCard /></el-icon>
            <span>Bank Accounts</span>
          </el-menu-item>
          <el-menu-item index="/dashboard/transactions">
            <el-icon><List /></el-icon>
            <span>Transactions</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-container>
        <el-header>
          <div class="header-content">
            <div class="breadcrumb">
              <el-breadcrumb>
                <el-breadcrumb-item>Dashboard</el-breadcrumb-item>
                <el-breadcrumb-item>{{ currentPage }}</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            <div class="user-menu">
              <el-dropdown @command="handleCommand">
                <span class="user-profile">
                  <el-avatar size="small">{{ userInitials }}</el-avatar>
                  <span class="username">{{ userName }}</span>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">Profile</el-dropdown-item>
                    <el-dropdown-item command="settings">Settings</el-dropdown-item>
                    <el-dropdown-item divided command="logout">Logout</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>
        
        <el-main>
          <template v-if="$route.path === '/dashboard'">
            <div class="dashboard-overview">
              <!-- 余额卡片 -->
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-card shadow="hover" class="balance-card">
                    <template #header>
                      <div class="card-header">
                        <span>Total Balance</span>
                        <el-tag type="success">Available</el-tag>
                      </div>
                    </template>
                    <div class="balance-amount">
                      <h2>${{ totalBalance.toFixed(2) }}</h2>
                      <p>Across all accounts</p>
                    </div>
                  </el-card>
                </el-col>
                <el-col :span="8">
                  <el-card shadow="hover" class="balance-card">
                    <template #header>
                      <div class="card-header">
                        <span>Pending</span>
                        <el-tag type="warning">In Progress</el-tag>
                      </div>
                    </template>
                    <div class="balance-amount">
                      <h2>${{ pendingBalance.toFixed(2) }}</h2>
                      <p>Pending transactions</p>
                    </div>
                  </el-card>
                </el-col>
                <el-col :span="8">
                  <el-card shadow="hover" class="balance-card">
                    <template #header>
                      <div class="card-header">
                        <span>Monthly Activity</span>
                        <el-tag type="info">This Month</el-tag>
                      </div>
                    </template>
                    <div class="balance-amount">
                      <h2>${{ monthlyActivity.toFixed(2) }}</h2>
                      <p>Total transactions</p>
                    </div>
                  </el-card>
                </el-col>
              </el-row>

              <!-- 快速操作 -->
              <el-row :gutter="20" class="quick-actions">
                <el-col :span="24">
                  <h3>Quick Actions</h3>
                  <div class="action-buttons">
                    <el-button type="primary" @click="$router.push('/dashboard/transfer')">
                      <el-icon><Money /></el-icon>
                      Send Money
                    </el-button>
                    <el-button type="success" @click="$router.push('/dashboard/request')">
                      <el-icon><Document /></el-icon>
                      Request Money
                    </el-button>
                    <el-button type="info" @click="$router.push('/dashboard/accounts')">
                      <el-icon><CreditCard /></el-icon>
                      Add Bank Account
                    </el-button>
                  </div>
                </el-col>
              </el-row>

              <!-- 最近交易 -->
              <el-row :gutter="20" class="recent-transactions">
                <el-col :span="24">
                  <el-card>
                    <template #header>
                      <div class="card-header">
                        <h3>Recent Transactions</h3>
                        <el-button type="primary" link @click="$router.push('/dashboard/transactions')">
                          View All
                        </el-button>
                      </div>
                    </template>
                    <el-table :data="recentTransactions" style="width: 100%">
                      <el-table-column prop="date" label="Date" width="150">
                        <template #default="scope">
                          {{ formatDate(scope.row.date) }}
                        </template>
                      </el-table-column>
                      <el-table-column prop="type" label="Type" width="120">
                        <template #default="scope">
                          <el-tag :type="getTransactionType(scope.row.type)">
                            {{ scope.row.type }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="description" label="Description" />
                      <el-table-column prop="amount" label="Amount" width="150" align="right">
                        <template #default="scope">
                          <span :class="{ 'amount-negative': scope.row.amount < 0 }">
                            ${{ Math.abs(scope.row.amount).toFixed(2) }}
                          </span>
                        </template>
                      </el-table-column>
                    </el-table>
                  </el-card>
                </el-col>
              </el-row>
            </div>
          </template>
          <router-view v-else></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Monitor, Money, Document, CreditCard, List } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getDashboardOverview, getRecentTransactions } from '../api/dashboard'
import { getUserProfile } from '../api/user'

const router = useRouter()

// 用户信息（模拟数据）
const userName = ref('John Doe')
const userInitials = computed(() => {
  return userName.value.split(' ').map(n => n[0]).join('')
})

// 余额信息（模拟数据）
const totalBalance = ref(5280.50)
const pendingBalance = ref(150.75)
const monthlyActivity = ref(1234.56)

// 最近交易（模拟数据）
const recentTransactions = ref([
  {
    date: new Date('2024-01-15'),
    type: 'Sent',
    description: 'Payment to Alice',
    amount: -50.00
  },
  {
    date: new Date('2024-01-14'),
    type: 'Received',
    description: 'Payment from Bob',
    amount: 75.00
  },
  {
    date: new Date('2024-01-13'),
    type: 'Sent',
    description: 'Dinner split',
    amount: -25.50
  }
])

const currentPage = computed(() => {
  const path = router.currentRoute.value.path.split('/').pop()
  return path.charAt(0).toUpperCase() + path.slice(1)
})

const formatDate = (date) => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date)
}

const getTransactionType = (type) => {
  return type === 'Received' ? 'success' : 'danger'
}

const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      // TODO: Navigate to profile page
      break
    case 'settings':
      // TODO: Navigate to settings page
      break
    case 'logout':
      try {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        await router.push('/login')
        ElMessage.success('Logged out successfully')
      } catch (error) {
        console.error('Logout error:', error)
      }
      break
  }
}

// 在 setup 中添加数据加载逻辑
const loading = ref(false)
const error = ref(null)

const loadDashboardData = async () => {
  if (loading.value) return // 防止重复加载
  
  loading.value = true
  error.value = null
  
  try {
    // 从localStorage获取用户信息
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      userName.value = user.name
    } else {
      // 如果localStorage中没有，则从API获取
      const profileResponse = await getUserProfile()
      userName.value = profileResponse.name
      // 更新localStorage
      localStorage.setItem('user', JSON.stringify(profileResponse))
    }
    
    // 加载概览数据
    const overviewResponse = await getDashboardOverview()
    totalBalance.value = overviewResponse.total_balance || 0
    pendingBalance.value = overviewResponse.pending_balance || 0
    monthlyActivity.value = overviewResponse.monthly_activity || 0
    
    // 加载最近交易
    const transactionsResponse = await getRecentTransactions({ limit: 5 })
    recentTransactions.value = (transactionsResponse.transactions || []).map(tx => ({
      ...tx,
      date: new Date(tx.date)
    }))
  } catch (err) {
    console.error('Error loading dashboard data:', err)
    error.value = 'Failed to load dashboard data'
    
    // 只在非401错误时显示错误消息
    if (err.response?.status === 401) {
      // 清除token和用户信息
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    } else if (!err.response) {
      // 如果是网络错误，使用模拟数据
      console.log('Using mock data due to network error')
      totalBalance.value = 0
      pendingBalance.value = 0
      monthlyActivity.value = 0
      recentTransactions.value = []
    } else {
      ElMessage.error('Failed to load dashboard data')
    }
  } finally {
    loading.value = false
  }
}

// 添加自动重试逻辑
let retryCount = 0
const maxRetries = 3
const retryDelay = 2000 // 2秒

const loadDataWithRetry = async () => {
  try {
    await loadDashboardData()
  } catch (error) {
    if (retryCount < maxRetries) {
      retryCount++
      console.log(`Retrying (${retryCount}/${maxRetries}) in ${retryDelay}ms...`)
      setTimeout(loadDataWithRetry, retryDelay)
    }
  }
}

// 在组件挂载时加载数据
onMounted(() => {
  // 检查是否是从登录页面跳转来的
  const fromLogin = router.currentRoute.value.query.from === 'login'
  if (fromLogin) {
    ElMessage.success('Welcome back!')
  }
  loadDataWithRetry()
})
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  border-bottom: 1px solid var(--border-color);
}

.el-aside {
  background-color: #fff;
  border-right: 1px solid var(--border-color);
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid var(--border-color);
  padding: 0 20px;
}

.header-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-profile {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 10px;
  color: var(--text-color);
}

.dashboard-menu {
  border-right: none;
}

.el-menu-item {
  display: flex;
  align-items: center;
}

.el-menu-item .el-icon {
  margin-right: 10px;
}

/* Dashboard Overview Styles */
.dashboard-overview {
  padding: 20px;
}

.balance-card {
  height: 100%;
}

.balance-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.balance-amount {
  text-align: center;
  padding: 10px 0;
}

.balance-amount h2 {
  font-size: 28px;
  margin: 0;
  color: var(--text-color);
}

.balance-amount p {
  margin: 5px 0 0;
  color: var(--text-color-secondary);
  font-size: 14px;
}

.quick-actions {
  margin-top: 30px;
}

.quick-actions h3 {
  margin-bottom: 20px;
  color: var(--text-color);
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.action-buttons .el-button {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
}

.recent-transactions {
  margin-top: 30px;
}

.recent-transactions .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recent-transactions .card-header h3 {
  margin: 0;
  color: var(--text-color);
}

.amount-negative {
  color: var(--danger-color);
}
</style> 