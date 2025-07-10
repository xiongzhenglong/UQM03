import type { SavedVisualization } from "../types/visualization";

const STORAGE_KEY = 'UQM_VISUALIZATIONS';

export const storageService = {
  /**
   * 获取所有已保存的可视化方案
   */
  getVisualizations(): SavedVisualization[] {
    try {
      const storedData = localStorage.getItem(STORAGE_KEY);
      if (storedData) {
        return JSON.parse(storedData) as SavedVisualization[];
      }
    } catch (error) {
      console.error("Failed to retrieve visualizations from localStorage:", error);
    }
    return [];
  },

  /**
   * 保存一个可视化方案
   * @param visualization 要保存的方案
   */
  saveVisualization(visualization: SavedVisualization): SavedVisualization[] {
    const all = this.getVisualizations();
    const existingIndex = all.findIndex(v => v.id === visualization.id);

    if (existingIndex > -1) {
      // 更新现有方案
      all[existingIndex] = visualization;
    } else {
      // 添加新方案
      all.push(visualization);
    }
    
    this.saveAll(all);
    return all;
  },

  /**
   * 删除一个可视化方案
   * @param id 要删除的方案 ID
   */
  deleteVisualization(id: string): SavedVisualization[] {
    let all = this.getVisualizations();
    all = all.filter(v => v.id !== id);
    this.saveAll(all);
    return all;
  },

  /**
   * 保存所有方案
   * @param visualizations 所有方案的数组
   */
  saveAll(visualizations: SavedVisualization[]) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(visualizations));
    } catch (error) {
      console.error("Failed to save visualizations to localStorage:", error);
      alert("无法保存可视化方案。可能是存储空间已满。");
    }
  },

  /**

   * 根据 ID 获取单个方案
   * @param id 方案 ID
   */
  getVisualizationById(id: string): SavedVisualization | undefined {
    return this.getVisualizations().find(v => v.id === id);
  }
}; 