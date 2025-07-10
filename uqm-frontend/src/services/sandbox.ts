import type { SandboxResult } from '../types/renderer';

export class SandboxService {
  private worker: Worker | null = null;
  
  constructor() {
    this.initWorker();
  }
  
  private initWorker() {
    try {
      // 'new URL' 确保 Vite 能正确地打包和处理 worker 文件
      this.worker = new Worker(
        new URL('../workers/renderer.worker.ts', import.meta.url),
        { type: 'module' }
      );
    } catch (error) {
      console.error('Failed to initialize worker:', error);
    }
  }
  
  async executeRenderer(
    code: string, 
    data: any[], 
    timeout = 5000
  ): Promise<SandboxResult> {
    return new Promise((resolve) => {
      if (!this.worker) {
        resolve({
          success: false,
          error: 'Web Worker is not initialized or failed to load.'
        });
        return;
      }
      
      const handleMessage = (e: MessageEvent) => {
        this.worker!.removeEventListener('message', handleMessage);
        this.worker!.removeEventListener('error', handleError);
        resolve(e.data as SandboxResult);
      };

      const handleError = (e: ErrorEvent) => {
        this.worker!.removeEventListener('message', handleMessage);
        this.worker!.removeEventListener('error', handleError);
        resolve({
          success: false,
          error: `Worker error: ${e.message}`
        });
      };

      this.worker.addEventListener('message', handleMessage);
      this.worker.addEventListener('error', handleError);
      
      // 发送执行请求
      this.worker.postMessage({
        code,
        data,
        timeout
      });
      
      // 设置外层超时保护
      setTimeout(() => {
        this.worker!.removeEventListener('message', handleMessage);
        resolve({
          success: false,
          error: `Execution timed out after ${timeout}ms`
        });
      }, timeout + 500); // 给予一定的宽限期
    });
  }
  
  destroy() {
    if (this.worker) {
      this.worker.terminate();
      this.worker = null;
    }
  }
} 