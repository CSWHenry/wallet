import request from '../utils/request'

/**
 * 获取所有用户账户信息
 */
export const getAllAccounts = () => {
  return request({
    url: 'admin/accounts',
    method: 'get'
  })
}

/**
 * 管理员执行转账操作
 * @param {Object} data
 * @param {string} data.from_account - 转出账户ID（可选，不传则从系统账户转出）
 * @param {string} data.to_account - 转入账户ID
 * @param {number} data.amount - 转账金额
 * @param {string} data.note - 转账备注（可选）
 */
export const adminTransfer = (data) => {
  return request({
    url: 'admin/transfer',
    method: 'post',
    data
  })
} 