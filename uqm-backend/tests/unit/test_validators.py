"""
数据验证器单元测试
"""

import pytest
import pandas as pd
from datetime import datetime

from src.utils.validators import (
    DataValidator,
    UQMValidator,
    DataTypeValidator,
    SchemaValidator,
    BusinessValidator,
    validate_sql_injection,
    validate_column_name,
    validate_expression,
    uqm_validator,
    data_type_validator,
    schema_validator,
    business_validator
)
from src.utils.exceptions import ValidationError


class TestDataValidator:
    """数据验证器基类测试"""
    
    def test_add_error(self):
        """测试添加错误"""
        validator = DataValidator()
        
        validator.add_error("field1", "错误信息1", "value1")
        validator.add_error("field2", "错误信息2")
        
        assert validator.has_errors() is True
        assert len(validator.get_errors()) == 2
        
        errors = validator.get_errors()
        assert errors[0]['field'] == "field1"
        assert errors[0]['message'] == "错误信息1"
        assert errors[0]['value'] == "value1"
    
    def test_clear_errors(self):
        """测试清空错误"""
        validator = DataValidator()
        
        validator.add_error("field1", "错误信息1")
        assert validator.has_errors() is True
        
        validator.clear_errors()
        assert validator.has_errors() is False
        assert len(validator.get_errors()) == 0
    
    def test_raise_if_errors(self):
        """测试有错误时抛出异常"""
        validator = DataValidator()
        
        # 没有错误时不应抛出异常
        validator.raise_if_errors()
        
        # 有错误时应抛出异常
        validator.add_error("field1", "错误信息1")
        with pytest.raises(ValidationError):
            validator.raise_if_errors()


class TestUQMValidator:
    """UQM 配置验证器测试"""
    
    def test_validate_valid_config(self, sample_uqm_config):
        """测试验证有效配置"""
        validator = UQMValidator()
        
        result = validator.validate_uqm_config(sample_uqm_config)
        assert result is True
        assert not validator.has_errors()
    
    def test_validate_missing_required_fields(self):
        """测试缺少必需字段"""
        validator = UQMValidator()
        config = {"name": "test"}  # 缺少 version 和 steps
        
        result = validator.validate_uqm_config(config)
        assert result is False
        assert validator.has_errors()
        
        errors = validator.get_errors()
        error_fields = [e['field'] for e in errors]
        assert 'version' in error_fields
        assert 'steps' in error_fields
    
    def test_validate_invalid_version_format(self):
        """测试无效的版本格式"""
        validator = UQMValidator()
        config = {
            "name": "test",
            "version": "invalid_version",
            "steps": []
        }
        
        result = validator.validate_uqm_config(config)
        assert result is False
        assert any("版本格式无效" in e['message'] for e in validator.get_errors())
    
    def test_validate_empty_name(self):
        """测试空名称"""
        validator = UQMValidator()
        config = {
            "name": "",
            "version": "1.0.0",
            "steps": []
        }
        
        result = validator.validate_uqm_config(config)
        assert result is False
        assert any("名称无效" in e['message'] for e in validator.get_errors())
    
    def test_validate_datasources(self):
        """测试数据源验证"""
        validator = UQMValidator()
        config = {
            "name": "test",
            "version": "1.0.0",
            "datasources": {
                "db1": {
                    "type": "postgres",
                    "connection": {"host": "localhost"}
                },
                "db2": {
                    "type": "invalid_type",
                    "connection": {"host": "localhost"}
                }
            },
            "steps": [{"name": "step1", "type": "query"}]
        }
        
        result = validator.validate_uqm_config(config)
        assert result is False
        assert any("不支持的数据源类型" in e['message'] for e in validator.get_errors())
    
    def test_validate_steps_structure(self):
        """测试步骤结构验证"""
        validator = UQMValidator()
        config = {
            "name": "test",
            "version": "1.0.0",
            "steps": [
                {"name": "step1", "type": "query"},
                {"name": "step1", "type": "enrich"},  # 重复名称
                {"type": "filter"},  # 缺少名称
                {"name": "step3", "type": "invalid_type"}  # 无效类型
            ]
        }
        
        result = validator.validate_uqm_config(config)
        assert result is False
        
        errors = validator.get_errors()
        error_messages = [e['message'] for e in errors]
        assert any("步骤名称重复" in msg for msg in error_messages)
        assert any("缺少必需字段" in msg for msg in error_messages)
        assert any("不支持的步骤类型" in msg for msg in error_messages)
    
    def test_validate_step_dependencies(self):
        """测试步骤依赖验证"""
        validator = UQMValidator()
        config = {
            "name": "test",
            "version": "1.0.0",
            "steps": [
                {"name": "step1", "type": "query"},
                {"name": "step2", "type": "enrich", "depends_on": ["nonexistent_step"]}
            ]
        }
        
        result = validator.validate_uqm_config(config)
        assert result is False
        assert any("引用了不存在的步骤" in e['message'] for e in validator.get_errors())
    
    def test_validate_output_config(self):
        """测试输出配置验证"""
        validator = UQMValidator()
        config = {
            "name": "test",
            "version": "1.0.0",
            "steps": [{"name": "step1", "type": "query"}],
            "output": {
                "format": "invalid_format"
            }
        }
        
        result = validator.validate_uqm_config(config)
        assert result is False
        assert any("不支持的输出格式" in e['message'] for e in validator.get_errors())


