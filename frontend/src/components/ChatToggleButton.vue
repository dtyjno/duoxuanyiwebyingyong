<template>
  <button class="chat-toggle" @click="$emit('toggle')">
    <span class="icon">💬</span>
    <span class="text">AI助手</span>
  </button>
</template>

<style scoped>
.chat-toggle {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 12px 24px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  z-index: 1000;
}

.chat-toggle:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
}

.icon {
  font-size: 1.2em;
}

.text {
  font-weight: 500;
}
</style>