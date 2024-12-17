<template>
  <div class="transactions-container">
    <el-card class="transactions-card">
      <template #header>
        <div class="card-header">
          <h3>Transaction History</h3>
          <div class="header-actions">
            <el-button type="primary" @click="exportTransactions">
              Export
            </el-button>
          </div>
        </div>
      </template>

      <div class="filters">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="Date Range">
              <el-date-picker
                v-model="filters.dateRange"
                type="daterange"
                range-separator="to"
                start-placeholder="Start date"
                end-placeholder="End date"
                style="width: 100%"
                @change="handleFilterChange"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="Type">
              <el-select
                v-model="filters.type"
                placeholder="All Types"
                style="width: 100%"
                @change="handleFilterChange"
              >
                <el-option label="All Types" value="" />
                <el-option label="Sent" value="sent" />
                <el-option label="Received" value="received" />
                <el-option label="Request" value="request" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="Status">
              <el-select
                v-model="filters.status"
                placeholder="All Status"
                style="width: 100%"
                @change="handleFilterChange"
              >
                <el-option label="All Status" value="" />
                <el-option label="Completed" value="completed" />
                <el-option label="Pending" value="pending" />
                <el-option label="Cancelled" value="cancelled" />
                <el-option label="Failed" value="failed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="Search">
              <el-input
                v-model="filters.search"
                placeholder="Search by ID, name, or email"
                @input="handleFilterChange"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <div class="summary-cards">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <div class="summary-header">
                  <span>Total Sent</span>
                  <el-tag type="danger">Outgoing</el-tag>
                </div>
              </template>
              <div class="summary-amount">
                ${{ totalSent.toFixed(2) }}
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <div class="summary-header">
                  <span>Total Received</span>
                  <el-tag type="success">Incoming</el-tag>
                </div>
              </template>
              <div class="summary-amount">
                ${{ totalReceived.toFixed(2) }}
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <div class="summary-header">
                  <span>Net Transfer</span>
                  <el-tag :type="netTransfer >= 0 ? 'success' : 'danger'">Balance</el-tag>
                </div>
              </template>
              <div class="summary-amount" :class="{ 'negative': netTransfer < 0 }">
                ${{ Math.abs(netTransfer).toFixed(2) }}
                <span class="direction">{{ netTransfer >= 0 ? 'Positive' : 'Negative' }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <div class="transactions-table">
        <el-table
          :data="filteredTransactions"
          style="width: 100%"
          :default-sort="{ prop: 'date', order: 'descending' }"
        >
          <el-table-column prop="date" label="Date" sortable width="150">
            <template #default="scope">
              {{ formatDate(scope.row.date) }}
            </template>
          </el-table-column>
          <el-table-column prop="type" label="Type" width="120">
            <template #default="scope">
              <el-tag :type="getTypeTag(scope.row.type)">
                {{ scope.row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="counterparty" label="Counterparty" />
          <el-table-column prop="amount" label="Amount" width="150" sortable>
            <template #default="scope">
              <span :class="{ 'amount-sent': scope.row.type === 'sent', 'amount-received': scope.row.type === 'received' }">
                ${{ scope.row.amount.toFixed(2) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="120">
            <template #default="scope">
              <el-tag :type="getStatusTag(scope.row.status)">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="note" label="Note" show-overflow-tooltip />
          <el-table-column label="Actions" width="120">
            <template #default="scope">
              <el-button
                v-if="scope.row.status === 'pending' && scope.row.type === 'sent'"
                type="danger"
                size="small"
                @click="cancelTransaction(scope.row)"
              >
                Cancel
              </el-button>
              <el-button
                type="primary"
                size="small"
                link
                @click="viewTransactionDetails(scope.row)"
              >
                Details
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            :total="totalTransactions"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-card>

    <!-- Transaction Details Dialog -->
    <el-dialog
      v-model="detailsDialogVisible"
      title="Transaction Details"
      width="600px"
    >
      <div v-if="selectedTransaction" class="transaction-details">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Transaction ID">
            {{ selectedTransaction.id }}
          </el-descriptions-item>
          <el-descriptions-item label="Date">
            {{ formatDate(selectedTransaction.date) }}
          </el-descriptions-item>
          <el-descriptions-item label="Type">
            <el-tag :type="getTypeTag(selectedTransaction.type)">
              {{ selectedTransaction.type }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Counterparty">
            {{ selectedTransaction.counterparty }}
          </el-descriptions-item>
          <el-descriptions-item label="Amount">
            ${{ selectedTransaction.amount.toFixed(2) }}
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTag(selectedTransaction.status)">
              {{ selectedTransaction.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Note">
            {{ selectedTransaction.note || 'No note' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

// Mock data for transactions
const transactions = ref([
  {
    id: 'TX123456',
    date: new Date('2024-01-15'),
    type: 'sent',
    counterparty: 'john@example.com',
    amount: 100.00,
    status: 'completed',
    note: 'Dinner payment'
  },
  {
    id: 'TX123457',
    date: new Date('2024-01-14'),
    type: 'received',
    counterparty: 'alice@example.com',
    amount: 50.00,
    status: 'completed',
    note: 'Movie tickets'
  },
  {
    id: 'TX123458',
    date: new Date('2024-01-13'),
    type: 'sent',
    counterparty: 'bob@example.com',
    amount: 75.00,
    status: 'pending',
    note: 'Shared utilities'
  }
])

const filters = reactive({
  dateRange: null,
  type: '',
  status: '',
  search: ''
})

const currentPage = ref(1)
const pageSize = ref(10)
const detailsDialogVisible = ref(false)
const selectedTransaction = ref(null)

const totalTransactions = computed(() => filteredTransactions.value.length)

const totalSent = computed(() => {
  return transactions.value
    .filter(t => t.type === 'sent' && t.status === 'completed')
    .reduce((sum, t) => sum + t.amount, 0)
})

const totalReceived = computed(() => {
  return transactions.value
    .filter(t => t.type === 'received' && t.status === 'completed')
    .reduce((sum, t) => sum + t.amount, 0)
})

const netTransfer = computed(() => totalReceived.value - totalSent.value)

const filteredTransactions = computed(() => {
  let result = transactions.value

  if (filters.dateRange) {
    const [start, end] = filters.dateRange
    result = result.filter(t => t.date >= start && t.date <= end)
  }

  if (filters.type) {
    result = result.filter(t => t.type === filters.type)
  }

  if (filters.status) {
    result = result.filter(t => t.status === filters.status)
  }

  if (filters.search) {
    const search = filters.search.toLowerCase()
    result = result.filter(t =>
      t.id.toLowerCase().includes(search) ||
      t.counterparty.toLowerCase().includes(search) ||
      t.note.toLowerCase().includes(search)
    )
  }

  return result
})

const formatDate = (date) => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const getTypeTag = (type) => {
  const types = {
    sent: 'danger',
    received: 'success',
    request: 'warning'
  }
  return types[type] || 'info'
}

const getStatusTag = (status) => {
  const types = {
    completed: 'success',
    pending: 'warning',
    cancelled: 'info',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const handleFilterChange = () => {
  currentPage.value = 1
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

const viewTransactionDetails = (transaction) => {
  selectedTransaction.value = transaction
  detailsDialogVisible.value = true
}

const cancelTransaction = async (transaction) => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to cancel this transaction?',
      'Warning',
      {
        confirmButtonText: 'Yes',
        cancelButtonText: 'No',
        type: 'warning'
      }
    )
    // TODO: Implement cancel transaction logic
    ElMessage.success('Transaction cancelled successfully')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to cancel transaction')
    }
  }
}

const exportTransactions = () => {
  // TODO: Implement export functionality
  ElMessage.success('Transactions exported successfully')
}
</script>

<style scoped>
.transactions-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  margin-bottom: 20px;
}

.summary-cards {
  margin-bottom: 20px;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-amount {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  text-align: center;
}

.summary-amount.negative {
  color: #f56c6c;
}

.direction {
  font-size: 14px;
  color: #909399;
  margin-left: 8px;
}

.amount-sent {
  color: #f56c6c;
}

.amount-received {
  color: #67c23a;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.transaction-details {
  padding: 20px;
}
</style> 