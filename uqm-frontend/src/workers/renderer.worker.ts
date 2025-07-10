/**
 * Web Worker for securely executing rendering functions.
 */
self.onmessage = (e: MessageEvent) => {
  const { code, data, timeout = 5000 } = e.data;
  
  let timeoutId: number;

  try {
    // 设置执行超时
    timeoutId = self.setTimeout(() => {
      throw new Error(`Execution timed out after ${timeout}ms`);
    }, timeout);
    
    // 创建一个受限制的、安全的执行作用域
    // 只暴露必要的、安全的全局变量
    const safeGlobals = {
      Math,
      Date,
      JSON,
      // 提供一个安全的 console 版本
      console: {
        log: (...args: any[]) => console.log('[Sandbox Worker]', ...args),
        error: (...args: any[]) => console.error('[Sandbox Worker]', ...args),
        warn: (...args: any[]) => console.warn('[Sandbox Worker]', ...args),
      },
      // 你可以在这里添加更多安全的工具函数
    };
    
    // 使用 new Function 来创建函数。
    // 'code' 变量包含AI生成的函数体字符串。
    // 'data' 和 'globals' 是传递给该函数的参数。
    const rendererFunction = new Function('data', 'globals', `
      // 严格模式可以防止一些不安全的操作
      'use strict';
      
      // 解构安全的全局变量
      const { Math, Date, JSON, console } = globals;
      
      // 'code' 应该是一个完整的、可返回的函数表达式字符串
      const func = ${code};
      return func(data);
    `);
    
    const startTime = performance.now();
    const config = rendererFunction(data, safeGlobals);
    const executionTime = performance.now() - startTime;
    
    self.clearTimeout(timeoutId);
    
    // 对返回结果进行基础的结构验证
    if (!config || typeof config !== 'object') {
      throw new Error('Renderer function must return a configuration object.');
    }
    if (!['table', 'chart'].includes(config.type)) {
      throw new Error('Configuration object must have a "type" property of "table" or "chart".');
    }
    
    self.postMessage({
      success: true,
      config,
      executionTime,
    });
    
  } catch (error: any) {
    if (timeoutId!) self.clearTimeout(timeoutId);
    
    self.postMessage({
      success: false,
      error: error.message || 'An unknown error occurred in the sandbox.',
    });
  }
}; 