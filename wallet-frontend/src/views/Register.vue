<template>
  <div class="register-container">
    <el-card class="register-card">
      <div class="card-header">
        <h2>Create WALLET Account</h2>
        <el-button link type="primary" @click="fillExampleData">
          Fill with Example
        </el-button>
      </div>
      <el-form 
        :model="form" 
        :rules="rules" 
        ref="registerFormRef"
        label-position="top"
      >
        <div class="form-content">
          <el-form-item label="Full Name" prop="name" required>
            <el-input v-model="form.name" placeholder="Enter your full name" />
          </el-form-item>
          
          <el-form-item label="Social Security Number (SSN)" prop="ssn" required>
            <el-input 
              v-model="form.ssn" 
              placeholder="XXX-XX-XXXX"
              maxlength="11"
              @input="formatSSN"
            />
          </el-form-item>

          <el-form-item label="Email" prop="email" required>
            <div class="input-with-verify">
              <el-input 
                v-model="form.email" 
                placeholder="Enter your email"
              />
              <el-button 
                type="primary" 
                @click="verifyEmail" 
                :disabled="form.emailVerified"
                :loading="emailVerifying"
                class="verify-button"
              >
                {{ form.emailVerified ? 'Verified' : 'Verify' }}
              </el-button>
            </div>
          </el-form-item>

          <el-form-item label="Phone Number" prop="phone" required>
            <div class="input-with-verify">
              <el-input 
                v-model="form.phone" 
                placeholder="Enter your phone number"
              />
              <el-button 
                type="primary" 
                @click="verifyPhone" 
                :disabled="form.phoneVerified"
                :loading="phoneVerifying"
                class="verify-button"
              >
                {{ form.phoneVerified ? 'Verified' : 'Verify' }}
              </el-button>
            </div>
          </el-form-item>

          <el-form-item label="Password" prop="password" required>
            <el-input 
              v-model="form.password" 
              type="password" 
              placeholder="Create a password"
              show-password
            />
          </el-form-item>

          <el-form-item label="Confirm Password" prop="confirmPassword" required>
            <el-input 
              v-model="form.confirmPassword" 
              type="password" 
              placeholder="Confirm your password"
              show-password
            />
          </el-form-item>

          <el-form-item>
            <el-button 
              type="primary" 
              @click="handleRegister" 
              :loading="loading"
              :disabled="!form.emailVerified || !form.phoneVerified"
              class="submit-button"
            >
              Create Account
            </el-button>
          </el-form-item>
        </div>
      </el-form>
      <div class="login-link">
        <router-link to="/login">Already have an account? Login</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '../api/auth'

const router = useRouter()
const loading = ref(false)
const emailVerifying = ref(false)
const phoneVerifying = ref(false)
const registerFormRef = ref(null)

const form = reactive({
  name: '',
  ssn: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: '',
  emailVerified: false,
  phoneVerified: false
})

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('Please enter password'))
  } else {
    if (form.confirmPassword !== '') {
      if (form.password !== form.confirmPassword) {
        callback(new Error('Passwords do not match!'))
      }
    }
    callback()
  }
}

const validateConfirmPass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('Please confirm password'))
  } else if (value !== form.password) {
    callback(new Error('Passwords do not match!'))
  } else {
    callback()
  }
}

