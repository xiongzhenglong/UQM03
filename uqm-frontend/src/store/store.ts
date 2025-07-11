import { create } from 'zustand';

interface StoreState {
  // 查询相关
  queryData: any;
  queryResult: any[];
  loading: boolean;
  error: string | null;
  
  // 可视化相关
  currentVisualization: any;
  currentCode: string;
  
  // Actions
  setQueryData: (data: any) => void;
  setQueryResult: (result: any[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setCurrentVisualization: (visualization: any) => void;
  setCurrentCode: (code: string) => void;
}

export const useStore = create<StoreState>((set) => ({
  // 初始状态
  queryData: null,
  queryResult: [],
  loading: false,
  error: null,
  currentVisualization: null,
  currentCode: '',
  
  // Actions
  setQueryData: (data) => set({ queryData: data }),
  setQueryResult: (result) => set({ queryResult: result }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setCurrentVisualization: (visualization) => set({ currentVisualization: visualization }),
  setCurrentCode: (code) => set({ currentCode: code }),
})); 