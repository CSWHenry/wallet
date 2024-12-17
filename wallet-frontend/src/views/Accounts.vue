<template>
  <div class="accounts-container">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="accounts-list">
          <template #header>
            <div class="card-header">
              <h3>Linked Bank Accounts</h3>
              <el-button type="primary" @click="showAddAccountDialog">
                Add New Account
              </el-button>
            </div>
          </template>

          <div v-if="accounts.length === 0" class="no-accounts">
            <el-empty description="No bank accounts linked yet" />
          </div>

          <div v-else class="account-items">
            <div v-for="account in accounts" :key="account.id" class="account-item">
              <el-card shadow="hover">
                <div class="account-content">
                  <div class="account-info">
                    <h4>{{ account.bankName }}</h4>
                    <p class="account-number">Account ending in {{ account.accountNumber.slice(-4) }}</p>
                    <p class="account-type">{{ account.accountType }}</p>
                    <el-tag
                      :type="account.isPrimary ? 'success' : 'info'"
                      size="small"
                      class="account-status"
                    >
                      {{ account.isPrimary ? 'Primary Account' : 'Secondary Account' }}
                    </el-tag>
                    <el-tag
                      :type="account.isVerified ? 'success' : 'warning'"
                      size="small"
                      class="account-status"
                    >
                      {{ account.isVerified ? 'Verified' : 'Pending Verification' }}
                    </el-tag>
                  </div>
                  <div class="account-actions">
                    <el-button-group>
                      <el-button
                        v-if="!account.isPrimary"
                        type="primary"
                        @click="setPrimaryAccount(account.id)"
                      >
                        Set as Primary
                      </el-button>
                      <el-button
                        v-if="!account.isVerified"
                        type="warning"
                        @click="showVerificationDialog(account)"
                      >
                        Verify
                      </el-button>
                      <el-button
                        type="danger"
                        @click="unlinkAccount(account.id)"
                      >
                        Unlink
                      </el-button>
                    </el-button-group>
                  </div>
                </div>
              </el-card>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="verification-info">
          <template #header>
            <h3>Account Verification</h3>
          </template>
          <div class="verification-steps">
            <h4>How it works</h4>
            <ol>
              <li>Add your bank account details</li>
              <li>We'll make two small deposits (less than $1.00)</li>
              <li>Verify the exact amounts to confirm your account</li>
              <li>Deposits will be refunded after verification</li>
            </ol>
            <el-alert
              title="Security Notice"
              type="info"
              description="Your bank information is encrypted and secure. We use industry-standard security measures to protect your data."
              :closable="false"
              show-icon
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Add Account Dialog -->
    <el-dialog
      v-model="addAccountDialogVisible"
      title="Add Bank Account"
      width="500px"
    >
      <el-form :model="newAccount" :rules="accountRules" ref="accountForm" label-position="top">
        <el-form-item label="Bank Name" prop="bankName">
          <el-input v-model="newAccount.bankName" />
        </el-form-item>
        <el-form-item label="Account Type" prop="accountType">
          <el-select v-model="newAccount.accountType" style="width: 100%">
            <el-option label="Checking" value="checking" />
            <el-option label="Savings" value="savings" />
          </el-select>
        </el-form-item>
        <el-form-item label="Routing Number" prop="routingNumber">
          <el-input v-model="newAccount.routingNumber" maxlength="9" />
        </el-form-item>
        <el-form-item label="Account Number" prop="accountNumber">
          <el-input v-model="newAccount.accountNumber" maxlength="17" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addAccountDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="addAccount" :loading="loading">
            Add Account
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Verification Dialog -->
    <el-dialog
      v-model="verificationDialogVisible"
      title="Verify Bank Account"
      width="500px"
    >
      <el-form :model="verification" :rules="verificationRules" ref="verificationForm" label-position="top">
        <p class="verification-instruction">
          Enter the exact amounts of the two deposits made to your account:
        </p>
        <el-form-item label="First Deposit Amount" prop="amount1">
          <el-input-number
            v-model="verification.amount1"
            :precision="2"
            :step="0.01"
            :max="1"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Second Deposit Amount" prop="amount2">
          <el-input-number
            v-model="verification.amount2"
            :precision="2"
            :step="0.01"
            :max="1"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="verificationDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="verifyAccount" :loading="loading">
            Verify Account
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const addAccountDialogVisible = ref(false)
const verificationDialogVisible = ref(false)
const selectedAccount = ref(null)

