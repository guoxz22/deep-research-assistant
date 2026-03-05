<template>
  <div class="app">
    <header class="app-header">
      <h1>🔍 深度研究助手</h1>
      <p class="subtitle">基于 LangChain/LangGraph 的学术文献研究智能体</p>
    </header>

    <main class="app-main">
      <div class="hero-section">
        <h2>智能化学术研究</h2>
        <p>
          输入研究主题，AI 将自动规划研究步骤、搜索学术文献、
          记录关键发现，并生成结构化双语研究报告。
        </p>

        <div class="features">
          <div class="feature">
            <span class="feature-icon">📋</span>
            <h3>自动规划</h3>
            <p>智能分解研究问题为具体步骤</p>
          </div>
          <div class="feature">
            <span class="feature-icon">🔍</span>
            <h3>深度搜索</h3>
            <p>Tavily 驱动的学术文献搜索</p>
          </div>
          <div class="feature">
            <span class="feature-icon">📝</span>
            <h3>笔记记录</h3>
            <p>自动提取并保存关键发现</p>
          </div>
          <div class="feature">
            <span class="feature-icon">📊</span>
            <h3>报告生成</h3>
            <p>结构化双语研究报告</p>
          </div>
        </div>

        <button class="start-research-btn" @click="showModal = true">
          开始深度研究
        </button>
      </div>

      <div class="tech-stack">
        <h3>技术栈</h3>
        <div class="tech-items">
          <span class="tech-item">FastAPI</span>
          <span class="tech-item">LangChain</span>
          <span class="tech-item">LangGraph</span>
          <span class="tech-item">Tavily</span>
          <span class="tech-item">Vue 3</span>
          <span class="tech-item">TypeScript</span>
        </div>
      </div>
    </main>

    <footer class="app-footer">
      <p>© 2024 深度研究助手 | ReAct + Plan-and-Solve 混合范式</p>
    </footer>

    <ResearchModal :visible="showModal" @close="showModal = false" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ResearchModal from './components/ResearchModal.vue';

const showModal = ref(false);
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}
</style>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  text-align: center;
  padding: 40px 20px;
  color: white;
}

.app-header h1 {
  font-size: 48px;
  margin-bottom: 12px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.subtitle {
  font-size: 18px;
  opacity: 0.9;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.hero-section {
  background: white;
  border-radius: 24px;
  padding: 60px 40px;
  max-width: 900px;
  width: 100%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.hero-section h2 {
  font-size: 32px;
  color: #333;
  margin-bottom: 16px;
}

.hero-section > p {
  font-size: 16px;
  color: #666;
  margin-bottom: 40px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.feature {
  padding: 24px;
  background: #f8f9fa;
  border-radius: 16px;
  transition: transform 0.2s;
}

.feature:hover {
  transform: translateY(-4px);
}

.feature-icon {
  font-size: 40px;
  display: block;
  margin-bottom: 12px;
}

.feature h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
}

.feature p {
  font-size: 13px;
  color: #666;
}

.start-research-btn {
  padding: 18px 64px;
  font-size: 18px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
}

.start-research-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.5);
}

.tech-stack {
  margin-top: 40px;
  text-align: center;
  color: white;
}

.tech-stack h3 {
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 2px;
  opacity: 0.8;
  margin-bottom: 16px;
}

.tech-items {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.tech-item {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 13px;
  backdrop-filter: blur(4px);
}

.app-footer {
  text-align: center;
  padding: 24px;
  color: white;
  opacity: 0.8;
  font-size: 14px;
}

@media (max-width: 768px) {
  .app-header h1 {
    font-size: 32px;
  }

  .hero-section {
    padding: 40px 24px;
  }

  .hero-section h2 {
    font-size: 24px;
  }

  .features {
    grid-template-columns: repeat(2, 1fr);
  }

  .start-research-btn {
    padding: 14px 40px;
    font-size: 16px;
  }
}
</style>
