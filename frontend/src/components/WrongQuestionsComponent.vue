<template>
  <div class="practice-container">
    <t-card v-if="!practiceQuestions || practiceQuestions.length === 0" class="empty-card">
      <t-result title="暂无错题可练习" description="继续保持全对！">
        <template #icon>
          <t-icon name="check-circle-filled" style="color: #00a870; font-size: 64px;" />
        </template>
        <template #operations>
          <t-button theme="primary" @click="goToExam">开始考试</t-button>
        </template>
      </t-result>
    </t-card>

    <div v-else>
      <t-card>
        <template #header>
          <div class="practice-header">
            <span>错题练习</span>
            <span>进度: {{ currentPracticeIndex + 1 }}/{{ practiceQuestions.length }}</span>
            <t-tag theme="warning">多选题</t-tag>
          </div>
        </template>

        <div class="question-content">
          <h3>{{ currentPracticeQuestion.question }}</h3>
          
          <t-checkbox-group 
            v-model="practiceAnswers[currentPracticeQuestion.id]"
          >
            <t-space direction="vertical" size="large">
              <t-checkbox 
                v-for="option in currentPracticeQuestion.options" 
                :key="option.key" 
                :value="option.key"
                class="option-item"
              >
                {{ option.key }}. {{ option.text }}
              </t-checkbox>
            </t-space>
          </t-checkbox-group>
        </div>

        <template #footer>
          <t-space>
            <t-button 
              :disabled="currentPracticeIndex === 0" 
              @click="prevPracticeQuestion"
            >
              上一题
            </t-button>
            <t-button 
              v-if="currentPracticeIndex < practiceQuestions.length - 1"
              theme="primary" 
              @click="nextPracticeQuestion"
            >
              下一题
            </t-button>
            <t-button 
              v-else
              theme="success" 
              @click="submitPractice"
              :disabled="!isAllAnswered"
            >
              提交练习
            </t-button>
          </t-space>
        </template>
      </t-card>
    </div>

    <!-- 练习结果弹窗 -->
    <t-dialog
      v-model:visible="showPracticeResult"
      header="练习结果"
      :footer="null"
      width="700px"
    >
      <div class="result-content">
        <t-result
          :title="`完成度: ${practiceResult.completed_count}/${practiceQuestions.length}`"
          :description="`本次正确: ${practiceResult.correct_count} (正确率: ${practiceResult.score || 0}%)`"
        >
          <template #icon>
            <t-icon :name="(practiceResult.score || 0) >= 60 ? 'check-circle-filled' : 'error-circle-filled'" 
                   :style="`color: ${(practiceResult.score || 0) >= 60 ? '#00a870' : '#e34d59'}; font-size: 64px;`" />
          </template>
        </t-result>
        
        <!-- 错题详情 -->
        <div v-if="practiceResult.wrong_questions && practiceResult.wrong_questions.length > 0" class="wrong-details">
          <h4>错题详情：</h4>
          <t-list>
            <t-list-item v-for="wrong in practiceResult.wrong_questions" :key="wrong.question_id">
              <div class="wrong-item">
                <p><strong>题目ID:</strong> {{ wrong.question_id }}</p>
                <p><strong>题目:</strong> {{ wrong.question_text }}</p>
                <p><strong>你的答案:</strong> <span class="wrong-answer">{{ wrong.user_answer || '未作答' }}</span></p>
                <p><strong>正确答案:</strong> <span class="correct-answer">{{ wrong.correct_answer }}</span></p>
              </div>
            </t-list-item>
          </t-list>
        </div>
        
        <!-- 正确题目统计 -->
        <div v-if="practiceResult.correct_questions && practiceResult.correct_questions.length > 0" class="correct-details">
          <h4>答对题目：</h4>
          <t-tag v-for="correct in practiceResult.correct_questions" :key="correct.question_id" 
                  theme="success" class="correct-tag">
            题目{{ correct.question_id }}
          </t-tag>
        </div>
        
        <!-- 移除的题目统计 -->
        <div v-if="practiceResult.updated_questions && practiceResult.updated_questions.length > 0" class="removed-details">
          <h4>已掌握题目：</h4>
          <t-tag v-for="updated in practiceResult.updated_questions.filter(q => q.action === 'removed')" 
                  :key="updated.question_id" theme="success" variant="light" class="removed-tag">
            题目{{ updated.question_id }} (连续答对3次)
          </t-tag>
        </div>
        
        <t-space>
          <t-button 
            v-if="hasRemainingQuestions"
            theme="primary" 
            @click="resetPractice"
          >
            继续练习
          </t-button>
          <t-button 
            v-else
            theme="success" 
            disabled
          >
            当前错题练习已完成
          </t-button>
          <t-button @click="goToExam">返回考试</t-button>
        </t-space>
      </div>
    </t-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import axios from 'axios'

// 定义事件
const emit = defineEmits(['switch-tab'])

const practiceQuestions = ref([])
const currentPracticeIndex = ref(0)
const practiceAnswers = ref({})
const showPracticeResult = ref(false)
const practiceResult = ref({})
const hasRemainingQuestions = ref(true)

// 创建axios实例
// const api = axios.create({
//   baseURL: 'http://localhost:5000',
//   timeout: 5000
// })

const currentPracticeQuestion = computed(() => {
  if (!practiceQuestions.value.length) return null
  return practiceQuestions.value[currentPracticeIndex.value]
})

const isAllAnswered = computed(() => {
  return practiceQuestions.value.every(q => 
    practiceAnswers.value[q.id] !== undefined && 
    Array.isArray(practiceAnswers.value[q.id]) && 
    practiceAnswers.value[q.id].length > 0
  )
})



