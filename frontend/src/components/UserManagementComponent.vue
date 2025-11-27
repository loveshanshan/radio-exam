<template>
  <div class="user-management">
    <t-card>
      <template #header>
        <div class="management-header">
          <h3>用户管理</h3>
          <t-button theme="primary" @click="showAddDialog = true">
            <template #icon>
              <t-icon name="add" />
            </template>
            添加用户
          </t-button>
        </div>
      </template>

      <t-table
        :data="users"
        :columns="columns"
        :loading="loading"
        row-key="user_id"
        :pagination="pagination"
        @page-change="handlePageChange"
      >
        <template #is_admin="{ row }">
          <t-tag :theme="row.is_admin ? 'primary' : 'default'">
            {{ row.is_admin ? '管理员' : '普通用户' }}
          </t-tag>
        </template>

        <template #status="{ row }">
          <t-space direction="vertical" size="small">
            <t-tag :theme="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </t-tag>
            <t-tag 
              v-if="!row.is_admin && row.access_status === 'expired'" 
              theme="danger"
              size="small"
            >
              已过期
            </t-tag>
            <t-tag 
              v-if="!row.is_admin && row.days_left !== undefined && row.days_left !== null" 
              :theme="row.days_left <= 7 ? 'warning' : 'success'"
              size="small"
            >
              剩余{{ row.days_left }}天
            </t-tag>
          </t-space>
        </template>

        <template #operation="{ row }">
          <t-space>
            <t-button
              v-if="!row.is_admin"
              theme="primary"
              variant="text"
              size="small"
              @click="editUserTime(row)"
            >
              设置时间
            </t-button>
            <t-button
              v-if="!row.is_admin"
              theme="warning"
              variant="text"
              size="small"
              @click="resetPassword(row)"
            >
              重置密码
            </t-button>
            <t-button
              v-if="!row.is_admin"
              theme="danger"
              variant="text"
              size="small"
              @click="deleteUser(row)"
            >
              删除
            </t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- 添加用户弹窗 -->
    <t-dialog
      v-model:visible="showAddDialog"
      header="添加用户"
      :on-confirm="handleAddUser"
      :confirm-loading="addLoading"
    >
      <t-form ref="addForm" :rules="addRules" :data="addFormData">
        <t-form-item label="手机号" name="phone">
          <t-input
            v-model="addFormData.phone"
            placeholder="请输入手机号"
            :maxlength="11"
          />
        </t-form-item>
        <t-form-item label="开始时间" name="start_time">
          <t-date-picker
            v-model="addFormData.start_time"
            placeholder="请选择开始时间（可选）"
            format="YYYY-MM-DD HH:mm:ss"
            enable-time-picker
            clearable
          />
        </t-form-item>
        <t-form-item label="到期时间" name="expire_time">
          <t-date-picker
            v-model="addFormData.expire_time"
            placeholder="请选择到期时间（可选）"
            format="YYYY-MM-DD HH:mm:ss"
            enable-time-picker
            clearable
          />
        </t-form-item>
      </t-form>
      
      <t-alert theme="info" message="新用户默认密码为: wxd666a" />
    </t-dialog>

    <!-- 重置密码确认弹窗 -->
    <t-dialog
      v-model:visible="showResetDialog"
      header="重置密码"
      :on-confirm="confirmResetPassword"
      :confirm-loading="resetLoading"
    >
      <p>确定要重置用户 <strong>{{ selectedUser?.phone }}</strong> 的密码吗？</p>
      <p>密码将重置为: <strong>wxd666a</strong></p>
    </t-dialog>

    <!-- 设置时间限制弹窗 -->
    <t-dialog
      v-model:visible="showTimeDialog"
      header="设置用户时间限制"
      :on-confirm="confirmUpdateTime"
      :confirm-loading="timeLoading"
    >
      <t-form ref="timeForm" :data="timeFormData">
        <t-form-item label="用户">
          <t-input :value="selectedUser?.phone" disabled />
        </t-form-item>
        <t-form-item label="开始时间">
          <t-date-picker
            v-model="timeFormData.start_time"
            placeholder="请选择开始时间（可选）"
            format="YYYY-MM-DD HH:mm:ss"
            enable-time-picker
            clearable
          />
        </t-form-item>
        <t-form-item label="到期时间">
          <t-date-picker
            v-model="timeFormData.expire_time"
            placeholder="请选择到期时间（可选）"
            format="YYYY-MM-DD HH:mm:ss"
            enable-time-picker
            clearable
          />
        </t-form-item>
      </t-form>
    </t-dialog>

    <!-- 删除用户确认弹窗 -->
    <t-dialog
      v-model:visible="showDeleteDialog"
      header="删除用户"
      :on-confirm="confirmDeleteUser"
      :confirm-loading="deleteLoading"
    >
      <p>确定要删除用户 <strong>{{ selectedUser?.phone }}</strong> 吗？</p>
      <t-alert theme="warning" message="此操作不可恢复！" />
    </t-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { MessagePlugin, DialogPlugin } from 'tdesign-vue-next'
