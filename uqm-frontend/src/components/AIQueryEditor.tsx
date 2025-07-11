import React, { useState } from 'react';
import { uqmApi } from '../api/uqmApi';
import { setCurrentQueryResult } from '../services/dataService';
import type { AIGenerateRequest, AIGenerateResponse, UQMExecuteResponse } from '../api/uqmApi';

interface AIQueryEditorProps {
  onQueryGenerated?: (schema: AIGenerateResponse) => void;
  onQueryExecuted?: (results: any[], query: string, uqmConfig: any) => void;
}

export const AIQueryEditor: React.FC<AIQueryEditorProps> = ({
  onQueryGenerated,
  onQueryExecuted
}) => {
  const [naturalLanguageQuery, setNaturalLanguageQuery] = useState('');
  const [generatedSchema, setGeneratedSchema] = useState<AIGenerateResponse | null>(null);
  const [executionResult, setExecutionResult] = useState<UQMExecuteResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateSchema = async () => {
    if (!naturalLanguageQuery.trim()) {
      setError('请输入自然语言查询');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const request: AIGenerateRequest = {
        query: naturalLanguageQuery.trim(),
        options: {
          include_parameters: true,
          include_options: true
        }
      };

      const schema = await uqmApi.generateSchema(request);
      setGeneratedSchema(schema);
      onQueryGenerated?.(schema);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail?.message || err.message || '生成查询失败');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExecuteQuery = async () => {
    if (!generatedSchema) {
      setError('请先生成查询Schema');
      return;
    }

    setIsExecuting(true);
    setError(null);

    try {
      const result = await uqmApi.executeQuery({
        uqm: generatedSchema.uqm,
        parameters: generatedSchema.parameters,
        options: generatedSchema.options
      });

      setExecutionResult(result);
      // 保存查询结果到数据服务
      setCurrentQueryResult(result.data || [], naturalLanguageQuery);
      const uqmConfig = {
        uqm: generatedSchema.uqm,
        parameters: generatedSchema.parameters,
        options: generatedSchema.options
      };
      onQueryExecuted?.(result.data || [], naturalLanguageQuery, uqmConfig);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail?.message || err.message || '执行查询失败');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleGenerateAndExecute = async () => {
    if (!naturalLanguageQuery.trim()) {
      setError('请输入自然语言查询');
      return;
    }

    setIsGenerating(true);
    setIsExecuting(true);
    setError(null);

    try {
      const request: AIGenerateRequest = {
        query: naturalLanguageQuery.trim(),
        options: {
          include_parameters: true,
          include_options: true
        }
      };

      const result = await uqmApi.generateAndExecute(request);
      setExecutionResult(result);

      // 从返回结果中提取 uqm config
      // 注意: generateAndExecute 并不直接返回用于下一次执行的完整 schema，我们得自己构建
      const uqmConfig = {
        uqm: result.config?.uqm, // 假设引擎在执行后会附带UQM定义
        parameters: request.options, // 这可能不准确，需要后端配合
        options: {}
      };

      // 保存查询结果到数据服务
      setCurrentQueryResult(result.data || [], naturalLanguageQuery);
      onQueryExecuted?.(result.data || [], naturalLanguageQuery, uqmConfig);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail?.message || err.message || '生成并执行查询失败');
    } finally {
      setIsGenerating(false);
      setIsExecuting(false);
    }
  };

  const handleSaveSchema = () => {
    if (!generatedSchema) {
      setError('没有可保存的Schema');
      return;
    }

    try {
      const schemaData = {
        ...generatedSchema,
        naturalLanguageQuery,
        savedAt: new Date().toISOString()
      };

      const savedSchemas = JSON.parse(localStorage.getItem('uqm_saved_schemas') || '[]');
      savedSchemas.push(schemaData);
      localStorage.setItem('uqm_saved_schemas', JSON.stringify(savedSchemas));
      
      alert('Schema已保存到本地存储');
    } catch (err) {
      setError('保存Schema失败');
    }
  };

  return (
    <div className="ai-query-editor p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">AI 自然语言查询</h2>
      
      {/* 自然语言输入 */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          自然语言查询
        </label>
        <textarea
          value={naturalLanguageQuery}
          onChange={(e) => setNaturalLanguageQuery(e.target.value)}
          placeholder="例如：查询所有用户的订单总金额，按用户分组"
          className="w-full h-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={isGenerating || isExecuting}
        />
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* 操作按钮 */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={handleGenerateSchema}
          disabled={isGenerating || isExecuting}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? '生成中...' : '生成查询'}
        </button>
        
        <button
          onClick={handleExecuteQuery}
          disabled={!generatedSchema || isExecuting}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isExecuting ? '执行中...' : '执行查询'}
        </button>
        
        <button
          onClick={handleGenerateAndExecute}
          disabled={isGenerating || isExecuting}
          className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {(isGenerating || isExecuting) ? '处理中...' : '生成并执行'}
        </button>
        
        <button
          onClick={handleSaveSchema}
          disabled={!generatedSchema}
          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          保存Schema
        </button>
      </div>

      {/* 生成的Schema */}
      {generatedSchema && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">生成的查询Schema</h3>
          <div className="bg-gray-50 p-4 rounded-md">
            <div className="mb-2">
              <strong>名称:</strong> {generatedSchema.uqm.metadata.name}
            </div>
            <div className="mb-2">
              <strong>描述:</strong> {generatedSchema.uqm.metadata.description}
            </div>
            <div className="mb-2">
              <strong>步骤数:</strong> {generatedSchema.uqm.steps.length}
            </div>
            <details className="mt-3">
              <summary className="cursor-pointer text-blue-600 hover:text-blue-800">
                查看完整Schema
              </summary>
              <pre className="mt-2 p-3 bg-gray-100 rounded text-sm overflow-auto">
                {JSON.stringify(generatedSchema, null, 2)}
              </pre>
            </details>
          </div>
        </div>
      )}

      {/* 执行结果 */}
      {executionResult && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">查询结果</h3>
          <div className="bg-gray-50 p-4 rounded-md">
            {executionResult.success ? (
              <div>
                <div className="mb-2">
                  <strong>状态:</strong> 
                  <span className="text-green-600 ml-1">成功</span>
                </div>
                <div className="mb-2">
                  <strong>数据行数:</strong> {executionResult.data?.length || 0}
                </div>
                {executionResult.execution_time && (
                  <div className="mb-2">
                    <strong>执行时间:</strong> {executionResult.execution_time.toFixed(2)}秒
                  </div>
                )}
                {executionResult.data && executionResult.data.length > 0 && (
                  <details className="mt-3">
                    <summary className="cursor-pointer text-blue-600 hover:text-blue-800">
                      查看数据 (前10行)
                    </summary>
                    <div className="mt-2 overflow-auto">
                      <table className="min-w-full border border-gray-300">
                        <thead>
                          <tr>
                            {Object.keys(executionResult.data[0]).map(key => (
                              <th key={key} className="border border-gray-300 px-2 py-1 bg-gray-200 text-left">
                                {key}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {executionResult.data.slice(0, 10).map((row: any, index: number) => (
                            <tr key={index}>
                              {Object.values(row).map((value, cellIndex) => (
                                <td key={cellIndex} className="border border-gray-300 px-2 py-1">
                                  {String(value)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </details>
                )}
              </div>
            ) : (
              <div className="text-red-600">
                <strong>执行失败:</strong> {executionResult.error}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}; 