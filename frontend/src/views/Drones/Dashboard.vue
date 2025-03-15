<template>
  <div class="dashboard">

    <div class="sidebar">
      <ul>
        <li @click="showDronesList">无人机列表</li>
        <li @click="showTargetsList">目标列表</li>
        <li @click="showMap">地图</li>
      </ul>
    </div>
    
    <div class="content">
      <h1>无人机管理</h1>
      
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading">加载中...</div>
      
      <!-- 错误提示 -->
      <div v-if="error" class="error-alert">
        {{ error }}
      </div>
      <!-- 创建按钮和搜索 -->
      <div class="list-controls">
        <router-link to="/dashboard/drone/create" class="btn-primary">
          新建无人机
        </router-link>
      </div>

      <!-- 无人机列表 -->
      <table v-if="showDrones" class="data-table">
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
                :to="`/dashboard/drone/${drone.id}`" 
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
              <button 
                @click="handleStart(drone.id)"
                class="btn-success"
                v-if="!isDroneStarted(drone.id)"
              >
                启动
              </button>
              <button 
                @click="handleStop(drone.id)"
                class="btn-warning"
                v-if="isDroneStarted(drone.id)"
              >
                停止
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 目标列表 -->
      <table v-if="showTargets" class="data-table">
        <thead>
          <tr>
            <th>任务名称</th>
            <th>任务状态</th>
            <th>地理坐标</th>
            <th>无人机数量</th>
            <th>最高状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          
          <tr v-for="target in allTargets" :key="target.id">
            <td>{{ target.properties.name }}</td>
            <td>
              <el-tag :type="getStatusTagType(target.properties.status)">
                <!-- {{ formatStatus(target.properties.status) }} -->
                {{ target.properties.status.text }}
              </el-tag>
            </td>
            <td>
              <div class="coordinates">
                <span class="longitude">经度: {{ formatNumber(target.geometry.coordinates[0], 4) }}</span>
                <span class="latitude">纬度: {{ formatNumber(target.geometry.coordinates[1], 4) }}</span>
              </div>
            </td>
            <td>{{ target.properties.drones ? target.properties.drones.length : 0 }} 架</td>
            <td>
              <!-- Dashboard.vue:128 
 Uncaught (in promise) TypeError: Cannot read properties of undefined (reading 'map')
    at Proxy.getMaxDroneStatus (Dashboard.vue:128:33)
    at Dashboard.vue?t=1742004641181:392:69
    at Proxy._sfc_render (Dashboard.vue?t=1742004641181:365:71) -->
              <!-- <el-tag :type="getDroneStatusTagType(getMaxDroneStatus(target.properties?.drones || []))">
                {{ formatDroneStatus(getMaxDroneStatus(target.properties?.drones || [])) }}
              </el-tag>  -->
            </td>
            <td>
              <router-link 
                :to="`/dashboard/mission/${target.properties.id}`" 
                class="btn-info"
              >
                任务详情
              </router-link>
              <router-link 
                :to="`/dashboard/target/${target.properties.target_id}`" 
                class="btn-info"
              >
                目标详情
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
      <!--地图-->
      <AMapContainer  v-if="showMapView" :config="mapConfig" :targets="allTargets"/>

    </div>
    
    <div class="dashboard-content">
      <!-- 这里是子路由组件的渲染位置 -->
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
    
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import moment from 'moment'
import DroneWebSocket from '@/utils/websocket'
// import { ElTag, ElButton } from 'element-plus'
import AMapContainer from './MapContainer.vue'

export default {
  name: 'Dashboard',
  
  components: {
    // ElTag,
    // ElButton,
    AMapContainer
  },

  data() {
    return {
      showDrones: true,
      showTargets: false,
      showMapView: false,
      mapConfig: {
        key: 'fe97d423fdb0de8f8bc51bfc01b576b5',
        center: [116.4, 39.912],
        zoom: 13,
        // markerIcon: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png',
        liveUpdate: true
      }
    }
  },

  computed: {
    ...mapGetters('drone', ['allDrones', 'allTargets', 'isLoading', 'error'])
  },

  created() {
    this.fetchDrones()
    DroneWebSocket.connect(this.$store)
  },

  beforeUnmount() {
    DroneWebSocket.close()
  },

  methods: {
    ...mapActions('drone', ['fetchDrones', 'deleteDrone', 'startDrone', 'stopDrone']),
    
    formatDate(date) {
      return moment(date).format('YYYY-MM-DD HH:mm')
    },

    formatNumber(value, decimals) {
      return Number(value).toFixed(decimals)
    },

    async handleDelete(id) {
      if (confirm('确定要删除此无人机吗？')) {
        await this.deleteDrone(id)
      }
    },

    async handleStart(id) {
      await this.startDrone(id)
    },

    async handleStop(id) {
      await this.stopDrone(id)
    },

    isDroneStarted(id) {
      return this.$store.state.drone.start.includes(id)
    },

    showDronesList() {
      this.showDrones = true
      this.showTargets = false
      this.showMapView = false
    },

    showTargetsList() {
      this.showDrones = false
      this.showTargets = true
      this.showMapView = false
    },

    showMap() {
      this.showDrones = false
      this.showTargets = false
      this.showMapView = true
    },

    formatStatus(status) {
      const statusMap = {
        0: '待执行',
        1: '执行中',
        2: '已完成',
        3: '已失败'
      }
      return statusMap[status] || '未知状态'
    },

    getStatusTagType(status) {
      const typeMap = {
        0: 'info',
        1: 'primary',
        2: 'success',
        3: 'danger'
      }
      return typeMap[status] || 'info'
    },


    getMaxDroneStatus(drones) {
      if (!Array.isArray(drones) || drones.length === 0) {
        return 0; // 或者返回一个默认状态
      }
      return Math.max(...drones.map(d => d.status));
    },

    formatDroneStatus(status) {
      const statusMap = {
        0: '空闲',
        1: '任务中',
        2: '返航中',
        3: '紧急'
      }
      return statusMap[status] || '未知'
    },

    getDroneStatusTagType(status) {
      const typeMap = {
        0: 'success',
        1: 'primary',
        2: 'warning',
        3: 'danger'
      }
      return typeMap[status] || 'info'
    }
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
}

.sidebar {
  width: 200px;
  background-color: #f8f9fa;
  padding: 20px;
}

.sidebar ul {
  list-style-type: none;
  padding: 0;
}

.sidebar li {
  padding: 10px;
  cursor: pointer;
}

.sidebar li:hover {
  background-color: #e9ecef;
}

.content {
  flex: 1;
  padding: 20px;
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

.btn-success {
  background: #28a745;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.btn-warning {
  background: #ffc107;
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

.coordinates {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.9em;
}

.longitude::before {
  content: "🌐 ";
}

.latitude::before {
  content: "📍 ";
}

.btn-info {
  margin-right: 8px;
}

.el-tag {
  margin: 2px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>