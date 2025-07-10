import type { AIGenerateRequest, AIGenerateResponse } from '../types/renderer';
import { tableTemplate, barChartTemplate } from '../utils/templates';

/**
 * 伪 AI 服务 API
 * MVP 阶段使用模板匹配来模拟 AI 生成渲染函数的行为
 */
export const aiApi = {
  async generateRenderer(request: AIGenerateRequest): Promise<AIGenerateResponse> {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 500));

    const { data, userPrompt } = request;
    
    try {
      if (!data || data.length === 0) {
        throw new Error('无法在没有数据的情况下生成可视化。');
      }

      const intent = analyzeUserIntent(userPrompt);
      const dataStructure = analyzeDataStructure(data);
      
      let rendererCode = '';
      if (intent.visualizationType === 'table') {
        rendererCode = tableTemplate(dataStructure.fields, intent.fields);
      } else if (intent.visualizationType === 'chart') {
        if (intent.chartType === 'bar') {
          rendererCode = barChartTemplate(dataStructure.fields, intent.fields);
        } else {
          // 为其他图表类型返回一个默认或错误提示
          throw new Error(`暂不支持生成 ${intent.chartType} 图表。`);
        }
      } else {
        throw new Error('无法识别您的可视化意图，请尝试“表格”或“柱状图”。');
      }
      
      return {
        success: true,
        rendererCode,
        explanation: `根据您的需求“${userPrompt}”，我生成了相应的 ${intent.visualizationType} 渲染代码。`,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `AI 生成失败: ${error.message}`,
      };
    }
  }
};

/**
 * 简单分析用户意图
 */
function analyzeUserIntent(prompt: string): {
  visualizationType: 'table' | 'chart' | 'unknown';
  chartType?: 'bar' | 'line' | 'pie' | 'scatter';
  fields?: string[];
} {
  const lowerPrompt = prompt.toLowerCase();
  
  const chartKeywords = {
    bar: ['柱状图', '条形图', 'bar', 'column'],
    line: ['折线图', '线图', 'line', 'trend'],
    pie: ['饼图', '圆饼图', 'pie'],
    scatter: ['散点图', 'scatter']
  };

  for (const [type, keywords] of Object.entries(chartKeywords)) {
    if (keywords.some(kw => lowerPrompt.includes(kw))) {
      return {
        visualizationType: 'chart',
        chartType: type as 'bar' | 'line' | 'pie' | 'scatter'
      };
    }
  }

  if (['表格', 'table', '列表', 'list'].some(kw => lowerPrompt.includes(kw))) {
    return { visualizationType: 'table' };
  }
  
  return { visualizationType: 'unknown' };
}

/**
 * 简单分析数据结构，提取字段名
 */
function analyzeDataStructure(data: any[]): { fields: string[] } {
  if (data.length === 0) {
    return { fields: [] };
  }
  return {
    fields: Object.keys(data[0])
  };
} 