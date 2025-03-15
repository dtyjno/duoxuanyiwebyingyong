import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  build:{
    // vite.config.js
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'vuex'],
        }
      }
    },
    outputDir:'dist', //#这里可以不加，生成的静态文档存放的文件夹名
    assetsDir:'static' //#静态资源存放的文件夹名
  },

  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true,
        rewrite: path => path.replace(/^\/api/, '')
      },
      '/ds_api': {
        target: 'https://deepseek.hdu.edu.cn',
        changeOrigin: true, // 是否跨域
        rewrite: path => path.replace(/^\/ds_api/, '')
      }
    }
  }
})

