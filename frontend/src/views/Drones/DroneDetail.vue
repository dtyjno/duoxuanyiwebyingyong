<!-- src/views/Drones/DroneDetail.vue -->
<template>
    <div class="drone-detail">
      <h1>无人机详情</h1>
      
      <div v-if="isLoading">加载中...</div>
      
      <div v-if="currentDrone" class="detail-card">
        <div class="detail-row">
          <label>ID:</label>
          <span>{{ currentDrone.id }}</span>
        </div>
        
        <div class="detail-row">
          <label>名称:</label>
          <span>{{ currentDrone.name }}</span>
        </div>
        
        <div class="detail-row">
          <label>状态:</label>
          <span :class="`status-badge ${currentDrone.status}`">
            {{ currentDrone.status }}
          </span>
        </div>
        
        <div class="detail-actions">
          <router-link 
            :to="`/dashboard/drones/${currentDrone.id}/edit`" 
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
    name: 'DroneDetail',
    
    computed: {
      ...mapGetters('drone', ['currentDrone', 'isLoading']),
    },
    methods: {
      ...mapActions('drone', ['fetchDrone']),
    },
    created() {
      this.fetchDrone(this.$route.params.id);
    },
  }
  </script>
  
  <style scoped>
  .drone-detail {
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
  