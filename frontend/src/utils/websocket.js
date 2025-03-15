class DroneWebSocket {
  constructor() {
    this.socket = null
    this.reconnectInterval = 5000
    this.store = null
    this.reconnectTimer = null // 新增重连定时器引用
    this.manualClose = false  // 更明确的关闭状态标识
  }

  connect(store) {
    if (this.socket && [WebSocket.OPEN, WebSocket.CONNECTING].includes(this.socket.readyState)) {
      return  // 避免重复连接
    }

    this.store = store
    this.manualClose = false
    const wsBaseUrl = import.meta.env.VITE_APP_WS_BASE_URL || 'ws://127.0.0.1:8000'
    
    // 清除旧连接
    this._cleanup() 

    this.socket = new WebSocket(`${wsBaseUrl}/ws/drones/?token=${store.state.auth.authToken}`)

    this.socket.onmessage = (event) => {
      console.log('WebSocket message:', event)
      const data = JSON.parse(event.data)
      console.log('WebSocket detail:', data)
      // console.log('type:', data.type)
      switch (data.type) {
        case 'FeatureCollection':
          // console.log("FeatureCollection", data)
          store.commit('drone/SET_DRONE_WEBSOCKET', data.features)
          break
        default:
      }
    }

    this.socket.onclose = (e) => {
      if (e.code === 1000) {
        console.log('WebSocket正常关闭')
      } else if (e.code === 4001) {
        console.log('未授权，断开连接')
      }
      if (!this.manualClose && !e.wasClean) {
        console.log('意外断开，尝试重连...')
        this.reconnectTimer = setTimeout(() => this.connect(store), this.reconnectInterval)
      }
    }

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }

  sendCommand(command) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(command))
    }
  }

  close() {
    this.manualClose = true
    this._cleanup()
  }

  // 私有清理方法
  _cleanup() {
    // 1. 清除重连定时器
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    // 2. 安全关闭连接
    if (this.socket) {
      const socketStates = [WebSocket.OPEN, WebSocket.CONNECTING]
      if (socketStates.includes(this.socket.readyState)) {
        this.socket.close(1000, '正常关闭') // 使用标准关闭代码
      }
      this.socket = null
    }
  }
}

export default new DroneWebSocket()
