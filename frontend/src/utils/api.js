import axios from 'axios'
import { getToken } from './crypto'
import Cookies from 'js-cookie'

// 登录时携带 CSRF Token
const csrftoken = Cookies.get('csrftoken')
// 全局配置 Axios
axios.defaults.headers.common['X-CSRFToken'] = csrftoken
axios.defaults.withCredentials = true // 允许跨域携带 Cookie

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/polls',
  timeout: 1000,
  headers: {'X-Custom-Header': 'foobar'}
})

// 请求拦截器
api.interceptors.request.use(config => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截器
api.interceptors.response.use(response => {
  // 手动添加 'X-Content-Type-Options' 头
  response.headers['X-Content-Type-Options'] = 'nosniff'
  return response.data
}, error => {
  const status = error.response?.status
  if (status === 401) {
    localStorage.removeItem('authToken')
    window.location.reload()
  }
  return Promise.reject(error)
})

export default api