"""
测试配置和公共工具
"""

import os
import sys
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import Settings
from src.utils.logging import setup_logging


# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///:memory:"
TEST_REDIS_URL = "redis://localhost:6379/15"

# 测试环境变量
TEST_ENV_VARS = {
    "DATABASE_URL": TEST_DATABASE_URL,
    "REDIS_URL": TEST_REDIS_URL,
    "LOG_LEVEL": "DEBUG",
    "TESTING": "true",
    "CACHE_BACKEND": "memory",
}


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环供测试使用"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """测试设置"""
    with patch.dict(os.environ, TEST_ENV_VARS):
        settings = Settings()
        yield settings


@pytest.fixture
def temp_dir():
    """临时目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_uqm_config():
    """示例 UQM 配置"""
    return {
        "name": "test_uqm",
        "version": "1.0.0",
        "description": "测试用 UQM 配置",
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
                "name": "query_step",
                "type": "query",
                "datasource": "test_db",
                "config": {
                    "sql": "SELECT 1 as test_column"
                }
            },
            {
                "name": "enrich_step",
                "type": "enrich",
                "depends_on": ["query_step"],
                "config": {
                    "enrichments": [
                        {
                            "column": "computed_column",
                            "expression": "test_column * 2"
                        }
                    ]
                }
            }
        ],
        "output": {
            "format": "json"
        }
    }


@pytest.fixture
def sample_dataframe():
    """示例 DataFrame"""
    import pandas as pd
    
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'salary': [50000, 60000, 70000, 55000, 65000],
        'department': ['IT', 'HR', 'IT', 'Finance', 'HR']
    })


@pytest.fixture
def mock_database():
    """模拟数据库连接"""
    db_mock = Mock()
    db_mock.execute.return_value = Mock()
    db_mock.fetchall.return_value = [
        {'id': 1, 'name': 'Test User', 'email': 'test@example.com'}
    ]
    return db_mock


@pytest.fixture
def mock_redis():
    """模拟 Redis 连接"""
    redis_mock = Mock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = 1
    redis_mock.exists.return_value = False
    return redis_mock


class MockDataConnector:
    """模拟数据连接器"""
    
    def __init__(self, data=None):
        self.data = data or []
        self.connected = False
    
    async def connect(self):
        self.connected = True
    
    async def disconnect(self):
        self.connected = False
    
    async def execute_query(self, sql: str, params: Dict[str, Any] = None):
        return self.data
    
    def get_connection_info(self):
        return {
            "type": "mock",
            "connected": self.connected
        }


class AsyncMock:
    """异步方法的模拟对象"""
    
    def __init__(self, return_value=None):
        self._return_value = return_value
        self.call_count = 0
        self.call_args_list = []
    
    async def __call__(self, *args, **kwargs):
        self.call_count += 1
        self.call_args_list.append((args, kwargs))
        return self._return_value


def create_test_file(content: str, file_path: str = None, temp_dir: str = None) -> str:
    """创建测试文件"""
    if file_path is None:
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, "test_file.txt")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path


def assert_dataframe_equal(df1, df2, check_dtype=True, check_index=True):
    """断言两个 DataFrame 相等"""
    import pandas as pd
    import pandas.testing as pdt
    
    pdt.assert_frame_equal(df1, df2, check_dtype=check_dtype, check_index=check_index)


def assert_dict_subset(subset: Dict[str, Any], superset: Dict[str, Any]):
    """断言字典是另一个字典的子集"""
    for key, value in subset.items():
        assert key in superset, f"键 '{key}' 不在目标字典中"
        assert superset[key] == value, f"键 '{key}' 的值不匹配: 期望 {value}, 实际 {superset[key]}"


class TestDataHelper:
    """测试数据辅助类"""
    
    @staticmethod
    def create_sample_csv(file_path: str, rows: int = 100):
        """创建示例 CSV 文件"""
        import pandas as pd
        import random
        
        data = {
            'id': range(1, rows + 1),
            'name': [f'User_{i}' for i in range(1, rows + 1)],
            'age': [random.randint(18, 80) for _ in range(rows)],
            'salary': [random.randint(30000, 100000) for _ in range(rows)],
            'department': [random.choice(['IT', 'HR', 'Finance', 'Marketing']) for _ in range(rows)]
        }
        
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        return file_path
    
    @staticmethod
    def create_sample_json(file_path: str, records: int = 50):
        """创建示例 JSON 文件"""
        import json
        import random
        
        data = []
        for i in range(1, records + 1):
            record = {
                'id': i,
                'name': f'Product_{i}',
                'price': round(random.uniform(10.0, 1000.0), 2),
                'category': random.choice(['Electronics', 'Clothing', 'Books', 'Home']),
                'in_stock': random.choice([True, False])
            }
            data.append(record)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return file_path


# 全局测试配置
def setup_test_logging():
    """设置测试日志"""
    setup_logging(level="DEBUG", format_type="simple")


# 自动设置测试环境
def pytest_configure(config):
    """pytest 配置钩子"""
    # 设置测试环境变量
    for key, value in TEST_ENV_VARS.items():
        os.environ.setdefault(key, value)
    
    # 设置测试日志
    setup_test_logging()


def pytest_sessionstart(session):
    """测试会话开始时的钩子"""
    print("开始运行 UQM Backend 测试套件...")


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时的钩子"""
    print(f"UQM Backend 测试套件完成，退出状态: {exitstatus}")


# 标记定义
pytest_plugins = []

# 自定义标记
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
pytest.mark.async_test = pytest.mark.asyncio
