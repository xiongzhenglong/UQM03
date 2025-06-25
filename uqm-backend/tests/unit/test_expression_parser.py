"""
表达式解析器单元测试
"""

import pytest
import pandas as pd
from datetime import datetime, date

from src.utils.expression_parser import (
    SafeExpressionEvaluator,
    ExpressionParser,
    DataFrameExpressionParser,
    SQLExpressionParser,
    expression_parser,
    dataframe_expression_parser,
    sql_expression_parser
)
from src.utils.exceptions import ExpressionError


class TestSafeExpressionEvaluator:
    """安全表达式求值器测试"""
    
    def test_basic_arithmetic(self):
        """测试基本算术运算"""
        evaluator = SafeExpressionEvaluator()
        
        assert evaluator.evaluate("1 + 2") == 3
        assert evaluator.evaluate("10 - 5") == 5
        assert evaluator.evaluate("3 * 4") == 12
        assert evaluator.evaluate("15 / 3") == 5
        assert evaluator.evaluate("2 ** 3") == 8
        assert evaluator.evaluate("10 % 3") == 1
    
    def test_comparison_operators(self):
        """测试比较运算符"""
        evaluator = SafeExpressionEvaluator()
        
        assert evaluator.evaluate("5 > 3") is True
        assert evaluator.evaluate("3 < 5") is True
        assert evaluator.evaluate("5 >= 5") is True
        assert evaluator.evaluate("3 <= 5") is True
        assert evaluator.evaluate("5 == 5") is True
        assert evaluator.evaluate("5 != 3") is True
    
    def test_logical_operators(self):
        """测试逻辑运算符"""
        evaluator = SafeExpressionEvaluator()
        
        assert evaluator.evaluate("True and True") is True
        assert evaluator.evaluate("True and False") is False
        assert evaluator.evaluate("True or False") is True
        assert evaluator.evaluate("False or False") is False
        assert evaluator.evaluate("not True") is False
        assert evaluator.evaluate("not False") is True
    
    def test_context_variables(self):
        """测试上下文变量"""
        context = {'x': 10, 'y': 20, 'name': 'test'}
        evaluator = SafeExpressionEvaluator(context)
        
        assert evaluator.evaluate("x + y") == 30
        assert evaluator.evaluate("x * 2") == 20
        assert evaluator.evaluate("name") == 'test'
    
    def test_builtin_functions(self):
        """测试内置函数"""
        evaluator = SafeExpressionEvaluator()
        
        assert evaluator.evaluate("abs(-5)") == 5
        assert evaluator.evaluate("max(1, 5, 3)") == 5
        assert evaluator.evaluate("min(1, 5, 3)") == 1
        assert evaluator.evaluate("round(3.14159, 2)") == 3.14
        assert evaluator.evaluate("len([1, 2, 3])") == 3
    
    def test_math_functions(self):
        """测试数学函数"""
        evaluator = SafeExpressionEvaluator()
        
        assert evaluator.evaluate("sqrt(16)") == 4
        assert evaluator.evaluate("ceil(3.2)") == 4
        assert evaluator.evaluate("floor(3.8)") == 3
        assert abs(evaluator.evaluate("sin(0)") - 0) < 1e-10
    
    def test_list_operations(self):
        """测试列表操作"""
        evaluator = SafeExpressionEvaluator()
        
        assert evaluator.evaluate("[1, 2, 3]") == [1, 2, 3]
        assert evaluator.evaluate("[1, 2, 3][0]") == 1
        assert evaluator.evaluate("[1, 2, 3][1:3]") == [2, 3]
    
    def test_string_operations(self):
        """测试字符串操作"""
        evaluator = SafeExpressionEvaluator()
        
        assert evaluator.evaluate("'hello' + ' world'") == 'hello world'
        assert evaluator.evaluate("'test'[0]") == 't'
        assert evaluator.evaluate("'hello'[1:4]") == 'ell'
    
    def test_forbidden_operations(self):
        """测试禁止的操作"""
        evaluator = SafeExpressionEvaluator()
        
        # 测试禁止的函数
        with pytest.raises(ExpressionError):
            evaluator.evaluate("eval('1+1')")
        
        with pytest.raises(ExpressionError):
            evaluator.evaluate("exec('print(1)')")
        
        with pytest.raises(ExpressionError):
            evaluator.evaluate("open('file.txt')")
    
    def test_syntax_errors(self):
        """测试语法错误"""
        evaluator = SafeExpressionEvaluator()
        
        with pytest.raises(ExpressionError):
            evaluator.evaluate("1 +")
        
        with pytest.raises(ExpressionError):
            evaluator.evaluate("((1 + 2)")
    
    def test_division_by_zero(self):
        """测试除零错误"""
        evaluator = SafeExpressionEvaluator()
        
        with pytest.raises(ExpressionError):
            evaluator.evaluate("1 / 0")


