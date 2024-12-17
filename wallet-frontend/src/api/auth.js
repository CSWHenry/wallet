import request from '../utils/request'
import { AUTH_APIS } from '../config/api'

/**
 * 用户登录
 * @param {Object} data
 * @param {string} data.identifier - 邮箱或手机号
 * @param {string} data.password - 密码
 */
export const login = (data) => {
  console.log('Login request:', data)  // 调试日志
  
  return request({
    url: AUTH_APIS.LOGIN,
    method: 'post',
    data
  }).then(response => {
    console.log('Login response:', response)  // 调试日志
    
    if (!response || !response.data) {
      throw new Error('Invalid response format')
    }
    
    const { user } = response.data
    console.log('User info:', user)  // 调试日志
    
    if (!user || typeof user.is_admin === 'undefined') {
      throw new Error('Invalid user data received')
    }
    
    // 保存用户信息
    localStorage.setItem('user', JSON.stringify(user))
    
    // 如果是管理员，设置标记
    if (user.is_admin) {
      localStorage.setItem('isAdmin', 'true')
    }
    
    console.log('Saved user:', user)  // 调试日志
    
    return response
  })
}

/**
 * 用户注册
 * @param {Object} data
 * @param {string} data.name - 用户名
 * @param {string} data.ssn - 社会安全号码（不带破折号）
 * @param {string} data.email - 邮箱
 * @param {string} data.phone - 手机号
 * @param {string} data.password - 密码
 */
export const register = (data) => {
  console.log('Sending registration request with data:', data)
  return request({
    url: AUTH_APIS.REGISTER,
    method: 'post',
    data,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

/**
 * 验证邮箱
 * @param {Object} data
 * @param {string} data.email - 邮箱
 */
export const verifyEmail = (data) => {
  return request({
    url: AUTH_APIS.VERIFY_EMAIL,
    method: 'post',
    data
  })
}

/**
 * 验证手机号
 * @param {Object} data
 * @param {string} data.phone - 手机号
 */
export const verifyPhone = (data) => {
  return request({
    url: AUTH_APIS.VERIFY_PHONE,
    method: 'post',
    data
  })
}

/**
 * 用户登出
 */
export const logout = () => {
  return request({
    url: AUTH_APIS.LOGOUT,
    method: 'post'
  })
} 