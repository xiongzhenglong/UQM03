"""
核心引擎集成测试
"""

import pytest
import asyncio
import pandas as pd
from unittest.mock import Mock, patch, AsyncMock

from src.core.engine import UQMEngine
from src.core.parser import UQMParser  
from src.core.cache import CacheManager
from src.connectors.base import DataConnectorManager
from src.utils.exceptions import UQMError, ValidationError, ExecutionError


class TestUQMEngineIntegration:
    """UQM 引擎集成测试"""
    
    @pytest.fixture
    async def engine(self, test_settings):
        """创建测试引擎实例"""
        engine = UQMEngine(test_settings)
        await engine.initialize()
        yield engine
        await engine.cleanup()
    
    @pytest.fixture
    def sample_simple_config(self):
        """简单的测试配置"""
        return {
            "name": "integration_test",
            "version": "1.0.0",
            "datasources": {
                "test_db": {
                    "type": "sqlite",
                    "connection": {
                        "database": ":memory:"
                    }
                }
            },
            "steps": [
                {
                    "name": "simple_query",
                    "type": "query",
                    "datasource": "test_db",
                    "config": {
                        "sql": "SELECT 1 as id, 'test' as name"
                    }
                }
            ]
        }
    
    @pytest.fixture
    def sample_complex_config(self):
        """复杂的测试配置"""
        return {
            "name": "complex_integration_test",
            "version": "1.0.0",
            "datasources": {
                "source_db": {
                    "type": "sqlite",
                    "connection": {
                        "database": ":memory:"
                    }
                }
            },
            "steps": [
                {
                    "name": "extract_data",
                    "type": "query",
                    "datasource": "source_db",
                    "config": {
                        "sql": """
                        SELECT 
                            1 as id, 'Alice' as name, 25 as age, 'IT' as department, 50000 as salary
                        UNION ALL
                        SELECT 
                            2 as id, 'Bob' as name, 30 as age, 'HR' as department, 45000 as salary
                        UNION ALL
                        SELECT 
                            3 as id, 'Charlie' as name, 35 as age, 'IT' as department, 60000 as salary
                        """
                    }
                },
                {
                    "name": "enrich_data",
                    "type": "enrich",
                    "depends_on": ["extract_data"],
                    "config": {
                        "enrichments": [
                            {
                                "column": "salary_grade",
                                "expression": "'High' if salary > 50000 else 'Low'"
                            },
                            {
                                "column": "full_info",
                                "expression": "name + ' (' + str(age) + ')'"
                            }
                        ]
                    }
                },
                {
                    "name": "filter_data",
                    "type": "filter",
                    "depends_on": ["enrich_data"],
                    "config": {
                        "condition": "department == 'IT'"
                    }
                },
                {
                    "name": "assert_data",
                    "type": "assert",
                    "depends_on": ["filter_data"],
                    "config": {
                        "assertions": [
                            {
                                "name": "check_record_count",
                                "condition": "len(df) >= 1",
                                "message": "应该至少有一条 IT 部门的记录"
                            },
                            {
                                "name": "check_department",
                                "condition": "all(df['department'] == 'IT')",
                                "message": "所有记录都应该是 IT 部门"
                            }
                        ]
                    }
                }
            ]
        }
    
    @pytest.mark.async_test
    async def test_simple_execution(self, engine, sample_simple_config):
        """测试简单配置的执行"""
        result = await engine.execute(sample_simple_config)
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'execution_id' in result
        assert 'results' in result
        assert 'simple_query' in result['results']
        
        # 验证查询结果
        query_result = result['results']['simple_query']
        assert len(query_result) == 1
        assert query_result[0]['id'] == 1
        assert query_result[0]['name'] == 'test'
    
    @pytest.mark.async_test
    async def test_complex_workflow_execution(self, engine, sample_complex_config):
        """测试复杂工作流的执行"""
        result = await engine.execute(sample_complex_config)
        
        assert result is not None
        assert result['status'] == 'success'
        assert 'execution_id' in result
        assert 'results' in result
        
        # 验证所有步骤都被执行
        expected_steps = ['extract_data', 'enrich_data', 'filter_data', 'assert_data']
        for step in expected_steps:
            assert step in result['results']
        
        # 验证最终筛选结果
        final_result = result['results']['filter_data']
        assert len(final_result) == 2  # 应该有两条 IT 部门的记录
        assert all(record['department'] == 'IT' for record in final_result)
        
        # 验证丰富化字段
        for record in final_result:
            assert 'salary_grade' in record
            assert 'full_info' in record
            assert record['full_info'].endswith(')')
    
    @pytest.mark.async_test
    async def test_execution_with_dependencies(self, engine):
        """测试带依赖关系的执行"""
        config = {
            "name": "dependency_test",
            "version": "1.0.0",
            "datasources": {
                "test_db": {
                    "type": "sqlite",
                    "connection": {"database": ":memory:"}
                }
            },
            "steps": [
                {
                    "name": "step_a",
                    "type": "query",
                    "datasource": "test_db",
                    "config": {"sql": "SELECT 'A' as step"}
                },
                {
                    "name": "step_b",
                    "type": "query", 
                    "datasource": "test_db",
                    "depends_on": ["step_a"],
                    "config": {"sql": "SELECT 'B' as step"}
                },
                {
                    "name": "step_c",
                    "type": "query",
                    "datasource": "test_db", 
                    "depends_on": ["step_a", "step_b"],
                    "config": {"sql": "SELECT 'C' as step"}
                }
            ]
        }
        
        result = await engine.execute(config)
        
        assert result['status'] == 'success'
        
        # 验证执行顺序记录
        execution_order = result.get('execution_order', [])
        assert len(execution_order) == 3
        
        # step_a 应该最先执行
        assert execution_order[0] == 'step_a'
        
        # step_b 应该在 step_a 之后执行
        step_a_index = execution_order.index('step_a')
        step_b_index = execution_order.index('step_b')
        assert step_b_index > step_a_index
        
        # step_c 应该最后执行
        step_c_index = execution_order.index('step_c')
        assert step_c_index > step_a_index
        assert step_c_index > step_b_index
    
    @pytest.mark.async_test
    async def test_execution_with_invalid_config(self, engine):
        """测试无效配置的执行"""
        invalid_config = {
            "name": "invalid_test",
            # 缺少 version 和 steps
        }
        
        with pytest.raises(ValidationError):
            await engine.execute(invalid_config)
    
    @pytest.mark.async_test
    async def test_execution_with_step_failure(self, engine):
        """测试步骤失败的处理"""
        config = {
            "name": "failure_test",
            "version": "1.0.0",
            "datasources": {
                "test_db": {
                    "type": "sqlite",
                    "connection": {"database": ":memory:"}
                }
            },
            "steps": [
                {
                    "name": "good_step",
                    "type": "query",
                    "datasource": "test_db",
                    "config": {"sql": "SELECT 1 as value"}
                },
                {
                    "name": "bad_step",
                    "type": "query",
                    "datasource": "test_db",
                    "depends_on": ["good_step"],
                    "config": {"sql": "SELECT * FROM nonexistent_table"}
                }
            ]
        }
        
        with pytest.raises(ExecutionError):
            await engine.execute(config)
    
    @pytest.mark.async_test 
    async def test_execution_with_caching(self, engine):
        """测试带缓存的执行"""
        config = {
            "name": "cache_test",
            "version": "1.0.0",
            "datasources": {
                "test_db": {
                    "type": "sqlite",
                    "connection": {"database": ":memory:"}
                }
            },
            "steps": [
                {
                    "name": "cached_step",
                    "type": "query",
                    "datasource": "test_db",
                    "config": {"sql": "SELECT datetime('now') as timestamp"},
                    "cache": {
                        "enabled": True,
                        "ttl": 3600
                    }
                }
            ]
        }
        
        # 第一次执行
        result1 = await engine.execute(config)
        first_timestamp = result1['results']['cached_step'][0]['timestamp']
        
        # 第二次执行（应该使用缓存）
        result2 = await engine.execute(config)
        second_timestamp = result2['results']['cached_step'][0]['timestamp']
        
        # 由于使用了缓存，时间戳应该相同
        assert first_timestamp == second_timestamp
    
    @pytest.mark.async_test
    async def test_parallel_execution(self, engine):
        """测试并行执行"""
        config = {
            "name": "parallel_test",
            "version": "1.0.0",
            "datasources": {
                "test_db": {
                    "type": "sqlite",
                    "connection": {"database": ":memory:"}
                }
            },
            "steps": [
                {
                    "name": "parallel_step_1",
                    "type": "query",
                    "datasource": "test_db",
                    "config": {"sql": "SELECT 1 as value"}
                },
                {
                    "name": "parallel_step_2", 
                    "type": "query",
                    "datasource": "test_db",
                    "config": {"sql": "SELECT 2 as value"}
                },
                {
                    "name": "parallel_step_3",
                    "type": "query",
                    "datasource": "test_db", 
                    "config": {"sql": "SELECT 3 as value"}
                },
                {
                    "name": "dependent_step",
                    "type": "union",
                    "depends_on": ["parallel_step_1", "parallel_step_2", "parallel_step_3"],
                    "config": {
                        "datasets": ["parallel_step_1", "parallel_step_2", "parallel_step_3"]
                    }
                }
            ],
            "options": {
                "parallel": True,
                "max_workers": 3
            }
        }
        
        result = await engine.execute(config)
        
        assert result['status'] == 'success'
        assert 'dependent_step' in result['results']
        
        # 验证合并结果
        union_result = result['results']['dependent_step']
        assert len(union_result) == 3
        values = [record['value'] for record in union_result]
        assert set(values) == {1, 2, 3}
    
    @pytest.mark.async_test
    async def test_memory_management(self, engine):
        """测试内存管理"""
        # 创建一个会产生较大数据集的配置
        config = {
            "name": "memory_test",
            "version": "1.0.0",
            "datasources": {
                "test_db": {
                    "type": "sqlite",
                    "connection": {"database": ":memory:"}
                }
            },
            "steps": [
                {
                    "name": "large_dataset",
                    "type": "query",
                    "datasource": "test_db",
                    "config": {
                        "sql": """
                        WITH RECURSIVE numbers(x) AS (
                            SELECT 1
                            UNION ALL
                            SELECT x+1 FROM numbers WHERE x < 1000
                        )
                        SELECT x as id, 'data_' || x as value FROM numbers
                        """
                    }
                }
            ]
        }
        
        result = await engine.execute(config)
        
        assert result['status'] == 'success'
        assert len(result['results']['large_dataset']) == 1000
    
    @pytest.mark.async_test
    async def test_timeout_handling(self, engine):
        """测试超时处理"""
        config = {
            "name": "timeout_test",
            "version": "1.0.0",
            "datasources": {
                "test_db": {
                    "type": "sqlite",
                    "connection": {"database": ":memory:"}
                }
            },
            "steps": [
                {
                    "name": "timeout_step",
                    "type": "query",
                    "datasource": "test_db",
                    "config": {"sql": "SELECT 1 as value"},
                    "timeout": 1  # 1秒超时
                }
            ],
            "options": {
                "timeout": 5  # 总超时5秒
            }
        }
        
        # 正常情况下应该成功执行
        result = await engine.execute(config)
        assert result['status'] == 'success'