const loadPracticeQuestions = async () => {
  try {
    const response = await axios.get('/api/wrong-questions')
    practiceQuestions.value = response.data.map(item => item.question)
    practiceAnswers.value = {}
    practiceQuestions.value.forEach(q => {
      practiceAnswers.value[q.id] = []
    })
  } catch (error) {
    console.error('加载错题失败:', error)
    MessagePlugin.error('加载错题失败，请检查后端服务')
  }
}



const nextPracticeQuestion = () => {
  if (currentPracticeIndex.value < practiceQuestions.value.length - 1) {
    currentPracticeIndex.value++
  }
}

const prevPracticeQuestion = () => {
  if (currentPracticeIndex.value > 0) {
    currentPracticeIndex.value--
  }
}

const submitPractice = async () => {
  try {
    // 准备提交数据
    const submitData = {
      exam_id: `practice_${Date.now()}`,
      answers: {}
    }
    
    // 构建答案对象
    for (const q of practiceQuestions.value) {
      const userAnswer = practiceAnswers.value[q.id]
      submitData.answers[q.id] = Array.isArray(userAnswer) ? userAnswer.sort().join('') : userAnswer
    }
    
    // 调用后端API提交练习结果
    const response = await axios.post('/api/wrong-questions/practice-submit', submitData)
    
    // 处理响应数据，确保包含完整的错题和正确题目信息
    practiceResult.value = {
      completed_count: response.data.total,
      correct_count: response.data.correct_count,
      score: response.data.score,
      wrong_questions: response.data.wrong_questions || [],
      correct_questions: response.data.correct_questions || [],
      updated_questions: response.data.updated_questions || [],
      results: response.data.results || []
    }
    
    // 检查是否还有剩余的错题
    const removedCount = (response.data.updated_questions || []).filter(q => q.action === 'removed').length
    const remainingCount = response.data.total - removedCount
    hasRemainingQuestions.value = remainingCount > 0
    
    showPracticeResult.value = true
    
    // 显示成功消息
    MessagePlugin.success(`练习提交成功！正确率: ${response.data.score}%`)
    
  } catch (error) {
    console.error('提交练习失败:', error)
    MessagePlugin.error('提交练习失败，请检查网络连接')
  }
}

const resetPractice = async () => {
  showPracticeResult.value = false
  currentPracticeIndex.value = 0
  practiceAnswers.value = {}
  
  // 重新加载错题，获取最新的错题列表
  await loadPracticeQuestions()
  
  // 重置答案
  practiceQuestions.value.forEach(q => {
    practiceAnswers.value[q.id] = []
  })
}

const goToExam = () => {
  // 触发父组件切换标签页
  emit('switch-tab', 'exam')
}



onMounted(() => {
  // 注释掉自动加载，让用户选择
  loadPracticeQuestions()
})
</script>

<style scoped>
.practice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.question-content {
  min-height: 300px;
}

.option-item {
  display: block;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.option-item:hover {
  background-color: #f5f5f5;
}

.result-content {
  text-align: center;
  padding: 20px;
}

.empty-card {
  max-width: 500px;
  margin: 50px auto;
}

/* 错题详情样式 */
.wrong-details {
  margin-top: 20px;
  text-align: left;
}

.wrong-details h4 {
  color: #e34d59;
  margin-bottom: 10px;
  font-size: 16px;
}

.wrong-item {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 8px;
}

.wrong-item p {
  margin: 4px 0;
  font-size: 14px;
  line-height: 1.5;
}

.wrong-answer {
  color: #e34d59;
  font-weight: bold;
}

.correct-answer {
  color: #00a870;
  font-weight: bold;
}

/* 正确题目样式 */
.correct-details {
  margin-top: 20px;
  text-align: left;
}

.correct-details h4 {
  color: #00a870;
  margin-bottom: 10px;
  font-size: 16px;
}

.correct-tag {
  margin: 4px;
}

/* 已掌握题目样式 */
.removed-details {
  margin-top: 20px;
  text-align: left;
}

.removed-details h4 {
  color: #00a870;
  margin-bottom: 10px;
  font-size: 16px;
}

.removed-tag {
  margin: 4px;
  background-color: #f0f9ff;
  border-color: #b3e0ff;
  color: #0052cc;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .practice-container {
    padding: 16px;
  }
  
  .empty-card {
    max-width: 100%;
    margin: 30px 16px;
  }
  
  .practice-header {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
  
  .question-content h3 {
    font-size: 16px;
    line-height: 1.5;
  }
  
  .option-item {
    font-size: 14px;
    line-height: 1.4;
  }
  
  .wrong-details,
  .correct-details {
    margin-top: 16px;
  }
  
  .wrong-item {
    padding: 8px;
    margin-bottom: 6px;
  }
  
  .wrong-item p {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .practice-container {
    padding: 8px;
  }
  
  .empty-card {
    margin: 20px 8px;
  }
  
  .question-content h3 {
    font-size: 14px;
  }
  
  .option-item {
    font-size: 12px;
  }
  
  .wrong-details h4,
  .correct-details h4 {
    font-size: 14px;
  }
  
  .wrong-item p {
    font-size: 11px;
  }
}

/* 平板端优化 */
@media (min-width: 769px) and (max-width: 1024px) {
  .empty-card {
    max-width: 600px;
    margin: 40px auto;
  }
  
  .question-content h3 {
    font-size: 18px;
  }
  
  .option-item {
    font-size: 15px;
  }
}

/* 大屏幕优化 */
@media (min-width: 1200px) {
  .empty-card {
    max-width: 600px;
    margin: 60px auto;
  }
  
  .question-content h3 {
    font-size: 20px;
  }
  
  .option-item {
    font-size: 16px;
  }
}
</style>