class TestDataTypeValidator:
    """数据类型验证器测试"""
    
    def test_validate_dataframe_structure(self, sample_dataframe):
        """测试 DataFrame 结构验证"""
        validator = DataTypeValidator()
        schema = {
            "columns": {
                "required": ["id", "name", "age"],
                "types": {
                    "id": "int",
                    "name": "string",
                    "age": "int"
                }
            }
        }
        
        result = validator.validate_dataframe(sample_dataframe, schema)
        assert result is True
        assert not validator.has_errors()
    
    def test_validate_missing_required_columns(self, sample_dataframe):
        """测试缺少必需列"""
        validator = DataTypeValidator()
        schema = {
            "columns": {
                "required": ["id", "name", "missing_column"]
            }
        }
        
        result = validator.validate_dataframe(sample_dataframe, schema)
        assert result is False
        assert any("缺少必需列" in e['message'] for e in validator.get_errors())
    
    def test_validate_column_types(self, sample_dataframe):
        """测试列类型验证"""
        validator = DataTypeValidator()
        schema = {
            "columns": {
                "types": {
                    "id": "string",  # 实际是 int，类型不匹配
                    "name": "string"
                }
            }
        }
        
        result = validator.validate_dataframe(sample_dataframe, schema)
        assert result is False
        assert any("列类型不匹配" in e['message'] for e in validator.get_errors())
    
    def test_validate_constraints(self):
        """测试数据约束验证"""
        validator = DataTypeValidator()
        
        # 创建包含问题的 DataFrame
        df = pd.DataFrame({
            'id': [1, 2, 2, 4],  # 包含重复值
            'name': ['Alice', None, 'Charlie', 'David'],  # 包含空值
            'score': [85, 95, 45, 105]  # 包含超出范围的值
        })
        
        schema = {
            "constraints": {
                "not_null": ["name"],
                "unique": ["id"],
                "range": {
                    "score": {"min": 0, "max": 100}
                }
            }
        }
        
        result = validator.validate_dataframe(df, schema)
        assert result is False
        
        errors = validator.get_errors()
        error_messages = [e['message'] for e in errors]
        assert any("包含" in msg and "空值" in msg for msg in error_messages)
        assert any("包含" in msg and "重复值" in msg for msg in error_messages)
        assert any("大于最大值" in msg for msg in error_messages)


