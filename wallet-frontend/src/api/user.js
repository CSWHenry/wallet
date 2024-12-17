import request from '../utils/request'

/**
 * 获取用户资料
 */
export const getUserProfile = () => {
  return request({
    url: '/api/user/profile',
    method: 'get'
  })
}

/**
 * 更新用户资料
 * @param {Object} data
 * @param {string} data.name - 用户名
 * @param {string} data.email - 邮箱
 * @param {string} data.phone - 电话号码
 */
export const updateUserProfile = (data) => {
  return request({
    url: '/api/user/profile',
    method: 'put',
    data
  })
}

/**
 * 更改密码
 * @param {Object} data
 * @param {string} data.oldPassword - 旧密码
 * @param {string} data.newPassword - 新密码
 */
export const changePassword = (data) => {
  return request({
    url: '/api/user/password',
    method: 'put',
    data
  })
}

/**
 * 添加新邮箱
 * @param {Object} data
 * @param {string} data.email - 新邮箱
 */
export const addEmail = (data) => {
  return request({
    url: '/api/user/emails',
    method: 'post',
    data
  })
}

/**
 * 添加新手机号
 * @param {Object} data
 * @param {string} data.phone - 新手机号
 */
export const addPhone = (data) => {
  return request({
    url: '/api/user/phones',
    method: 'post',
    data
  })
} 