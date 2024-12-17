import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import { STATUS } from '../config/api'

// 创建axios实例
const request = axios.create({
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 打印当前请求的URL
    console.log('Requesting URL:', config.url)
    
    // 确保所有请求都有正确的 Content-Type
    config.headers['Content-Type'] = 'application/json'
    
    // 从localStorage获取token，除了登录和注册接口外都需要带token
    if (!config.url.includes('/auth/login') && !config.url.includes('/auth/register')) {
      const token = localStorage.getItem('token')
      console.log('Current token in localStorage:', token)
      
      if (token) {
        // 如果 token 已经包含 Bearer 前缀，直接使用；否则添加前缀
        const finalToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`
        config.headers['Authorization'] = finalToken
        
        // 打印完整的请求头
        console.log('Request headers:', config.headers)
      } else {
        console.warn('No token found in localStorage for URL:', config.url)
      }
    } else {
      console.log('Skipping token for auth endpoint')
    }

    // 打印完整请求配置
    console.log('Full request config:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      data: config.data,
      baseURL: config.baseURL,
      timeout: config.timeout
    })

    return config
  },
  error => {
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    
    // 打印完整响应信息
    console.log('Full response:', {
      url: response.config.url,
      status: response.status,
      data: res,
      headers: response.headers
    })
    
    // 如果有错误信息，显示错误信息
    if (res.error) {
      console.error('API Error:', res.error)
      ElMessage.error(res.error)
      return Promise.reject(new Error(res.error))
    }
    
    // 如果是登录响应，确保token被正确存储
    if (response.config.url.includes('/auth/login') && res.data?.access_token) {
      const token = res.data.access_token
      console.log('Storing new token from login:', token)
      localStorage.setItem('token', token)
    }
    
    // 如果有成功信息，显示成功信息（登录接口除外）
    if (res.message && response.config.method !== 'get' && !response.config.url.includes('/auth/login')) {
      ElMessage.success(res.message)
    }
    
    return res
  },
  error => {
    console.error('Response error details:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
      headers: error.response?.headers
    })

    if (error.response) {
      // 服务器返回错误状态码
      switch (error.response.status) {
        case STATUS.UNAUTHORIZED:
          console.error('Unauthorized error:', {
            url: error.config.url,
            data: error.response.data,
            headers: error.response.headers
          })
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          localStorage.removeItem('isAdmin')
          router.push('/login')
          ElMessage.error(error.response.data?.message || 'Session expired, please login again')
          break
          
        case 422:
          console.error('Token validation error:', {
            url: error.config.url,
            data: error.response.data,
            headers: error.response.headers
          })
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          localStorage.removeItem('isAdmin')
          router.push('/login')
          ElMessage.error(error.response.data?.message || 'Invalid token, please login again')
          break
          
        case STATUS.FORBIDDEN:
          ElMessage.error(error.response.data?.message || 'Access denied')
          break
          
        case STATUS.NOT_FOUND:
          ElMessage.error(error.response.data?.message || 'Resource not found')
          break
          
        case STATUS.SERVER_ERROR:
          ElMessage.error(error.response.data?.message || 'Server error, please try again later')
          break
          
        default:
          ElMessage.error(error.response.data?.message || 'Request failed')
      }
    } else if (error.request) {
      console.error('Request error:', error.request)
      if (error.code === 'ECONNABORTED') {
        ElMessage.error('Request timeout, please try again')
      } else {
        ElMessage.error('Network error, please check your connection and server status')
      }
    } else {
      ElMessage.error('Request configuration error')
    }
    
    return Promise.reject(error)
  }
)

export default request 