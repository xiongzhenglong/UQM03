import type { AIGenerateRequest, AIGenerateResponse } from '../types/renderer';
import { tableTemplate, barChartTemplate, pieChartTemplate, lineChartTemplate } from '../utils/templates';

/**
 * AI 服务 API (MVP 阶段使用模板匹配)
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
        } else if (intent.chartType === 'pie') {
          rendererCode = pieChartTemplate(dataStructure.fields, intent.fields);
        } else if (intent.chartType === 'line') {
          rendererCode = lineChartTemplate(dataStructure.fields, intent.fields);
        } else {
          // 默认使用柱状图
          rendererCode = barChartTemplate(dataStructure.fields, intent.fields);
        }
      } else {
        throw new Error('无法识别您的可视化意图，请尝试"表格"、"柱状图"、"饼图"或"折线图"。');
      }
      
      return {
        success: true,
        rendererCode,
        explanation: `根据您的需求"${userPrompt}"，我生成了相应的${intent.visualizationType}渲染代码。`,
      };
    } catch (error: any) {
      return {
        success: false,
        error: `AI 生成失败: ${error.message}`
      };
    }
  }
};

/**
 * 意图分析函数
 */
function analyzeUserIntent(prompt: string): {
  visualizationType: 'table' | 'chart' | 'unknown';
  chartType?: 'bar' | 'line' | 'pie' | 'scatter';
  fields?: string[];
} {
  const lowerPrompt = prompt.toLowerCase();
  
  // 图表关键词检测
  const chartKeywords = {
    bar: ['柱状图', '条形图', 'bar', 'column', '薪资分布', '工资分布'],
    line: ['折线图', '线图', 'line', 'trend', '趋势', '变化'],
    pie: ['饼图', '圆饼图', 'pie', '分布', '占比'],
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

  // 表格关键词
  const tableKeywords = ['表格', 'table', '列表', 'list', '员工信息', '详细信息'];
  if (tableKeywords.some(kw => lowerPrompt.includes(kw))) {
    return { visualizationType: 'table' };
  }
  
  // 如果没有明确指定，根据数据特征智能选择
  return { visualizationType: 'unknown' };
}

/**
 * 数据结构分析函数
 */
function analyzeDataStructure(data: any[]): { fields: string[] } {
  if (data.length === 0) {
    return { fields: [] };
  }
  return {
    fields: Object.keys(data[0])
  };
} 