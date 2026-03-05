<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="handleClose">
        <div class="modal-container">
          <!-- 头部 -->
          <div class="modal-header">
            <h2>🔍 深度研究助手</h2>
            <button class="close-btn" @click="handleClose" :disabled="isProcessing">
              ✕
            </button>
          </div>

          <!-- 输入区域 -->
          <div class="input-section" v-if="!isProcessing && !report">
            <div class="input-wrapper">
              <input
                v-model="topic"
                type="text"
                placeholder="输入研究主题，例如：大语言模型在医疗诊断中的应用"
                @keyup.enter="startResearch"
                :disabled="isProcessing"
              />
            </div>
            <div class="options">
              <div class="option-group">
                <label>研究深度：</label>
                <select v-model="maxSteps">
                  <option :value="3">快速 (3步)</option>
                  <option :value="5">标准 (5步)</option>
                  <option :value="8">深度 (8步)</option>
                </select>
              </div>
              <div class="option-group">
                <label>输出语言：</label>
                <select v-model="language">
                  <option value="zh">中文</option>
                  <option value="en">English</option>
                </select>
              </div>
            </div>
            <button
              class="start-btn"
              @click="startResearch"
              :disabled="!topic.trim() || isProcessing"
            >
              开始研究
            </button>
          </div>

          <!-- 研究进度区域 -->
          <div class="progress-section" v-if="isProcessing">
            <ResearchProgress
              :phase="progress.phase"
              :status="progress.status"
              :steps="progress.steps"
              :current-step="progress.currentStep"
              :total-steps="progress.totalSteps"
              :current-message="progress.message"
              :search-results="progress.searchResults"
              :notes="progress.notes"
              :is-processing="isProcessing"
            />
          </div>

          <!-- 报告展示区域 -->
          <div class="report-section" v-if="report && !isProcessing">
            <div class="report-tabs">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                :class="['tab-btn', { active: activeTab === tab.id }]"
                @click="activeTab = tab.id"
              >
                {{ tab.label }}
              </button>
            </div>

            <div class="report-content">
              <div v-show="activeTab === 'report'" class="tab-panel">
                <MarkdownViewer :content="reportContent" />
              </div>
              <div v-show="activeTab === 'bullets'" class="tab-panel">
                <MarkdownViewer :content="bulletPoints" />
              </div>
              <div v-show="activeTab === 'comparison'" class="tab-panel">
                <MarkdownViewer :content="comparisonTable" />
              </div>
            </div>

            <div class="report-actions">
              <button class="export-btn" @click="exportReport">
                📥 导出报告
              </button>
              <button class="new-research-btn" @click="resetResearch">
                🔄 新研究
              </button>
            </div>
          </div>

          <!-- 错误显示 -->
          <div class="error-section" v-if="error">
            <div class="error-message">
              <span class="error-icon">⚠️</span>
              {{ error }}
            </div>
            <button class="retry-btn" @click="resetResearch">重试</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import ResearchProgress from './ResearchProgress.vue';
import MarkdownViewer from './MarkdownViewer.vue';
import { researchApi, type ResearchEvent } from '../services/researchApi';

