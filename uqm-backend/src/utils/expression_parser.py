"""
表达式解析器模块

提供安全的表达式解析和执行功能，支持数据转换、计算、条件判断等操作。
"""

import ast
import re
import operator
import math
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from ..utils.exceptions import ExpressionError, ValidationError

logger = logging.getLogger(__name__)


class SafeExpressionEvaluator(ast.NodeVisitor):
    """安全的表达式求值器"""
    
    # 允许的操作符
    ALLOWED_OPERATORS = {
        # 算术运算符
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        
        # 比较运算符
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        
        # 逻辑运算符
        ast.And: lambda x, y: x and y,
        ast.Or: lambda x, y: x or y,
        
        # 位运算符
        ast.BitAnd: operator.and_,
        ast.BitOr: operator.or_,
        ast.BitXor: operator.xor,
        
        # 一元运算符
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
        ast.Not: operator.not_,
        ast.Invert: operator.inv,
    }
    
    # 允许的内置函数
    ALLOWED_BUILTINS = {
        'abs': abs,
        'round': round,
        'max': max,
        'min': min,
        'sum': sum,
        'len': len,
        'int': int,
        'float': float,
        'str': str,
        'bool': bool,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'set': set,
    }
    
    # 允许的数学函数
    ALLOWED_MATH_FUNCTIONS = {
        'sqrt': math.sqrt,
        'ceil': math.ceil,
        'floor': math.floor,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'pow': math.pow,
        'pi': math.pi,
        'e': math.e,
    }
    
    def __init__(self, context: Dict[str, Any] = None):
        self.context = context or {}
        self.allowed_names = set(self.context.keys())
        self.allowed_names.update(self.ALLOWED_BUILTINS.keys())
        self.allowed_names.update(self.ALLOWED_MATH_FUNCTIONS.keys())
    
    def evaluate(self, expression: str) -> Any:
        """安全地执行表达式"""
        try:
            # 解析表达式为 AST
            tree = ast.parse(expression, mode='eval')
            # 访问并执行 AST
            return self.visit(tree.body)
        except SyntaxError as e:
            raise ExpressionError(f"表达式语法错误: {str(e)}")
        except Exception as e:
            raise ExpressionError(f"表达式执行错误: {str(e)}")
    
    def visit_Expression(self, node):
        """访问表达式节点"""
        return self.visit(node.body)
    
    def visit_Constant(self, node):
        """访问常量节点"""
        return node.value
    
    def visit_Num(self, node):
        """访问数字节点（Python < 3.8）"""
        return node.n
    
    def visit_Str(self, node):
        """访问字符串节点（Python < 3.8）"""
        return node.s
    
    def visit_Name(self, node):
        """访问名称节点"""
        name = node.id
        
        # 检查是否在允许的名称列表中
        if name not in self.allowed_names:
            raise ExpressionError(f"不允许访问变量或函数: {name}")
        
        # 返回相应的值
        if name in self.context:
            return self.context[name]
        elif name in self.ALLOWED_BUILTINS:
            return self.ALLOWED_BUILTINS[name]
        elif name in self.ALLOWED_MATH_FUNCTIONS:
            return self.ALLOWED_MATH_FUNCTIONS[name]
        else:
            raise ExpressionError(f"未定义的变量: {name}")
    
    def visit_BinOp(self, node):
        """访问二元操作节点"""
        op_type = type(node.op)
        
        if op_type not in self.ALLOWED_OPERATORS:
            raise ExpressionError(f"不允许的操作符: {op_type.__name__}")
        
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        try:
            return self.ALLOWED_OPERATORS[op_type](left, right)
        except ZeroDivisionError:
            raise ExpressionError("除零错误")
        except Exception as e:
            raise ExpressionError(f"操作执行错误: {str(e)}")
    
    def visit_UnaryOp(self, node):
        """访问一元操作节点"""
        op_type = type(node.op)
        
        if op_type not in self.ALLOWED_OPERATORS:
            raise ExpressionError(f"不允许的一元操作符: {op_type.__name__}")
        
        operand = self.visit(node.operand)
        
        try:
            return self.ALLOWED_OPERATORS[op_type](operand)
        except Exception as e:
            raise ExpressionError(f"一元操作执行错误: {str(e)}")
    
    def visit_Compare(self, node):
        """访问比较操作节点"""
        left = self.visit(node.left)
        
        for op, comparator in zip(node.ops, node.comparators):
            op_type = type(op)
            
            if op_type not in self.ALLOWED_OPERATORS:
                raise ExpressionError(f"不允许的比较操作符: {op_type.__name__}")
            
            right = self.visit(comparator)
            
            try:
                result = self.ALLOWED_OPERATORS[op_type](left, right)
                if not result:
                    return False
                left = right
            except Exception as e:
                raise ExpressionError(f"比较操作执行错误: {str(e)}")
        
        return True
    
    def visit_BoolOp(self, node):
        """访问布尔操作节点"""
        op_type = type(node.op)
        
        if op_type == ast.And:
            for value in node.values:
                result = self.visit(value)
                if not result:
                    return False
            return True
        elif op_type == ast.Or:
            for value in node.values:
                result = self.visit(value)
                if result:
                    return True
            return False
        else:
            raise ExpressionError(f"不允许的布尔操作符: {op_type.__name__}")
    
    def visit_Call(self, node):
        """访问函数调用节点"""
        func_name = None
        
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        else:
            raise ExpressionError("不支持复杂的函数调用")
        
        # 检查函数是否被允许
        if func_name not in self.allowed_names:
            raise ExpressionError(f"不允许调用函数: {func_name}")
        
        # 获取函数对象
        if func_name in self.ALLOWED_BUILTINS:
            func = self.ALLOWED_BUILTINS[func_name]
        elif func_name in self.ALLOWED_MATH_FUNCTIONS:
            func = self.ALLOWED_MATH_FUNCTIONS[func_name]
        elif func_name in self.context and callable(self.context[func_name]):
            func = self.context[func_name]
        else:
            raise ExpressionError(f"函数不可调用: {func_name}")
        
        # 计算参数
        args = [self.visit(arg) for arg in node.args]
        kwargs = {kw.arg: self.visit(kw.value) for kw in node.keywords}
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise ExpressionError(f"函数调用错误 {func_name}: {str(e)}")
    
    def visit_List(self, node):
        """访问列表节点"""
        return [self.visit(item) for item in node.elts]
    
    def visit_Tuple(self, node):
        """访问元组节点"""
        return tuple(self.visit(item) for item in node.elts)
    
    def visit_Dict(self, node):
        """访问字典节点"""
        return {
            self.visit(key): self.visit(value)
            for key, value in zip(node.keys, node.values)
        }
    
    def visit_Subscript(self, node):
        """访问下标节点"""
        value = self.visit(node.value)
        index = self.visit(node.slice)
        
        try:
            return value[index]
        except Exception as e:
            raise ExpressionError(f"下标访问错误: {str(e)}")
    
    def visit_Slice(self, node):
        """访问切片节点"""
        lower = self.visit(node.lower) if node.lower else None
        upper = self.visit(node.upper) if node.upper else None
        step = self.visit(node.step) if node.step else None
        
        return slice(lower, upper, step)
    
    def visit_Index(self, node):
        """访问索引节点（Python < 3.9）"""
        return self.visit(node.value)
    
    def generic_visit(self, node):
        """访问未知节点类型"""
        raise ExpressionError(f"不支持的表达式节点类型: {type(node).__name__}")


