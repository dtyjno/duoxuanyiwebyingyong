// src/store/modules/drones.js
import api from '@/utils/api'

const state = {
  items: [],      // 无人机列表数据
  counts: null,      // 无人机数量
  current: null,  // 当前操作的无人机
  loading: false,
  error: null,
  start: [],      // 启动的无人机ID列表
  features: []    // 存储接收到的所有数据
}

const mutations = {
  SET_LOADING(state, status) {
    state.loading = status
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  SET_DRONES(state, drones) {
    state.counts = drones.count
    state.items = drones.results
  },
  ADD_DRONE(state, drone) {
    state.items.unshift(drone)
  },
  UPDATE_DRONE(state, updatedDrone) {
    const index = state.items.findIndex(d => d.id === updatedDrone.id)
    if (index !== -1) {
      state.items.splice(index, 1, updatedDrone)
    }
  },
  REMOVE_DRONE(state, id) {
    state.items = state.items.filter(d => d.id !== id)
  },
  SET_CURRENT(state, drone) {
    state.current = drone
  },
  SET_DRONE_WEBSOCKET(state, features) {
    state.features = features
  },
  START_DRONE(state, id) {
    if (!state.start.includes(id)) {
      state.start.push(id)
    }
  },
  STOP_DRONE(state, id) {
    state.start = state.start.filter(d => d !== id)
  }
}

const actions = {
  // 获取无人机列表
  async fetchDrones({ commit }) {
    commit('SET_LOADING', true)
    try {
      const response = await api.get('api/drones/')
      console.log("无人机列表：", response)
      commit('SET_DRONES', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data || error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 创建无人机
  async createDrone({ commit }, droneData) {
    commit('SET_LOADING', true)
    try {
      const response = await api.post('api/drones/', droneData)
      console.log("创建无人机：", response)
      commit('SET_DRONE', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data || error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取单个无人机详情
  async fetchDrone({ commit }, id) {
    commit('SET_LOADING', true)
    try {
      const response = await api.get(`api/drones/${id}/`)
      console.log("获取无人机详情：", response)
      commit('SET_CURRENT', response)
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data || error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 更新无人机
  async updateDrone({ commit }, { id, data }) {
    commit('SET_LOADING', true)
    try {
      const response = await api.put(`api/drones/${id}/`, data)
      console.log("更新无人机：", response.data)
      commit('UPDATE_DRONE', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data || error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 删除无人机
  async deleteDrone({ commit }, id) {
    commit('SET_LOADING', true)
    try {
      await api.delete(`api/drones/${id}/`)
      commit('REMOVE_DRONE', id)
    } catch (error) {
      commit('SET_ERROR', error.response?.data || error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 启动无人机
  async startDrone({ commit }, id) {
    commit('SET_LOADING', true)
    try {
      // 构造请求数据
      const data = {
        type: "start",
        id: id
      };
      // 更新状态
      commit('START_DRONE', id)
      // 发送请求
      await api.post('/api/drone_manage/', data, { timeout: 30000 });
    } catch (error) {
      commit('SET_ERROR', error.response?.data || error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  async stopDrone({ commit }, id) {
    commit('SET_LOADING', true)
    try {
      // 构造请求数据
      const data = {
        type: "stop",
        id: id
      };
      // 更新状态
      commit('STOP_DRONE', id)
      // 发送请求
      await api.post('/api/drone_manage/', data);
    } catch (error) {
      commit('SET_ERROR', error.response?.data || error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const getters = {
  allDrones: state => state.items,

  droneFeatures: state => state.features.filter(f => 
    f.type === 'Feature' && 
    f.properties?.type === 'drone'
  ),

  missionFeatures: state => state.features.filter(f => 
    f.type === 'Feature' && 
    f.properties?.type === 'mission'
  ),

  // Get features related to a specific drone
  droneRelatedFeatures: state => droneId => state.features.filter(f => {
    // For drone type features, check the ID
    if (f.properties?.type === 'drone') {
      return f.properties.id === droneId;
    }
    // For mission type features, check the drones array
    if (f.properties?.type === 'mission') {
      return f.properties.drones?.some(d => d.id === droneId);
    }
    return false;
  }),
  

  droneById: state => id => state.items.find(d => d.id === id),
  featureById: state => id => state.features.find(f => f.properties.id === id),
  getCurrentMission: state => droneId => {
    return state.features.find(f => 
      f.properties.type === 'mission' && 
      f.properties.drones?.some(d => d.id === droneId)
    );
  },
  getDroneStatus: (state, getters) => droneId => {
    const droneFeature = getters.droneFeatures.find(f => f.properties.id === droneId);
    return droneFeature?.properties.status || null;
  },
 
  allTargets: state => state.features,
  currentDrone: state => state.current,
  isLoading: state => state.loading,
  error: state => state.error
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}