const props = defineProps<{
  visible: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

// 状态
const topic = ref('');
const maxSteps = ref(5);
const language = ref<'zh' | 'en'>('zh');
const isProcessing = ref(false);
const error = ref('');

// 进度状态
const progress = ref({
  phase: 'planning' as 'planning' | 'execution' | 'synthesis' | 'complete' | 'error',
  status: '',
  steps: [] as Array<{ step: number; action: string; query: string; purpose: string }>,
  currentStep: 0,
  totalSteps: 0,
  message: '',
  searchResults: [] as Array<{ title: string; url: string; content: string }>,
  notes: [] as string[]
});

// 报告内容
const report = ref<any>(null);
const reportContent = ref('');
const bulletPoints = ref('');
const comparisonTable = ref('');

// 标签页
const activeTab = ref('report');
const tabs = [
  { id: 'report', label: '📄 完整报告' },
  { id: 'bullets', label: '📋 要点清单' },
  { id: 'comparison', label: '📊 对比表格' }
];

// 事件处理
let abortController: AbortController | null = null;

const handleEvent = (event: ResearchEvent) => {
  console.log('Received event:', event);

  switch (event.type) {
    case 'plan':
      progress.value.steps = event.data.steps;
      progress.value.totalSteps = event.data.total_steps;
      progress.value.phase = 'execution';
      progress.value.status = 'started';
      progress.value.message = '研究计划已制定，开始执行...';
      break;

    case 'progress':
      progress.value.phase = event.data.phase || progress.value.phase;
      progress.value.status = event.data.status;
      progress.value.message = event.data.message;
      if (event.data.step !== undefined) {
        progress.value.currentStep = event.data.step - 1; // 0-indexed
      }
      if (event.data.query) {
        progress.value.message = `正在搜索: ${event.data.query}`;
      }
      break;

    case 'search_result':
      progress.value.searchResults = event.data.results;
      progress.value.message = `找到 ${event.data.count} 个相关结果`;
      break;

    case 'note':
      progress.value.notes.push(event.data.id);
      progress.value.message = '笔记已保存';
      break;

    case 'report':
      report.value = event.data;
      reportContent.value = event.data.report;
      bulletPoints.value = event.data.bullet_points;
      comparisonTable.value = event.data.comparison_table;
      progress.value.phase = 'complete';
      progress.value.status = 'completed';
      progress.value.message = '研究报告已生成！';
      break;

    case 'done':
      isProcessing.value = false;
      break;

    case 'error':
      error.value = event.data.message;
      progress.value.phase = 'error';
      progress.value.status = 'error';
      break;
  }
};

const startResearch = async () => {
  if (!topic.value.trim()) return;

  isProcessing.value = true;
  error.value = '';
  report.value = null;

  // 重置进度
  progress.value = {
    phase: 'planning',
    status: 'started',
    steps: [],
    currentStep: 0,
    totalSteps: 0,
    message: '正在制定研究计划...',
    searchResults: [],
    notes: []
  };

  try {
    await researchApi.streamResearch(
      {
        topic: topic.value,
        max_steps: maxSteps.value,
        language: language.value
      },
      handleEvent,
      (err) => {
        error.value = err.message;
        isProcessing.value = false;
      },
      () => {
        isProcessing.value = false;
      }
    );
  } catch (e: any) {
    error.value = e.message;
    isProcessing.value = false;
  }
};

const resetResearch = () => {
  topic.value = '';
  report.value = null;
  reportContent.value = '';
  bulletPoints.value = '';
  comparisonTable.value = '';
  error.value = '';
  isProcessing.value = false;
  progress.value = {
    phase: 'planning',
    status: '',
    steps: [],
    currentStep: 0,
    totalSteps: 0,
    message: '',
    searchResults: [],
    notes: []
  };
  activeTab.value = 'report';
};

const handleClose = () => {
  if (isProcessing.value) {
    if (confirm('研究正在进行中，确定要关闭吗？')) {
      abortController?.abort();
      emit('close');
    }
  } else {
    emit('close');
  }
};

const exportReport = () => {
  if (!reportContent.value) return;

  const blob = new Blob([reportContent.value], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `research-${topic.value.slice(0, 20)}-${Date.now()}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-container {
  width: 95%;
  max-width: 1400px;
  height: 90vh;
  background: white;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
  background: #fafafa;
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #f0f0f0;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover:not(:disabled) {
  background: #e0e0e0;
}

.close-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-section {
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  flex: 1;
  justify-content: center;
}

.input-wrapper {
  width: 100%;
  max-width: 700px;
}

.input-wrapper input {
  width: 100%;
  padding: 16px 20px;
  font-size: 18px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  outline: none;
  transition: border-color 0.2s;
}

.input-wrapper input:focus {
  border-color: #2196f3;
}

.options {
  display: flex;
  gap: 24px;
}

.option-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-group label {
  font-size: 14px;
  color: #666;
}

.option-group select {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.start-btn {
  padding: 14px 48px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #2196f3, #1976d2);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.start-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
}

.start-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.progress-section {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.report-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.report-tabs {
  display: flex;
  gap: 8px;
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
  background: #fafafa;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #f0f0f0;
}

.tab-btn.active {
  background: #2196f3;
  color: white;
}

.report-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.tab-panel {
  max-width: 900px;
  margin: 0 auto;
}

.report-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  border-top: 1px solid #eee;
  background: #fafafa;
}

.export-btn,
.new-research-btn {
  padding: 12px 32px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.export-btn {
  background: #4caf50;
  color: white;
}

.export-btn:hover {
  background: #388e3c;
}

.new-research-btn {
  background: #f0f0f0;
  color: #333;
}

.new-research-btn:hover {
  background: #e0e0e0;
}

.error-section {
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: #ffebee;
  border-radius: 12px;
  color: #c62828;
}

.error-icon {
  font-size: 24px;
}

.retry-btn {
  padding: 12px 32px;
  background: #f57c00;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:hover {
  background: #ef6c00;
}

/* 过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
}
</style>
