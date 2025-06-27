"""
测试修复后的 PivotStep 完整功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_pivot_step_complete():
    """完整测试 PivotStep 功能"""
    print("开始完整测试 PivotStep...")
    
    try:
        from src.steps.pivot_step import PivotStep
        
        # 测试各种配置
        test_cases = [
            {
                'name': '基本配置 - mean',
                'config': {
                    'source': 'test_data',
                    'index': 'department_name',
                    'columns': 'job_title',
                    'values': 'salary',
                    'agg_func': 'mean'
                }
            },
            {
                'name': '基本配置 - sum',
                'config': {
                    'source': 'test_data',
                    'index': 'department_name',
                    'columns': 'job_title',
                    'values': 'salary',
                    'agg_func': 'sum'
                }
            },
            {
                'name': '基本配置 - count',
                'config': {
                    'source': 'test_data',
                    'index': 'department_name',
                    'columns': 'job_title',
                    'values': 'employee_id',
                    'agg_func': 'count'
                }
            },
            {
                'name': '列表配置',
                'config': {
                    'source': 'test_data',
                    'index': ['department_name'],
                    'columns': ['job_title'],
                    'values': ['salary'],
                    'agg_func': 'mean'
                }
            }
        ]
        
        success_count = 0
        
        for test_case in test_cases:
            try:
                print(f"测试: {test_case['name']}")
                pivot_step = PivotStep(test_case['config'])
                print(f"  ✓ 配置验证通过")
                print(f"  ✓ 聚合函数: {test_case['config']['agg_func']}")
                success_count += 1
            except Exception as e:
                print(f"  ✗ 失败: {e}")
        
        print(f"\n总计: {success_count}/{len(test_cases)} 个测试通过")
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f'✗ 测试失败: {e}')
        return False

def test_invalid_configurations():
    """测试无效配置"""
    print("\n开始测试无效配置...")
    
    try:
        from src.steps.pivot_step import PivotStep
        
        invalid_cases = [
            {
                'name': '缺少 source',
                'config': {
                    'index': 'department_name',
                    'columns': 'job_title',
                    'values': 'salary'
                },
                'expected_error': 'source'
            },
            {
                'name': '缺少 index',
                'config': {
                    'source': 'test_data',
                    'columns': 'job_title',
                    'values': 'salary'
                },
                'expected_error': 'index'
            },
            {
                'name': '无效聚合函数',
                'config': {
                    'source': 'test_data',
                    'index': 'department_name',
                    'columns': 'job_title',
                    'values': 'salary',
                    'agg_func': 'invalid_func'
                },
                'expected_error': '不支持的聚合函数'
            }
        ]
        
        success_count = 0
        
        for test_case in invalid_cases:
            try:
                print(f"测试: {test_case['name']}")
                pivot_step = PivotStep(test_case['config'])
                print(f"  ✗ 应该抛出错误但没有")
            except Exception as e:
                if test_case['expected_error'] in str(e):
                    print(f"  ✓ 正确捕获错误: {e}")
                    success_count += 1
                else:
                    print(f"  ✗ 错误不匹配，期望包含 '{test_case['expected_error']}'，实际: {e}")
        
        print(f"\n无效配置测试: {success_count}/{len(invalid_cases)} 个测试通过")
        return success_count == len(invalid_cases)
        
    except Exception as e:
        print(f'✗ 无效配置测试失败: {e}')
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PivotStep 修复后完整功能测试")
    print("=" * 60)
    
    # 测试正常配置
    valid_success = test_pivot_step_complete()
    
    # 测试无效配置
    invalid_success = test_invalid_configurations()
    
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print(f"正常配置测试: {'通过' if valid_success else '失败'}")
    print(f"无效配置测试: {'通过' if invalid_success else '失败'}")
    print(f"整体测试: {'通过' if (valid_success and invalid_success) else '失败'}")
    print("=" * 60)
    
    if valid_success and invalid_success:
        print("\n🎉 PivotStep 修复成功！所有测试通过！")
    else:
        print("\n❌ 还有问题需要解决")
