<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>WALLET Login</h2>
      <el-form 
        :model="loginForm" 
        :rules="rules" 
        ref="loginFormRef"
        label-position="top"
      >
        <el-form-item prop="identifier" label="Email or Phone Number" required>
          <el-input
            v-model="loginForm.identifier"
            placeholder="Enter your email or phone number"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password" label="Password" required>
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="Enter your password"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin" 
            :loading="loading" 
            class="login-button"
          >
            Login
          </el-button>
        </el-form-item>
      </el-form>
      <div class="register-link">
        <router-link to="/register">Don't have an account? Register now</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '../api/auth'

const router = useRouter()
const loading = ref(false)
const loginFormRef = ref(null)

const loginForm = reactive({
  identifier: '',
  password: ''
})

const rules = {
  identifier: [
    { required: true, message: 'Please enter your email or phone number', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    loading.value = true
    // 表单验证
    await loginFormRef.value.validate()
    
    console.log('Sending login request...')  // 调试日志
    
    // 发送登录请求
    const response = await login(loginForm)
    
    console.log('Login response:', response)  // 调试日志
    
    // 显示成功消息
    ElMessage.success('Login successful')
    
    // 从响应中直接获取用户信息
    const { data } = response
    console.log('Login data:', data)  // 调试日志
    
    if (!data || !data.user) {
      throw new Error('Invalid response data')
    }
    
    const { user } = data
    console.log('User info:', user)  // 调试日志
    console.log('Is admin?', user.is_admin)  // 调试日志
    
    // 根据用户角色跳转到不同页面
    if (user.is_admin) {
      console.log('User is admin, redirecting to admin panel...')  // 调试日志
      // 使用 replace 而不是 push，防止用户返回到登录页
      await router.replace('/admin')
    } else {
      console.log('User is not admin, redirecting to dashboard...')  // 调试日志
      await router.replace({
        path: '/dashboard',
        query: { from: 'login' }
      })
    }
  } catch (error) {
    console.error('Login error:', error)
    if (error.response) {
      console.error('Error response:', error.response)  // 调试日志
      ElMessage.error(error.response.data?.message || 'Invalid credentials')
    } else if (error.request) {
      console.error('Error request:', error.request)  // 调试日志
      ElMessage.error('Network error. Please check your connection.')
    } else {
      console.error('Error details:', error)  // 调试日志
      ElMessage.error(error.message || 'Login failed')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--background-color);
}


.login-card {
  width: 100%;
  max-width: 400px;
  margin: 0 20px;
}

.login-card h2 {
  text-align: center;
  margin-bottom: 30px;
  color: var(--primary-color);
  font-size: 24px;
}

.login-button {
  width: 100%;
  padding: 12px 0;
  font-size: 16px;
}

.register-link {
  text-align: center;
  margin-top: 20px;
}

:deep(.el-input__wrapper) {
  width: 100%;
}

:deep(.el-input__inner) {
  padding: 12px;
  height: 42px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  padding-bottom: 8px;
}
</style> 