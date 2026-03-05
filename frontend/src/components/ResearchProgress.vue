<template>
  <div class="research-progress">
    <!-- 总体进度 -->
    <div class="progress-header">
      <h3>{{ phaseTitle }}</h3>
      <span class="status-badge" :class="statusClass">{{ statusText }}</span>
    </div>

    <!-- 进度条 -->
    <div class="progress-bar">
      <div
        class="progress-fill"
        :style="{ width: progressPercent + '%' }"
        :class="{ 'animate': isProcessing }"
      ></div>
    </div>

    <!-- 步骤列表 -->
    <div class="steps-list" v-if="steps.length > 0">
      <div
        v-for="(step, index) in steps"
        :key="index"
        class="step-item"
        :class="{
          'completed': index < currentStep,
          'active': index === currentStep,
          'pending': index > currentStep
        }"
      >
        <div class="step-indicator">
          <span v-if="index < currentStep" class="check-icon">✓</span>
          <span v-else-if="index === currentStep && isProcessing" class="loading-icon">⟳</span>
          <span v-else class="step-number">{{ index + 1 }}</span>
        </div>
        <div class="step-content">
          <div class="step-title">{{ step.action }}</div>
          <div class="step-purpose">{{ step.purpose }}</div>
        </div>
      </div>
    </div>

    <!-- 当前消息 -->
    <div class="current-message" v-if="currentMessage">
      <span class="message-icon">💬</span>
      {{ currentMessage }}
    </div>

    <!-- 搜索结果预览 -->
    <div class="search-preview" v-if="lastSearchResults.length > 0">
      <h4>最近搜索结果</h4>
      <div class="result-item" v-for="(result, index) in lastSearchResults.slice(0, 3)" :key="index">
        <a :href="result.url" target="_blank" class="result-title">{{ result.title }}</a>
        <p class="result-snippet">{{ result.content.slice(0, 100) }}...</p>
      </div>
    </div>

    <!-- 笔记预览 -->
    <div class="notes-preview" v-if="notes.length > 0">
      <h4>已记录笔记 ({{ notes.length }})</h4>
      <div class="note-count">
        <span class="note-icon">📝</span>
        {{ notes.length }} 条笔记已保存
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

interface Step {
  step: number;
  action: string;
  query: string;
  purpose: string;
}

interface SearchResult {
  title: string;
  url: string;
  content: string;
}

const props = defineProps<{
  phase: 'planning' | 'execution' | 'synthesis' | 'complete' | 'error';
  status: string;
  steps: Step[];
  currentStep: number;
  totalSteps: number;
  currentMessage?: string;
  searchResults?: SearchResult[];
  notes?: string[];
  isProcessing?: boolean;
}>();

const lastSearchResults = computed(() => props.searchResults || []);
const notes = computed(() => props.notes || []);

const phaseTitle = computed(() => {
  const titles = {
    planning: '📋 规划阶段',
    execution: '🔍 执行阶段',
    synthesis: '📊 综合阶段',
    complete: '✅ 完成',
    error: '❌ 出错'
  };
  return titles[props.phase] || '研究中';
});

const statusText = computed(() => {
  const statuses: Record<string, string> = {
    started: '进行中',
    completed: '已完成',
    error: '错误',
    searching: '搜索中',
    report_generated: '报告生成中'
  };
  return statuses[props.status] || props.status;
});

const statusClass = computed(() => {
  return {
    'status-active': props.isProcessing,
    'status-complete': props.phase === 'complete',
    'status-error': props.phase === 'error'
  };
});

const progressPercent = computed(() => {
  if (props.totalSteps === 0) return 0;
  return Math.round((props.currentStep / props.totalSteps) * 100);
});
</script>

<style scoped>
.research-progress {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: #e3f2fd;
  color: #1976d2;
}

.status-badge.status-active {
  background: #fff3e0;
  color: #f57c00;
  animation: pulse 2s infinite;
}

.status-badge.status-complete {
  background: #e8f5e9;
  color: #388e3c;
}

.status-badge.status-error {
  background: #ffebee;
  color: #d32f2f;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 20px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #8bc34a);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill.animate {
  background: linear-gradient(90deg, #2196f3, #03a9f4);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { opacity: 0.8; }
  50% { opacity: 1; }
  100% { opacity: 0.8; }
}

.steps-list {
  margin-bottom: 16px;
}

.step-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid transparent;
  transition: all 0.2s;
}

.step-item.completed {
  border-left-color: #4caf50;
  opacity: 0.8;
}

.step-item.active {
  border-left-color: #2196f3;
  background: #e3f2fd;
}

.step-item.pending {
  opacity: 0.5;
}

.step-indicator {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #e0e0e0;
  font-size: 12px;
  flex-shrink: 0;
}

.step-item.completed .step-indicator {
  background: #4caf50;
  color: white;
}

.step-item.active .step-indicator {
  background: #2196f3;
  color: white;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.step-content {
  flex: 1;
}

.step-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.step-purpose {
  font-size: 12px;
  color: #666;
}

.current-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
}

.message-icon {
  font-size: 16px;
}

.search-preview,
.notes-preview {
  margin-top: 16px;
  padding: 12px;
  background: white;
  border-radius: 8px;
}

.search-preview h4,
.notes-preview h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #333;
}

.result-item {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.result-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.result-title {
  color: #1976d2;
  text-decoration: none;
  font-weight: 500;
  display: block;
  margin-bottom: 4px;
}

.result-title:hover {
  text-decoration: underline;
}

.result-snippet {
  margin: 0;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

.note-count {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.note-icon {
  font-size: 16px;
}
</style>
