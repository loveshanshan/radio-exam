<template>
  <div class="exam-container">
    <t-card v-if="!currentExam" class="start-card">
      <template #actions>
        <t-button theme="primary" @click="startExam">开始考试</t-button>
        <t-button @click="startExamFromCustom">从指定题号开始</t-button>
      </template>
      <p>每次考试包含20道题目，全部完成后可提交</p>
      <p class="exam-tip">所有题目均为多选题，请选择所有正确答案</p>
    </t-card>

    <div v-else>
      <t-card>
        <template #header>
          <div class="exam-header">
            <span>题目ID: {{ currentQuestion.id }}</span>
            <span>进度: {{ currentQuestionIndex + 1 }}/{{ currentExam.questions.length }}</span>
            <t-tag theme="warning">多选题</t-tag>
          </div>
        </template>

        <div class="question-content">
          <h3>{{ currentQuestion.question }}</h3>
          
          <t-checkbox-group 
            v-model="userAnswers[currentQuestion.id]"
          >
            <t-space direction="vertical" size="large">
              <t-checkbox 
                v-for="option in currentQuestion.options" 
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
              :disabled="currentQuestionIndex === 0" 
              @click="prevQuestion"
            >
              上一题
            </t-button>
            <t-button 
              v-if="currentQuestionIndex < currentExam.questions.length - 1"
              theme="primary" 
              @click="nextQuestion"
            >
              下一题
            </t-button>
            <t-button 
              v-else
              theme="success" 
              @click="submitExam"
            >
              提交试卷
            </t-button>
          </t-space>
        </template>
      </t-card>
    </div>

    <!-- 自定义起始题号弹窗 -->
    <t-dialog
      v-model:visible="showCustomStartDialog"
      header="从指定题号开始"
      :on-confirm="confirmCustomStart"
    >
      <t-form>
        <t-form-item label="起始题号">
          <t-input-number v-model="customStartNumber" :min="1" :max="1000" />
        </t-form-item>
        <t-form-item label="题目数量">
          <t-input-number v-model="customQuestionCount" :min="1" :max="50" />
        </t-form-item>
      </t-form>
    </t-dialog>

    <!-- 提交结果弹窗 -->
    <t-dialog
      v-model:visible="showResult"
      header="考试结果"
      :footer="null"
      width="600px"
    >
      <div class="result-content">
        <t-result
          :title="`得分: ${examResult.score || 0}`"
          :description="`正确: ${examResult.correct_count || 0}/${examResult.total || 0} (正确率: ${examResult.score || 0}%)`"
        >
          <template #icon>
            <t-icon :name="(examResult.score || 0) >= 60 ? 'check-circle-filled' : 'error-circle-filled'" 
                   :style="`color: ${(examResult.score || 0) >= 60 ? '#00a870' : '#e34d59'}; font-size: 64px;`" />
          </template>
        </t-result>
        
        <div v-if="examResult.wrong_questions && examResult.wrong_questions.length > 0" class="wrong-details">
          <h4>错题详情：</h4>
          <t-list>
            <t-list-item v-for="wrong in examResult.wrong_questions" :key="wrong.question_id">
              <div class="wrong-item">
                <p><strong>题目ID:</strong> {{ wrong.question_id }}</p>
                <p><strong>题目:</strong> {{ wrong.question_text }}</p>
                <p><strong>你的答案:</strong> {{ wrong.user_answer || '未作答' }}</p>
                <p><strong>正确答案:</strong> {{ wrong.correct_answer }}</p>
              </div>
            </t-list-item>
          </t-list>
        </div>
        
        <t-space>
          <t-button theme="primary" @click="resetExam">返回首页</t-button>
          <t-button v-if="examResult.wrong_questions && examResult.wrong_questions.length > 0" 
                   theme="warning" @click="goToWrongPractice">练习错题</t-button>
        </t-space>
      </div>
    </t-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import axios from 'axios'

const emit = defineEmits(['switch-tab'])

