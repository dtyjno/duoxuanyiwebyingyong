<template>
  <div class="login-container">
    <h2>用户登录</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label>用户名：</label>
        <input 
          v-model="formData.username" 
          type="text" 
          required
          @input="clearError('username')"
        >
      </div>
      
      <div class="form-group">
        <label>密码：</label>
        <input
          v-model="formData.password"
          type="password"
          required
          @input="clearError('password')"
        >
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? '登录中...' : '立即登录' }}
      </button>
    </form>
  </div>
</template>

<script>
import api from '@/utils/api'
import { nextTick } from 'vue';



export default {
  data() {
    return {
      formData: {
        username: '',
        password: ''
      },
      errors: {}, // 确保在data中定义errors
      error: '',
      loading: false
    }
  },
  async created() {
    // 检查是否已经登录
    const token = localStorage.getItem('authToken');
    const username = localStorage.getItem('user');
    
    if (token && username) {
      try {
        // 设置 token 到 axios header
        api.defaults.headers.common['Authorization'] = `Token ${token}`;
        
        // 验证 token 是否有效
        const userResponse = await api.get('/api/users/me/');
        const currentUser = userResponse;
        

        // 更新 Vuex store
        this.$store.commit('auth/SET_TOKEN', token);
        this.$store.commit('auth/SET_AUTH_USER', {
          username: currentUser.username,
          email: currentUser.email,
          groups: currentUser.groups,
        });
        
        // 跳转到仪表盘
        this.$router.push('/dashboard');
        return;
      } catch (error) {
        // token 无效，清除本地存储
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        console.error('自动登录失败:', error);
      }
    } 
    // 未登录，清除本地存储
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    console.log('未登录');
    
    // if (this.formData.username && this.formData.password) {
    //   await this.handleLogin();
    // }
  },
  methods: {
    clearError(field) {
      if (this.errors[field]) {
        delete this.errors[field];
      }
    }, 
    async handleLogin() {
      this.errors = {}; // 重置错误信息
      try {
        this.loading = true;
        
        // 构造请求数据
        const data = {
          username: this.formData.username,
          password: this.formData.password
        };

        // 发送登录请求
        const response = await api.post('/api/login/', data);

        // 处理登录成功
        console.log('登录响应:', response);
        const authToken = response.token; // 假设 token 在 response.data 中

        if (authToken) {
          // 1. 存储 Token
          localStorage.setItem('authToken', authToken);
          // 2. 配置 axios 全局携带 Token（关键步骤！）
          api.defaults.headers.common['Authorization'] = `Token ${authToken}`;

          // 3. 获取完整用户信息（通过专用接口更高效）
          try {
            // 后端提供 /api/users/me/ 接口直接获取当前用户
            const userResponse = await api.get('/api/users/me/');
            const currentUser = userResponse;
            
            console.log('当前用户信息:', currentUser);
            // 提交完整用户信息到 Vuex 设置Token
            this.$store.commit('auth/SET_TOKEN', authToken);
            this.$store.commit('auth/SET_AUTH_USER', {
              username: currentUser.username,
              email: currentUser.email,
              groups: currentUser.groups,
              // 其他必要字段...
            });
            // 存储用户信息到 localStorage
            localStorage.setItem('user', JSON.stringify(currentUser.username));

          } catch (error) {
            console.error('获取用户信息失败:', error);
            this.error = '获取用户信息失败';
            // 处理错误（如 Token 失效时跳转登录页）
            this.$router.push('/login');
            return;
          }

          await nextTick()

          // this.$store. 
          // 4. 跳转到目标页面
          // 修改后的跳转逻辑
          this.$router.push('/dashboard').catch(error => {
            if (error.name !== 'NavigationDuplicated') {
              console.error('导航错误:', error)
              this.$router.push('/error') // 跳转到通用错误页
            }
          })



        } else {
          this.error = '登录失败，请检查凭证'; // 通用错误信息
        }
      } catch (error) {
        console.error(error);
        if (error.response) {
          // 处理字段级错误
          // const { data } = error.response;
          // if (data?.errors) {
            // console.log(data.errors);
            // this.errors = { ...data.errors }; // 假设后端返回 { errors: { username: ['错误1'] } }
          // } else {
            this.handleLoginError(error); // 处理其他类型错误
          // }
        } else {
          this.error = '网络错误，请检查连接';
        }
      } finally {
        this.loading = false;
      }
    },
    handleLoginError(error) {
      const status = error.response?.status;
      const data = error.response?.data;

      switch (status) {
        case 400:
          this.error = data['error'] || data['non_field_errors'][0] || '请求参数无效';
          break;
        case 401:
          this.error = '用户名或密码错误';
          break;
        case 429:
          this.error = '尝试过多，请稍后再试';
          break;
        default:
          this.error = '登录失败，请重试';
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  background: #007bff;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  margin-bottom: 1rem;
}
</style>