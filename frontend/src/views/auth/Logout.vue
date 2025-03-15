<template>
  <div>
    <h1>正在注销...</h1>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import { useStore } from 'vuex'

export default {
  name: 'Logout',
  setup() {
    const router = useRouter()
    const store = useStore()
    const errorMessage = ref('')

    const handleLogout = async () => {

      try {
        // 发送注销请求
        const response = await api.post('/api/logout/', {}, {
          headers: { 'Content-Type': 'application/json' }
        })
        

        // 处理注销成功
        console.log('注销响应:', response)

        // 清除本地存储中的身份验证令牌
        localStorage.removeItem('authToken')

        // 移除所有axios请求头中的Authorization字段
        delete api.defaults.headers.common['Authorization']

        // 清楚所有pending请求
        const controller = new AbortController()
        controller.abort()

        // 重置Vuex状态
        store.commit('auth/CLEAR_AUTH_USER')

        // 重定向到主页
        router.push('/')
      } catch (error) {
        console.error('注销失败:', error)
        errorMessage.value = '注销失败，请稍后重试。'
      }
    }

    // 调用注销函数
    handleLogout()

    return {
      errorMessage
    }
  }
}
</script>

<style scoped>
.error {
  color: red;
}
</style>