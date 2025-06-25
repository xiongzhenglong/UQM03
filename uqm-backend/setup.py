"""
UQM Backend 安装配置
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README 文件
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取版本信息
version_file = this_directory / "src" / "__version__.py"
version_info = {}
if version_file.exists():
    exec(version_file.read_text(), version_info)
    version = version_info.get('__version__', '1.0.0')
else:
    version = '1.0.0'

# 读取依赖
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    requirements = [
        'fastapi>=0.104.0',
        'uvicorn[standard]>=0.24.0',
        'pydantic>=2.5.0',
        'pydantic-settings>=2.1.0',
        'sqlalchemy>=2.0.0',
        'alembic>=1.13.0',
        'asyncpg>=0.29.0',
        'aiomysql>=0.2.0',
        'aiosqlite>=0.19.0',
        'redis>=5.0.0',
        'aioredis>=2.0.0',
        'pandas>=2.1.0',
        'numpy>=1.24.0',
        'jsonschema>=4.20.0',
        'jinja2>=3.1.0',
        'python-multipart>=0.0.6',
        'python-jose[cryptography]>=3.3.0',
        'passlib[bcrypt]>=1.7.4',
        'aiofiles>=23.2.0',
        'loguru>=0.7.0',
        'prometheus-client>=0.19.0',
        'structlog>=23.2.0'
    ]

# 开发依赖
dev_requirements = [
    'pytest>=7.4.0',
    'pytest-asyncio>=0.21.0',
    'pytest-cov>=4.1.0',
    'pytest-mock>=3.12.0',
    'black>=23.10.0',
    'isort>=5.12.0',
    'flake8>=6.1.0',
    'mypy>=1.7.0',
    'pre-commit>=3.5.0',
    'bandit>=1.7.5',
    'safety>=2.3.0'
]

# 测试依赖
test_requirements = [
    'pytest>=7.4.0',
    'pytest-asyncio>=0.21.0',
    'pytest-cov>=4.1.0',
    'pytest-mock>=3.12.0',
    'httpx>=0.25.0',
    'factory-boy>=3.3.0',
    'faker>=20.1.0'
]

# 文档依赖
docs_requirements = [
    'mkdocs>=1.5.0',
    'mkdocs-material>=9.4.0',
    'mkdocstrings[python]>=0.24.0',
    'mkdocs-mermaid2-plugin>=1.1.0'
]

# 生产依赖
prod_requirements = [
    'gunicorn>=21.2.0',
    'setproctitle>=1.3.0'
]

setup(
    name="uqm-backend",
    version=version,
    author="UQM Team",
    author_email="team@uqm.com",
    description="统一查询模型（UQM）后端执行引擎",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/uqm/uqm-backend",
    project_urls={
        "Bug Tracker": "https://github.com/uqm/uqm-backend/issues",
        "Documentation": "https://uqm-backend.readthedocs.io/",
        "Source Code": "https://github.com/uqm/uqm-backend",
    },
    packages=find_packages(include=['src', 'src.*']),
    package_dir={'': '.'},
    include_package_data=True,
    package_data={
        'src': ['schema/*.json', 'templates/*.html', 'static/*'],
        '': ['*.md', '*.txt', '*.yml', '*.yaml'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Framework :: FastAPI",
        "Framework :: Pydantic",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
        'test': test_requirements,
        'docs': docs_requirements,
        'prod': prod_requirements,
        'all': dev_requirements + test_requirements + docs_requirements + prod_requirements,
    },
    entry_points={
        'console_scripts': [
            'uqm-server=src.main:main',
            'uqm-cli=src.cli:main',
        ],
    },
    keywords=[
        'uqm', 'unified-query-model', 'data-processing', 'etl', 'sql',
        'fastapi', 'async', 'pandas', 'database', 'query-engine'
    ],
    license="MIT",
    zip_safe=False,
    platforms=['any'],
    
    # 元数据
    maintainer="UQM Team",
    maintainer_email="team@uqm.com",
    
    # 依赖约束
    python_requires=">=3.9,<4.0",
    
    # 安全配置
    options={
        'bdist_wheel': {
            'universal': False,
        },
    },
)

# 安装后脚本
def post_install():
    """安装后执行的脚本"""
    print("UQM Backend 安装成功!")
    print("运行 'uqm-server --help' 查看使用说明")
    print("访问 http://localhost:8000/docs 查看 API 文档")

if __name__ == "__main__":
    import sys
    if 'install' in sys.argv:
        post_install()
