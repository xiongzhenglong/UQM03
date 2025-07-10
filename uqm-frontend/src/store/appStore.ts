import { create } from 'zustand';
import type { SavedVisualization, VisualizationConfig } from '../types/visualization';
import { uqmApi } from '../api/uqmApi';
import { aiApi } from '../api/aiApi';
import { SandboxService } from '../services/sandbox';
import { storageService } from '../services/storage';

const sandboxService = new SandboxService();

interface AppState {
  // === 核心数据状态 ===
  currentUqmQuery: object | null;          // 当前 UQM 查询
  currentData: any[] | null;               // 当前查询结果数据
  currentRendererCode: string | null;      // 当前渲染函数代码
  currentVisualization: VisualizationConfig | null; // 当前可视化配置
  
  // === UI 状态 ===
  isExecutingQuery: boolean;               // 正在执行查询
  isGeneratingRenderer: boolean;           // 正在生成渲染函数
  isExecutingRenderer: boolean;            // 正在执行渲染函数
  activeTab: 'visualization' | 'code';     // 当前激活的标签页
  
  // === 保存的方案 ===
  savedVisualizations: SavedVisualization[];
  currentSavedId: string | null;           // 当前加载的保存方案 ID
  
  // === 错误状态 ===
  queryError: string | null;
  rendererError: string | null;
  aiError: string | null;
  
  // === 操作方法 ===
  // 查询相关
  setUqmQuery: (query: object) => void;
  executeQuery: () => Promise<void>;
  clearQueryError: () => void;
  
  // AI 生成相关
  generateRenderer: (prompt: string) => Promise<void>;
  clearAiError: () => void;
  
  // 渲染函数相关
  updateRendererCode: (code: string) => void;
  executeRenderer: () => Promise<void>;
  clearRendererError: () => void;
  
  // UI 控制
  setActiveTab: (tab: 'visualization' | 'code') => void;
  
  // 保存与加载
  saveVisualization: (name: string, description?: string) => Promise<void>;
  loadVisualization: (id: string) => Promise<void>;
  deleteVisualization: (id: string) => void;
  loadSavedVisualizations: () => void;
  
  // 重置状态
  resetAll: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
    // === 初始状态 ===
    currentUqmQuery: null,
    currentData: null,
    currentRendererCode: null,
    currentVisualization: null,
    isExecutingQuery: false,
    isGeneratingRenderer: false,
    isExecutingRenderer: false,
    activeTab: 'visualization',
    savedVisualizations: [],
    currentSavedId: null,
    queryError: null,
    rendererError: null,
    aiError: null,
  
    // === 操作实现 ===
    setUqmQuery: (query) => set({ currentUqmQuery: query }),
    executeQuery: async () => {
        const { currentUqmQuery } = get();
        if (!currentUqmQuery) {
            set({ queryError: '查询对象为空，无法执行。' });
            return;
        }

        set({ isExecutingQuery: true, queryError: null, currentData: null });
        try {
            const response = await uqmApi.executeQuery(currentUqmQuery as any);
            if (response.success) {
                set({ currentData: response.data, isExecutingQuery: false });
            } else {
                set({ queryError: response.error || '执行查询时发生未知错误。', isExecutingQuery: false });
            }
        } catch (error: any) {
            set({ queryError: error.message || '请求后端服务失败。', isExecutingQuery: false });
        }
    },
    clearQueryError: () => set({ queryError: null }),

    generateRenderer: async (prompt) => {
        const { currentData } = get();
        if (!currentData || currentData.length === 0) {
            set({ aiError: '没有可用于生成可视化的数据。' });
            // Re-throw to be caught by the component's try-catch block
            throw new Error('没有可用于生成可视化的数据。');
        }

        set({ isGeneratingRenderer: true, aiError: null });
        try {
            const response = await aiApi.generateRenderer({ data: currentData, userPrompt: prompt });
            if (response.success && response.rendererCode) {
                set({ currentRendererCode: response.rendererCode, isGeneratingRenderer: false });
            } else {
                const error = response.error || 'AI 服务未能生成代码。';
                set({ aiError: error, isGeneratingRenderer: false });
                throw new Error(error);
            }
        } catch (error: any) {
            set({ aiError: error.message || '请求 AI 服务失败。', isGeneratingRenderer: false });
            throw error; // Re-throw for component
        }
    },
    clearAiError: () => set({ aiError: null }),

    updateRendererCode: (code) => set({ currentRendererCode: code }),
    executeRenderer: async () => {
        const { currentData, currentRendererCode } = get();
        if (!currentData || !currentRendererCode) {
            // No data or code to render
            return;
        }

        set({ isExecutingRenderer: true, rendererError: null });
        try {
            const result = await sandboxService.executeRenderer(currentRendererCode, currentData);
            if (result.success && result.config) {
                set({ currentVisualization: result.config, isExecutingRenderer: false });
            } else {
                set({ rendererError: result.error || '沙箱执行失败。', isExecutingRenderer: false });
            }
        } catch (error: any) {
            set({ rendererError: error.message || '沙箱执行时发生未知错误。', isExecutingRenderer: false });
        }
    },
    clearRendererError: () => set({ rendererError: null }),

    setActiveTab: (tab) => set({ activeTab: tab }),

    saveVisualization: async (name, description) => {
        const { currentUqmQuery, currentRendererCode } = get();
        if (!currentUqmQuery || !currentRendererCode) return;

        const newVis: SavedVisualization = {
            id: Date.now().toString(),
            name,
            description,
            uqmQuery: currentUqmQuery,
            rendererFunction: currentRendererCode,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
        };
        const updatedList = storageService.saveVisualization(newVis);
        set({ savedVisualizations: updatedList });
    },
    loadVisualization: async (id) => {
        const vis = storageService.getVisualizationById(id);
        if (vis) {
            set({
                currentUqmQuery: vis.uqmQuery,
                currentRendererCode: vis.rendererFunction,
                currentSavedId: id,
                queryError: null,
                rendererError: null,
                aiError: null,
                currentVisualization: null,
                currentData: null,
            });
            // 自动执行一次查询
            get().executeQuery();
        }
    },
    deleteVisualization: (id) => {
        const updatedList = storageService.deleteVisualization(id);
        set({ savedVisualizations: updatedList });
    },
    loadSavedVisualizations: () => {
        const all = storageService.getVisualizations();
        set({ savedVisualizations: all });
    },

    resetAll: () => set({
        currentUqmQuery: null,
        currentData: null,
        currentRendererCode: null,
        currentVisualization: null,
        queryError: null,
        rendererError: null,
        aiError: null,
        currentSavedId: null,
        activeTab: 'visualization',
    }),
})); 