class TestUQMParserIntegration:
    """UQM 解析器集成测试"""
    
    def test_parse_and_validate_complete_config(self, sample_uqm_config):
        """测试解析和验证完整配置"""
        parser = UQMParser()
        
        parsed_config = parser.parse(sample_uqm_config)
        
        assert parsed_config is not None
        assert parsed_config.name == sample_uqm_config['name']
        assert parsed_config.version == sample_uqm_config['version']
        assert len(parsed_config.steps) == len(sample_uqm_config['steps'])
        assert len(parsed_config.datasources) == len(sample_uqm_config['datasources'])
    
    def test_parse_with_validation_errors(self):
        """测试解析时的验证错误"""
        parser = UQMParser()
        
        invalid_config = {
            "name": "",  # 无效名称
            "version": "invalid",  # 无效版本
            "steps": []  # 空步骤
        }
        
        with pytest.raises(ValidationError):
            parser.parse(invalid_config)
    
    def test_parse_complex_expressions(self):
        """测试复杂表达式的解析"""
        parser = UQMParser()
        
        config = {
            "name": "expression_test",
            "version": "1.0.0",
            "steps": [
                {
                    "name": "enrich_step",
                    "type": "enrich",
                    "config": {
                        "enrichments": [
                            {
                                "column": "complex_calc",
                                "expression": "round((salary * 0.1) + (age * 100), 2)"
                            },
                            {
                                "column": "conditional",
                                "expression": "'Senior' if age > 30 else 'Junior'"
                            }
                        ]
                    }
                }
            ]
        }
        
        parsed_config = parser.parse(config)
        
        assert parsed_config is not None
        enrichments = parsed_config.steps[0].config['enrichments']
        assert len(enrichments) == 2
        
        # 验证表达式被正确解析
        assert enrichments[0]['expression'] == "round((salary * 0.1) + (age * 100), 2)"
        assert enrichments[1]['expression'] == "'Senior' if age > 30 else 'Junior'"


