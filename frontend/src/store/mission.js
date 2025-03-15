import api from '@/utils/api'

const state = {
  mission: null,
  isLoading: false,
  error: null
}

const mutations = {
  SET_MISSION(state, mission) {
    state.mission = mission
  },
  SET_LOADING(state, isLoading) {
    state.isLoading = isLoading
  },
  SET_ERROR(state, error) {
    state.error = error
  }
}

// const actions = {
//   async fetchMission({ commit }, missionId) {
//     is
//     commit('SET_LOADING', true)
//     commit('SET_ERROR', null)
//     try {
//         // http://127.0.0.1:8000/polls/api/assignments/id/
//       const response = await api.get(`/api/assignments/${missionId}`)
//       console.log("assignments response:", response)
//       commit('SET_MISSION', response)
//     } catch (error) {
//       commit('SET_ERROR', error)
//     } finally {
//       commit('SET_LOADING', false)
//     }
//   }
const actions = {
  async fetchMission({ commit }, missionId) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    commit('SET_MISSION', null) // 清空旧数据
    
    try {
      const response = await api.get(`/api/assignments/${missionId}/`) // 注意结尾斜杠
      console.log("Assignment response:", response)
      commit('SET_MISSION', response)
      
    } catch (error) {
      // 结构化错误处理
      const errorInfo = {
        timestamp: new Date().toISOString(),
        message: '获取任务数据失败',
        details: {}
      }

      if (error.response) {
        // HTTP 状态码相关错误
        errorInfo.status = error.response.status
        errorInfo.details = error.response.data || {}

        // 针对 404 的特殊处理
        if (error.response.status === 404) {
          errorInfo.message = `任务 ID ${missionId} 不存在`
          commit('SET_MISSION', null) // 明确清除数据
        }

        // 其他状态码处理示例
        else if (error.response.status === 403) {
          errorInfo.message = "无权访问此任务"
        }

      } else if (error.request) {
        // 请求已发送但无响应
        errorInfo.message = "服务器无响应"
        errorInfo.details = error.request

      } else {
        // 其他客户端错误
        errorInfo.message = "请求配置错误"
        errorInfo.details = error.message
      }

      console.error('[API Error]', errorInfo)
      commit('SET_ERROR', errorInfo)

      // // 可选：触发全局错误处理
      // if (error.response?.status === 404) {
      //   this.$router.push('/not-found') // 跳转404页面
      // }
      
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const getters = {
  mission: state => state.mission,
  isLoading: state => state.isLoading,
  error: state => state.error
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}