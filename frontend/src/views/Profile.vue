<template>
    <div class="profile">
      <h1>个人中心</h1>
      <div v-if="isAuthenticated">
        <div class="user-info">
          <p><strong>用户名:</strong> {{ currentUser.username }}</p>
          <p><strong>邮箱:</strong> {{ currentUser.email }}</p>
          <p><strong>用户组:</strong> {{ currentUser.groups.join(', ') }}</p>
        </div>
        <div class="actions">
          <button @click="logout" class="btn btn-danger">注销</button>
        </div>
      </div>
      <div v-else>
        <p>请先登录。</p>
      </div>
    </div>
  </template>
  
  <script>
  import { mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'Profile',
    computed: {
      ...mapGetters('auth', ['isAuthenticated', 'currentUser'])
    },
    methods: {
      ...mapActions('auth', ['logout']),
    }
  }
  </script>
  
  <style scoped>
  .profile {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  }
  
  .user-info {
    margin-bottom: 20px;
  }
  
  .actions {
    text-align: right;
  }
  
  .btn {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .btn-danger {
    background-color: #dc3545;
    color: white;
  }
  </style>