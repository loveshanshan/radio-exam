<template>
  <t-config-provider :global-config="globalConfig">
    <div class="app-container">
      <t-header class="header">
        <h1>业余无线电考试练习系统</h1>
      </t-header>
      
      <t-tabs v-model="activeTab" class="main-tabs">
        <t-tab-panel value="exam" label="考试题库">
          <ExamComponent @switch-tab="activeTab = $event" />
        </t-tab-panel>
        <t-tab-panel value="wrong" label="错题本">
          <WrongQuestionsComponent @switch-tab="activeTab = $event" />
        </t-tab-panel>
      </t-tabs>
    </div>
  </t-config-provider>
</template>

<script setup>
import { ref } from 'vue'
import ExamComponent from './components/ExamComponent.vue'
import WrongQuestionsComponent from './components/WrongQuestionsComponent.vue'

const activeTab = ref('exam')
const globalConfig = {
  calendar: {},
  table: {},
  pagination: {}
}
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
  text-align: center;
}

.main-tabs {
  margin: 20px;
}

.t-tabs__content {
  background: white;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>