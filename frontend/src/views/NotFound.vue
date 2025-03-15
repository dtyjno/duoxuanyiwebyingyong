<template>
<div class="not-found-container">
    <div class="text-center">
    <h1 class="status-code">404</h1>
    <p class="status-message">页面未找到</p>
    <p class="description">您访问的页面可能已丢失在数字宇宙中...</p>
    <router-link 
        to="/" 
        class="return-home"
    >
        返回首页
    </router-link>
    </div>
</div>
</template>

<script>
export default {
name: 'NotFound',
mounted() {
    // 动态修改页面标题
    document.title = '页面未找到'
}
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f9fafb;
}

.text-center {
  text-align: center;
  padding-left: 1rem;
  padding-right: 1rem;
}

.status-code {
  font-size: 9rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 1rem;
}

.status-message {
  font-size: 1.5rem;
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 0.5rem;
}

.description {
  color: #6b7280;
  margin-bottom: 2rem;
  font-size: 1.125rem;
}

.return-home {
  display: inline-block;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
  background-color: #3b82f6;
  color: white;
  border-radius: 0.375rem;
  transition-property: background-color;
  transition-duration: 200ms;
}

.return-home:hover {
  background-color: #2563eb;
}
</style>
