// 沙箱服务 - 用于安全执行用户代码
export interface CodeExecutionResult {
  type: 'table' | 'chart';
  config: any;
}

// 简单的代码执行函数（在实际生产环境中应该使用 Web Worker 或更安全的沙箱）
export const executeCode = async (code: string, data: any[]): Promise<CodeExecutionResult> => {
  try {
    // 创建一个安全的执行环境
    const safeEval = new Function('data', `
      // 限制可用的全局对象
      const allowedGlobals = {
        console: {
          log: console.log,
          error: console.error,
          warn: console.warn
        },
        Math: Math,
        Date: Date,
        Array: Array,
        Object: Object,
        String: String,
        Number: Number,
        Boolean: Boolean,
        JSON: JSON,
        parseInt: parseInt,
        parseFloat: parseFloat,
        isNaN: isNaN,
        isFinite: isFinite,
        encodeURIComponent: encodeURIComponent,
        decodeURIComponent: decodeURIComponent
      };
      
      // 设置全局对象
      Object.keys(allowedGlobals).forEach(key => {
        globalThis[key] = allowedGlobals[key];
      });
      
      // 执行用户代码
      ${code}
    `);

    // 执行代码
    const result = safeEval(data);
    
    // 验证返回结果
    if (!result || typeof result !== 'object') {
      throw new Error('代码必须返回一个对象');
    }
    
    if (!result.type || !['table', 'chart'].includes(result.type)) {
      throw new Error('返回对象必须包含有效的 type 字段 (table 或 chart)');
    }
    
    if (!result.config || typeof result.config !== 'object') {
      throw new Error('返回对象必须包含 config 字段');
    }
    
    return result as CodeExecutionResult;
  } catch (error) {
    console.error('代码执行失败:', error);
    throw new Error(`代码执行失败: ${error instanceof Error ? error.message : '未知错误'}`);
  }
};

// 验证代码安全性
export const validateCode = (code: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  // 检查危险的关键字
  const dangerousKeywords = [
    'eval', 'Function', 'setTimeout', 'setInterval', 'fetch', 'XMLHttpRequest',
    'localStorage', 'sessionStorage', 'indexedDB', 'document', 'window',
    'import', 'require', 'process', 'global', '__dirname', '__filename'
  ];
  
  dangerousKeywords.forEach(keyword => {
    if (code.includes(keyword)) {
      errors.push(`不允许使用关键字: ${keyword}`);
    }
  });
  
  // 检查是否有函数定义
  if (!code.includes('function') && !code.includes('=>')) {
    errors.push('代码必须包含函数定义');
  }
  
  // 检查是否有 return 语句
  if (!code.includes('return')) {
    errors.push('代码必须包含 return 语句');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}; 