class ExpressionParser:
    """表达式解析器"""
    
    def __init__(self):
        self.functions = {}
        self.variables = {}
        self._register_default_functions()
    
    def _register_default_functions(self):
        """注册默认函数"""
        # 字符串函数
        self.functions.update({
            'upper': lambda x: str(x).upper(),
            'lower': lambda x: str(x).lower(),
            'strip': lambda x: str(x).strip(),
            'split': lambda x, sep=' ': str(x).split(sep),
            'replace': lambda x, old, new: str(x).replace(old, new),
            'startswith': lambda x, prefix: str(x).startswith(prefix),
            'endswith': lambda x, suffix: str(x).endswith(suffix),
            'contains': lambda x, substr: substr in str(x),
            'length': lambda x: len(str(x)),
        })
        
        # 日期时间函数
        self.functions.update({
            'now': lambda: datetime.now(),
            'today': lambda: date.today(),
            'year': lambda x: x.year if isinstance(x, (date, datetime)) else None,
            'month': lambda x: x.month if isinstance(x, (date, datetime)) else None,
            'day': lambda x: x.day if isinstance(x, (date, datetime)) else None,
            'weekday': lambda x: x.weekday() if isinstance(x, (date, datetime)) else None,
            'strftime': lambda x, fmt: x.strftime(fmt) if isinstance(x, (date, datetime)) else None,
        })
        
        # 类型转换函数
        self.functions.update({
            'to_int': lambda x: int(x) if x is not None else None,
            'to_float': lambda x: float(x) if x is not None else None,
            'to_str': lambda x: str(x) if x is not None else None,
            'to_bool': lambda x: bool(x) if x is not None else None,
        })
        
        # 条件函数
        self.functions.update({
            'if_null': lambda x, default: default if x is None else x,
            'if_empty': lambda x, default: default if not x else x,
            'coalesce': lambda *args: next((arg for arg in args if arg is not None), None),
        })
        
        # 数组函数
        self.functions.update({
            'first': lambda arr: arr[0] if arr else None,
            'last': lambda arr: arr[-1] if arr else None,
            'join': lambda arr, sep=',': sep.join(str(x) for x in arr),
            'sort': lambda arr: sorted(arr),
            'unique': lambda arr: list(set(arr)),
        })
    
    def register_function(self, name: str, func: Callable):
        """注册自定义函数"""
        if not callable(func):
            raise ValueError(f"函数 {name} 必须是可调用对象")
        
        self.functions[name] = func
        logger.debug(f"注册自定义函数: {name}")
    
    def set_variable(self, name: str, value: Any):
        """设置变量值"""
        self.variables[name] = value
    
    def set_variables(self, variables: Dict[str, Any]):
        """批量设置变量"""
        self.variables.update(variables)
    
    def parse_and_evaluate(self, expression: str, context: Dict[str, Any] = None) -> Any:
        """解析并执行表达式"""
        # 合并上下文
        full_context = self.variables.copy()
        full_context.update(self.functions)
        if context:
            full_context.update(context)
        
        # 创建求值器
        evaluator = SafeExpressionEvaluator(full_context)
        
        # 执行表达式
        return evaluator.evaluate(expression)
    
    def validate_expression(self, expression: str) -> Tuple[bool, str]:
        """验证表达式语法"""
        try:
            # 检查是否包含危险模式
            dangerous_patterns = [
                r'__\w+__',  # 双下划线属性
                r'import\s+',  # import 语句
                r'exec\s*\(',  # exec 函数
                r'eval\s*\(',  # eval 函数
                r'open\s*\(',  # open 函数
                r'file\s*\(',  # file 函数
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, expression, re.IGNORECASE):
                    return False, f"表达式包含危险模式: {pattern}"
            
            # 解析语法
            ast.parse(expression, mode='eval')
            return True, ""
            
        except SyntaxError as e:
            return False, f"语法错误: {str(e)}"
        except Exception as e:
            return False, f"验证失败: {str(e)}"


