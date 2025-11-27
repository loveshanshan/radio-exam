<template>
  <div class="login-container">
    <t-card class="login-card">
      <template #header>
        <div class="login-header">
          <h2>业余无线电考试系统</h2>
          <p>请登录以继续</p>
        </div>
      </template>

      <t-form ref="loginForm" :rules="rules" :data="formData" @submit="handleLogin">
        <t-form-item label="手机号" name="phone">
          <t-input
            v-model="formData.phone"
            placeholder="请输入手机号"
            size="large"
            :maxlength="11"
          />
        </t-form-item>

        <t-form-item label="密码" name="password">
          <t-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            size="large"
          />
        </t-form-item>

        <t-form-item>
          <t-space direction="vertical" size="large" style="width: 100%;">
            <t-button
              type="submit"
              theme="primary"
              size="large"
              :loading="loading"
              block
            >
              登录
            </t-button>
          </t-space>
        </t-form-item>
      </t-form>
    </t-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import axios from 'axios'

const emit = defineEmits(['login-success'])

const loading = ref(false)
const loginForm = ref()

const formData = reactive({
  phone: '',
  password: ''
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }
  ],
  password: [
    { required: true, message: '请输入密码' },
    { min: 6, message: '密码长度不能少于6位' }
  ]
}

const handleLogin = async () => {
  const valid = await loginForm.value.validate()
  if (!valid) return

  loading.value = true
  
  try {
    const response = await axios.post('/api/auth/login', formData)
    
    if (response.data.success) {
      // 保存token到localStorage
      localStorage.setItem('token', response.data.token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      
      // 设置axios默认header
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`
      
      MessagePlugin.success('登录成功')
      emit('login-success', response.data.user)
    }
  } catch (error) {
    console.error('登录失败:', error)
    const message = error.response?.data?.error || '登录失败，请重试'
    MessagePlugin.error(message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

.login-header {
  text-align: center;
  margin-bottom: 20px;
}

.login-header h2 {
  color: #1f2937;
  margin-bottom: 8px;
  font-size: 24px;
  font-weight: 600;
}

.login-header p {
  color: #6b7280;
  margin: 0;
  font-size: 14px;
}

:deep(.t-card__header) {
  padding-bottom: 0;
}

:deep(.t-form-item__label) {
  font-weight: 500;
  color: #374151;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 16px;
  }
  
  .login-card {
    max-width: 100%;
  }
  
  .login-header h2 {
    font-size: 20px;
  }
  
  .login-header p {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .login-container {
    padding: 12px;
  }
  
  .login-card {
    max-width: 100%;
  }
  
  .login-header {
    margin-bottom: 16px;
  }
  
  .login-header h2 {
    font-size: 18px;
  }
  
  .login-header p {
    font-size: 12px;
  }
  
  :deep(.t-input) {
    font-size: 16px; /* 防止iOS缩放 */
  }
}

/* 平板端优化 */
@media (min-width: 769px) and (max-width: 1024px) {
  .login-card {
    max-width: 450px;
  }
  
  .login-header h2 {
    font-size: 22px;
  }
}

/* 大屏幕优化 */
@media (min-width: 1200px) {
  .login-card {
    max-width: 500px;
  }
  
  .login-header h2 {
    font-size: 26px;
  }
  
  .login-header p {
    font-size: 15px;
  }
}
</style>