// Mock data for bank accounts
const accounts = ref([
  {
    id: 1,
    bankName: 'Chase Bank',
    accountNumber: '****5678',
    accountType: 'Checking',
    isPrimary: true,
    isVerified: true
  },
  {
    id: 2,
    bankName: 'Bank of America',
    accountNumber: '****9012',
    accountType: 'Savings',
    isPrimary: false,
    isVerified: false
  }
])

const newAccount = reactive({
  bankName: '',
  accountType: '',
  routingNumber: '',
  accountNumber: ''
})

const verification = reactive({
  amount1: null,
  amount2: null
})

const accountRules = {
  bankName: [
    { required: true, message: 'Please enter bank name', trigger: 'blur' }
  ],
  accountType: [
    { required: true, message: 'Please select account type', trigger: 'change' }
  ],
  routingNumber: [
    { required: true, message: 'Please enter routing number', trigger: 'blur' },
    { pattern: /^\d{9}$/, message: 'Invalid routing number', trigger: 'blur' }
  ],
  accountNumber: [
    { required: true, message: 'Please enter account number', trigger: 'blur' },
    { pattern: /^\d{4,17}$/, message: 'Invalid account number', trigger: 'blur' }
  ]
}

const verificationRules = {
  amount1: [
    { required: true, message: 'Please enter first deposit amount', trigger: 'blur' }
  ],
  amount2: [
    { required: true, message: 'Please enter second deposit amount', trigger: 'blur' }
  ]
}

const showAddAccountDialog = () => {
  addAccountDialogVisible.value = true
}

const showVerificationDialog = (account) => {
  selectedAccount.value = account
  verificationDialogVisible.value = true
}

const addAccount = async () => {
  loading.value = true
  try {
    // TODO: Implement add account logic
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('Bank account added successfully')
    addAccountDialogVisible.value = false
  } catch (error) {
    ElMessage.error('Failed to add bank account')
  } finally {
    loading.value = false
  }
}

const verifyAccount = async () => {
  loading.value = true
  try {
    // TODO: Implement verification logic
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('Account verified successfully')
    verificationDialogVisible.value = false
  } catch (error) {
    ElMessage.error('Verification failed')
  } finally {
    loading.value = false
  }
}

const setPrimaryAccount = async (accountId) => {
  try {
    // TODO: Implement set primary account logic
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('Primary account updated successfully')
  } catch (error) {
    ElMessage.error('Failed to update primary account')
  }
}

const unlinkAccount = async (accountId) => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to unlink this account?',
      'Warning',
      {
        confirmButtonText: 'Unlink',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
    // TODO: Implement unlink account logic
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('Account unlinked successfully')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to unlink account')
    }
  }
}
</script>

<style scoped>
.accounts-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.account-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.account-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.account-info h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.account-number,
.account-type {
  margin: 5px 0;
  color: #606266;
}

.account-status {
  margin-right: 10px;
}

.verification-info {
  height: 100%;
}

.verification-steps {
  padding: 20px 0;
}

.verification-steps h4 {
  margin-bottom: 15px;
  color: #303133;
}

.verification-steps ol {
  padding-left: 20px;
  margin-bottom: 20px;
}

.verification-steps li {
  margin-bottom: 10px;
  color: #606266;
}

.verification-instruction {
  margin-bottom: 20px;
  color: #606266;
}

.no-accounts {
  padding: 40px 0;
}
</style> 