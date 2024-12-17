import axios from 'axios'

// API Base URL
axios.defaults.baseURL = 'http://localhost:5000/api'

// Auth APIs
export const AUTH_APIS = {
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  VERIFY_EMAIL: '/auth/verify-email',
  VERIFY_PHONE: '/auth/verify-phone',
  LOGOUT: '/auth/logout'
}

// Bank Account APIs
export const ACCOUNT_APIS = {
  LIST: '/accounts',
  ADD: '/accounts/add',
  VERIFY: '/accounts/verify',
  SET_PRIMARY: '/accounts/set-primary',
  REMOVE: '/accounts/remove'
}

// Transaction APIs
export const TRANSACTION_APIS = {
  TRANSFER: '/transactions/transfer',
  REQUEST: '/transactions/request',
  LIST: '/transactions',
  CANCEL: '/transactions/cancel'
}

// Response status
export const STATUS = {
  SUCCESS: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  SERVER_ERROR: 500
}

// Response messages
export const MESSAGES = {
  LOGIN_SUCCESS: 'Login successful',
  REGISTER_SUCCESS: 'Registration successful',
  TRANSFER_SUCCESS: 'Transfer successful',
  REQUEST_SUCCESS: 'Payment request sent successfully',
  ACCOUNT_ADDED: 'Bank account added successfully',
  ACCOUNT_VERIFIED: 'Bank account verified successfully',
  ACCOUNT_REMOVED: 'Bank account removed successfully'
} 