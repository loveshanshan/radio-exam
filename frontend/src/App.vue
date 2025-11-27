<template>
  <t-config-provider :global-config="globalConfig">
    <!-- 登录页面 -->
    <LoginComponent v-if="!isLoggedIn" @login-success="handleLoginSuccess" />
    
    <!-- 主应用 -->
    <div v-else class="app-container">
      <t-header class="header">
        <div class="header-content">
          <h1>业余无线电考试练习系统</h1>
          <div class="user-info">
            <div class="user-basic-info">
              <span>{{ currentUser.phone }}</span>
              <t-tag :theme="currentUser.is_admin ? 'primary' : 'default'" size="small">
                {{ currentUser.is_admin ? '管理员' : '普通用户' }}
              </t-tag>
              <!-- 显示时间限制信息 -->
              <div v-if="!currentUser.is_admin && userAccessInfo" class="access-info">
                <t-tag 
                  v-if="userAccessInfo.days_left !== undefined && userAccessInfo.days_left !== null" 
                  :theme="userAccessInfo.days_left <= 7 ? 'warning' : 'success'"
                  size="small"
                >
                  剩余{{ userAccessInfo.days_left }}天
                </t-tag>
                <t-tag 
                  v-if="userAccessInfo.expire_time" 
                  theme="info"
                  size="small"
                >
                  {{ formatDate(userAccessInfo.expire_time) }}
                </t-tag>
              </div>
            </div>
          <div class="user-actions">
            <t-button 
              variant="outline" 
              size="small"
              @click="showPasswordDialog = true"
              class="action-btn"
            >
              <t-icon name="lock-on" />
              修改密码
            </t-button>
            <t-button 
              variant="outline" 
              theme="danger" 
              size="small"
              @click="handleLogout"
              class="action-btn"
            >
              <t-icon name="logout" />
              退出登录
            </t-button>
          </div>
          </div>
        </div>
      </t-header>
      
      <t-tabs v-model="activeTab" class="main-tabs">
        <t-tab-panel value="exam" label="考试题库">
          <ExamComponent @switch-tab="activeTab = $event" />
        </t-tab-panel>
        <t-tab-panel value="wrong" label="错题本">
          <WrongQuestionsComponent @switch-tab="activeTab = $event" />
        </t-tab-panel>
        <t-tab-panel v-if="currentUser.is_admin" value="users" label="用户管理">
          <UserManagementComponent />
        </t-tab-panel>

      </t-tabs>
    </div>

    <!-- 修改密码弹窗 -->
    <t-dialog
      v-model:visible="showPasswordDialog"
      header="修改密码"
      width="600px"
      :confirm-btn="null"
      :cancel-btn="{ content: '关闭', theme: 'default' }"
    >
      <PasswordChangeComponent @success="showPasswordDialog = false" />
    </t-dialog>

    <!-- 账号过期提示弹窗 -->
    <t-dialog
      v-model:visible="showExpiredDialog"
      header="账号已过期"
      :confirm-btn="null"
      :cancel-btn="{ content: '确定', theme: 'primary' }"
    >
      <div class="expired-content">
        <t-icon name="error-circle" size="48px" color="#ed7b2f" />
        <p class="expired-message">当前账号已到期，请联系管理员！</p>
        <p class="expired-contact">请联系管理员续费或重置使用时间。</p>
      </div>
    </t-dialog>
  </t-config-provider>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import axios from 'axios'
import LoginComponent from './components/LoginComponent.vue'
import ExamComponent from './components/ExamComponent.vue'
import WrongQuestionsComponent from './components/WrongQuestionsComponent.vue'
import UserManagementComponent from './components/UserManagementComponent.vue'
import PasswordChangeComponent from './components/PasswordChangeComponent.vue'

const activeTab = ref('exam')
const isLoggedIn = ref(false)
const currentUser = ref({})
const userAccessInfo = ref(null)
const showExpiredDialog = ref(false)
const showPasswordDialog = ref(false)



