import { createApp } from 'vue'
import TDesign from 'tdesign-vue-next'
import App from './App.vue'
import 'tdesign-vue-next/es/style/index.css'

// 导入axios配置
import './utils/axios.js'

// 导入响应式样式
import './styles/responsive.css'

const app = createApp(App)
app.use(TDesign)
app.mount('#app')