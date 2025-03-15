// store/modules/auth.js
import api from '@/utils/api'

export default {
  namespaced: true, // 启用命名空间
  state: {
    user: null,
    authToken: null
  },
  getters: {
    // 动态计算认证状态
    isAuthenticated: (state) =>!!state.authToken,
    currentUser: (state) => state.user,
  },
  mutations: {
    SET_AUTH_USER(state, userData) {
      state.user = {
        id: userData.id,
        username: userData.username,
        email: userData.email,
        groups: userData.groups
      };
      state.isAuthenticated = true;
    },
    SET_TOKEN(state, token) {
      state.authToken = token
    },
    CLEAR_AUTH_USER(state) {
      state.user = null;
      state.authToken = null;
    //   state.isAuthenticated = false;
    }
  },
  actions: {
    initializeAuth({ commit }) {
      const token = localStorage.getItem('authToken');
      if (token) {
        // 配置 axios 全局头
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        // 自动获取用户信息
        api.get('/api/users/me/')
          .then(response => {
            commit('SET_AUTH_USER', response.data);
          })
          .catch(() => {
            commit('CLEAR_AUTH_USER');
            localStorage.removeItem('authToken');
          });
      }
    }
  }
}