const globalConfig = {
  calendar: {},
  table: {},
  pagination: {}
}

const handleLoginSuccess = (user) => {
  currentUser.value = user
  isLoggedIn.value = true
  
  // 检查用户访问权限
  if (!user.is_admin) {
    checkUserAccess()
  }
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  delete axios.defaults.headers.common['Authorization']
  currentUser.value = {}
  isLoggedIn.value = false
  MessagePlugin.success('已退出登录')
}

const checkUserAccess = async () => {
  try {
    const response = await axios.get('/api/auth/user-access')
    if (response.data.success) {
      userAccessInfo.value = response.data
      
      if (!response.data.access) {
        showExpiredDialog.value = true
      }
    }
  } catch (error) {
    console.error('检查用户访问权限失败:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const checkAuth = () => {
  const token = localStorage.getItem('token')
  const user = localStorage.getItem('user')
  
  if (token && user) {
    try {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      currentUser.value = JSON.parse(user)
      isLoggedIn.value = true
      
      // 验证token是否有效
      axios.post('/api/auth/verify')
        .then(() => {
          // 检查用户访问权限
          if (!currentUser.value.is_admin) {
            checkUserAccess()
          }
        })
        .catch(() => {
          handleLogout()
        })
    } catch (error) {
      handleLogout()
    }
  }
}

onMounted(() => {
  checkAuth()
})
</script>

<style>
.app-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  background: #0052d9;
  color: white;
  padding: 20px;
  position: relative;
  z-index: 10;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.access-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.expired-content {
  text-align: center;
  padding: 20px;
}

.expired-content .t-icon {
  margin-bottom: 16px;
}

.expired-message {
  font-size: 16px;
  font-weight: 600;
  color: #ed7b2f;
  margin: 16px 0 8px 0;
}

.expired-contact {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.main-tabs {
  margin: 20px;
  max-width: 1200px;
  position: relative;
  z-index: 1;
}

.t-tabs__content {
  background: white;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .header-content {
    max-width: 100%;
  }
  
  .main-tabs {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .header {
    padding: 16px;
    min-height: 120px;
  }
  
  .header-content {
    padding: 0;
    height: auto;
    min-height: auto;
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }
  
  .header-content h1 {
    font-size: 18px;
    text-align: center;
    margin-bottom: 4px;
  }
  
  .user-info {
    width: 100%;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  
  .user-basic-info {
    display: flex;
    align-items: center;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .user-actions {
    flex-direction: row;
    gap: 8px;
    width: 100%;
    max-width: 280px;
    justify-content: center;
  }
  
  .action-btn {
    flex: 1;
    min-width: 100px;
    justify-content: center;
  }
  
  .access-info {
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }
  
  .main-tabs {
    margin: 16px;
    position: relative;
    z-index: 1;
  }
  
  .t-tabs__content {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 12px;
    min-height: 110px;
  }
  
  .header-content {
    padding: 0;
  }
  
  .header-content h1 {
    font-size: 16px;
  }
  
  .user-info {
    font-size: 12px;
    gap: 6px;
  }
  
  .user-actions {
    gap: 6px;
    margin-top: 6px;
  }
  
  .action-btn {
    font-size: 10px;
    padding: 6px 8px;
    max-width: 100px;
  }
  
  .main-tabs {
    margin: 8px;
  }
  
  .t-tabs__content {
    padding: 12px;
  }
  
  .expired-content {
    padding: 16px;
  }
  
  .expired-message {
    font-size: 14px;
  }
  
  .expired-contact {
    font-size: 12px;
  }
}

/* 平板端优化 */
@media (min-width: 769px) and (max-width: 1024px) {
  .header-content {
    padding: 0 24px;
  }
  
  .header-content h1 {
    font-size: 19px;
  }
  
  .main-tabs {
    margin: 24px;
  }
}

/* 弹窗响应式优化 */
@media (max-width: 768px) {
  :deep(.t-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
  
  :deep(.t-dialog__body) {
    padding: 16px;
  }
}
</style>