class TestExpressionParser:
    """表达式解析器测试"""
    
    def test_register_function(self):
        """测试注册自定义函数"""
        parser = ExpressionParser()
        
        def custom_add(a, b):
            return a + b + 1
        
        parser.register_function("custom_add", custom_add)
        result = parser.parse_and_evaluate("custom_add(2, 3)")
        assert result == 6
    
    def test_set_variables(self):
        """测试设置变量"""
        parser = ExpressionParser()
        
        parser.set_variable("x", 10)
        parser.set_variables({"y": 20, "z": 30})
        
        assert parser.parse_and_evaluate("x + y + z") == 60
    
    def test_string_functions(self):
        """测试字符串函数"""
        parser = ExpressionParser()
        
        assert parser.parse_and_evaluate("upper('hello')") == "HELLO"
        assert parser.parse_and_evaluate("lower('WORLD')") == "world"
        assert parser.parse_and_evaluate("strip('  test  ')") == "test"
        assert parser.parse_and_evaluate("length('hello')") == 5
    
    def test_conditional_functions(self):
        """测试条件函数"""
        parser = ExpressionParser()
        
        assert parser.parse_and_evaluate("if_null(None, 'default')") == "default"
        assert parser.parse_and_evaluate("if_null('value', 'default')") == "value"
        assert parser.parse_and_evaluate("coalesce(None, None, 'first')") == "first"
    
    def test_array_functions(self):
        """测试数组函数"""
        parser = ExpressionParser()
        
        assert parser.parse_and_evaluate("first([1, 2, 3])") == 1
        assert parser.parse_and_evaluate("last([1, 2, 3])") == 3
        assert parser.parse_and_evaluate("join([1, 2, 3], '-')") == "1-2-3"
    
    def test_validate_expression(self):
        """测试表达式验证"""
        parser = ExpressionParser()
        
        # 有效表达式
        valid, msg = parser.validate_expression("1 + 2")
        assert valid is True
        assert msg == ""
        
        # 无效语法
        valid, msg = parser.validate_expression("1 +")
        assert valid is False
        assert "语法错误" in msg
        
        # 危险模式
        valid, msg = parser.validate_expression("__import__('os')")
        assert valid is False
        assert "危险模式" in msg


class TestDataFrameExpressionParser:
    """DataFrame 表达式解析器测试"""
    
    def test_apply_to_dataframe(self, sample_dataframe):
        """测试应用到 DataFrame"""
        parser = DataFrameExpressionParser()
        
        # 计算列的总和
        result = parser.apply_to_dataframe(sample_dataframe, "sum_col(df, 'age')")
        assert result == sample_dataframe['age'].sum()
        
        # 获取列的最大值
        result = parser.apply_to_dataframe(sample_dataframe, "max_col(df, 'salary')")
        assert result == sample_dataframe['salary'].max()
    
    def test_create_computed_column(self, sample_dataframe):
        """测试创建计算列"""
        parser = DataFrameExpressionParser()
        
        # 创建年龄 * 1000 的列
        result_df = parser.create_computed_column(
            sample_dataframe, 
            "age_times_1000", 
            "age * 1000"
        )
        
        assert "age_times_1000" in result_df.columns
        expected_values = sample_dataframe['age'] * 1000
        pd.testing.assert_series_equal(
            result_df['age_times_1000'], 
            expected_values, 
            check_names=False
        )
    
    def test_filter_dataframe(self, sample_dataframe):
        """测试筛选 DataFrame"""
        parser = DataFrameExpressionParser()
        
        # 筛选年龄大于 30 的记录
        result_df = parser.filter_dataframe(sample_dataframe, "age > 30")
        
        expected_df = sample_dataframe[sample_dataframe['age'] > 30]
        pd.testing.assert_frame_equal(result_df.reset_index(drop=True), 
                                    expected_df.reset_index(drop=True))
    
    def test_complex_expression(self, sample_dataframe):
        """测试复杂表达式"""
        parser = DataFrameExpressionParser()
        
        # 创建包含条件逻辑的列
        result_df = parser.create_computed_column(
            sample_dataframe,
            "salary_category",
            "if_null('High' if salary > 60000 else 'Low', 'Unknown')"
        )
        
        assert "salary_category" in result_df.columns
        # 验证部分结果
        high_salary_mask = sample_dataframe['salary'] > 60000
        assert all(result_df.loc[high_salary_mask, 'salary_category'] == 'High')