class TestCacheIntegration:
    """缓存集成测试"""
    
    @pytest.fixture
    async def cache_manager(self, test_settings):
        """创建缓存管理器"""
        cache_manager = CacheManager(test_settings)
        await cache_manager.initialize()
        yield cache_manager
        await cache_manager.cleanup()
    
    @pytest.mark.async_test
    async def test_cache_step_results(self, cache_manager):
        """测试缓存步骤结果"""
        step_name = "test_step"
        test_data = [{"id": 1, "name": "test"}]
        cache_key = f"step:{step_name}"
        
        # 缓存数据
        await cache_manager.set(cache_key, test_data, ttl=3600)
        
        # 获取缓存数据
        cached_data = await cache_manager.get(cache_key)
        
        assert cached_data == test_data
    
    @pytest.mark.async_test
    async def test_cache_invalidation(self, cache_manager):
        """测试缓存失效"""
        cache_key = "test_key"
        test_data = {"value": "test"}
        
        # 设置短TTL的缓存
        await cache_manager.set(cache_key, test_data, ttl=1)
        
        # 立即获取应该有数据
        cached_data = await cache_manager.get(cache_key)
        assert cached_data == test_data
        
        # 等待缓存过期
        await asyncio.sleep(1.1)
        
        # 现在应该没有数据
        expired_data = await cache_manager.get(cache_key)
        assert expired_data is None


