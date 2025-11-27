import axios from 'axios'
import { MessagePlugin } from 'tdesign-vue-next'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          MessagePlugin.error('登录已过期，请重新登录')
          window.location.reload()
          break
        case 403:
          MessagePlugin.error('权限不足')
          break
        case 404:
          MessagePlugin.error('请求的资源不存在')
          break
        case 500:
          MessagePlugin.error('服务器内部错误')
          break
        default:
          MessagePlugin.error(data.error || '请求失败')
      }
    } else if (error.request) {
      MessagePlugin.error('网络连接失败')
    } else {
      MessagePlugin.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default api