class DataFrameExpressionParser(ExpressionParser):
    """DataFrame 表达式解析器"""
    
    def __init__(self):
        super().__init__()
        self._register_dataframe_functions()
    
    def _register_dataframe_functions(self):
        """注册 DataFrame 相关函数"""
        # 聚合函数
        self.functions.update({
            'sum_col': lambda df, col: df[col].sum() if col in df.columns else 0,
            'mean_col': lambda df, col: df[col].mean() if col in df.columns else 0,
            'count_col': lambda df, col: df[col].count() if col in df.columns else 0,
            'max_col': lambda df, col: df[col].max() if col in df.columns else None,
            'min_col': lambda df, col: df[col].min() if col in df.columns else None,
        })
        
        # 条件筛选函数
        self.functions.update({
            'filter_rows': lambda df, condition: df.query(condition),
            'select_cols': lambda df, cols: df[cols] if isinstance(cols, list) else df[[cols]],
            'drop_cols': lambda df, cols: df.drop(columns=cols),
        })
    
    def apply_to_dataframe(self, df: pd.DataFrame, expression: str, 
                          column_name: str = None) -> Union[pd.DataFrame, pd.Series, Any]:
        """将表达式应用到 DataFrame"""
        try:
            # 设置 DataFrame 作为上下文变量
            context = {'df': df}
            
            # 添加列作为变量
            for col in df.columns:
                context[col] = df[col]
            
            # 解析并执行表达式
            result = self.parse_and_evaluate(expression, context)
            
            # 如果结果是标量且指定了列名，创建新列
            if column_name and not isinstance(result, (pd.DataFrame, pd.Series)):
                if isinstance(result, (list, tuple)):
                    if len(result) == len(df):
                        df[column_name] = result
                        return df
                    else:
                        raise ExpressionError(f"结果长度 {len(result)} 与 DataFrame 行数 {len(df)} 不匹配")
                else:
                    df[column_name] = result
                    return df
            
            return result
            
        except Exception as e:
            raise ExpressionError(f"DataFrame 表达式执行失败: {str(e)}")
    
    def create_computed_column(self, df: pd.DataFrame, column_name: str, 
                              expression: str) -> pd.DataFrame:
        """创建计算列"""
        # 为每行创建上下文并执行表达式
        results = []
        
        for index, row in df.iterrows():
            # 创建行上下文
            context = row.to_dict()
            context['index'] = index
            
            try:
                result = self.parse_and_evaluate(expression, context)
                results.append(result)
            except Exception as e:
                logger.warning(f"第 {index} 行表达式执行失败: {str(e)}")
                results.append(None)
        
        # 添加新列
        df_copy = df.copy()
        df_copy[column_name] = results
        
        return df_copy
    
    def filter_dataframe(self, df: pd.DataFrame, condition: str) -> pd.DataFrame:
        """根据条件筛选 DataFrame"""
        try:
            # 使用 pandas query 方法进行筛选
            return df.query(condition)
        except Exception as e:
            # 如果 query 失败，尝试使用自定义解析
            try:
                mask_results = []
                
                for index, row in df.iterrows():
                    context = row.to_dict()
                    context['index'] = index
                    
                    result = self.parse_and_evaluate(condition, context)
                    mask_results.append(bool(result))
                
                return df[mask_results]
                
            except Exception as e2:
                raise ExpressionError(f"条件筛选失败: {str(e2)}")