class TestSchemaValidator:
    """Schema 验证器测试"""
    
    def test_validate_basic_types(self):
        """测试基本类型验证"""
        validator = SchemaValidator()
        
        # 字符串类型
        schema = {"type": "string"}
        assert validator.validate_json_schema("test", schema) is True
        assert validator.validate_json_schema(123, schema) is False
        
        # 数字类型
        schema = {"type": "number"}
        validator.clear_errors()
        assert validator.validate_json_schema(123, schema) is True
        validator.clear_errors()
        assert validator.validate_json_schema("test", schema) is False
    
    def test_validate_object_schema(self):
        """测试对象 Schema 验证"""
        validator = SchemaValidator()
        
        schema = {
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        
        # 有效对象
        data = {"name": "Alice", "age": 25}
        assert validator.validate_json_schema(data, schema) is True
        
        # 缺少必需字段
        validator.clear_errors()
        data = {"name": "Alice"}
        assert validator.validate_json_schema(data, schema) is False
        assert any("缺少必需字段" in e['message'] for e in validator.get_errors())


class TestBusinessValidator:
    """业务逻辑验证器测试"""
    
    def test_validate_pivot_config(self):
        """测试透视配置验证"""
        validator = BusinessValidator()
        
        # 有效配置
        config = {
            "index_columns": ["date", "category"],
            "pivot_column": "metric",
            "value_columns": ["value"]
        }
        assert validator.validate_pivot_config(config) is True
        
        # 缺少必需字段
        config = {"index_columns": ["date"]}
        validator.clear_errors()
        assert validator.validate_pivot_config(config) is False
        assert validator.has_errors()
    
    def test_validate_join_config(self):
        """测试连接配置验证"""
        validator = BusinessValidator()
        
        # 有效配置
        config = {
            "left_on": "id",
            "right_on": "user_id",
            "how": "inner"
        }
        assert validator.validate_join_config(config) is True
        
        # 无效连接类型
        config["how"] = "invalid_join"
        validator.clear_errors()
        assert validator.validate_join_config(config) is False
        assert any("不支持的连接类型" in e['message'] for e in validator.get_errors())
    
    def test_validate_aggregation_config(self):
        """测试聚合配置验证"""
        validator = BusinessValidator()
        
        # 有效配置
        config = {
            "group_by": ["category"],
            "agg_functions": {
                "sales": "sum",
                "quantity": ["count", "avg"]
            }
        }
        assert validator.validate_aggregation_config(config) is True
        
        # 无效聚合函数
        config["agg_functions"]["sales"] = "invalid_function"
        validator.clear_errors()
        assert validator.validate_aggregation_config(config) is False
        assert any("不支持的聚合函数" in e['message'] for e in validator.get_errors())


class TestUtilityFunctions:
    """工具函数测试"""
    
    def test_validate_sql_injection(self):
        """测试 SQL 注入验证"""
        # 安全的 SQL
        safe_sql = "SELECT * FROM users WHERE age > 25"
        is_safe, risks = validate_sql_injection(safe_sql)
        assert is_safe is True
        assert len(risks) == 0
        
        # 包含危险模式的 SQL
        dangerous_sql = "SELECT * FROM users; DROP TABLE users;"
        is_safe, risks = validate_sql_injection(dangerous_sql)
        assert is_safe is False
        assert len(risks) > 0
        
        # 包含注释的 SQL
        comment_sql = "SELECT * FROM users -- WHERE age > 25"
        is_safe, risks = validate_sql_injection(comment_sql)
        assert is_safe is False
        assert len(risks) > 0
    
    def test_validate_column_name(self):
        """测试列名验证"""
        # 有效列名
        valid, msg = validate_column_name("user_id")
        assert valid is True
        assert msg == ""
        
        valid, msg = validate_column_name("columnA")
        assert valid is True
        
        # 无效列名
        valid, msg = validate_column_name("123column")
        assert valid is False
        assert "必须以字母开头" in msg
        
        valid, msg = validate_column_name("select")
        assert valid is False
        assert "SQL 保留字" in msg
        
        valid, msg = validate_column_name("")
        assert valid is False
        assert "不能为空" in msg
    
    def test_validate_expression(self):
        """测试表达式验证"""
        # 安全表达式
        safe_expr = "x + y * 2"
        valid, msg = validate_expression(safe_expr)
        assert valid is True
        assert msg == ""
        
        # 包含危险函数的表达式
        dangerous_expr = "eval('x + y')"
        valid, msg = validate_expression(dangerous_expr)
        assert valid is False
        assert "危险函数" in msg
        
        # 包含危险属性访问的表达式
        dangerous_expr = "x.__class__.__bases__"
        valid, msg = validate_expression(dangerous_expr)
        assert valid is False
        assert "危险的属性访问" in msg


class TestGlobalValidators:
    """测试全局验证器实例"""
    
    def test_uqm_validator_instance(self, sample_uqm_config):
        """测试全局 UQM 验证器实例"""
        result = uqm_validator.validate_uqm_config(sample_uqm_config)
        assert result is True
    
    def test_data_type_validator_instance(self, sample_dataframe):
        """测试全局数据类型验证器实例"""
        schema = {"columns": {"required": ["id", "name"]}}
        result = data_type_validator.validate_dataframe(sample_dataframe, schema)
        assert result is True
    
    def test_schema_validator_instance(self):
        """测试全局 Schema 验证器实例"""
        schema = {"type": "string"}
        result = schema_validator.validate_json_schema("test", schema)
        assert result is True
    
    def test_business_validator_instance(self):
        """测试全局业务验证器实例"""
        config = {
            "index_columns": ["date"],
            "pivot_column": "metric",
            "value_columns": ["value"]
        }
        result = business_validator.validate_pivot_config(config)
        assert result is True


class TestValidationIntegration:
    """验证器集成测试"""
    
    def test_comprehensive_uqm_validation(self):
        """测试综合 UQM 验证"""
        validator = UQMValidator()
        
        # 复杂的 UQM 配置
        config = {
            "name": "complex_uqm",
            "version": "2.1.0",
            "description": "复杂的 UQM 配置示例",
            "datasources": {
                "main_db": {
                    "type": "postgres",
                    "connection": {
                        "host": "localhost",
                        "port": 5432,
                        "database": "testdb"
                    }
                },
                "cache_db": {
                    "type": "redis",
                    "connection": {
                        "host": "localhost",
                        "port": 6379
                    }
                }
            },
            "steps": [
                {
                    "name": "extract_users",
                    "type": "query",
                    "datasource": "main_db",
                    "config": {
                        "sql": "SELECT * FROM users"
                    }
                },
                {
                    "name": "enrich_users",
                    "type": "enrich",
                    "depends_on": ["extract_users"],
                    "config": {
                        "enrichments": [
                            {"column": "full_name", "expression": "first_name + ' ' + last_name"}
                        ]
                    }
                },
                {
                    "name": "pivot_data",
                    "type": "pivot",
                    "depends_on": ["enrich_users"],
                    "config": {
                        "index_columns": ["department"],
                        "pivot_column": "role",
                        "value_columns": ["salary"]
                    }
                }
            ],
            "output": {
                "format": "json",
                "file_path": "output.json"
            }
        }
        
        result = validator.validate_uqm_config(config)
        assert result is True
        assert not validator.has_errors()
    
    def test_validation_error_accumulation(self):
        """测试验证错误累积"""
        validator = UQMValidator()
        
        # 包含多种错误的配置
        config = {
            "name": "",  # 空名称
            "version": "invalid",  # 无效版本
            "datasources": {
                "db1": {
                    "type": "invalid_type",  # 无效类型
                    "connection": "not_a_dict"  # 错误的连接配置类型
                }
            },
            "steps": [
                {"type": "query"},  # 缺少名称
                {"name": "step1", "type": "invalid_step_type"},  # 无效步骤类型
                {"name": "step2", "type": "enrich", "depends_on": ["nonexistent"]}  # 无效依赖
            ]
        }
        
        result = validator.validate_uqm_config(config)
        assert result is False
        assert len(validator.get_errors()) >= 5  # 应该有多个错误
