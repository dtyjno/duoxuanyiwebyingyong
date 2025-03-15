<template>
    <div class="mission-detail">
      <h1>任务详情</h1>
      
      <div v-if="isLoading">加载中...</div>
      
      <div v-if="error" class="error-alert">
        {{ error.message }}
      </div>

      <div v-if="mission" class="detail-card">
        <div class="detail-row">
          <label>ID:</label>
          <span>{{ mission.id }}</span>
        </div>
        
        <div class="detail-row">
          <label>名称:</label>
          <span>{{ mission.name }}</span>
        </div>
        
        <div class="detail-row">
          <label>状态:</label>
          <span :class="`status-badge ${mission.status}`">
            {{ mission.status }}
          </span>
        </div>
        
        <div class="detail-actions">
          <router-link 
            :to="`/dashboard/missions/${mission.id}/edit`" 
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
    name: 'MissionDetail',
    
    props: {
      missionId: {
        type: String,
        required: true
      }
    },
  
    computed: {
      ...mapGetters('mission', ['mission', 'isLoading', 'error']),
    },
  
    methods: {
      ...mapActions('mission', ['fetchMission']),
    },
  
    // 按下不同的任务详情时，重新获取任务详情（重写）
    // watch: {
    //     mission.id: {
    //     immediate: true,
    //     handler(newId) {
    //         this.fetchMission(newId);
    //     }
    //     }
    // },

    created() {
      this.fetchMission(this.missionId);
    },
  }
  </script>
  
  <style scoped>
  .mission-detail {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }

  .error-alert {
    background: #f8d7da;
    color: #721c24;
    padding: 10px;
    border-radius: 4px;
    margin: 15px 0;
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