const currentExam = ref(null)
const currentQuestionIndex = ref(0)
const userAnswers = ref({})
const showResult = ref(false)
const examResult = ref({
  exam_id: '',
  total: 0,
  correct_count: 0,
  score: 0,
  wrong_questions: [],
  results: []
})
const showCustomStartDialog = ref(false)
const customStartNumber = ref(1)
const customQuestionCount = ref(20)

const currentQuestion = computed(() => {
  if (!currentExam.value) return null
  return currentExam.value.questions[currentQuestionIndex.value]
})

// 监听题目变化，初始化答案（总是初始化为数组）
watch(currentQuestion, (newQuestion) => {
  if (newQuestion && !userAnswers.value[newQuestion.id]) {
    userAnswers.value[newQuestion.id] = []
  }
})

const startExam = async () => {
  try {
    const response = await axios.get('/api/exam')
    // 确保题目按ID排序
    if (response.data.questions) {
      response.data.questions.sort((a, b) => a.id - b.id)
    }
    currentExam.value = response.data
    currentQuestionIndex.value = 0
    userAnswers.value = {}
  } catch (error) {
    MessagePlugin.error('获取试卷失败')
  }
}

const startExamFromCustom = () => {
  showCustomStartDialog.value = true
}

const confirmCustomStart = async () => {
  try {
    const response = await axios.get('/api/exam/custom', {
      params: {
        start_id: customStartNumber.value,
        count: customQuestionCount.value
      }
    })
    
    if (response.data.questions) {
      response.data.questions.sort((a, b) => a.id - b.id)
    }
    currentExam.value = response.data
    currentQuestionIndex.value = 0
    userAnswers.value = {}
    showCustomStartDialog.value = false
  } catch (error) {
    MessagePlugin.error('获取试卷失败')
  }
}

const nextQuestion = () => {
  if (currentQuestionIndex.value < currentExam.value.questions.length - 1) {
    currentQuestionIndex.value++
  }
}

const prevQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

const submitExam = async () => {
  try {
    // 处理多选题答案格式（数组转字符串）
    const processedAnswers = {}
    Object.keys(userAnswers.value).forEach(qId => {
      const answer = userAnswers.value[qId]
      processedAnswers[qId] = Array.isArray(answer) ? answer.sort().join('') : answer
    })

    const response = await axios.post('/api/exam/submit', {
      exam_id: currentExam.value.exam_id,
      answers: processedAnswers
    })
    
    console.log('考试提交结果:', response.data)
    
    // 确保结果数据包含所有必要的字段
    examResult.value = {
      exam_id: response.data.exam_id || currentExam.value.exam_id,
      total: response.data.total || currentExam.value.questions.length,
      correct_count: response.data.correct_count || 0,
      score: response.data.score || (response.data.correct_count && response.data.total 
        ? Math.round((response.data.correct_count / response.data.total) * 100)
        : 0),
      wrong_questions: response.data.wrong_questions || [],
      results: response.data.results || []
    }
    
    console.log('处理后的考试结果:', examResult.value)
    showResult.value = true
  } catch (error) {
    console.error('提交试卷失败:', error)
    MessagePlugin.error('提交试卷失败')
  }
}

const resetExam = () => {
  currentExam.value = null
  showResult.value = false
  examResult.value = {
    exam_id: '',
    total: 0,
    correct_count: 0,
    score: 0,
    wrong_questions: [],
    results: []
  }
}

const goToWrongPractice = () => {
  showResult.value = false
  emit('switch-tab', 'wrong')
}
</script>

<style scoped>
.exam-header {
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

.wrong-details {
  margin: 20px 0;
  text-align: left;
  max-height: 300px;
  overflow-y: auto;
}

.wrong-item {
  padding: 10px;
  border-left: 3px solid #e34d59;
  background-color: #fff1f1;
  margin: 5px 0;
}

.start-card {
  text-align: center;
  max-width: 400px;
  margin: 100px auto;
}

.exam-tip {
  color: #e34d59;
  font-weight: bold;
  margin-top: 10px;
}
</style>