class SQLExpressionParser:
    """SQL 表达式解析器"""
    
    def __init__(self):
        self.sql_functions = {
            # 字符串函数
            'UPPER': 'UPPER',
            'LOWER': 'LOWER',
            'TRIM': 'TRIM',
            'LENGTH': 'LENGTH',
            'SUBSTRING': 'SUBSTRING',
            'CONCAT': 'CONCAT',
            'REPLACE': 'REPLACE',
            
            # 数值函数
            'ABS': 'ABS',
            'ROUND': 'ROUND',
            'CEIL': 'CEIL',
            'FLOOR': 'FLOOR',
            'SQRT': 'SQRT',
            'POWER': 'POWER',
            
            # 日期函数
            'NOW': 'NOW',
            'CURRENT_DATE': 'CURRENT_DATE',
            'YEAR': 'YEAR',
            'MONTH': 'MONTH',
            'DAY': 'DAY',
            'DATE_ADD': 'DATE_ADD',
            'DATE_SUB': 'DATE_SUB',
            
            # 聚合函数
            'SUM': 'SUM',
            'COUNT': 'COUNT',
            'AVG': 'AVG',
            'MAX': 'MAX',
            'MIN': 'MIN',
            'GROUP_CONCAT': 'GROUP_CONCAT',
            
            # 条件函数
            'CASE': 'CASE',
            'IF': 'IF',
            'IFNULL': 'IFNULL',
            'COALESCE': 'COALESCE',
        }
    
    def convert_expression_to_sql(self, expression: str, 
                                 dialect: str = 'standard') -> str:
        """将表达式转换为 SQL"""
        # 简化实现，实际应该根据不同数据库方言进行转换
        sql_expression = expression
        
        # 替换一些常见的 Python 表达式为 SQL
        replacements = {
            ' and ': ' AND ',
            ' or ': ' OR ',
            ' not ': ' NOT ',
            '==': '=',
            '!=': '<>',
            'True': '1',
            'False': '0',
            'None': 'NULL',
        }
        
        for old, new in replacements.items():
            sql_expression = sql_expression.replace(old, new)
        
        return sql_expression
    
    def validate_sql_expression(self, expression: str) -> Tuple[bool, str]:
        """验证 SQL 表达式"""
        try:
            # 检查基本语法
            if not expression.strip():
                return False, "表达式不能为空"
            
            # 检查平衡的括号
            if expression.count('(') != expression.count(')'):
                return False, "括号不匹配"
            
            # 检查引号
            single_quotes = expression.count("'")
            double_quotes = expression.count('"')
            
            if single_quotes % 2 != 0:
                return False, "单引号不匹配"
            
            if double_quotes % 2 != 0:
                return False, "双引号不匹配"
            
            return True, ""
            
        except Exception as e:
            return False, f"SQL 表达式验证失败: {str(e)}"


# 全局解析器实例
expression_parser = ExpressionParser()
dataframe_expression_parser = DataFrameExpressionParser()
sql_expression_parser = SQLExpressionParser()
