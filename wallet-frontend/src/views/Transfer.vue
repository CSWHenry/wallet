<template>
  <div class="transfer-container">
    <el-card class="transfer-card">
      <template #header>
        <div class="card-header">
          <h3>Transfer Money</h3>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="transferForm" label-position="top">
        <el-form-item label="Recipient" prop="recipient">
          <el-input
            v-model="form.recipient"
            placeholder="Enter email or phone number"
          />
        </el-form-item>

        <el-form-item label="Amount" prop="amount">
          <el-input-number
            v-model="form.amount"
            :min="0.01"
            :precision="2"
            :step="1"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="Source Account" prop="sourceAccount">
          <el-select v-model="form.sourceAccount" placeholder="Select source account" style="width: 100%">
            <el-option
              v-for="account in bankAccounts"
              :key="account.id"
              :label="account.name"
              :value="account.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Note (Optional)" prop="note">
          <el-input
            v-model="form.note"
            type="textarea"
            :rows="3"
            placeholder="Add a note"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleTransfer" :loading="loading" class="transfer-button">
            Send Money
          </el-button>
        </el-form-item>
      </el-form>

      <div class="recent-transfers" v-if="recentTransfers.length">
        <h4>Recent Transfers</h4>
        <el-table :data="recentTransfers" style="width: 100%">
          <el-table-column prop="recipient" label="Recipient" />
          <el-table-column prop="amount" label="Amount">
            <template #default="scope">
              ${{ scope.row.amount.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="date" label="Date">
            <template #default="scope">
              {{ formatDate(scope.row.date) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const form = reactive({
  recipient: '',
  amount: 0,
  sourceAccount: '',
  note: ''
})

// Mock data for bank accounts
const bankAccounts = ref([
  { id: 1, name: 'Primary Checking Account (*1234)' },
  { id: 2, name: 'Savings Account (*5678)' }
])

// Mock data for recent transfers
const recentTransfers = ref([
  {
    recipient: 'john@example.com',
    amount: 100.00,
    date: new Date('2024-01-15'),
    status: 'completed'
  },
  {
    recipient: '+1234567890',
    amount: 50.00,
    date: new Date('2024-01-14'),
    status: 'pending'
  }
])

const rules = {
  recipient: [
    { required: true, message: 'Please enter recipient email or phone', trigger: 'blur' }
  ],
  amount: [
    { required: true, message: 'Please enter amount', trigger: 'blur' },
    { type: 'number', min: 0.01, message: 'Amount must be greater than 0', trigger: 'blur' }
  ],
  sourceAccount: [
    { required: true, message: 'Please select source account', trigger: 'blur' }
  ]
}

const formatDate = (date) => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date)
}

const getStatusType = (status) => {
  const types = {
    completed: 'success',
    pending: 'warning',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const handleTransfer = async () => {
  loading.value = true
  try {
    // TODO: Implement transfer logic
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('Transfer initiated successfully')
    form.recipient = ''
    form.amount = 0
    form.note = ''
  } catch (error) {
    ElMessage.error('Transfer failed. Please try again.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.transfer-container {
  padding: 20px;
}

.transfer-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.transfer-button {
  width: 100%;
}

.recent-transfers {
  margin-top: 30px;
}

.recent-transfers h4 {
  margin-bottom: 20px;
  color: #606266;
}
</style> 