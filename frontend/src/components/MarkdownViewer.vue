<template>
  <div class="markdown-viewer" v-html="renderedContent"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css';

// 配置 marked
marked.setOptions({
  highlight: function(code: string, lang: string) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch (e) {
        console.error('Highlight error:', e);
      }
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true,
  gfm: true,
});

const props = defineProps<{
  content: string;
}>();

const renderedContent = computed(() => {
  if (!props.content) return '';

  try {
    const rawHtml = marked.parse(props.content) as string;
    // 使用 DOMPurify 清理 HTML 防止 XSS
    return DOMPurify.sanitize(rawHtml);
  } catch (e) {
    console.error('Markdown parse error:', e);
    return `<pre>${props.content}</pre>`;
  }
});
</script>

<style scoped>
.markdown-viewer {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.6;
  color: #333;
}

.markdown-viewer :deep(h1) {
  font-size: 2em;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3em;
  margin-bottom: 16px;
}

.markdown-viewer :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3em;
  margin-top: 24px;
  margin-bottom: 16px;
}

.markdown-viewer :deep(h3) {
  font-size: 1.25em;
  margin-top: 24px;
  margin-bottom: 16px;
}

.markdown-viewer :deep(p) {
  margin-bottom: 16px;
}

.markdown-viewer :deep(ul),
.markdown-viewer :deep(ol) {
  padding-left: 2em;
  margin-bottom: 16px;
}

.markdown-viewer :deep(li) {
  margin-bottom: 4px;
}

.markdown-viewer :deep(code) {
  background-color: rgba(175, 184, 193, 0.2);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 85%;
}

.markdown-viewer :deep(pre) {
  background-color: #0d1117;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
  margin-bottom: 16px;
}

.markdown-viewer :deep(pre code) {
  background-color: transparent;
  padding: 0;
  font-size: 85%;
}

.markdown-viewer :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 16px;
}

.markdown-viewer :deep(th),
.markdown-viewer :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.markdown-viewer :deep(th) {
  background-color: #f5f5f5;
  font-weight: 600;
}

.markdown-viewer :deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 16px;
  color: #666;
  margin-bottom: 16px;
}

.markdown-viewer :deep(a) {
  color: #0366d6;
  text-decoration: none;
}

.markdown-viewer :deep(a:hover) {
  text-decoration: underline;
}

.markdown-viewer :deep(hr) {
  border: none;
  border-top: 1px solid #eee;
  margin: 24px 0;
}
</style>
