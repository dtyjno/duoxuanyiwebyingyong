<template>
  <div class="dialogue-container">
    <div class="dialogue-header">
      <h2>{{ title }}</h2>
      <button @click="close" class="close_button">×</button>
    </div>
    <div class="chat-history" ref="chatHistory">
      <div 
        v-for="msg in messages" 
        :key="msg.id" 
        class="chat-message"
        :data-role="msg.role"
      >
        <div class="chat-message-content">
          {{ msg.content }}
          <span v-if="loading && msg === currentAssistantMessage" class="typing-indicator">...</span>
        </div>
        <div class="chat-message-meta">
          <span class="message-time">{{ msg.time }}</span>
        </div>
      </div>
    </div>
    <div class="chat-input">
      <input 
        ref="input"
        v-model="input" 
        @keyup.enter="send" 
        placeholder="请输入消息内容"
        :disabled="loading"
      >
      <button 
        @click="send" 
        class="send_button"
        :disabled="loading || !input.trim()"
      >
        {{ loading ? '发送中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      title: 'AI对话',
      messages: [],
      input: '',
      loading: false,
      currentAssistantMessage: null,
      cancelTokenSource: null
    }
  },
  methods: {
    async send() {
      if (!this.input.trim() || this.loading) return;
      
      await this.scrollToBottom();

      const userInput = this.input;
      this.input = '';
      this.loading = true;

      // Add user message
      this.addMessage('user', userInput);

      try {
        // Cancel previous request if exists
        if (this.cancelTokenSource) {
          this.cancelTokenSource.cancel('取消之前的请求');
        }
        this.cancelTokenSource = axios.CancelToken.source();

        // Add assistant message
        this.currentAssistantMessage = this.addMessage('assistant', '');

        // 修改发送请求部分
        const response = await fetch('https://deepseek.hdu.edu.cn/api/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            model: "deepseek-r1:32b",
            prompt: userInput,
            stream: true
          })
        });

        // 正确获取流读取器
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split(/\n(?=\{)/g);
          buffer = lines.pop() || '';

          for (const line of lines) {
            try {
              const data = JSON.parse(line.trim());
              if (data.response) {
                this.currentAssistantMessage.content += data.response;
                await this.scrollToBottom();
              }
            } catch (e) {
              console.error('解析错误:', line);
            }
          }
        }
      } catch (error) {
        if (!axios.isCancel(error)) {
          console.error('请求错误:', error);
          this.currentAssistantMessage.content = '抱歉，请求出现错误，请稍后再试';
        }
      } finally {
        this.loading = false;
        this.cancelTokenSource = null;
        await this.scrollToBottom();
        this.$refs.input.focus();
      }
    },

    addMessage(role, content) {
      const message = {
        id: Date.now(),
        role,
        content,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      this.messages.push(message);
      return message;
    },

    async scrollToBottom() {
      await this.$nextTick();
      const container = this.$refs.chatHistory;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },

    close() {
      if (this.cancelTokenSource) {
        this.cancelTokenSource.cancel('用户关闭对话框');
      }
      this.$emit('close');
    }
  }
}
</script>

<style scoped>
.dialogue-container {
  width: 100%;
  height: 100%;
  margin: 0 auto;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

.dialogue-header {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.chat-message {
  margin-bottom: 12px;
  max-width: 80%;
  padding: 8px 12px;
}

.chat-message[data-role="user"] {
  background-color: #007bff;
  color: white;
  border-radius: 12px 12px 0 12px;
  margin-left: auto;
}

.chat-message[data-role="assistant"] {
  background-color: #f0f0f0;
  color: #333;
  border-radius: 12px 12px 12px 0;
  margin-right: auto;
}

.chat-message-content {
  white-space: pre-line;
  word-break: break-word;
}

.chat-message-meta {
  margin-top: 4px;
  font-size: 0.8em;
  color: #666;
  text-align: right;
}

.typing-indicator::after {
  content: '...';
  animation: typing 1.5s infinite;
}

@keyframes typing {
  0% { content: '.'; }
  33% { content: '..'; }
  66% { content: '...'; }
}

.chat-input {
  display: flex;
  padding: 16px;
  border-top: 1px solid #e0e0e0;
}

.chat-input input {
  flex: 1;
  padding: 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-right: 8px;
}

.send_button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.close_button {
  background: none;
  border: none;
  font-size: 1.5em;
  cursor: pointer;
  padding: 0 8px;
}
</style>
