<script setup>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import AIDialogue from '@/components/AIDialogue.vue'
import ChatToggleButton from '@/components/ChatToggleButton.vue'

const store = useStore()
const router = useRouter()

// AI对话框显示状态
const showChat = ref(false)

const toggleChat = () => {
  showChat.value = !showChat.value
}

// 登录状态计算属性
const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])

// 导航菜单配置
const navLinks = computed(() => [
  { path: '/', name: '首页', auth: false },
  { path: '/dashboard', name: '控制台', auth: true },
  { path: '/login', name: '登录', auth: false, hideWhenLoggedIn: true },
  { path: '/profile', name: '个人中心', auth: true }
])

// 退出登录处理
const handleLogout = () => {
  store.commit('auth/CLEAR_AUTH_USER');
  router.push('/index')
}
</script>

<template>
  <header class="app-header">
    <nav class="nav-container">
      <!-- 网站Logo -->
      <router-link 
        to="/" 
        class="brand-logo"
        aria-label="返回首页"
      >
        <img 
          src="./assets/logo.svg" 
          alt="网站Logo" 
          class="logo"
          width="60" 
          height="60"
        />
      </router-link>

      <!-- 导航菜单 -->
      <div class="nav-links">
        <template v-for="link in navLinks" :key="link.path">
          <router-link 
            v-if="(!link.auth || isAuthenticated) && 
                  !(link.hideWhenLoggedIn && isAuthenticated)"
            :to="link.path"
            class="nav-link"
            active-class="active-link"
            :exact="link.path === '/'"
          >
            {{ link.name }}
          </router-link>
        </template>
        
        <!-- 退出按钮 -->
        <router-link 
          v-if="isAuthenticated" 
          to="/logout" 
          class="logout-button"
          aria-label="退出登录"
        >退出</router-link>
        <!-- <button 
          v-if="isAuthenticated"
          @click="handleLogout"
          class="logout-button"
          aria-label="退出登录"
        >
          退出
        </button> -->
      </div>
    </nav>
  </header>

  <main class="main-content">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <Transition name="slide-fade">
      <div v-show="showChat" class="AI-chat">
        <AIDialogue @close="toggleChat" />
      </div>
    </Transition>
    <ChatToggleButton 
      v-show="!showChat" 
      @toggle="toggleChat" 
      class="chat-toggle-button"
    />
  </main>
</template>

<style scoped>
/* CSS 变量 */
:root {
  --header-bg: #ffffff;
  --nav-gap: 1.5rem;
  --transition-speed: 0.3s;
}

.app-header {
  /* background: var(--header-bg); */
  /* box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); */
  /* padding: 1rem 0; */
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 70px;
  /* padding: 1rem 0; */

}

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0.5rem 2rem;
}

.brand-logo {
  transition: opacity var(--transition-speed);
}

.brand-logo:hover {
  opacity: 0.8;
}

.logo {
  display: block;
  max-width: 100px;
  height: auto;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: var(--nav-gap);
}

.nav-link {
  color: #2c3e50;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: 
    background-color var(--transition-speed),
    color var(--transition-speed);
}

.nav-link:hover,
.active-link {
  background-color: rgba(66, 153, 225, 0.1);
  color: #4299e1;
}

.logout-button {
  background: none;
  border: 1px solid #e2e8f0;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: 
    background-color var(--transition-speed),
    border-color var(--transition-speed);
}

.logout-button:hover {
  background-color: #f8fafc;
  border-color: #cbd5e0;
}
.main-content {
  position: fixed;
  top: 70px;
  left: 0;
  right: 0;
  bottom: 0;
  overflow-y: auto;
  padding: 2rem;
  background-color: #f8f9fa;
}

.AI-chat {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  height: 60vh;
  max-height: calc(100vh - 120px);
  width: 600px;
  z-index: 1000;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chat-toggle-button {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1000;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

@media (max-width: 768px) {
  .AI-chat {
    width: 90%;
    right: 5%;
    height: 50vh;
    bottom: 1rem;
  }
  
  .chat-toggle-button {
    right: 1rem;
    bottom: 1rem;
  }
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    /* flex-direction: column;
    gap: 1rem; */
    padding: 0.5rem 1rem;
  }

  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }

  .logo {
    max-width: 80px;
  }
}
/* 全局样式 */
body {
  font-family: 'Noto Sans SC', 'Helvetica Neue', sans-serif;
  margin: 0;
}
</style>