class TestSQLExpressionParser:
    """SQL 表达式解析器测试"""
    
    def test_convert_expression_to_sql(self):
        """测试表达式转换为 SQL"""
        parser = SQLExpressionParser()
        
        # 测试基本转换
        sql = parser.convert_expression_to_sql("age > 30 and salary != 0")
        assert "AND" in sql
        assert "<>" in sql or "!=" in sql
        
        # 测试布尔值转换
        sql = parser.convert_expression_to_sql("active == True")
        assert "1" in sql or "TRUE" in sql.upper()
    
    def test_validate_sql_expression(self):
        """测试 SQL 表达式验证"""
        parser = SQLExpressionParser()
        
        # 有效表达式
        valid, msg = parser.validate_sql_expression("age > 30")
        assert valid is True
        assert msg == ""
        
        # 括号不匹配
        valid, msg = parser.validate_sql_expression("age > (30")
        assert valid is False
        assert "括号不匹配" in msg
        
        # 引号不匹配
        valid, msg = parser.validate_sql_expression("name = 'test")
        assert valid is False
        assert "引号不匹配" in msg
    
    def test_empty_expression(self):
        """测试空表达式"""
        parser = SQLExpressionParser()
        
        valid, msg = parser.validate_sql_expression("")
        assert valid is False
        assert "不能为空" in msg


class TestGlobalParsers:
    """测试全局解析器实例"""
    
    def test_expression_parser_instance(self):
        """测试全局表达式解析器实例"""
        result = expression_parser.parse_and_evaluate("1 + 2")
        assert result == 3
    
    def test_dataframe_expression_parser_instance(self, sample_dataframe):
        """测试全局 DataFrame 表达式解析器实例"""
        result = dataframe_expression_parser.apply_to_dataframe(
            sample_dataframe, 
            "len(df)"
        )
        assert result == len(sample_dataframe)
    
    def test_sql_expression_parser_instance(self):
        """测试全局 SQL 表达式解析器实例"""
        valid, msg = sql_expression_parser.validate_sql_expression("SELECT * FROM table")
        assert valid is True
        assert msg == ""


class TestExpressionIntegration:
    """表达式解析器集成测试"""
    
    def test_complex_dataframe_workflow(self, sample_dataframe):
        """测试复杂的 DataFrame 工作流"""
        parser = DataFrameExpressionParser()
        
        # 步骤 1: 添加计算列
        df = parser.create_computed_column(
            sample_dataframe,
            "salary_per_age",
            "salary / age"
        )
        
        # 步骤 2: 筛选数据
        df = parser.filter_dataframe(df, "department == 'IT'")
        
        # 步骤 3: 再添加一列
        df = parser.create_computed_column(
            df,
            "is_senior",
            "age > 30"
        )
        
        # 验证结果
        assert "salary_per_age" in df.columns
        assert "is_senior" in df.columns
        assert all(df['department'] == 'IT')
    
    def test_error_handling_in_computed_column(self, sample_dataframe):
        """测试计算列中的错误处理"""
        parser = DataFrameExpressionParser()
        
        # 包含可能出错的表达式
        result_df = parser.create_computed_column(
            sample_dataframe,
            "error_prone",
            "salary / (age - age)"  # 会导致除零错误
        )
        
        # 应该包含 None 值（错误处理结果）
        assert "error_prone" in result_df.columns
        assert result_df['error_prone'].isnull().any()
    
    def test_expression_with_custom_context(self):
        """测试自定义上下文的表达式"""
        parser = ExpressionParser()
        
        # 注册自定义函数
        def calculate_tax(salary, rate=0.1):
            return salary * rate
        
        parser.register_function("calculate_tax", calculate_tax)
        
        # 设置变量
        context = {"base_salary": 50000}
        
        # 执行表达式
        result = parser.parse_and_evaluate("calculate_tax(base_salary, 0.15)", context)
        assert result == 7500