class TestConnectorIntegration:
    """连接器集成测试"""
    
    @pytest.fixture
    async def connector_manager(self, test_settings):
        """创建连接器管理器"""
        manager = DataConnectorManager(test_settings)
        await manager.initialize()
        yield manager
        await manager.cleanup()
    
    @pytest.mark.async_test
    async def test_sqlite_connector_integration(self, connector_manager):
        """测试 SQLite 连接器集成"""
        # 注册 SQLite 数据源
        datasource_config = {
            "type": "sqlite",
            "connection": {
                "database": ":memory:"
            }
        }
        
        connector = await connector_manager.get_connector("test_sqlite", datasource_config)
        
        # 创建测试表并插入数据
        await connector.execute_query("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER
            )
        """)
        
        await connector.execute_query("""
            INSERT INTO users (name, age) VALUES 
            ('Alice', 25),
            ('Bob', 30),
            ('Charlie', 35)
        """)
        
        # 查询数据
        result = await connector.execute_query("SELECT * FROM users ORDER BY id")
        
        assert len(result) == 3
        assert result[0]['name'] == 'Alice'
        assert result[1]['name'] == 'Bob' 
        assert result[2]['name'] == 'Charlie'
    
    @pytest.mark.async_test
    async def test_connector_pool_management(self, connector_manager):
        """测试连接器池管理"""
        datasource_config = {
            "type": "sqlite",
            "connection": {
                "database": ":memory:"
            }
        }
        
        # 获取多个连接器实例
        connector1 = await connector_manager.get_connector("test_db", datasource_config)
        connector2 = await connector_manager.get_connector("test_db", datasource_config)
        
        # 应该返回相同的连接器实例（池化）
        assert connector1 is connector2
        
        # 验证连接器状态
        info1 = connector1.get_connection_info()
        info2 = connector2.get_connection_info()
        
        assert info1 == info2
        assert info1['type'] == 'sqlite'


class TestEndToEndWorkflows:
    """端到端工作流测试"""
    
    @pytest.mark.async_test
    async def test_data_pipeline_workflow(self, test_settings):
        """测试完整数据管道工作流"""
        engine = UQMEngine(test_settings)
        await engine.initialize()
        
        try:
            # 定义数据管道配置
            pipeline_config = {
                "name": "data_pipeline",
                "version": "1.0.0",
                "description": "完整的数据处理管道",
                "datasources": {
                    "source_db": {
                        "type": "sqlite",
                        "connection": {"database": ":memory:"}
                    }
                },
                "steps": [
                    # 步骤1: 数据提取
                    {
                        "name": "extract_raw_data",
                        "type": "query",
                        "datasource": "source_db",
                        "config": {
                            "sql": """
                            SELECT 
                                'sales' as type, 'Q1' as quarter, 1000 as amount, 'Product A' as product
                            UNION ALL
                            SELECT 
                                'sales' as type, 'Q2' as quarter, 1200 as amount, 'Product A' as product
                            UNION ALL
                            SELECT 
                                'sales' as type, 'Q1' as quarter, 800 as amount, 'Product B' as product
                            UNION ALL
                            SELECT 
                                'sales' as type, 'Q2' as quarter, 900 as amount, 'Product B' as product
                            """
                        }
                    },
                    
                    # 步骤2: 数据清洗和丰富化
                    {
                        "name": "clean_and_enrich",
                        "type": "enrich",
                        "depends_on": ["extract_raw_data"],
                        "config": {
                            "enrichments": [
                                {
                                    "column": "amount_category",
                                    "expression": "'High' if amount > 1000 else 'Low'"
                                },
                                {
                                    "column": "product_code",
                                    "expression": "'PA' if product == 'Product A' else 'PB'"
                                }
                            ]
                        }
                    },
                    
                    # 步骤3: 数据透视
                    {
                        "name": "pivot_by_quarter",
                        "type": "pivot",
                        "depends_on": ["clean_and_enrich"],
                        "config": {
                            "index_columns": ["product"],
                            "pivot_column": "quarter",
                            "value_columns": ["amount"],
                            "aggregation": "sum"
                        }
                    },
                    
                    # 步骤4: 数据验证
                    {
                        "name": "validate_results",
                        "type": "assert",
                        "depends_on": ["pivot_by_quarter"],
                        "config": {
                            "assertions": [
                                {
                                    "name": "check_product_count",
                                    "condition": "len(df) == 2",
                                    "message": "应该有两个产品"
                                },
                                {
                                    "name": "check_columns",
                                    "condition": "'Q1' in df.columns and 'Q2' in df.columns",
                                    "message": "应该包含Q1和Q2列"
                                }
                            ]
                        }
                    }
                ],
                "output": {
                    "format": "json"
                },
                "options": {
                    "parallel": False,
                    "validate_data": True,
                    "cache_enabled": True
                }
            }
            
            # 执行管道
            result = await engine.execute(pipeline_config)
            
            # 验证执行结果
            assert result['status'] == 'success'
            assert 'execution_id' in result
            assert len(result['results']) == 4
            
            # 验证最终透视结果
            pivot_result = result['results']['pivot_by_quarter']
            assert len(pivot_result) == 2  # 两个产品
            
            # 检查列结构
            if len(pivot_result) > 0:
                columns = set(pivot_result[0].keys())
                assert 'product' in columns
                assert any('Q1' in col or 'amount_Q1' in col for col in columns)
                assert any('Q2' in col or 'amount_Q2' in col for col in columns)
            
        finally:
            await engine.cleanup()
    
    @pytest.mark.async_test
    async def test_error_recovery_workflow(self, test_settings):
        """测试错误恢复工作流"""
        engine = UQMEngine(test_settings)
        await engine.initialize()
        
        try:
            # 包含故意错误的配置
            config_with_error = {
                "name": "error_recovery_test",
                "version": "1.0.0",
                "datasources": {
                    "test_db": {
                        "type": "sqlite",
                        "connection": {"database": ":memory:"}
                    }
                },
                "steps": [
                    {
                        "name": "good_step",
                        "type": "query",
                        "datasource": "test_db",
                        "config": {"sql": "SELECT 1 as value"}
                    },
                    {
                        "name": "error_step",
                        "type": "query",
                        "datasource": "test_db",
                        "config": {"sql": "SELECT * FROM non_existent_table"},
                        "retry": {
                            "enabled": True,
                            "max_attempts": 2,
                            "delay": 0.1
                        }
                    }
                ],
                "options": {
                    "fail_fast": False
                }
            }
            
            # 执行应该失败但记录错误信息
            with pytest.raises(ExecutionError) as exc_info:
                await engine.execute(config_with_error)
            
            # 验证错误信息包含重试信息
            error_details = str(exc_info.value)
            assert "error_step" in error_details
            
        finally:
            await engine.cleanup()
