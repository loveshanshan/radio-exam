import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // 将TDesign UI库单独打包
          'tdesign': ['tdesign-vue-next'],
          // 将Vue相关库单独打包
          'vue-vendor': ['vue', 'vue-router'],
          // 将axios单独打包
          'utils': ['axios']
        }
      }
    },
    // 提高chunk大小警告阈值到1MB
    chunkSizeWarningLimit: 1000
  },
  server: {
    host: '0.0.0.0', // 监听所有IP地址，支持局域网访问
    port: 3000,      // 指定端口
    strictPort: false, // 如果端口被占用，尝试其他端口
    cors: true,      // 启用CORS
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
