"""
测试 PivotStep 初始化问题的测试文件
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pivot_step_initialization():
    """测试 PivotStep 的初始化问题"""
    print("开始测试 PivotStep 初始化...")
    
    try:
        from src.steps.pivot_step import PivotStep
        
        # 测试基础配置
        config = {
            'source': 'test_data',
            'index': 'department_name',
            'columns': 'job_title',
            'values': 'salary',
            'agg_func': 'mean'
        }
        
        print("创建 PivotStep 实例...")
        pivot_step = PivotStep(config)
        print('✓ PivotStep 初始化成功')
        print(f'✓ 支持的聚合函数: {list(pivot_step.supported_agg_functions.keys())}')
        
        return True
        
    except Exception as e:
        print(f'✗ 初始化失败: {e}')
        print(f'✗ 错误类型: {type(e).__name__}')
        import traceback
        print(f'✗ 完整错误信息:\n{traceback.format_exc()}')
        return False

def test_validation_errors():
    """测试验证错误的情况"""
    print("\n开始测试验证错误...")
    
    try:
        from src.steps.pivot_step import PivotStep
        
        # 测试缺少必需字段的配置
        invalid_config = {
            'source': 'test_data',
            # 缺少 index, columns, values
        }
        
        print("测试无效配置...")
        try:
            pivot_step = PivotStep(invalid_config)
            print('✗ 应该抛出验证错误，但没有')
            return False
        except Exception as e:
            print(f'✓ 正确捕获验证错误: {e}')
            return True
            
    except Exception as e:
        print(f'✗ 测试验证错误失败: {e}')
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("PivotStep 初始化问题测试")
    print("=" * 50)
    
    # 测试初始化
    init_success = test_pivot_step_initialization()
    
    # 如果初始化成功，测试验证
    if init_success:
        validation_success = test_validation_errors()
    else:
        validation_success = False
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"初始化测试: {'通过' if init_success else '失败'}")
    print(f"验证测试: {'通过' if validation_success else '失败'}")
    print("=" * 50)
