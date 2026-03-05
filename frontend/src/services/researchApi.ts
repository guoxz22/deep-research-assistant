/**
 * 研究API服务 - SSE流式通信
 */

export interface ResearchRequest {
  topic: string;
  max_steps?: number;
  language?: 'zh' | 'en';
}

export interface PlanEvent {
  steps: Array<{
    step: number;
    action: string;
    query: string;
    purpose: string;
  }>;
  total_steps: number;
}

export interface ProgressEvent {
  phase: string;
  status: string;
  step?: number;
  total_steps?: number;
  message: string;
  query?: string;
}

export interface SearchResult {
  title: string;
  url: string;
  content: string;
  score: number;
}

export interface SearchEvent {
  query: string;
  results: SearchResult[];
  count: number;
}

export interface NoteEvent {
  id: string;
  content: string;
  tags: string[];
}

export interface ReportEvent {
  topic: string;
  report: string;
  bullet_points: string;
  comparison_table: string;
  metadata: {
    total_steps: number;
    search_count: number;
    findings_count: number;
  };
}

export interface ErrorEvent {
  phase?: string;
  step?: number;
  message: string;
}

export type ResearchEventType =
  | 'plan'
  | 'progress'
  | 'search_result'
  | 'note'
  | 'report'
  | 'done'
  | 'error'
  | 'state_update';

export interface ResearchEvent {
  type: ResearchEventType;
  data: PlanEvent | ProgressEvent | SearchEvent | NoteEvent | ReportEvent | ErrorEvent | any;
}

export type ResearchEventHandler = (event: ResearchEvent) => void;

/**
 * 研究API客户端
 */
export class ResearchApi {
  private baseUrl: string;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  /**
   * 启动研究流程并订阅SSE事件
   */
  async streamResearch(
    request: ResearchRequest,
    onEvent: ResearchEventHandler,
    onError?: (error: Error) => void,
    onComplete?: () => void
  ): Promise<EventSource> {
    const params = new URLSearchParams({
      topic: request.topic,
      max_steps: String(request.max_steps || 5),
      language: request.language || 'zh'
    });

    // 使用POST请求需要手动处理SSE，改用EventSource
    // 这里我们创建一个自定义的流式处理
    const response = await fetch(`${this.baseUrl}/research/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    const processBuffer = () => {
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      let currentEvent = '';
      let currentData = '';

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.substring(7);
        } else if (line.startsWith('data: ')) {
          currentData = line.substring(6);
        } else if (line === '' && currentEvent && currentData) {
          try {
            const data = JSON.parse(currentData);
            onEvent({ type: currentEvent as ResearchEventType, data });
          } catch (e) {
            console.error('Failed to parse SSE data:', currentData, e);
          }
          currentEvent = '';
          currentData = '';
        }
      }
    };

    const readChunk = async (): Promise<void> => {
      if (!reader) return;

      try {
        const { done, value } = await reader.read();

        if (done) {
          // 处理剩余buffer
          if (buffer) {
            buffer += '\n';
            processBuffer();
          }
          onComplete?.();
          return;
        }

        buffer += decoder.decode(value, { stream: true });
        processBuffer();
        await readChunk();
      } catch (error) {
        onError?.(error as Error);
      }
    };

    readChunk();

    // 返回一个可中止的控制器
    return {
      close: () => reader?.cancel(),
      readyState: 0,
      url: '',
      withCredentials: false,
      onerror: null,
      onmessage: null,
      onopen: null,
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    } as unknown as EventSource;
  }

  /**
   * 同步研究接口
   */
  async syncResearch(request: ResearchRequest): Promise<any> {
    const response = await fetch(`${this.baseUrl}/research/sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

// 导出默认实例
export const researchApi = new ResearchApi();
