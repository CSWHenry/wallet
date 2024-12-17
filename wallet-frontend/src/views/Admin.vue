<template>
  <div class="admin-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>Wallet Admin Panel</h2>
          <el-button type="danger" @click="handleLogout">Logout</el-button>
        </div>
      </el-header>
      
      <el-main>
        <!-- 账户列表 -->
        <el-card class="account-list">
          <template #header>
            <div class="card-header">
              <h3>All Accounts</h3>
              <el-button type="primary" @click="refreshAccounts">Refresh</el-button>
            </div>
          </template>
          
          <el-table 
            :data="accounts" 
            style="width: 100%"
            v-loading="loading"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="Name" width="150" />
            <el-table-column prop="email" label="Email" width="200" />
            <el-table-column prop="phone" label="Phone" width="150" />
            <el-table-column prop="balance" label="Balance" width="150">
              <template #default="scope">
                ${{ scope.row.balance.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="200">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small"
                  @click="openTransferDialog(scope.row)"
                >
                  Transfer
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 转账表单 -->
        <el-dialog
          v-model="transferDialogVisible"
          title="Admin Transfer"
          width="500px"
        >
          <el-form
            ref="transferFormRef"
            :model="transferForm"
            :rules="transferRules"
            label-width="120px"
          >
            <el-form-item label="From Account">
              <el-select
                v-model="transferForm.from_account"
                placeholder="Select source account (optional)"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="account in accounts"
                  :key="account.id"
                  :label="account.name + ' - $' + account.balance.toFixed(2)"
                  :value="account.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="To Account" prop="to_account">
              <el-select
                v-model="transferForm.to_account"
                placeholder="Select target account"
                style="width: 100%"
              >
                <el-option
                  v-for="account in accounts"
                  :key="account.id"
                  :label="account.name + ' - $' + account.balance.toFixed(2)"
                  :value="account.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="Amount" prop="amount">
              <el-input
                v-model.number="transferForm.amount"
                type="number"
                placeholder="Enter amount"
              >
                <template #prefix>$</template>
              </el-input>
            </el-form-item>

            <el-form-item label="Note" prop="note">
              <el-input
                v-model="transferForm.note"
                type="textarea"
                placeholder="Enter transfer note"
              />
            </el-form-item>
          </el-form>

          <template #footer>
            <span class="dialog-footer">
              <el-button @click="transferDialogVisible = false">Cancel</el-button>
              <el-button
                type="primary"
                @click="handleTransfer"
                :loading="transferLoading"
              >
                Confirm Transfer
              </el-button>
            </span>
          </template>
        </el-dialog>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllAccounts, adminTransfer } from '../api/admin'

const router = useRouter()
const loading = ref(false)
const transferLoading = ref(false)
const accounts = ref([])
const transferDialogVisible = ref(false)
const transferFormRef = ref(null)

// 转账表单数据
const transferForm = reactive({
  from_account: '',
  to_account: '',
  amount: '',
  note: ''
})

// 转账表单验证规则
const transferRules = {
  to_account: [
    { required: true, message: 'Please select target account', trigger: 'change' }
  ],
  amount: [
    { required: true, message: 'Please enter amount', trigger: 'blur' },
    { type: 'number', min: 0.01, message: 'Amount must be greater than 0', trigger: 'blur' }
  ]
}

// 加载所有账户信息
const loadAccounts = async () => {
  loading.value = true
  try {
    const response = await getAllAccounts()
    accounts.value = response.accounts
  } catch (error) {
    console.error('Failed to load accounts:', error)
    ElMessage.error('Failed to load accounts')
  } finally {
    loading.value = false
  }
}

// 刷新账户列表
const refreshAccounts = async () => {
  loading.value = true
  try {
    console.log('Refreshing accounts list...')
    const response = await getAllAccounts()
    accounts.value = response.accounts
    ElMessage.success('Account list refreshed successfully')
  } catch (error) {
    console.error('Failed to refresh accounts:', error)
    ElMessage.error('Failed to refresh accounts')
  } finally {
    loading.value = false
  }
}

// 打开转账对话框
const openTransferDialog = (account) => {
  transferForm.to_account = account.id
  transferDialogVisible.value = true
}

// 处理转账
const handleTransfer = async () => {
  if (!transferFormRef.value) return
  
  try {
    await transferFormRef.value.validate()
    
    // 二次确认
    await ElMessageBox.confirm(
      'Are you sure you want to perform this transfer?',
      'Confirmation',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
    
    transferLoading.value = true
    
    // 执行转账
    await adminTransfer({
      from_account: transferForm.from_account || undefined,
      to_account: transferForm.to_account,
      amount: transferForm.amount,
      note: transferForm.note
    })
    
    ElMessage.success('Transfer completed successfully')
    transferDialogVisible.value = false
    
    // 重新加载账户列表
    await loadAccounts()
    
  } catch (error) {
    if (error === 'cancel') return
    
    console.error('Transfer failed:', error)
    ElMessage.error(error.response?.data?.message || 'Transfer failed')
  } finally {
    transferLoading.value = false
  }
}

// 处理登出
const handleLogout = async () => {
  try {
    localStorage.removeItem('token')
    localStorage.removeItem('isAdmin')
    await router.push('/login')
    ElMessage.success('Logged out successfully')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadAccounts()
})
</script>

<style scoped>
.admin-container {
  height: 100vh;
  background-color: var(--background-color);
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid var(--border-color);
  padding: 0 20px;
}

.header-content {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-content h2 {
  color: var(--primary-color);
  margin: 0;
}

.el-main {
  padding: 20px;
}

.account-list {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: var(--text-color);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 