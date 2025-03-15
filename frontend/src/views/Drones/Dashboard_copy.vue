<!-- src/views/Drones/DroneList.vue -->
<template>
  <div class="drone-list">
    <h1>无人机管理</h1>
    
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading">加载中...</div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-alert">
      {{ error }}
    </div>

    <!-- 创建按钮和搜索 -->
    <div class="list-controls">
      <router-link to="/drone/create" class="btn-primary">
        新建无人机
      </router-link>
    </div>

    <!-- 无人机列表 -->
    <table class="data-table">
      <thead>
        <tr>
          <th>名称</th>
          <th>状态</th>
          <th>位置信息</th>
          <th>创建时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="drone in allDrones" :key="drone.id">
          <td>{{ drone.name }}</td>
          <td>
            <span :class="`status-badge ${drone.dock_status_display}`">
              {{ drone.dock_status_display }}
            </span>
          </td>
          <td>
            <small class="text-muted">
                经度: {{ formatNumber(drone.longitude, 4) }}<br/>
                纬度: {{ formatNumber(drone.latitude, 4) }}<br/>
                高度: {{ drone.height }}米
            </small>
          </td>
          <td>{{ formatDate(drone.created_at) }}</td>
          <td class="actions">
            <router-link 
              :to="`/drone/${drone.id}`" 
              class="btn-info"
            >
              详情
            </router-link>
            <button 
              @click="handleDelete(drone.id)"
              class="btn-danger"
            >
              删除
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <!-- 目标列表 -->
     
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import moment from 'moment'
import DroneWebSocket from '@/utils/websocket'

export default {
  name: 'DroneList',
  
  computed: {
    ...mapGetters('drone', ['allTarget', 'allDrones', 'isLoading', 'error'])
  },

  created() {
    // this.fetchDrones();
    this.fetchDrones()
    DroneWebSocket.connect(this.$store)
  },

  beforeUnmount() {
    DroneWebSocket.close()
  },

  methods: {
    ...mapActions('drone', ['fetchDrones', 'deleteDrone']),
    
    formatDate(date) {
      return moment(date).format('YYYY-MM-DD HH:mm')
    },

    formatNumber(value, decimals) {
      return Number(value).toFixed(decimals);
    },

    async handleDelete(id) {
      if (confirm('确定要删除此无人机吗？')) {
        await this.deleteDrone(id)
      }
    }
  },

  // getters: {
  //   allDrones(state) {
  //     return state.allDrones
  //   }
  // }
}
</script>

<style scoped>
.drone-list {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.9em;
}

.active {
  background: #e3fcef;
  color: #00875a;
}

.maintenance {
  background: #fffae6;
  color: #ff8b00;
}

.btn-primary {
  background: #007bff;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  text-decoration: none;
}

.btn-info {
  background: #17a2b8;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  margin-right: 8px;
}

.btn-danger {
  background: #dc3545;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.error-alert {
  background: #fee;
  color: #d33;
  padding: 12px;
  margin: 20px 0;
  border-radius: 4px;
}
</style>