import axios from 'axios'

const loading = ref(false)
const addLoading = ref(false)
const resetLoading = ref(false)
const deleteLoading = ref(false)
const timeLoading = ref(false)
const showAddDialog = ref(false)
const showResetDialog = ref(false)
const showDeleteDialog = ref(false)
const showTimeDialog = ref(false)
const selectedUser = ref(null)
const addForm = ref()
const timeForm = ref()

const users = ref([])

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const addFormData = reactive({
  phone: '',
  start_time: '',
  expire_time: ''
})

const timeFormData = reactive({
  start_time: '',
  expire_time: ''
})

const addRules = {
  phone: [
    { required: true, message: '请输入手机号' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }
  ]
}

const columns = [
  {
    colKey: 'user_id',
    title: '用户ID',
    width: 120
  },
  {
    colKey: 'phone',
    title: '手机号',
    width: 150
  },
  {
    colKey: 'is_admin',
    title: '角色',
    width: 100
  },
  {
    colKey: 'status',
    title: '状态',
    width: 120
  },
  {
    colKey: 'start_time',
    title: '开始时间',
    width: 180
  },
  {
    colKey: 'expire_time',
    title: '到期时间',
    width: 180
  },
  {
    colKey: 'created_at',
    title: '创建时间',
    width: 180
  },
  {
    colKey: 'operation',
    title: '操作',
    width: 200
  }
]

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/auth/users')
    users.value = response.data.users
    pagination.total = users.value.length
  } catch (error) {
    console.error('加载用户列表失败:', error)
    MessagePlugin.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleAddUser = async () => {
  const valid = await addForm.value.validate()
  if (!valid) return

  addLoading.value = true
  try {
    const response = await axios.post('/api/auth/register', addFormData)
    
    if (response.data.success) {
      MessagePlugin.success(`用户添加成功，默认密码: ${response.data.user.password}`)
      showAddDialog.value = false
      addFormData.phone = ''
      await loadUsers()
    }
  } catch (error) {
    console.error('添加用户失败:', error)
    const message = error.response?.data?.error || '添加用户失败'
    MessagePlugin.error(message)
  } finally {
    addLoading.value = false
  }
}

const resetPassword = (user) => {
  selectedUser.value = user
  showResetDialog.value = true
}

const confirmResetPassword = async () => {
  resetLoading.value = true
  try {
    const response = await axios.post(`/api/auth/reset-password/${selectedUser.value.user_id}`)
    
    if (response.data.success) {
      MessagePlugin.success(`密码重置成功: ${response.data.new_password}`)
      showResetDialog.value = false
    }
  } catch (error) {
    console.error('重置密码失败:', error)
    const message = error.response?.data?.error || '重置密码失败'
    MessagePlugin.error(message)
  } finally {
    resetLoading.value = false
  }
}

const deleteUser = (user) => {
  selectedUser.value = user
  showDeleteDialog.value = true
}

const confirmDeleteUser = async () => {
  deleteLoading.value = true
  try {
    const response = await axios.delete(`/api/auth/users/${selectedUser.value.user_id}`)
    
    if (response.data.success) {
      MessagePlugin.success('用户删除成功')
      showDeleteDialog.value = false
      await loadUsers()
    }
  } catch (error) {
    console.error('删除用户失败:', error)
    const message = error.response?.data?.error || '删除用户失败'
    MessagePlugin.error(message)
  } finally {
    deleteLoading.value = false
  }
}

const editUserTime = (user) => {
  selectedUser.value = user
  timeFormData.start_time = user.start_time || ''
  timeFormData.expire_time = user.expire_time || ''
  showTimeDialog.value = true
}

const confirmUpdateTime = async () => {
  timeLoading.value = true
  try {
    const response = await axios.post(`/api/auth/update-user-time/${selectedUser.value.user_id}`, timeFormData)
    
    if (response.data.success) {
      MessagePlugin.success('用户时间限制更新成功')
      showTimeDialog.value = false
      await loadUsers()
    }
  } catch (error) {
    console.error('更新时间限制失败:', error)
    const message = error.response?.data?.error || '更新时间限制失败'
    MessagePlugin.error(message)
  } finally {
    timeLoading.value = false
  }
}

const handlePageChange = (pageInfo) => {
  pagination.current = pageInfo.current
  pagination.pageSize = pageInfo.pageSize
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.management-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 18px;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-management {
    padding: 16px;
  }
  
  .management-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .management-header h3 {
    font-size: 16px;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .user-management {
    padding: 8px;
  }
  
  .management-header {
    gap: 8px;
  }
  
  .management-header h3 {
    font-size: 14px;
  }
}

/* 平板端优化 */
@media (min-width: 769px) and (max-width: 1024px) {
  .user-management {
    padding: 18px;
  }
  
  .management-header h3 {
    font-size: 17px;
  }
}

/* 大屏幕优化 */
@media (min-width: 1200px) {
  .user-management {
    padding: 24px;
  }
  
  .management-header h3 {
    font-size: 20px;
  }
}
</style>