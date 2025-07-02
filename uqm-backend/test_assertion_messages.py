#!/usr/bin/env python
"""
测试断言消息修复
验证用户自定义的消息是否正确显示
"""

import sys
import json
import asyncio
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.steps.assert_step import AssertStep
from src.utils.exceptions import ValidationError, ExecutionError


async def test_custom_assertion_message():
    """测试自定义断言的消息显示"""
    
    print("测试自定义断言的消息显示...")
    
    # 模拟有问题的数据
    mock_data = [
        {
            "total_customers": 100,
            "null_email_count": 0,
            "null_name_count": 0,
            "invalid_email_count": 5  # 有无效邮箱，这应该触发断言失败
        }
    ]
    
    config = {
        "source": "data_quality_check",
        "assertions": [
            {
                "type": "custom",
                "expression": "null_email_count == 0",
                "message": "发现客户邮箱字段为空"
            },
            {
                "type": "custom",
                "expression": "null_name_count == 0", 
                "message": "发现客户姓名字段为空"
            },
            {
                "type": "custom",
                "expression": "invalid_email_count == 0",  # 这个会失败
                "message": "发现无效的邮箱格式"
            }
        ]
    }
    
    try:
        assert_step = AssertStep(config)
        
        def mock_get_source_data(source_name):
            return mock_data
        
        context = {
            "get_source_data": mock_get_source_data
        }
        
        # 执行断言，应该失败
        result = await assert_step.execute(context)
        
        print("❌ 断言应该失败但却通过了")
        return False
        
    except ExecutionError as e:
        error_message = str(e)
        print(f"断言失败信息: {error_message}")
        
        # 检查是否包含用户自定义的消息
        if "发现无效的邮箱格式" in error_message:
            print("✅ 用户自定义消息正确显示")
            return True
        else:
            print("❌ 用户自定义消息没有正确显示")
            print(f"实际错误消息: {error_message}")
            return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False


async def test_range_assertion_message():
    """测试范围断言的消息显示"""
    
    print("\n测试范围断言的消息显示...")
    
    # 模拟超出范围的数据
    mock_data = [
        {
            "product_price": 150000  # 超过最大值
        }
    ]
    
    config = {
        "source": "price_check",
        "assertions": [
            {
                "type": "range",
                "field": "product_price",
                "max": 100000,
                "message": "产品价格超过限制"
            }
        ]
    }
    
    try:
        assert_step = AssertStep(config)
        
        def mock_get_source_data(source_name):
            return mock_data
        
        context = {
            "get_source_data": mock_get_source_data
        }
        
        # 执行断言，应该失败
        result = await assert_step.execute(context)
        
        print("❌ 断言应该失败但却通过了")
        return False
        
    except ExecutionError as e:
        error_message = str(e)
        print(f"断言失败信息: {error_message}")
        
        # 检查是否包含用户自定义的消息
        if "产品价格超过限制" in error_message:
            print("✅ 范围断言的用户自定义消息正确显示")
            return True
        else:
            print("❌ 范围断言的用户自定义消息没有正确显示")
            print(f"实际错误消息: {error_message}")
            return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False


async def test_row_count_assertion_message():
    """测试行数断言的消息显示"""
    
    print("\n测试行数断言的消息显示...")
    
    # 模拟行数不符合预期的数据
    mock_data = [{"id": 1}, {"id": 2}]  # 只有2行
    
    config = {
        "source": "row_count_check",
        "assertions": [
            {
                "type": "row_count",
                "expected": 0,
                "message": "发现重复的客户邮箱地址"
            }
        ]
    }
    
    try:
        assert_step = AssertStep(config)
        
        def mock_get_source_data(source_name):
            return mock_data
        
        context = {
            "get_source_data": mock_get_source_data
        }
        
        # 执行断言，应该失败
        result = await assert_step.execute(context)
        
        print("❌ 断言应该失败但却通过了")
        return False
        
    except ExecutionError as e:
        error_message = str(e)
        print(f"断言失败信息: {error_message}")
        
        # 检查是否包含用户自定义的消息
        if "发现重复的客户邮箱地址" in error_message:
            print("✅ 行数断言的用户自定义消息正确显示")
            return True
        else:
            print("❌ 行数断言的用户自定义消息没有正确显示")
            print(f"实际错误消息: {error_message}")
            return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False


async def main():
    """主测试函数"""
    
    print("开始测试断言消息修复...")
    print("=" * 60)
    
    # 运行所有测试
    test_results = []
    
    test_results.append(await test_custom_assertion_message())
    test_results.append(await test_range_assertion_message())
    test_results.append(await test_row_count_assertion_message())
    
    print("\n" + "=" * 60)
    print("测试结果总结:")
    
    if all(test_results):
        print("✅ 所有测试通过！断言消息修复成功")
        print("\n现在用户自定义的错误消息会正确显示在断言失败报告中。")
        return True
    else:
        print("❌ 某些测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
