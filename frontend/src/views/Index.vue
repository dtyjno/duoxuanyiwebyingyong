<template>
<div class="index-container">
    <!-- 导航栏登录入口 -->
    <nav class="main-nav">
    <router-link to="/">首页</router-link>
    <div class="auth-section" v-if="!isAuthenticated">
        <button @click="showLoginModal = true">登录</button>
        <router-link to="/login" class="login-link">立即登录</router-link>
    </div>
    <div class="user-info" v-else>
        欢迎，{{ currentUser.username }}！
        <button @click="handleLogout">退出 </button>
    </div>
    </nav>

    <!-- 登录模态框 -->
    <div v-if="showLoginModal" class="login-modal">
    <div class="modal-content">
        <h3>用户登录</h3>
        <form @submit.prevent="handleLogin">
        <div class="form-group">
            <label>用户名：</label>
            <input v-model="loginForm.username" type="text" required>
        </div>
        <div class="form-group">
            <label>密码：</label>
            <input v-model="loginForm.password" type="password" required>
        </div>
        <div class="form-actions">
            <button type="submit">登录</button>
            <!-- <button @click="showLoginModal = false">取消</button> -->
            <router-link to="/logout">取消</router-link>
        </div>
        </form>
    </div>
    </div>

    <!-- 首页主要内容 -->
    <main>
    <h1>首页主要内容</h1>
    <!-- 投票列表内容 -->
    </main>
</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import { useStore } from 'vuex'

const route = useRoute()
const router = useRouter()
const store = useStore()

const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])

const currentUser = computed(() => store.getters['auth/currentUser'])
const showLoginModal = ref(false)
const loginForm = ref({
username: '',
password: ''
})

const checkAuthStatus = async () => {
try {
    const response = await api.get('/auth/check/')
    // isAuthenticated.value = true
    // currentUser.value = response.data.user
} catch (error) {
    // isAuthenticated.value = false
    // currentUser.value = {}
}
}

const handleLogin = async () => {
try {
    const response = await api.post('/api/login/', loginForm.value)
    
    localStorage.setItem('authToken', response.data.token)
    // isAuthenticated.value = true
    // currentUser.value = response.data.user
    showLoginModal.value = false
    
    // 处理重定向逻辑
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
    
} catch (error) {
    alert('登录失败: ' + (error.response.non_field_errors || '未知错误'))
}
}

// const handleLogout = () => {
// localStorage.removeItem('authToken')

//     // 发送注销请求
//     const response = api.post('/api/logout/', {
//         headers: { 'Content-Type': 'application/json' }
//     });

//     // 处理注销成功
//     console.log('注销响应:', response);

// // isAuthenticated.value = false
// // currentUser.value = {}
// router.push('/')
// }

checkAuthStatus()
</script>

<style scoped>
.index-container {
max-width: 1200px;
margin: 0 auto;
}

.main-nav {
display: flex;
justify-content: space-between;
padding: 1rem;
background: #f8f9fa;
border-bottom: 1px solid #dee2e6;
}

.auth-section button, .login-link {
margin-left: 1rem;
padding: 0.5rem 1rem;
background: #007bff;
color: white;
border: none;
border-radius: 4px;
cursor: pointer;
}

.login-modal {
position: fixed;
top: 0;
left: 0;
right: 0;
bottom: 0;
background: rgba(0,0,0,0.5);
display: flex;
align-items: center;
justify-content: center;
}

.modal-content {
background: white;
padding: 2rem;
border-radius: 8px;
width: 400px;
}

.form-group {
margin-bottom: 1rem;
}

.form-group label {
display: block;
margin-bottom: 0.5rem;
}

.form-group input {
width: 100%;
padding: 0.5rem;
border: 1px solid #ddd;
border-radius: 4px;
}

.form-actions {
margin-top: 1rem;
display: flex;
gap: 1rem;
justify-content: flex-end;
}
</style>