const rules = {
  name: [
    { required: true, message: 'Please enter your name', trigger: 'blur' },
    { min: 2, message: 'Name must be at least 2 characters', trigger: 'blur' }
  ],
  ssn: [
    { required: true, message: 'Please enter your SSN', trigger: 'blur' },
    { pattern: /^\d{3}-\d{2}-\d{4}$/, message: 'Invalid SSN format (XXX-XX-XXXX)', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter valid email', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: 'Please enter your phone number', trigger: 'blur' },
    { pattern: /^\+?1?\d{10}$/, message: 'Please enter valid 10-digit phone number', trigger: 'blur' }
  ],
  password: [
    { required: true, validator: validatePass, trigger: 'blur' },
    { min: 8, message: 'Password must be at least 8 characters', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPass, trigger: 'blur' }
  ]
}

const verifyEmail = async () => {
  if (!form.email) {
    ElMessage.warning('Please enter your email first')
    return
  }
  
  emailVerifying.value = true
  try {
    // 模拟验证过程
    await new Promise(resolve => setTimeout(resolve, 1000))
    form.emailVerified = true
    ElMessage.success('Email verified successfully')
  } catch (error) {
    ElMessage.error('Failed to verify email')
  } finally {
    emailVerifying.value = false
  }
}

const verifyPhone = async () => {
  if (!form.phone) {
    ElMessage.warning('Please enter your phone number first')
    return
  }
  
  phoneVerifying.value = true
  try {
    // 模拟验证过程
    await new Promise(resolve => setTimeout(resolve, 1000))
    form.phoneVerified = true
    ElMessage.success('Phone number verified successfully')
  } catch (error) {
    ElMessage.error('Failed to verify phone number')
  } finally {
    phoneVerifying.value = false
  }
}

const handleRegister = async () => {
  if (!form.emailVerified || !form.phoneVerified) {
    ElMessage.warning('Please verify both email and phone number')
    return
  }

  if (!registerFormRef.value) return

  try {
    loading.value = true
    // 表单验证
    await registerFormRef.value.validate()
    
    // 发送注册请求
    const response = await register({
      name: form.name,
      ssn: form.ssn.replace(/-/g, ''), // 移除SSN中的破折号
      email: form.email,
      phone: form.phone,
      password: form.password
    })

    console.log('Registration response:', response)
    ElMessage.success('Registration successful! Please login.')
    router.push('/login')
  } catch (error) {
    console.error('Registration error:', error)
    if (error.response) {
      // 处理特定的错误情况
      const errorMessage = error.response.data?.message
      if (errorMessage?.includes('email already registered')) {
        ElMessage.error('This email is already registered. Please use a different email or login.')
      } else if (errorMessage?.includes('phone already registered')) {
        ElMessage.error('This phone number is already registered. Please use a different number or login.')
      } else if (errorMessage?.includes('SSN already registered')) {
        ElMessage.error('This SSN is already registered. Please contact support if you believe this is an error.')
      } else {
        ElMessage.error(errorMessage || 'Registration failed')
      }
    } else if (error.request) {
      ElMessage.error('Network error. Please check if the server is running.')
    } else {
      ElMessage.error(error.message || 'Registration failed')
    }
  } finally {
    loading.value = false
  }
}

// SSN格式化函数
const formatSSN = (value) => {
  // 移除所有非数字字符
  const numbers = value.replace(/\D/g, '')
  
  // 根据输入的数字长度添加分隔符
  if (numbers.length <= 3) {
    form.ssn = numbers
  } else if (numbers.length <= 5) {
    form.ssn = `${numbers.slice(0, 3)}-${numbers.slice(3)}`
  } else {
    form.ssn = `${numbers.slice(0, 3)}-${numbers.slice(3, 5)}-${numbers.slice(5, 9)}`
  }
}

// 添加示例数据填充函数
const fillExampleData = () => {
  form.name = 'John Smith'
  form.ssn = '123-45-6789'
  form.email = 'john.smith@example.com'
  form.phone = '1234567890'
  form.password = 'Password123!'
  form.confirmPassword = 'Password123!'
}
</script>

<style scoped>
.register-container {
  min-height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--background-color);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 500px;
}

.register-card h2 {
  text-align: center;
  margin-bottom: 30px;
  color: var(--primary-color);
  font-size: 24px;
}

.form-content {
  width: 100%;
  padding: 0 20px;
}

.input-with-verify {
  display: flex;
  gap: 12px;
  align-items: center;
  width: 100%;
}

.input-with-verify .el-input {
  width: calc(100% - 102px); /* 102px = 按钮宽度(90px) + 间距(12px) */
}

.verify-button {
  width: 90px;
  height: 42px;
  padding: 0;
  flex-shrink: 0;
}

.submit-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
  margin-top: 20px;
}

.login-link {
  text-align: center;
  margin-top: 20px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
  width: 100%;
}

:deep(.el-input__wrapper) {
  width: 100%;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  padding-bottom: 8px;
}

:deep(.el-input__inner) {
  padding: 0 12px;
  height: 42px;
}

:deep(.el-form-item.is-required > .el-form-item__label::before) {
  color: #ff4949;
}

:deep(.el-form-item__content) {
  width: 100%;
}

:deep(.el-button) {
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.card-header h2 {
  margin: 0;
  color: var(--primary-color);
  font-size: 24px;
}
</style> 