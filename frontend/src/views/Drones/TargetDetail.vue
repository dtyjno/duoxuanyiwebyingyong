<!-- filepath: /home/linhao/code/tutorial_copy/frontend/src/views/Drones/TargetDetail.vue -->
<template>
    <div class="target-detail">
      <h1>目标详情</h1>
      
      <div v-if="isLoading">加载中...</div>
      
      <div v-if="target" class="detail-card">
        <div class="detail-row">
          <label>ID:</label>
          <span>{{ target.id }}</span>
        </div>
        
        <div class="detail-row">
          <label>名称:</label>
          <span>{{ target.name }}</span>
        </div>
        
        <div class="detail-row">
          <label>状态:</label>
          <span :class="`status-badge ${target.status}`">
            {{ target.status }}
          </span>
        </div>
        
        <div class="detail-actions">
          <router-link 
            :to="`/dashboard/targets/${target.id}/edit`" 
            class="btn-edit"
          >
            编辑
          </router-link>
        </div>
      </div>
      <button 
        @click="$router.go(-1)" 
        class="btn-back"
      >
        返回
      </button>
      <router-link to="/dashboard" class="btn-cancel">
        取消
      </router-link>
    </div>
  </template>
  
  <script>
  import { mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'TargetDetail',
    
    props: {
      targetId: {
        type: String,
        required: true
      }
    },
  
    computed: {
      ...mapGetters('target', ['target', 'isLoading']),
    },
  
    methods: {
      ...mapActions('target', ['fetchTarget']),
    },
  
    created() {
      this.fetchTarget(this.targetId);
    },
  }
  </script>
  
  <style scoped>
  .target-detail {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .detail-card {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
  }
  
  .detail-row {
    margin: 15px 0;
    display: flex;
    align-items: center;
  }
  
  label {
    width: 80px;
    font-weight: bold;
    color: #666;
  }
  
  .btn-edit {
    background: #ffc107;
    color: black;
    padding: 8px 16px;
    border-radius: 4px;
    text-decoration: none;
  }
  
  .btn-cancel {
    margin-left: 15px;
    color: #666;
  }
  
  .btn-back {
    background: #6c757d;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    margin-left: 10px;
    cursor: pointer;
  }
  </style>