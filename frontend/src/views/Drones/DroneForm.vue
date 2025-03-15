
<!-- src/views/Drones/DroneForm.vue -->
<template>
    <div class="drone-form">
      <h1>{{ isEditMode ? '编辑无人机' : '新建无人机' }}</h1>
      
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>名称</label>
          <input 
            v-model="formData.name" 
            type="text" 
            required
          >
        </div>
  
        <div class="form-group">
          <label>状态</label>
          <select v-model="formData.status">
            <option value="active">正常</option>
            <option value="maintenance">维护中</option>
          </select>
        </div>
  
        <div class="form-actions">
          <button type="submit" :disabled="isLoading">
            {{ isEditMode ? '更新' : '创建' }}
          </button>
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
  
        <div v-if="error" class="error-alert">
          {{ error }}
        </div>
      </form>
    </div>
  </template>
  
  <script>
  import { mapGetters, mapActions } from 'vuex'
  
  export default {
    name: 'DroneForm',
    
    props: {
      droneId: {
        type: [String, Number],
        default: null
      }
    },
  
    data() {
      return {
        formData: {
          name: '',
          status: 'active'
        }
      }
    },
  
    
    computed: {
      ...mapGetters('drone', ['isLoading', 'error']),
      isEditMode() {
        return !!this.droneId
      }
    },
  
    async created() {
      if (this.isEditMode) {
        const drone = await this.$store.dispatch('drones/fetchDrone', this.droneId)
        this.formData = { ...drone }
      }
    },
  
    methods: {
      ...mapActions('drone', ['createDrone', 'updateDrone']),
  
      async handleSubmit() {
        try {
          if (this.isEditMode) {
            await this.updateDrone({
              id: this.droneId,
              data: this.formData
            })
          } else {
            await this.createDrone(this.formData)
          }
          this.$router.push('/dashboard')
        } catch (error) {
          console.error('操作失败:', error)
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .drone-form {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    margin-bottom: 8px;
  }
  
  input, select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  .form-actions {
    margin-top: 30px;
  }
  
  button {
    background: #28a745;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
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
  