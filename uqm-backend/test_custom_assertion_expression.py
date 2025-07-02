#!/usr/bin/env python
"""
测试修复后的自定义断言配置
验证expression字段是否正常工作
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


async def test_custom_assertion_with_expression():
    """测试使用expression字段的自定义断言"""
    
    print("测试使用expression字段的自定义断言...")
    
    # 模拟查询结果数据
    mock_data = [
        {
            "total_customers": 100,
            "null_email_count": 0,
            "null_name_count": 0,
            "invalid_email_count": 0
        }
    ]
    
    # 使用expression字段的断言配置
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
                "expression": "invalid_email_count == 0",
                "message": "发现无效的邮箱格式"
            }
        ]
    }
    
    try:
        # 创建断言步骤
        assert_step = AssertStep(config)
        
        # 验证配置
        assert_step.validate()
        print("✅ 断言配置验证通过")
        
        # 模拟执行上下文
        def mock_get_source_data(source_name):
            return mock_data
        
        context = {
            "get_source_data": mock_get_source_data
        }
        
        # 执行断言
        result = await assert_step.execute(context)
        
        print("✅ 断言执行成功，所有检查通过")
        print(f"返回数据行数: {len(result)}")
        
        return True
        
    except ValidationError as e:
        print(f"❌ 配置验证失败: {e}")
        return False
    except ExecutionError as e:
        print(f"❌ 断言执行失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False


async def test_custom_assertion_failure_case():
    """测试自定义断言失败的情况"""
    
    print("\n测试自定义断言失败的情况...")
    
    # 模拟包含问题的数据
    mock_data = [
        {
            "total_customers": 100,
            "null_email_count": 5,  # 有空邮箱
            "null_name_count": 0,
            "invalid_email_count": 2  # 有无效邮箱
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
                "expression": "invalid_email_count == 0",
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
        
        # 这里应该抛出断言失败的异常
        result = await assert_step.execute(context)
        
        print("❌ 断言应该失败但却通过了")
        return False
        
    except ExecutionError as e:
        if "断言检查失败" in str(e):
            print("✅ 断言正确检测到数据质量问题")
            print(f"错误信息: {e}")
            return True
        else:
            print(f"❌ 断言失败但错误信息不正确: {e}")
            return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False


async def test_old_condition_field():
    """测试使用旧的condition字段是否会报错"""
    
    print("\n测试使用旧的condition字段...")
    
    config = {
        "source": "data_quality_check",
        "assertions": [
            {
                "type": "custom",
                "condition": "null_email_count == 0",  # 使用旧字段
                "message": "发现客户邮箱字段为空"
            }
        ]
    }
    
    mock_data = [{"null_email_count": 0}]
    
    try:
        assert_step = AssertStep(config)
        
        def mock_get_source_data(source_name):
            return mock_data
        
        context = {
            "get_source_data": mock_get_source_data
        }
        
        result = await assert_step.execute(context)
        
        print("❌ 使用condition字段不应该成功")
        return False
        
    except ExecutionError as e:
        if "缺少expression参数" in str(e):
            print("✅ 正确检测到缺少expression参数")
            return True
        else:
            print(f"❌ 错误信息不正确: {e}")
            return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False


async def main():
    """主测试函数"""
    
    print("开始测试自定义断言expression字段修复...")
    print("=" * 60)
    
    # 运行所有测试
    test_results = []
    
    test_results.append(await test_custom_assertion_with_expression())
    test_results.append(await test_custom_assertion_failure_case())
    test_results.append(await test_old_condition_field())
    
    print("\n" + "=" * 60)
    print("测试结果总结:")
    
    if all(test_results):
        print("✅ 所有测试通过！expression字段修复成功")
        print("\n现在用户可以正常使用带有expression字段的自定义断言配置了。")
        return True
    else:
        print("❌ 某些测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
