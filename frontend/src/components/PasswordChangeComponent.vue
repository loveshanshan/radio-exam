<template>
  <div class="password-change">
    <t-card>
      <template #header>
        <h3>修改密码</h3>
      </template>

      <t-form
        ref="passwordForm"
        :rules="passwordRules"
        :data="passwordData"
        @submit="handleSubmit"
      >
        <t-form-item label="当前密码" name="old_password">
          <t-input
            v-model="passwordData.old_password"
            type="password"
            placeholder="请输入当前密码"
            :maxlength="50"
          />
        </t-form-item>

        <t-form-item label="新密码" name="new_password">
          <t-input
            v-model="passwordData.new_password"
            type="password"
            placeholder="请输入新密码"
            :maxlength="50"
          />
        </t-form-item>

        <t-form-item label="确认新密码" name="confirm_password">
          <t-input
            v-model="passwordData.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            :maxlength="50"
          />
        </t-form-item>

        <t-form-item>
          <t-space size="large" class="button-group">
            <t-button
              theme="primary"
              type="submit"
              :loading="loading"
              size="large"
              class="submit-btn"
            >
              <t-icon name="check" />
              确认修改
            </t-button>
            <t-button
              theme="default"
              @click="resetForm"
              size="large"
              class="reset-btn"
            >
              <t-icon name="refresh" />
              重置表单
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

const loading = ref(false)
const passwordForm = ref()

const passwordData = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码' }
  ],
  new_password: [
    { required: true, message: '请输入新密码' },
    { min: 6, message: '密码长度不能少于6位' },
    { max: 50, message: '密码长度不能超过50位' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码' },
    {
      validator: (val) => val === passwordData.new_password,
      message: '两次输入的密码不一致'
    }
  ]
}

const emit = defineEmits(['success'])

const handleSubmit = async () => {
  const valid = await passwordForm.value.validate()
  if (!valid) return

  loading.value = true
  try {
    const response = await axios.post('/api/auth/change-password', {
      old_password: passwordData.old_password,
      new_password: passwordData.new_password
    })
    
    if (response.data.success) {
      MessagePlugin.success('密码修改成功')
      resetForm()
      emit('success') // 通知父组件关闭弹窗
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    const message = error.response?.data?.error || '修改密码失败'
    MessagePlugin.error(message)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  passwordData.old_password = ''
  passwordData.new_password = ''
  passwordData.confirm_password = ''
  passwordForm.value?.clearValidate()
}
</script>

<style scoped>
.password-change {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.password-change h3 {
  margin: 0;
  color: #1f2937;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.button-group {
  width: 100%;
  justify-content: center;
  margin-top: 8px;
}

.submit-btn, .reset-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 120px;
  transition: all 0.2s ease;
}

.submit-btn:hover, .reset-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .password-change {
    padding: 16px;
    max-width: 100%;
  }
  
  .password-change h3 {
    font-size: 16px;
  }
  
  .button-group {
    flex-direction: column;
    gap: 12px;
  }
  
  .submit-btn, .reset-btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .password-change {
    padding: 12px;
  }
  
  .password-change h3 {
    font-size: 14px;
  }
  
  :deep(.t-input) {
    font-size: 16px; /* 防止iOS缩放 */
  }
  
  .button-group {
    flex-direction: column;
    gap: 8px;
  }
  
  .submit-btn, .reset-btn {
    width: 100%;
    justify-content: center;
    font-size: 14px;
    padding: 12px;
  }
}

/* 平板端优化 */
@media (min-width: 769px) and (max-width: 1024px) {
  .password-change {
    padding: 18px;
    max-width: 500px;
  }
  
  .password-change h3 {
    font-size: 17px;
  }
}

/* 大屏幕优化 */
@media (min-width: 1200px) {
  .password-change {
    padding: 24px;
    max-width: 700px;
  }
  
  .password-change h3 {
    font-size: 20px;
  }
}
</style>