<template>
  <div class="a-map-container">
    <!-- 地图容器 -->
    <div id="map-container" class="map-wrapper"></div>
  </div>
</template>

<script>
import AMapLoader from "@amap/amap-jsapi-loader";

export default {
  name: 'AMapContainer',
  props: {
    // 地图配置
    config: {
      type: Object,
      required: true,
      validator: config => {
        return !!config.key && Array.isArray(config.center)
      }
    },
    // 目标点数据
    targets: {
      type: Array,
      default: () => []
    }
  },

  data() {
    return {
      map: null,
      AMap: null,
      markers: [],
      updateInterval: null,
      isMounted: false,
      currentInfoWindow: null,
    }
  },

  watch: {
    // 数据变化时更新地图
    targets: {
      deep: true,
      handler() {
        this.refreshMarkers()
      }
    }
  },

  
  async mounted() {
    this.isMounted = true
    try {
      await this.initAMapSDK()  // Await the SDK initialization
      if (this.isMounted) {
        this.initMapInstance()
        this.setupMapFeatures()
        this.map.setFitView()
      }
    } catch (error) {
      console.error('地图初始化失败:', error)
      this.$emit('init-failed', error)
    }
  },

  beforeUnmount() {
    this.isMounted = false
    this.cleanupResources()
  },


  methods: {
    /* 核心方法 */
    // 初始化SDK
    // AMapContainer.vue
    async initAMapSDK() {
      if (window.myAMapLoaderPromise) {
        this.AMap = await window.myAMapLoaderPromise;
        return;
      }

      window._AMapSecurityConfig = { 
        securityJsCode: "fc6ed7655310a89e5173ac881d053f37" 
      };

      window.myAMapLoaderPromise = new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.id = 'amap-script';
        script.src = `https://webapi.amap.com/loader.js?t=${Date.now()}`;
        script.onload = () => {
          // 使用高德地图的AMapLoader加载配置
          window.AMapLoader.load({
            key: this.config.key,
            version: '2.0',
            plugins: ['AMap.InfoWindow', 'AMap.Scale', 'AMap.ToolBar']
          }).then(AMap => {
            resolve(AMap);
          }).catch(reject);
        };
        script.onerror = reject;
        document.head.appendChild(script);
      });
      try {
        this.AMap = await window.myAMapLoaderPromise;
      } catch (error) {
        console.error("地图SDK加载失败", error);
        throw error;
      }
    },



    // 地图实例初始化
    initMapInstance() {
      console.log(this.AMap)
      console.log("targets:", this.targets)
      if(!this.AMap?.Map) {
        console.error('AMap.Map 未定义')
        return
      }
      this.map = new this.AMap.Map('map-container', {
        viewMode: '3D',
        zoom: this.config.zoom || 13,
        center: this.validateCoordinates(this.config.center),
        resizeEnable: true,
        ...this.config.advancedOptions
      })
    },

    // 创建地图元素
    setupMapFeatures() {
      // this.addMainMarker()
      this.refreshMarkers()
    },

    /* 标记点管理 */
    // 主标记点
    // addMainMarker() {
    //   const marker = this.createMarker(this.config.center, {
    //     icon: this.defaultMarkerIcon()
    //   })
    //   marker.on('click', this.handleMainMarkerClick)
    //   this.map.add(marker)
    // },

    // 更新目标标记
    // refreshMarkers() {
    //   this.clearMarkers()
      
    //   this.markers = this.targets.map(target => {
    //     const marker = this.createMarker(target.coordinates, {
    //       icon: this.varMarkerIcon()
    //     })
    //     marker.setExtData(target)
    //     marker.on('click', this.handleMarkerClick)
    //     return marker
    //   })

    //   if (this.markers.length) {
    //     this.map.add(this.markers)
    //     this.map.setFitView(this.markers)
    //   }
    // },
    refreshMarkers() {
      // 1. 检查地图实例
      if (!this.map || !this.AMap) return

      // 2. 生成新标记数组
      const newMarkers = []
      this.targets.forEach(target => {   
        // Check if target has valid coordinates
        if (!target.geometry?.coordinates) {
          console.warn('Missing coordinates for target:', target)
          return
        }

        // Exclude points with coordinates [0, 0] 排除未起飞时生成的无效点
        const [lng, lat] = target.geometry.coordinates
        if (lng === 0 && lat === 0) {
          console.warn('Excluding target with coordinates [0, 0]:', target)
          return
        }

        const existing = this.markers.find(m => m.getExtData().id === target.properties.id)
        if (existing) {
          existing.setPosition(this.validateCoordinates(target.geometry.coordinates))
          newMarkers.push(existing)
        } else {
          const marker = this.createMarker(target.geometry.coordinates, {
            icon: this.getMarkerIcon(target.properties.type)
          })
          marker.setExtData(target.properties)
          marker.on('click', this.handleMarkerClick)
          newMarkers.push(marker)
        }
      })

      // 3. 计算需移除的旧标记
      const toRemove = this.markers.filter(m => 
        !newMarkers.some(nm => nm.getExtData()?.id === m.getExtData()?.id)
      )
      this.map.remove(toRemove)

      console.log("newMarkers:", newMarkers)
      console.log("toRemove:", toRemove)

      // 4. 计算需添加的新标记
      const toAdd = newMarkers.filter(m => 
        !this.markers.some(old => old.getExtData().id === m.getExtData().id)
      )

      // 5. 添加新标记并调整视图
      if (toAdd.length) {
        this.map.add(toAdd, () => {
          this.markers = newMarkers;
          // this.zoomToMarkers();
          // this.map.setFitView()
        })
        // this.map.setFitView()

      } else {
        this.markers = newMarkers;
        // this.zoomToMarkers();
        // this.map.setFitView()
      }
    },

    // 通过点绘制区域
    /**
     * positions：经纬度点位坐标 例子 [[x,y],[x,y].....]
    */
    // handleDrawFilter(positions) {
    //   let polygon = new AMap.Polygon({
    //     path: positions, //以positions.length个点的坐标创建一个隐藏的多边形
    //     map: this.mapObj, //地图对象实例
    //     strokeOpacity: 0, //透明
    //     fillOpacity: 0, //透明
    //     bubble: true, //事件穿透到地图
    //   });
    //   //获取多边形图层
    //   let overlaysList = this.mapObj.getAllOverlays("polygon"); 
    //   return overlaysList;
    // },
    // 修改后的 refreshMarkers 方法

    // 新增视野调整方法
    zoomToMarkers() {
      if (!this.markers.length) return;

      // 防抖处理防止频繁调用
      clearTimeout(this.zoomTimer);
      this.zoomTimer = setTimeout(() => {
        try {
          const validPositions = this.markers
            .map(m => m.getPosition())
            .filter(pos => 
              pos && 
              !isNaN(pos.lng) && 
              !isNaN(pos.lat)
            );

          if (validPositions.length === 0) return;

          // 方法一：直接使用标记数组
          // this.map.setFitView(this.markers, {
          //   padding: [100, 100],
          //   duration: 300
          // });

          // 方法二：通过坐标范围计算（备选方案）
          const bounds = this.calculateBounds(validPositions);
          this.map.setBounds(bounds);
          
        } catch (error) {
          console.error('视野调整失败:', error);
        }
      }, 50);
    },

    // 新增边界计算工具方法
    calculateBounds(positions) {
      const lngs = positions.map(p => p.lng);
      const lats = positions.map(p => p.lat);
      
      return new this.AMap.Bounds(
        [Math.min(...lngs), Math.min(...lats)],
        [Math.max(...lngs), Math.max(...lats)]
      );
    },

    // 废弃 handleDrawFilter 方法


    // 清除旧标记
    clearMarkers() {
      this.markers.forEach(marker => marker.off())
      this.map.remove(this.markers)
    },

    /* 工具方法 */
    createMarker(position, config = {}) {
      return new this.AMap.Marker({
        position: this.validateCoordinates(position),
        icon: config.icon || this.defaultMarkerIcon(),
        offset: new this.AMap.Pixel(-13, -30),
        ...config.options
      })
    },

    validateCoordinates(coords) {
      if (!Array.isArray(coords) || coords.length !== 2) {
        console.error('无效坐标:', coords)
        return this.config.center
      }
      return coords.map(Number)
    },

    getMarkerIcon(type) {
      switch (type) {
        case 'drone':
          return '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png'
        case 'mission':
          return '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png'//'//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-blue.png'
        default:
          return this.defaultMarkerIcon()
      }
      // return '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png'
    },

    defaultMarkerIcon() {
      return '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png'
    },

    varMarkerIcon() {
      return new this.AMap.Icon({
        // 图标尺寸
        size: new this.AMap.Size(25, 34),
        // 图标的取图地址
        image: '//a.amap.com/jsapi_demos/static/demo-center/icons/dir-var-marker.png',
        // 图标所用图片大小
        imageSize: new this.AMap.Size(135, 40),
        // 图标取图偏移量
        imageOffset: new this.AMap.Pixel(-9, -3)
      })
    },

    /* 事件处理 */
    handleMarkerClick(e) {
      const infoWindow = new this.AMap.InfoWindow({
        content: this.createInfoContent(e.target.getExtData()),
        offset: new this.AMap.Pixel(0, -30)
      })
      infoWindow.open(this.map, e.target.getPosition())
    },

    handleMainMarkerClick(e) {
      // 主标记点点击逻辑
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

    createInfoContent(data) {
      if (!data) return '';
      
      const markerPosition = this.map.getAllOverlays('marker')
        .find(m => m.getExtData()?.id === data.id)
        ?.getPosition();
        
      const coords = markerPosition ? 
        [markerPosition.getLng(), markerPosition.getLat()] : 
        this.config.center;

      let content = `
        <div class="drone-info">
          <h4>${data.name || data.sn || '未命名'}</h4>
          <p>类型: ${data.type === 'drone' ? '无人机' : '任务点'}</p>`;

      if (data.type === 'drone') {
        content += `
          <p>状态: ${data.status?.text || '未知'}</p>
          <p>电量: ${data.battery || 0}%</p>
          <p>高度: ${data.altitude || 0}米</p>
          <p>编号: ${data.sn || '未知'}</p>`;
      } else if (data.type === 'mission') {
        content += `
          <p>状态: ${data.status?.text || '未知'}</p>
          <p>开始时间: ${new Date(data.start_time).toLocaleString()}</p>
          ${data.end_time ? `<p>结束时间: ${new Date(data.end_time).toLocaleString()}</p>` : ''}
          <p>关联无人机: ${data.drones?.map(d => d.sn).join(', ') || '无'}</p>`;
      }

      content += `
          <p>位置：${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}</p>
        </div>`;

      return content;
    },

    /* 资源清理 */
    cleanupResources() {
      if (this.currentInfoWindow) {
        this.currentInfoWindow.close()
        this.currentInfoWindow = null
      }
      if (this.updateInterval) clearInterval(this.updateInterval)
      if (this.map) {
        this.map.destroy()
        this.map = null
      }
      if (window.AMapLoader && !document.querySelector('#amap-script')) {
        delete window.AMapLoader
      }
    }
  }
}
</script>

<style scoped>
.a-map-container {
  position: relative;
  width: 100%;
  height: 100vh;
}

.map-wrapper {
  width: 100%;
  height: 100%;
}

/* 自定义标记样式 */
.drone-marker {
  position: relative;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #3388FF;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
}

.drone-marker .pulse {
  position: absolute;
  border: 2px solid #3388FF;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(2); opacity: 0; }
}

.drone-info {
  padding: 12px;
  min-width: 200px;
}
</style>