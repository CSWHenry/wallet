<template>
  <div class="request-container">
    <el-card class="request-card">
      <template #header>
        <div class="card-header">
          <h3>Request Money</h3>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="requestForm" label-position="top">
        <el-form-item label="Total Amount" prop="totalAmount">
          <el-input-number
            v-model="form.totalAmount"
            :min="0.01"
            :precision="2"
            :step="1"
            style="width: 100%"
            @change="handleTotalAmountChange"
          />
        </el-form-item>

        <div class="split-section">
          <div class="split-header">
            <h4>Split Between</h4>
            <el-button type="primary" link @click="addPayer">
              Add Person
            </el-button>
          </div>

          <div v-for="(payer, index) in form.payers" :key="index" class="payer-item">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item
                  :prop="'payers.' + index + '.identifier'"
                  :rules="rules.payerIdentifier"
                >
                  <el-input
                    v-model="payer.identifier"
                    placeholder="Enter email or phone number"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="10">
                <el-form-item
                  :prop="'payers.' + index + '.amount'"
                  :rules="rules.payerAmount"
                >
                  <el-input-number
                    v-model="payer.amount"
                    :min="0.01"
                    :precision="2"
                    :step="1"
                    style="width: 100%"
                    @change="calculateRemaining"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="2" class="delete-button">
                <el-button
                  type="danger"
                  circle
                  icon="Delete"
                  @click="removePayer(index)"
                  v-if="form.payers.length > 1"
                />
              </el-col>
            </el-row>
          </div>

          <div class="split-info">
            <el-alert
              v-if="remainingAmount !== 0"
              :title="'Remaining amount: $' + remainingAmount.toFixed(2)"
              :type="remainingAmount > 0 ? 'warning' : 'error'"
              show-icon
            />
            <el-button type="primary" link @click="splitEvenly">
              Split Evenly
            </el-button>
          </div>
        </div>

        <el-form-item label="Note (Optional)" prop="note">
          <el-input
            v-model="form.note"
            type="textarea"
            :rows="3"
            placeholder="Add a note"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleRequest"
            :loading="loading"
            :disabled="remainingAmount !== 0"
            class="request-button"
          >
            Send Request
          </el-button>
        </el-form-item>
      </el-form>

      <div class="recent-requests" v-if="recentRequests.length">
        <h4>Recent Requests</h4>
        <el-table :data="recentRequests" style="width: 100%">
          <el-table-column prop="from" label="From" />
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
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const form = reactive({
  totalAmount: 0,
  payers: [
    { identifier: '', amount: 0 }
  ],
  note: ''
})

// Mock data for recent requests
const recentRequests = ref([
  {
    from: 'alice@example.com',
    amount: 75.00,
    date: new Date('2024-01-15'),
    status: 'pending'
  },
  {
    from: '+1987654321',
    amount: 120.00,
    date: new Date('2024-01-14'),
    status: 'completed'
  }
])

const rules = {
  totalAmount: [
    { required: true, message: 'Please enter total amount', trigger: 'blur' },
    { type: 'number', min: 0.01, message: 'Amount must be greater than 0', trigger: 'blur' }
  ],
  payerIdentifier: [
    { required: true, message: 'Please enter email or phone', trigger: 'blur' }
  ],
  payerAmount: [
    { required: true, message: 'Please enter amount', trigger: 'blur' },
    { type: 'number', min: 0.01, message: 'Amount must be greater than 0', trigger: 'blur' }
  ]
}

const remainingAmount = computed(() => {
  const totalRequested = form.payers.reduce((sum, payer) => sum + (payer.amount || 0), 0)
  return form.totalAmount - totalRequested
})

const handleTotalAmountChange = () => {
  if (form.payers.length === 1) {
    form.payers[0].amount = form.totalAmount
  }
}

const addPayer = () => {
  form.payers.push({ identifier: '', amount: 0 })
}

const removePayer = (index) => {
  form.payers.splice(index, 1)
  calculateRemaining()
}

const calculateRemaining = () => {
  const remaining = remainingAmount.value
  if (remaining !== 0) {
    ElMessage.warning(`Remaining amount: $${remaining.toFixed(2)}`)
  }
}

const splitEvenly = () => {
  const evenAmount = form.totalAmount / form.payers.length
  form.payers.forEach(payer => {
    payer.amount = Number(evenAmount.toFixed(2))
  })
  // Adjust last payer's amount to account for rounding
  const totalSplit = form.payers.reduce((sum, payer) => sum + payer.amount, 0)
  const difference = form.totalAmount - totalSplit
  if (difference !== 0) {
    form.payers[form.payers.length - 1].amount += difference
  }
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

const handleRequest = async () => {
  loading.value = true
  try {
    // TODO: Implement request logic
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('Payment request sent successfully')
    form.totalAmount = 0
    form.payers = [{ identifier: '', amount: 0 }]
    form.note = ''
  } catch (error) {
    ElMessage.error('Request failed. Please try again.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.request-container {
  padding: 20px;
}

.request-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.split-section {
  margin: 20px 0;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.split-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.split-header h4 {
  margin: 0;
  color: #606266;
}

.payer-item {
  margin-bottom: 15px;
}

.delete-button {
  display: flex;
  align-items: center;
  justify-content: center;
}

.split-info {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.request-button {
  width: 100%;
}

.recent-requests {
  margin-top: 30px;
}

.recent-requests h4 {
  margin-bottom: 20px;
  color: #606266;
}
</style> 