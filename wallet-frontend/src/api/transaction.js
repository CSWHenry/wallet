import request from '../utils/request'
import { TRANSACTION_APIS } from '../config/api'

/**
 * 转账
 * @param {Object} data
 * @param {string} data.recipient_identifier - 收款人邮箱或手机号
 * @param {number} data.amount - 金额
 * @param {string} data.source_account - 支付账户
 * @param {string} data.note - 备注（可选）
 */
export const transfer = (data) => {
  return request({
    url: TRANSACTION_APIS.TRANSFER,
    method: 'post',
    data
  })
}

/**
 * 请求付款
 * @param {Object} data
 * @param {number} data.total_amount - 总金额
 * @param {string} data.note - 备注（可选）
 * @param {Array} data.payers - 付款人列表
 * @param {string} data.payers[].identifier - 付款人邮箱或手机号
 * @param {number} data.payers[].amount - 付款金额
 */
export const requestPayment = (data) => {
  return request({
    url: TRANSACTION_APIS.REQUEST,
    method: 'post',
    data
  })
}

/**
 * 获取交易列表
 * @param {Object} params
 * @param {string} params.type - 交易类型（可选）
 * @param {string} params.status - 交易状态（可选）
 * @param {string} params.startDate - 开始日期（可选）
 * @param {string} params.endDate - 结束日期（可选）
 */
export const getTransactions = (params) => {
  return request({
    url: TRANSACTION_APIS.LIST,
    method: 'get',
    params
  })
}

/**
 * 取消交易
 * @param {string} transactionId - 交易ID
 */
export const cancelTransaction = (transactionId) => {
  return request({
    url: TRANSACTION_APIS.CANCEL,
    method: 'post',
    data: { transaction_id: transactionId }
  })
} 