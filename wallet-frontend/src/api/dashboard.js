import request from '../utils/request'

/**
 * 获取仪表盘概览数据
 */
export const getDashboardOverview = () => {
  return request({
    url: '/dashboard/overview',
    method: 'get'
  })
}

/**
 * 获取最近交易记录
 * @param {Object} params
 * @param {number} params.limit - 获取条数
 */
export const getRecentTransactions = (params) => {
  return request({
    url: '/dashboard/recent-transactions',
    method: 'get',
    params
  })
}

/**
 * 获取用户资料
 */
export const getUserProfile = () => {
  return request({
    url: '/user/profile',
    method: 'get'
  })
} 