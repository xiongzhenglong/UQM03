```sql
-- 数据库准备
-- CREATE DATABASE IF NOT EXISTS uqm_ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE uqm_ecommerce_db;

-- ----------------------------
-- 1. 部门表 (departments)
-- 描述：存储公司的所有部门信息。
-- ----------------------------
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '部门名称',
    location VARCHAR(100) COMMENT '办公地点',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT='公司部门表';

-- ----------------------------
-- 2. 员工表 (employees)
-- 描述：存储公司员工信息，包含上下级汇报关系。
-- ----------------------------
CREATE TABLE IF NOT EXISTS employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL COMMENT '名',
    last_name VARCHAR(50) NOT NULL COMMENT '姓',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    phone_number VARCHAR(20) COMMENT '电话',
    hire_date DATE NOT NULL COMMENT '入职日期',
    job_title VARCHAR(100) NOT NULL COMMENT '职位',
    salary DECIMAL(10, 2) NOT NULL COMMENT '薪水',
    department_id INT COMMENT '所属部门ID',
    manager_id INT COMMENT '直属经理ID',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否在职',
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL
) COMMENT='员工信息表';

-- ----------------------------
-- 3. 客户表 (customers)
-- 描述：存储客户的基本信息。
-- ----------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL COMMENT '客户姓名',
    email VARCHAR(150) UNIQUE NOT NULL COMMENT '客户邮箱',
    country VARCHAR(50) NOT NULL COMMENT '所在国家',
    city VARCHAR(50) COMMENT '所在城市',
    registration_date DATE NOT NULL COMMENT '注册日期',
    customer_segment ENUM('VIP', '普通', '新客户') DEFAULT '新客户' COMMENT '客户分层'
) COMMENT='客户信息表';

-- ----------------------------
-- 4. 供应商表 (suppliers)
-- 描述：存储产品供应商信息。
-- ----------------------------
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL COMMENT '供应商名称',
    contact_person VARCHAR(100) COMMENT '联系人',
    phone VARCHAR(20) COMMENT '联系电话',
    country VARCHAR(50) NOT NULL COMMENT '所在国家'
) COMMENT='供应商信息表';

-- ----------------------------
-- 5. 产品表 (products)
-- 描述：存储商品信息。
-- ----------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL COMMENT '产品名称',
    category VARCHAR(100) NOT NULL COMMENT '产品类别',
    unit_price DECIMAL(10, 2) NOT NULL COMMENT '单价',
    supplier_id INT COMMENT '供应商ID',
    discontinued BOOLEAN DEFAULT FALSE COMMENT '是否已下架',
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
) COMMENT='产品目录表';

-- ----------------------------
-- 6. 订单主表 (orders)
-- 描述：存储客户订单的概要信息。
-- ----------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL COMMENT '客户ID',
    employee_id INT COMMENT '负责员工ID',
    order_date DATETIME NOT NULL COMMENT '下单日期',
    status ENUM('待处理', '处理中', '已发货', '已完成', '已取消') NOT NULL COMMENT '订单状态',
    shipping_fee DECIMAL(8, 2) DEFAULT 0.00 COMMENT '运费',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
) COMMENT='客户订单主表';

-- ----------------------------
-- 7. 订单详情表 (order_items)
-- 描述：存储每个订单中包含的具体商品项。
-- ----------------------------
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL COMMENT '订单ID',
    product_id INT NOT NULL COMMENT '产品ID',
    quantity INT NOT NULL COMMENT '数量',
    unit_price DECIMAL(10, 2) NOT NULL COMMENT '成交单价',
    discount DECIMAL(4, 2) DEFAULT 0.00 COMMENT '折扣率',
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
) COMMENT='订单商品详情表';

-- ----------------------------
-- 8. 仓库表 (warehouses)
-- 描述：存储仓库信息。
-- ----------------------------
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_name VARCHAR(100) NOT NULL COMMENT '仓库名称',
    location VARCHAR(100) NOT NULL COMMENT '仓库位置'
) COMMENT='仓库信息表';

-- ----------------------------
-- 9. 库存表 (inventory)
-- 描述：存储每个产品在不同仓库的库存水平。
-- ----------------------------
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL COMMENT '产品ID',
    warehouse_id INT NOT NULL COMMENT '仓库ID',
    quantity_on_hand INT NOT NULL COMMENT '现有库存量',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (product_id, warehouse_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
) COMMENT='产品库存表';
```

您好！您提供的这套数据库结构非常全面和专业，确实能支持非常多样的业务查询场景。基于这些表，我为您构思了以下一些常见的查询与分析场景，由浅入深，希望能给您带来启发：

### **一、 人力资源与部门管理 (HR & Department)**

这类查询主要围绕 `employees` 和 `departments` 表。

* **基础查询**:
    * 查询“信息技术部”的所有在职员工列表。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "信息技术部在职员工列表",
        "description": "查询信息技术部所有在职员工的详细信息"
        },
        "steps": [
        {
            "name": "get_it_active_employees",
            "type": "query",
            "config": {
            "data_source": "employees",
            "dimensions": [
                "employees.employee_id",
                "employees.first_name",
                "employees.last_name",
                "employees.email",
                "employees.phone_number",
                "employees.hire_date",
                "employees.job_title",
                "employees.salary",
                "departments.name AS department_name",
                "departments.location AS department_location"
            ],
            "joins": [
                {
                "type": "INNER",
                "table": "departments",
                "on": {
                    "left": "employees.department_id",
                    "right": "departments.department_id",
                    "operator": "="
                }
                }
            ],
            "filters": [
                {
                "field": "departments.name",
                "operator": "=",
                "value": "信息技术部"
                },
                {
                "field": "employees.is_active",
                "operator": "=",
                "value": true
                }
            ]
            }
        }
        ],
        "output": "get_it_active_employees"
    },
    "parameters": {},
    "options": {}
    }
    ------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "employee_id": 1,
                "first_name": "伟",
                "last_name": "张",
                "email": "zhang.wei@example.com",
                "phone_number": "13800138001",
                "hire_date": "2022-01-10",
                "job_title": "IT总监",
                "salary": "35000.00",
                "department_name": "信息技术部",
                "department_location": "上海"
            },
            {
                "employee_id": 3,
                "first_name": "强",
                "last_name": "李",
                "email": "li.qiang@example.com",
                "phone_number": "13800138003",
                "hire_date": "2022-02-20",
                "job_title": "软件工程师",
                "salary": "18000.00",
                "department_name": "信息技术部",
                "department_location": "上海"
            },
            {
                "employee_id": 10,
                "first_name": "Emily",
                "last_name": "Jones",
                "email": "emily.jones@example.com",
                "phone_number": "13700137009",
                "hire_date": "2024-04-08",
                "job_title": "高级软件工程师",
                "salary": "22000.00",
                "department_name": "信息技术部",
                "department_location": "上海"
            }
        ],
        "metadata": {
            "name": "信息技术部在职员工列表",
            "description": "查询信息技术部所有在职员工的详细信息",
            "version": "1.0",
            "author": "",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.05601000785827637,
            "row_count": 3,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "get_it_active_employees",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 3,
                "execution_time": 0.05601000785827637,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 查找所有在2023年之后入职的员工。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "2023年后入职员工",
        "description": "查询所有在2023年之后入职的员工列表"
        },
        "steps": [
        {
            "name": "get_employees_hired_after_2023",
            "type": "query",
            "config": {
            "data_source": "employees",
            "dimensions": [
                "employee_id",
                "first_name",
                "last_name",
                "email",
                "hire_date",
                "job_title",
                "salary"
            ],
            "filters": [
                {
                "field": "hire_date",
                "operator": ">",
                "value": "2023-12-31"
                }
            ]
            }
        }
        ],
        "output": "get_employees_hired_after_2023"
    },
    "parameters": {},
    "options": {}
    }
    --------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "employee_id": 9,
                "first_name": "Yuki",
                "last_name": "Tanaka",
                "email": "yuki.tanaka@example.com",
                "hire_date": "2024-02-19",
                "job_title": "市场专员",
                "salary": "14000.00"
            },
            {
                "employee_id": 10,
                "first_name": "Emily",
                "last_name": "Jones",
                "email": "emily.jones@example.com",
                "hire_date": "2024-04-08",
                "job_title": "高级软件工程师",
                "salary": "22000.00"
            },
            {
                "employee_id": 11,
                "first_name": "Carlos",
                "last_name": "Garcia",
                "email": "carlos.garcia@example.com",
                "hire_date": "2025-01-15",
                "job_title": "运营经理",
                "salary": "31000.00"
            },
            {
                "employee_id": 12,
                "first_name": "Sophia",
                "last_name": "Müller",
                "email": "sophia.muller@example.com",
                "hire_date": "2025-03-20",
                "job_title": "销售助理",
                "salary": "16000.00"
            }
        ],
        "metadata": {
            "name": "2023年后入职员工",
            "description": "查询所有在2023年之后入职的员工列表",
            "version": "1.0",
            "author": "",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.04599642753601074,
            "row_count": 4,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "get_employees_hired_after_2023",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 4,
                "execution_time": 0.04599642753601074,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 获取某位员工（如：张伟）的详细信息，包括他所在的部门名称和办公地点。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "查询特定员工详情",
        "description": "获取张伟的详细信息，包括他所在的部门名称和办公地点"
        },
        "steps": [
        {
            "name": "get_zhang_wei_details",
            "type": "query",
            "config": {
            "data_source": "employees",
            "dimensions": [
                "employees.employee_id",
                "employees.first_name",
                "employees.last_name",
                "employees.email",
                "employees.job_title",
                "employees.salary",
                "departments.name AS department_name",
                "departments.location AS department_location"
            ],
            "joins": [
                {
                "type": "LEFT",
                "table": "departments",
                "on": {
                    "left": "employees.department_id",
                    "right": "departments.department_id",
                    "operator": "="
                }
                }
            ],
            "filters": [
                {
                "field": "employees.first_name",
                "operator": "=",
                "value": "张"
                },
                {
                "field": "employees.last_name",
                "operator": "=",
                "value": "伟"
                }
            ]
            }
        }
        ],
        "output": "get_zhang_wei_details"
    },
    "parameters": {},
    "options": {}
    }
    ---------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "employee_id": 1,
                "first_name": "张",
                "last_name": "伟",
                "email": "zhang.wei@example.com",
                "job_title": "IT总监",
                "salary": "35000.00",
                "department_name": "信息技术部",
                "department_location": "上海"
            }
        ],
        "metadata": {
            "name": "查询特定员工详情",
            "description": "获取张伟的详细信息，包括他所在的部门名称和办公地点",
            "version": "1.0",
            "author": "",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.05763673782348633,
            "row_count": 1,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "get_zhang_wei_details",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 1,
                "execution_time": 0.05663704872131348,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

* **聚合分析**:
    * 统计每个部门的员工人数，并按人数降序排列。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "部门员工人数统计",
        "description": "统计每个部门的员工人数，并按人数降序排列"
        },
        "steps": [
        {
            "name": "department_employee_count",
            "type": "query",
            "config": {
            "data_source": "employees",
            "dimensions": [
                "departments.name AS department_name"
            ],
            "metrics": [
                {
                "name": "employees.employee_id",
                "aggregation": "COUNT",
                "alias": "employee_count"
                }
            ],
            "joins": [
                {
                "type": "INNER",
                "table": "departments",
                "on": {
                    "left": "employees.department_id",
                    "right": "departments.department_id",
                    "operator": "="
                }
                }
            ],
            "group_by": [
                "departments.name"
            ],
            "order_by": [
                {
                "field": "employee_count",
                "direction": "DESC"
                }
            ]
            }
        }
        ],
        "output": "department_employee_count"
    },
    "parameters": {},
    "options": {}
    }
    ----------------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "department_name": "信息技术部",
                "employee_count": 3
            },
            {
                "department_name": "人力资源部",
                "employee_count": 2
            },
            {
                "department_name": "销售部",
                "employee_count": 2
            },
            {
                "department_name": "欧洲销售部",
                "employee_count": 2
            },
            {
                "department_name": "研发中心",
                "employee_count": 1
            },
            {
                "department_name": "财务部",
                "employee_count": 1
            },
            {
                "department_name": "市场营销部",
                "employee_count": 1
            }
        ],
        "metadata": {
            "name": "部门员工人数统计",
            "description": "统计每个部门的员工人数，并按人数降序排列",
            "version": "1.0",
            "author": "",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.024122238159179688,
            "row_count": 7,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "department_employee_count",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 7,
                "execution_time": 0.024122238159179688,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 计算每个部门的平均薪资、最高薪资和最低薪资。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "部门薪资统计",
        "description": "计算每个部门的平均薪资、最高薪资和最低薪资"
        },
        "steps": [
        {
            "name": "department_salary_stats",
            "type": "query",
            "config": {
            "data_source": "employees",
            "dimensions": [
                "departments.name AS department_name"
            ],
            "metrics": [
                {
                "name": "employees.salary",
                "aggregation": "AVG",
                "alias": "avg_salary"
                },
                {
                "name": "employees.salary",
                "aggregation": "MAX",
                "alias": "max_salary"
                },
                {
                "name": "employees.salary",
                "aggregation": "MIN",
                "alias": "min_salary"
                }
            ],
            "joins": [
                {
                "type": "INNER",
                "table": "departments",
                "on": {
                    "left": "employees.department_id",
                    "right": "departments.department_id",
                    "operator": "="
                }
                }
            ],
            "group_by": [
                "departments.name"
            ]
            }
        }
        ],
        "output": "department_salary_stats"
    },
    "parameters": {},
    "options": {}
    }
    ----------------------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "department_name": "信息技术部",
                "avg_salary": "25000.000000",
                "max_salary": "35000.00",
                "min_salary": "18000.00"
            },
            {
                "department_name": "人力资源部",
                "avg_salary": "18500.000000",
                "max_salary": "25000.00",
                "min_salary": "12000.00"
            },
            {
                "department_name": "销售部",
                "avg_salary": "26500.000000",
                "max_salary": "38000.00",
                "min_salary": "15000.00"
            },
            {
                "department_name": "财务部",
                "avg_salary": "28000.000000",
                "max_salary": "28000.00",
                "min_salary": "28000.00"
            },
            {
                "department_name": "欧洲销售部",
                "avg_salary": "29000.000000",
                "max_salary": "42000.00",
                "min_salary": "16000.00"
            },
            {
                "department_name": "市场营销部",
                "avg_salary": "14000.000000",
                "max_salary": "14000.00",
                "min_salary": "14000.00"
            },
            {
                "department_name": "研发中心",
                "avg_salary": "31000.000000",
                "max_salary": "31000.00",
                "min_salary": "31000.00"
            }
        ],
        "metadata": {
            "name": "部门薪资统计",
            "description": "计算每个部门的平均薪资、最高薪资和最低薪资",
            "version": "1.0",
            "author": "",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.05674409866333008,
            "row_count": 7,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "department_salary_stats",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 7,
                "execution_time": 0.05674409866333008,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 按年份统计每年入职的员工数量。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "按年份入职员工数量统计",
        "description": "按年份统计每年入职的员工数量"
        },
        "steps": [
        {
            "name": "employees_hired_by_year",
            "type": "query",
            "config": {
            "data_source": "employees",
            "dimensions": [
                {
                "expression": "YEAR(hire_date)",
                "alias": "hire_year"
                }
            ],
            "metrics": [
                {
                "name": "employee_id",
                "aggregation": "COUNT",
                "alias": "employee_count"
                }
            ],
            "group_by": [
                "hire_year"
            ],
            "order_by": [
                {
                "field": "hire_year",
                "direction": "ASC"
                }
            ]
            }
        }
        ],
        "output": "employees_hired_by_year"
    },
    "parameters": {},
    "options": {}
    }
    --------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "hire_year": 2020,
                "employee_count": 1
            },
            {
                "hire_year": 2021,
                "employee_count": 1
            },
            {
                "hire_year": 2022,
                "employee_count": 4
            },
            {
                "hire_year": 2023,
                "employee_count": 2
            },
            {
                "hire_year": 2024,
                "employee_count": 2
            },
            {
                "hire_year": 2025,
                "employee_count": 2
            }
        ],
        "metadata": {
            "name": "按年份入职员工数量统计",
            "description": "按年份统计每年入职的员工数量",
            "version": "1.0",
            "author": "",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.037999629974365234,
            "row_count": 6,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "employees_hired_by_year",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 6,
                "execution_time": 0.037999629974365234,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

* **关联与层级查询**:
    * 查询所有员工及其直属经理的姓名（需要在 `employees` 表上进行自连接）。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "员工及其直属经理姓名查询",
        "description": "查询所有员工的姓名及其直属经理的姓名，即使员工没有经理也会被列出。"
        },
        "steps": [
        {
            "name": "employees_and_managers",
            "type": "query",
            "config": {
            "data_source": "employees",
            "dimensions": [
                {
                "expression": "CONCAT(employees.first_name, ' ', employees.last_name)",
                "alias": "employee_full_name"
                },
                {
                "expression": "CONCAT(managers.first_name, ' ', managers.last_name)",
                "alias": "manager_full_name"
                }
            ],
            "joins": [
                {
                "type": "LEFT",
                "table": "employees AS managers",
                "on": {
                    "left": "employees.manager_id",
                    "right": "managers.employee_id",
                    "operator": "="
                }
                }
            ],
            "order_by": [
                {
                "field": "employee_full_name",
                "direction": "ASC"
                }
            ]
            }
        }
        ],
        "output": "employees_and_managers"
    },
    "parameters": {},
    "options": {}
    }
    --------------------------------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "employee_full_name": "Carlos Garcia",
                "manager_full_name": null
            },
            {
                "employee_full_name": "Emily Jones",
                "manager_full_name": "张 伟"
            },
            {
                "employee_full_name": "Ming Li",
                "manager_full_name": null
            },
            {
                "employee_full_name": "Peter Schmidt",
                "manager_full_name": "陈 军"
            },
            {
                "employee_full_name": "Sophia Müller",
                "manager_full_name": "Peter Schmidt"
            },
            {
                "employee_full_name": "Yuki Tanaka",
                "manager_full_name": null
            },
            {
                "employee_full_name": "刘 娜",
                "manager_full_name": "王 芳"
            },
            {
                "employee_full_name": "张 伟",
                "manager_full_name": null
            },
            {
                "employee_full_name": "李 强",
                "manager_full_name": "张 伟"
            },
            {
                "employee_full_name": "杨 静",
                "manager_full_name": "陈 军"
            },
            {
                "employee_full_name": "王 芳",
                "manager_full_name": null
            },
            {
                "employee_full_name": "陈 军",
                "manager_full_name": null
            }
        ],
        "metadata": {
            "name": "员工及其直属经理姓名查询",
            "description": "查询所有员工的姓名及其直属经理的姓名，即使员工没有经理也会被列出。",
            "version": "1.0",
            "author": "",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.05534505844116211,
            "row_count": 12,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "employees_and_managers",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 12,
                "execution_time": 0.05534505844116211,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 列出所有没有分配部门的员工。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "未分配部门员工列表",
        "description": "列出所有没有分配部门的员工的详细信息。"
        },
        "steps": [
        {
            "name": "employees_without_department",
            "type": "query",
            "config": {
            "data_source": "employees",
            "dimensions": [
                "employee_id",
                "first_name",
                "last_name",
                "email",
                "job_title",
                "salary",
                "hire_date"
            ],
            "filters": [
                {
                "field": "department_id",
                "operator": "IS NULL"
                }
            ],
            "order_by": [
                {
                "field": "employee_id",
                "direction": "ASC"
                }
            ]
            }
        }
        ],
        "output": "employees_without_department"
    },
    "parameters": {},
    "options": {}
    }
    --------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [],
        "metadata": {
            "name": "未分配部门员工列表",
            "description": "列出所有没有分配部门的员工的详细信息。",
            "version": "1.0",
            "author": "",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.0503692626953125,
            "row_count": 0,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "employees_without_department",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 0,
                "execution_time": 0.0503692626953125,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

### **二、 销售与订单分析 (Sales & Order)**

这类查询是电商系统的核心，主要涉及 `orders`, `order_items`, `products`, `customers` 等表。

* **基础查询**:
    * 查询某个特定订单（如 order_id = 1）的所有商品项及其详情。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "特定订单商品详情查询",
        "description": "查询指定订单ID下所有商品项的详细信息，包括商品名称、类别、数量、单价、折扣及计算后的总价。",
        "version": "1.0",
        "author": "UQM Team"
        },
        "steps": [
        {
            "name": "order_items_details",
            "type": "query",
            "config": {
            "data_source": "order_items",
            "dimensions": [
                "order_items.order_item_id",
                "order_items.order_id",
                "order_items.product_id",
                "order_items.quantity",
                {
                "expression": "order_items.unit_price",
                "alias": "item_sale_price"
                },
                "order_items.discount",
                "products.product_name",
                "products.category",
                {
                "expression": "(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
                "alias": "total_item_price"
                }
            ],
            "joins": [
                {
                "type": "INNER",
                "table": "products",
                "on": {
                    "left": "order_items.product_id",
                    "right": "products.product_id",
                    "operator": "="
                }
                }
            ],
            "filters": [
                {
                "field": "order_items.order_id",
                "operator": "=",
                "value": "$orderId"
                }
            ],
            "order_by": [
                {
                "field": "order_items.order_item_id",
                "direction": "ASC"
                }
            ]
            }
        }
        ],
        "output": "order_items_details"
    },
    "parameters": {
        "orderId": 1
    },
    "options": {
        
    }
    }
    -----------------------------------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "order_item_id": 1,
                "order_id": 1,
                "product_id": 1,
                "quantity": 1,
                "item_sale_price": "499.00",
                "discount": "0.05",
                "product_name": "超高速SSD 1TB",
                "category": "电子产品",
                "total_item_price": "474.0500"
            },
            {
                "order_item_id": 2,
                "order_id": 1,
                "product_id": 2,
                "quantity": 1,
                "item_sale_price": "380.00",
                "discount": "0.05",
                "product_name": "机械键盘",
                "category": "电子产品",
                "total_item_price": "361.0000"
            }
        ],
        "metadata": {
            "name": "特定订单商品详情查询",
            "description": "查询指定订单ID下所有商品项的详细信息，包括商品名称、类别、数量、单价、折扣及计算后的总价。",
            "version": "1.0",
            "author": "UQM Team",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.02700042724609375,
            "row_count": 2,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "order_items_details",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 2,
                "execution_time": 0.02700042724609375,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 查找所有状态为“待处理”的订单，以便进行后续操作。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "待处理订单列表",
        "description": "列出所有状态为'待处理'的订单的详细信息。",
        "version": "1.0",
        "author": "UQM Team"
        },
        "steps": [
        {
            "name": "pending_orders",
            "type": "query",
            "config": {
            "data_source": "orders",
            "dimensions": [
                "order_id",
                "customer_id",
                "employee_id",
                "order_date",
                "status",
                "shipping_fee"
            ],
            "filters": [
                {
                "field": "status",
                "operator": "=",
                "value": "待处理"
                }
            ],
            "order_by": [
                {
                "field": "order_date",
                "direction": "ASC"
                }
            ]
            }
        }
        ],
        "output": "pending_orders"
    },
    "parameters": {},
    "options": {
        "cache_enabled": true
    }
    }
    -------------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "order_id": 4,
                "customer_id": 1,
                "employee_id": 6,
                "order_date": "2024-03-10T09:00:00",
                "status": "待处理",
                "shipping_fee": "10.00"
            }
        ],
        "metadata": {
            "name": "待处理订单列表",
            "description": "列出所有状态为'待处理'的订单的详细信息。",
            "version": "1.0",
            "author": "UQM Team",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.044182538986206055,
            "row_count": 1,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "pending_orders",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 1,
                "execution_time": 0.043177127838134766,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

* **销售业绩分析**:
    * 统计上个月（或指定时间段内）的总销售额（`order_items.quantity * order_items.unit_price`）。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "指定时间段总销售额",
        "description": "计算指定时间段内所有订单的总销售额（含折扣）。",
        "version": "1.0",
        "author": "UQM Team"
        },
        "steps": [
        {
            "name": "total_sales_calculation",
            "type": "query",
            "config": {
            "data_source": "order_items",
            "dimensions": [],
            "metrics": [
                {
                "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
                "alias": "total_sales_amount"
                }
            ],
            "joins": [
                {
                "type": "INNER",
                "table": "orders",
                "on": {
                    "left": "order_items.order_id",
                    "right": "orders.order_id",
                    "operator": "="
                }
                }
            ],
            "filters": [
                {
                "field": "orders.order_date",
                "operator": ">=",
                "value": "$startDate"
                },
                {
                "field": "orders.order_date",
                "operator": "<=",
                "value": "$endDate"
                }
            ]
            }
        }
        ],
        "output": "total_sales_calculation"
    },
    "parameters": {
        "startDate": "2024-11-01 00:00:00",
        "endDate": "2024-11-30 23:59:59"
    },
    "options": {
    
    }
    }
    ----------------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "total_sales_amount": "1519.0500"
            }
        ],
        "metadata": {
            "name": "指定时间段总销售额",
            "description": "计算指定时间段内所有订单的总销售额（含折扣）。",
            "version": "1.0",
            "author": "UQM Team",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.03469657897949219,
            "row_count": 1,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "total_sales_calculation",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 1,
                "execution_time": 0.03469657897949219,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 查询销量最高（或销售额最高）的 Top 10 商品。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "Top10商品按销售额",
        "description": "查询销售额最高的Top 10商品。",
        "version": "1.0",
        "author": "UQM Team"
        },
        "steps": [
        {
            "name": "top_products_by_sales_amount",
            "type": "query",
            "config": {
            "data_source": "order_items",
            "dimensions": [
                "products.product_name"
            ],
            "metrics": [
                {
                "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
                "alias": "total_sales_amount"
                }
            ],
            "joins": [
                {
                "type": "INNER",
                "table": "products",
                "on": {
                    "left": "order_items.product_id",
                    "right": "products.product_id",
                    "operator": "="
                }
                }
            ],
            "group_by": [
                "products.product_name"
            ],
            "order_by": [
                {
                "field": "total_sales_amount",
                "direction": "DESC"
                }
            ],
            "limit": 10
            }
        }
        ],
        "output": "top_products_by_sales_amount"
    },
    "parameters": {},
    "options": {
        "cache_enabled": true
    }
    }
    -----------------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "product_name": "AI智能音箱",
                "total_sales_amount": "1677.2000"
            },
            {
                "product_name": "智能升降学习桌",
                "total_sales_amount": "1519.0500"
            },
            {
                "product_name": "蓝牙降噪耳机",
                "total_sales_amount": "1104.1500"
            },
            {
                "product_name": "《SQL从入门到大神》",
                "total_sales_amount": "1032.0000"
            },
            {
                "product_name": "超高速SSD 1TB",
                "total_sales_amount": "973.0500"
            },
            {
                "product_name": "日式和风床品四件套",
                "total_sales_amount": "799.0000"
            },
            {
                "product_name": "潮流印花T恤",
                "total_sales_amount": "748.2000"
            },
            {
                "product_name": "机械键盘",
                "total_sales_amount": "741.0000"
            },
            {
                "product_name": "高精度光学鼠标",
                "total_sales_amount": "725.2000"
            },
            {
                "product_name": "商务休闲裤",
                "total_sales_amount": "299.0000"
            }
        ],
        "metadata": {
            "name": "Top10商品按销售额",
            "description": "查询销售额最高的Top 10商品。",
            "version": "1.0",
            "author": "UQM Team",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.03630185127258301,
            "row_count": 10,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "top_products_by_sales_amount",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 10,
                "execution_time": 0.03529667854309082,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 计算网站的平均客单价 (AOV, Average Order Value)。
    ```json
    {
    "uqm": { // <-- **这里是缺失的必需字段**
        "metadata": {
        "name": "计算平均客单价",
        "description": "此UQM查询用于计算网站的平均客单价。",
        "author": "UQM User",
        "version": "1.0"
        },
        "steps": [
        {
            "name": "calculate_aov",
            "type": "query",
            "config": {
            "data_source": "order_items",
            "metrics": [
                {
                "expression": "SUM(quantity * unit_price * (1 - discount)) / COUNT(DISTINCT order_id)",
                "alias": "average_order_value"
                }
            ]
            }
        }
        ],
        "output": "calculate_aov"
    },
    "parameters": {}, // 可选，如果查询中没有运行时参数，可以为空对象 [1]
    "options": { // 可选，用于配置缓存等执行选项 [1]
        "cache_enabled": false
    }
    }
    --------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "average_order_value": "739.83461538"
            }
        ],
        "metadata": {
            "name": "计算平均客单价",
            "description": "此UQM查询用于计算网站的平均客单价。",
            "version": "1.0",
            "author": "UQM User",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.032230377197265625,
            "row_count": 1,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "calculate_aov",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 1,
                "execution_time": 0.032230377197265625,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 按产品类别（category）统计销售额和销量，找出最受欢迎的品类。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "按产品类别统计销售额和销量",
        "description": "按产品类别统计销售额和销量，找出最受欢迎的品类。",
        "version": "1.0",
        "author": "UQM Team"
        },
        "steps": [
        {
            "name": "sales_by_category",
            "type": "query",
            "config": {
            "data_source": "order_items",
            "dimensions": [
                "products.category"
            ],
            "metrics": [
                {
                "expression": "SUM(order_items.quantity)",
                "alias": "total_quantity_sold"
                },
                {
                "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
                "alias": "total_sales_amount"
                }
            ],
            "joins": [
                {
                "type": "INNER",
                "table": "products",
                "on": {
                    "left": "order_items.product_id",
                    "right": "products.product_id",
                    "operator": "="
                }
                }
            ],
            "group_by": [
                "products.category"
            ],
            "order_by": [
                {
                "field": "total_sales_amount",
                "direction": "DESC"
                }
            ]
            }
        }
        ],
        "output": "sales_by_category"
    },
    "parameters": {},
    "options": {
        "cache_enabled": true
    }
    }
    -----------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "category": "电子产品",
                "total_quantity_sold": "11",
                "total_sales_amount": "5220.6000"
            },
            {
                "category": "家居用品",
                "total_quantity_sold": "2",
                "total_sales_amount": "2318.0500"
            },
            {
                "category": "服装",
                "total_quantity_sold": "8",
                "total_sales_amount": "1047.2000"
            },
            {
                "category": "图书",
                "total_quantity_sold": "13",
                "total_sales_amount": "1032.0000"
            }
        ],
        "metadata": {
            "name": "按产品类别统计销售额和销量",
            "description": "按产品类别统计销售额和销量，找出最受欢迎的品类。",
            "version": "1.0",
            "author": "UQM Team",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.014682769775390625,
            "row_count": 4,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "sales_by_category",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 4,
                "execution_time": 0.013682365417480469,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

* **折扣与利润分析**:
    * 计算每个订单的总折扣金额。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "订单总折扣金额统计",
        "description": "计算每个订单的总折扣金额，基于订单详情表中的数量、单价和折扣率。"
        },
        "steps": [
        {
            "name": "calculate_order_discounts",
            "type": "query",
            "config": {
            "data_source": "order_items",
            "dimensions": [
                "order_id"
            ],
            "metrics": [
                {
                "expression": "sum(quantity * unit_price * discount)",
                "alias": "total_discount"             
                }
            ],
            "group_by": [
                "order_id"
            ]
            }
        }
        ],
        "output": "calculate_order_discounts"
    }
    }
    ----------------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "order_id": 1,
                "total_discount": "43.9500"
            },
            {
                "order_id": 2,
                "total_discount": "25.8000"
            },
            {
                "order_id": 3,
                "total_discount": "0.0000"
            },
            {
                "order_id": 4,
                "total_discount": "0.0000"
            },
            {
                "order_id": 5,
                "total_discount": "246.6500"
            },
            {
                "order_id": 6,
                "total_discount": "0.0000"
            },
            {
                "order_id": 7,
                "total_discount": "79.9500"
            },
            {
                "order_id": 8,
                "total_discount": "129.0000"
            },
            {
                "order_id": 9,
                "total_discount": "0.0000"
            },
            {
                "order_id": 10,
                "total_discount": "0.0000"
            },
            {
                "order_id": 11,
                "total_discount": "0.0000"
            },
            {
                "order_id": 12,
                "total_discount": "119.8000"
            },
            {
                "order_id": 13,
                "total_discount": "85.0000"
            }
        ],
        "metadata": {
            "name": "订单总折扣金额统计",
            "description": "计算每个订单的总折扣金额，基于订单详情表中的数量、单价和折扣率。",
            "version": "1.0",
            "author": "",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.016553640365600586,
            "row_count": 13,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "calculate_order_discounts",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 13,
                "execution_time": 0.015552520751953125,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 分析不同产品或品类的平均折扣率。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "平均折扣率分析",
        "description": "计算每个产品或产品类别的平均折扣率。",
        "author": "您的团队名称",
        "version": "1.0"
        },
        "steps": [
        {
            "name": "calculate_average_discount_rate",
            "type": "query",
            "config": {
            "data_source": "order_items",
            "joins": [
                {
                "type": "INNER",
                "table": "products",
                "on": "order_items.product_id = products.product_id"
                }
            ],
            "dimensions": [
                "products.category",
                "products.product_name"
            ],
            "metrics": [
                {
                "expression": "AVG(order_items.discount)",
                "alias": "average_discount_rate"
                }
            ],
            "group_by": [
                "products.category",
                "products.product_name"
            ],
            "order_by": [
                { "field": "average_discount_rate", "direction": "DESC" }
            ]
            }
        }
        ],
        "output": "calculate_average_discount_rate"
    },
    "parameters": {},
    "options": {
        "cache_enabled": true
    }
    }
    ---------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "category": "电子产品",
                "product_name": "蓝牙降噪耳机",
                "average_discount_rate": "0.150000"
            },
            {
                "category": "服装",
                "product_name": "潮流印花T恤",
                "average_discount_rate": "0.150000"
            },
            {
                "category": "电子产品",
                "product_name": "高精度光学鼠标",
                "average_discount_rate": "0.050000"
            },
            {
                "category": "家居用品",
                "product_name": "智能升降学习桌",
                "average_discount_rate": "0.050000"
            },
            {
                "category": "图书",
                "product_name": "《SQL从入门到大神》",
                "average_discount_rate": "0.050000"
            },
            {
                "category": "电子产品",
                "product_name": "AI智能音箱",
                "average_discount_rate": "0.050000"
            },
            {
                "category": "电子产品",
                "product_name": "超高速SSD 1TB",
                "average_discount_rate": "0.025000"
            },
            {
                "category": "电子产品",
                "product_name": "机械键盘",
                "average_discount_rate": "0.025000"
            },
            {
                "category": "家居用品",
                "product_name": "日式和风床品四件套",
                "average_discount_rate": "0.000000"
            },
            {
                "category": "服装",
                "product_name": "商务休闲裤",
                "average_discount_rate": "0.000000"
            }
        ],
        "metadata": {
            "name": "平均折扣率分析",
            "description": "计算每个产品或产品类别的平均折扣率。",
            "version": "1.0",
            "author": "您的团队名称",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.052246809005737305,
            "row_count": 10,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "calculate_average_discount_rate",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 10,
                "execution_time": 0.05124616622924805,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

### **三、 客户行为分析 (Customer Behavior)**

主要围绕 `customers`, `orders`, `order_items` 表。

* **基础查询**:
    * 查询某位客户（如：孙悟空）的所有历史订单。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "客户历史订单查询",
        "description": "查询指定客户的所有历史订单及其商品详情，通过连接客户、订单和订单项表。",
        "author": "UQM Team"
        },
        "steps": [
        {
            "name": "get_customer_orders",
            "type": "query",
            "config": {
            "data_source": "customers",
            "joins": [
                {
                "type": "INNER",
                "table": "orders",
                "on": {
                    "left": "customers.customer_id",
                    "right": "orders.customer_id",
                    "operator": "="
                }
                },
                {
                "type": "LEFT",
                "table": "order_items",
                "on": {
                    "left": "orders.order_id",
                    "right": "order_items.order_id",
                    "operator": "="
                }
                }
            ],
            "filters": [
                {
                "field": "customers.customer_name",
                "operator": "=",
                "value": "$customer_name_param"
                }
            ],
            "dimensions": [
                "customers.customer_name",
                "orders.order_id",
                "orders.order_date",
                "orders.status",
                "orders.shipping_fee",
                "order_items.order_item_id",
                "order_items.product_id",
                "order_items.quantity",
                "order_items.unit_price",
                "order_items.discount"
            ],
            "order_by": [
                { "field": "orders.order_date", "direction": "DESC" },
                { "field": "orders.order_id", "direction": "ASC" }
            ]
            }
        }
        ],
        "output": "get_customer_orders"
    },
    "parameters": {
        "customer_name_param": "孙悟空"
    }
    }
    ---------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "customer_name": "孙悟空",
                "order_id": 10,
                "order_date": "2025-03-05T13:00:00",
                "status": "已发货",
                "shipping_fee": "10.00",
                "order_item_id": 13,
                "product_id": 1,
                "quantity": 1,
                "unit_price": "499.00",
                "discount": "0.00"
            },
            {
                "customer_name": "孙悟空",
                "order_id": 4,
                "order_date": "2024-03-10T09:00:00",
                "status": "待处理",
                "shipping_fee": "10.00",
                "order_item_id": 5,
                "product_id": 4,
                "quantity": 1,
                "unit_price": "299.00",
                "discount": "0.00"
            },
            {
                "customer_name": "孙悟空",
                "order_id": 1,
                "order_date": "2024-01-20T10:30:00",
                "status": "已完成",
                "shipping_fee": "10.00",
                "order_item_id": 1,
                "product_id": 1,
                "quantity": 1,
                "unit_price": "499.00",
                "discount": "0.05"
            },
            {
                "customer_name": "孙悟空",
                "order_id": 1,
                "order_date": "2024-01-20T10:30:00",
                "status": "已完成",
                "shipping_fee": "10.00",
                "order_item_id": 2,
                "product_id": 2,
                "quantity": 1,
                "unit_price": "380.00",
                "discount": "0.05"
            }
        ],
        "metadata": {
            "name": "客户历史订单查询",
            "description": "查询指定客户的所有历史订单及其商品详情，通过连接客户、订单和订单项表。",
            "version": "1.0",
            "author": "UQM Team",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.06743288040161133,
            "row_count": 4,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "get_customer_orders",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 4,
                "execution_time": 0.06743288040161133,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 按国家或城市统计客户数量，分析客户的地理分布。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "客户地理分布分析",
        "description": "统计按国家或城市分组的客户数量，分析客户的地理分布。",
        "author": "UQM Team"
        },
        "steps": [
        {
            "name": "count_customers_by_location",
            "type": "query",
            "config": {
            "data_source": "customers",
            "dimensions": [
                "country",
                "city"
            ],
            "metrics": [
                {
                "name": "customer_id",
                "aggregation": "COUNT",
                "alias": "customer_count"
                }
            ],
            "group_by": [
                "country",
                "city"
            ],
            "order_by": [
                { "field": "customer_count", "direction": "DESC" }
            ]
            }
        }
        ],
        "output": "count_customers_by_location"
    }
    }
    ----------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "country": "美国",
                "city": "纽约",
                "customer_count": 2
            },
            {
                "country": "日本",
                "city": "风车村",
                "customer_count": 1
            },
            {
                "country": "德国",
                "city": "柏林",
                "customer_count": 1
            },
            {
                "country": "法国",
                "city": "巴黎",
                "customer_count": 1
            },
            {
                "country": "中国",
                "city": "北京",
                "customer_count": 1
            },
            {
                "country": "意大利",
                "city": "罗马",
                "customer_count": 1
            },
            {
                "country": "中国",
                "city": "上海",
                "customer_count": 1
            },
            {
                "country": "加拿大",
                "city": "多伦多",
                "customer_count": 1
            },
            {
                "country": "新加坡",
                "city": "新加坡",
                "customer_count": 1
            },
            {
                "country": "日本",
                "city": "神奈川",
                "customer_count": 1
            },
            {
                "country": "英国",
                "city": "伦敦",
                "customer_count": 1
            }
        ],
        "metadata": {
            "name": "客户地理分布分析",
            "description": "统计按国家或城市分组的客户数量，分析客户的地理分布。",
            "version": "1.0",
            "author": "UQM Team",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.022446632385253906,
            "row_count": 11,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "count_customers_by_location",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 11,
                "execution_time": 0.022446632385253906,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

* **客户价值分析**:
    * 找出消费总额最高的 Top 10 VIP 客户。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "Top10VIPCustomersByTotalSpent",
        "description": "找出消费总额最高的 Top 10 VIP 客户。",
        "author": "AI Assistant"
        // ... 其他 metadata 字段 (可选) [9]
        },
        "steps": [
        {
            "name": "calculate_vip_customer_spending",
            "type": "query",
            "config": {
            "data_source": "customers",
            "joins": [
                {
                "type": "INNER",
                "table": "orders",
                "on": "customers.customer_id = orders.customer_id"
                },
                {
                "type": "INNER",
                "table": "order_items",
                "on": "orders.order_id = order_items.order_id"
                }
            ],
            "dimensions": [
                "customers.customer_id",
                "customers.customer_name",
                "customers.email"
            ],
            "metrics": [
                {
                "expression": "SUM(order_items.quantity * order_items.unit_price)",
                "alias": "total_spent"
                }
            ],
            "filters": [
                {
                "field": "customers.customer_segment",
                "operator": "=",
                "value": "VIP"
                }
            ],
            "group_by": [
                "customers.customer_id",
                "customers.customer_name",
                "customers.email"
            ],
            "order_by": [
                {
                "field": "total_spent",
                "direction": "DESC"
                }
            ],
            "limit": 10
            }
        }
        ],
        "output": "calculate_vip_customer_spending"
    },
    "parameters": {},   // 可选，如果查询中没有参数，可以为空对象或省略 [2]
    "options": {}      // 可选，用于控制执行选项，如缓存 [2, 10]
    }
    ```
    * 根据客户的注册日期、订单频率和消费金额，对客户进行分层（如高价值客户、潜力客户、流失风险客户）。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "CustomerSegmentationByValue",
        "description": "根据客户的注册日期、订单频率和消费总额对客户进行分层。",
        "author": "AI Assistant"
        },
        "steps": [
        {
            "name": "calculate_customer_value_and_segment",
            "type": "query",
            "config": {
            "data_source": "customers",
            "joins": [
                {
                "type": "LEFT",
                "table": "orders",
                "on": "customers.customer_id = orders.customer_id"
                },
                {
                "type": "LEFT",
                "table": "order_items",
                "on": "orders.order_id = order_items.order_id"
                }
            ],
            "dimensions": [
                "customers.customer_id",
                "customers.customer_name",
                "customers.email",
                "customers.registration_date"
            ],
            "metrics": [
                {
                "expression": "COALESCE(SUM(order_items.quantity * order_items.unit_price), 0)",
                "alias": "total_spent"
                },
                {
                "expression": "COUNT(DISTINCT orders.order_id)",
                "alias": "order_count"
                },
                {
                "expression": "MAX(orders.order_date)",
                "alias": "last_order_date"
                }
            ],
            "group_by": [
                "customers.customer_id",
                "customers.customer_name",
                "customers.email",
                "customers.registration_date"
            ],
            "calculated_fields": [
                {
                "alias": "customer_segment_calculated",
                "expression": "CASE  WHEN COALESCE(SUM(order_items.quantity * order_items.unit_price), 0) >= 1000 AND COUNT(DISTINCT orders.order_id) >= 3 THEN '高价值客户'                        WHEN COUNT(DISTINCT orders.order_id) >= 3 THEN '忠诚客户' WHEN DATEDIFF(CURRENT_DATE(), customers.registration_date) <= 90 THEN '新客户'  WHEN MAX(orders.order_date) IS NULL OR DATEDIFF(CURRENT_DATE(), MAX(orders.order_date)) > 180 THEN '流失风险客户' ELSE '普通客户'   END"
                }
            ]
            }
        }
        ],
        "output": "calculate_customer_value_and_segment"
    }
    }
    -------------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "customer_id": 1,
                "customer_name": "孙悟空",
                "email": "sun.wukong@test.com",
                "registration_date": "2023-01-15",
                "total_spent": "1677.00",
                "order_count": 3,
                "last_order_date": "2025-03-05T13:00:00",
                "customer_segment_calculated": "高价值客户"
            },
            {
                "customer_id": 2,
                "customer_name": "白骨精",
                "email": "baigujing@test.com",
                "registration_date": "2023-02-20",
                "total_spent": "1108.00",
                "order_count": 2,
                "last_order_date": "2025-06-20T11:50:00",
                "customer_segment_calculated": "普通客户"
            },
            {
                "customer_id": 3,
                "customer_name": "托尼·斯塔克",
                "email": "tony.stark@test.com",
                "registration_date": "2022-11-10",
                "total_spent": "1797.00",
                "order_count": 2,
                "last_order_date": "2025-05-01T10:10:00",
                "customer_segment_calculated": "普通客户"
            },
            {
                "customer_id": 4,
                "customer_name": "蜘蛛侠",
                "email": "spiderman@test.com",
                "registration_date": "2023-08-05",
                "total_spent": "0.00",
                "order_count": 0,
                "last_order_date": null,
                "customer_segment_calculated": "流失风险客户"
            },
            {
                "customer_id": 5,
                "customer_name": "桜木花道",
                "email": "sakuragi@test.com",
                "registration_date": "2023-03-12",
                "total_spent": "0.00",
                "order_count": 0,
                "last_order_date": null,
                "customer_segment_calculated": "流失风险客户"
            },
            {
                "customer_id": 6,
                "customer_name": "赫敏·格兰杰",
                "email": "hermione.granger@test.com",
                "registration_date": "2021-07-22",
                "total_spent": "0.00",
                "order_count": 0,
                "last_order_date": null,
                "customer_segment_calculated": "流失风险客户"
            },
            {
                "customer_id": 7,
                "customer_name": "路飞",
                "email": "luffy.monkey@test.com",
                "registration_date": "2022-08-30",
                "total_spent": "1817.00",
                "order_count": 1,
                "last_order_date": "2024-05-20T11:00:00",
                "customer_segment_calculated": "流失风险客户"
            },
            {
                "customer_id": 8,
                "customer_name": "Max Mustermann",
                "email": "max.mustermann@test.com",
                "registration_date": "2023-09-01",
                "total_spent": "799.00",
                "order_count": 1,
                "last_order_date": "2024-07-16T20:10:00",
                "customer_segment_calculated": "流失风险客户"
            },
            {
                "customer_id": 9,
                "customer_name": "élodie Dubois",
                "email": "elodie.dubois@test.com",
                "registration_date": "2024-05-12",
                "total_spent": "1599.00",
                "order_count": 1,
                "last_order_date": "2024-11-11T01:15:00",
                "customer_segment_calculated": "流失风险客户"
            },
            {
                "customer_id": 10,
                "customer_name": "Isabella Rossi",
                "email": "isabella.rossi@test.com",
                "registration_date": "2024-10-25",
                "total_spent": "645.00",
                "order_count": 1,
                "last_order_date": "2024-12-25T19:30:00",
                "customer_segment_calculated": "流失风险客户"
            },
            {
                "customer_id": 11,
                "customer_name": "John Smith",
                "email": "john.smith.ca@test.com",
                "registration_date": "2025-02-18",
                "total_spent": "267.00",
                "order_count": 1,
                "last_order_date": "2025-01-30T16:22:00",
                "customer_segment_calculated": "普通客户"
            },
            {
                "customer_id": 12,
                "customer_name": "Chen Wei",
                "email": "chen.wei.sg@test.com",
                "registration_date": "2025-04-03",
                "total_spent": "639.00",
                "order_count": 1,
                "last_order_date": "2025-04-10T09:45:00",
                "customer_segment_calculated": "新客户"
            }
        ],
        "metadata": {
            "name": "CustomerSegmentationByValue",
            "description": "根据客户的注册日期、订单频率和消费总额对客户进行分层。",
            "version": "1.0",
            "author": "AI Assistant",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.05386662483215332,
            "row_count": 12,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "calculate_customer_value_and_segment",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 12,
                "execution_time": 0.05386662483215332,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 查询最近一次下单时间距今已超过6个月的客户列表（流失预警）。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "ChurnRiskCustomers",
        "description": "查询最近一次下单时间距今已超过6个月的客户列表。",
        "author": "AI Assistant"
        },
        "steps": [
        {
            "name": "get_customer_last_order_and_days",
            "type": "query",
            "config": {
            "data_source": "customers",
            "joins": [
                {
                "type": "INNER",
                "table": "orders",
                "on": "customers.customer_id = orders.customer_id"
                }
            ],
            "dimensions": [
                "customers.customer_id",
                "customers.customer_name",
                "customers.email"
            ],
            "metrics": [
                {
                "expression": "MAX(orders.order_date)",
                "alias": "last_order_date"
                }
            ],
            "group_by": [
                "customers.customer_id",
                "customers.customer_name",
                "customers.email"
            ],
            "calculated_fields": [
                {
                "alias": "days_since_last_order",
                "expression": "DATEDIFF(CURRENT_DATE(), MAX(orders.order_date))"
                }
            ],
            "having": [
                {
                "field": "days_since_last_order",
                "operator": ">",
                "value": 180
                }
            ]
            }
        }
        ],
        "output": "get_customer_last_order_and_days"
    }
    }
    ----------------------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "customer_id": 7,
                "customer_name": "路飞",
                "email": "luffy.monkey@test.com",
                "last_order_date": "2024-05-20T11:00:00",
                "days_since_last_order": 402
            },
            {
                "customer_id": 8,
                "customer_name": "Max Mustermann",
                "email": "max.mustermann@test.com",
                "last_order_date": "2024-07-16T20:10:00",
                "days_since_last_order": 345
            },
            {
                "customer_id": 9,
                "customer_name": "élodie Dubois",
                "email": "elodie.dubois@test.com",
                "last_order_date": "2024-11-11T01:15:00",
                "days_since_last_order": 227
            },
            {
                "customer_id": 10,
                "customer_name": "Isabella Rossi",
                "email": "isabella.rossi@test.com",
                "last_order_date": "2024-12-25T19:30:00",
                "days_since_last_order": 183
            }
        ],
        "metadata": {
            "name": "ChurnRiskCustomers",
            "description": "查询最近一次下单时间距今已超过6个月的客户列表。",
            "version": "1.0",
            "author": "AI Assistant",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.03789019584655762,
            "row_count": 4,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "get_customer_last_order_and_days",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 4,
                "execution_time": 0.03789019584655762,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
* **复购分析**:
    * 统计所有客户的平均复购率。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "CalculateAverageRepurchaseRate_MultiStep",
        "description": "通过多步骤计算所有客户的平均复购率（复购客户数 / 至少购买过1次的客户总数）。",
        "version": "1.0",
        "author": "UQM Expert"
        },
        "steps": [
        {
            "name": "get_customer_order_counts",
            "type": "query",
            "config": {
            "data_source": "orders",
            "dimensions": ["customer_id"],
            "metrics": [
                {
                "name": "order_id",
                "aggregation": "COUNT",
                "alias": "order_count"
                }
            ],
            "group_by": ["customer_id"]
            }
        },
        {
            "name": "categorize_customers",
            "type": "query",
            "config": {
            "data_source": "get_customer_order_counts",
            "dimensions": [
                "customer_id",
                {
                "expression": "CASE WHEN order_count > 1 THEN 1 ELSE 0 END",
                "alias": "is_repurchase_customer_flag"
                },
                {
                "expression": "1",
                "alias": "is_any_order_customer_flag"
                }
            ],
            "metrics": []
            }
        },
        {
            "name": "calculate_average_repurchase_rate",
            "type": "query",
            "config": {
            "data_source": "categorize_customers",
            "dimensions": [],
            "metrics": [
                {
                "expression": "CAST(SUM(is_repurchase_customer_flag) AS DECIMAL(10, 4)) / NULLIF(CAST(SUM(is_any_order_customer_flag) AS DECIMAL(10, 4)), 0)",
                "alias": "average_repurchase_rate"
                }
            ]
            }
        }
        ],
        "output": "calculate_average_repurchase_rate"
    }
    }
    ---------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "average_repurchase_rate": 0.3333333333333333
            }
        ],
        "metadata": {
            "name": "CalculateAverageRepurchaseRate_MultiStep",
            "description": "通过多步骤计算所有客户的平均复购率（复购客户数 / 至少购买过1次的客户总数）。",
            "version": "1.0",
            "author": "UQM Expert",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.0009987354278564453,
            "row_count": 1,
            "cache_hit": false,
            "steps_executed": 3
        },
        "step_results": [
            {
                "step_name": "get_customer_order_counts",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 9,
                "execution_time": 0.0,
                "cache_hit": true,
                "error": null
            },
            {
                "step_name": "categorize_customers",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 9,
                "execution_time": 0.0,
                "cache_hit": true,
                "error": null
            },
            {
                "step_name": "calculate_average_repurchase_rate",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 1,
                "execution_time": 0.0009987354278564453,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 找出复购次数最多的客户。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "FindTopRepurchaseCustomer",
        "description": "通过多步骤计算找出复购次数最多的客户。复购次数定义为客户总订单数减1（仅考虑订单总数大于1的客户）。",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": ["customer_analysis", "repurchase_customer", "top_customer"]
        },
        "parameters": [],
        "steps": [
        {
            "name": "get_customer_order_counts",
            "type": "query",
            "config": {
            "data_source": "orders",
            "dimensions": ["customer_id"],
            "metrics": [
                {
                "name": "order_id",
                "aggregation": "COUNT",
                "alias": "total_orders"
                }
            ],
            "group_by": ["customer_id"]
            }
        },
        {
            "name": "find_top_repurchase_customer",
            "type": "query",
            "config": {
            "data_source": "get_customer_order_counts",
            "dimensions": ["customer_id"],
            "calculated_fields": [
                {
                "alias": "repurchase_count",
                "expression": "total_orders - 1"
                }
            ],
            "filters": [
                {
                "field": "total_orders",
                "operator": ">",
                "value": 1
                }
            ],
            "order_by": [
                {
                "field": "repurchase_count",
                "direction": "DESC"
                }
            ],
            "limit": 1
            }
        }
        ],
        "output": "find_top_repurchase_customer",
        "options": {
        "cache_enabled": true,
        "timeout": 300
        }
    }
    }
    ```

### **四、 产品与供应链管理 (Product, Supplier & Inventory)**

涉及 `products`, `suppliers`, `inventory`, `warehouses` 表。

* **基础查询**:
    * 查询某个供应商（如：华南电子配件厂）提供的所有在售商品。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "GetProductsBySupplierAndStatus",
        "description": "查询某个特定供应商提供的所有在售商品，可指定供应商名称和产品下架状态。",
        "version": "1.0",
        "author": "UQM Expert",
        "tags": ["product_management", "supplier_analysis", "sales_product"]
        },
        "parameters": [
        {
            "name": "supplier_name",
            "type": "string",
            "default": "华南电子配件厂",
            "required": true,
            "description": "要查询的供应商名称。"
        },
        {
            "name": "is_discontinued",
            "type": "boolean",
            "default": false,
            "required": true,
            "description": "产品是否已下架 (true 表示已下架，false 表示在售)。"
        }
        ],
        "steps": [
        {
            "name": "get_active_products_from_supplier",
            "type": "query",
            "config": {
            "data_source": "products",
            "dimensions": [
                "products.product_id",
                "products.product_name",
                "products.category",
                "products.unit_price",
                "suppliers.supplier_name"
            ],
            "joins": [
                {
                "type": "INNER",
                "table": "suppliers",
                "on": "products.supplier_id = suppliers.supplier_id"
                }
            ],
            "filters": [
                {
                "field": "suppliers.supplier_name",
                "operator": "=",
                "value": "$supplier_name"
                },
                {
                "field": "products.discontinued",
                "operator": "=",
                "value": "$is_discontinued"
                }
            ],
            "order_by": [
                {
                "field": "products.product_name",
                "direction": "ASC"
                }
            ]
            }
        }
        ],
        "output": "get_active_products_from_supplier"
    },
    "parameters": {
        "supplier_name": "华南电子配件厂",
        "is_discontinued": false
    },
    "options": {
        "cache_enabled": true,
        "timeout": 300
    }
    }
    -------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "product_id": 2,
                "product_name": "机械键盘",
                "category": "电子产品",
                "unit_price": "380.00",
                "supplier_name": "华南电子配件厂"
            },
            {
                "product_id": 1,
                "product_name": "超高速SSD 1TB",
                "category": "电子产品",
                "unit_price": "499.00",
                "supplier_name": "华南电子配件厂"
            }
        ],
        "metadata": {
            "name": "GetProductsBySupplierAndStatus",
            "description": "查询某个特定供应商提供的所有在售商品，可指定供应商名称和产品下架状态。",
            "version": "1.0",
            "author": "UQM Expert",
            "created_at": null,
            "updated_at": null,
            "tags": [
                "product_management",
                "supplier_analysis",
                "sales_product"
            ]
        },
        "execution_info": {
            "total_time": 0.05325770378112793,
            "row_count": 2,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "get_active_products_from_supplier",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 2,
                "execution_time": 0.05325770378112793,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 查找指定商品（如：机械键盘）在所有仓库的总库存量。
    ```json
    
  {    
    "uqm": {
        "metadata": {
        "name": "指定商品总库存查询",
        "description": "查找某个特定商品在所有仓库的总库存量",
        "author": "YourName"
        },
        "parameters": [
        {
            "name": "product_name",
            "type": "string",
            "description": "要查询总库存量的商品名称",
            "required": true,
            "default": "机械键盘"
        }
        ],
        "steps": [
        {
            "name": "calculate_total_inventory_for_product",
            "type": "query",
            "config": {
            "data_source": "inventory",
            "joins": [
                {
                "type": "INNER",
                "table": "products",
                "on": "inventory.product_id = products.product_id"
                }
            ],
            "filters": [
                {
                "field": "products.product_name",
                "operator": "=",
                "value": "$product_name"
                }
            ],
            "metrics": [
                {
                "name": "quantity_on_hand",
                "aggregation": "SUM",
                "alias": "total_quantity"
                }
            ]
            }
        }
        ],
        "output": "calculate_total_inventory_for_product"
    },
    "parameters": {
        "product_name": "机械键盘"
    },
    "options": {
        "cache_enabled": true,
        "timeout": 60
    }
    }
    -------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "total_quantity": "350"
            }
        ],
        "metadata": {
            "name": "指定商品总库存查询",
            "description": "查找某个特定商品在所有仓库的总库存量",
            "version": "1.0",
            "author": "YourName",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.047756195068359375,
            "row_count": 1,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "calculate_total_inventory_for_product",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 1,
                "execution_time": 0.047756195068359375,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

* **库存与成本分析**:
    * 列出所有库存低于警戒线（例如20件）的商品，以便及时补货。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "低库存商品查询",
        "description": "列出所有库存低于指定警戒线的商品，用于及时补货",
        "author": "YourName"
        },
        "parameters": [
        {
            "name": "threshold",
            "type": "integer",
            "description": "库存警戒线（例如：20）",
            "required": true,
            "default": 20
        }
        ],
        "steps": [
        {
            "name": "low_inventory_products",
            "type": "query",
            "config": {
            "data_source": "inventory",
            "joins": [
                {
                "type": "INNER",
                "table": "products",
                "on": "inventory.product_id = products.product_id"
                }
            ],
            "filters": [
                {
                "field": "inventory.quantity_on_hand",
                "operator": "<",
                "value": "$threshold"
                }
            ],
            "dimensions": [
                "products.product_name",
                "inventory.quantity_on_hand"
            ],
            "order_by": [
                {
                "field": "inventory.quantity_on_hand",
                "direction": "ASC"
                }
            ]
            }
        }
        ],
        "output": "low_inventory_products"
    },
    "parameters": {
        "threshold": 20
    },
    "options": {
        "cache_enabled": true,
        "timeout": 60
    }
    }
    -----------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "product_name": "设计师联名卫衣",
                "quantity_on_hand": 0
            }
        ],
        "metadata": {
            "name": "低库存商品查询",
            "description": "列出所有库存低于指定警戒线的商品，用于及时补货",
            "version": "1.0",
            "author": "YourName",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.054472923278808594,
            "row_count": 1,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "low_inventory_products",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 1,
                "execution_time": 0.054472923278808594,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 计算每个仓库中所有商品的总库存价值（`inventory.quantity_on_hand * products.unit_price`）。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "仓库总库存价值",
        "description": "计算每个仓库中所有商品的总库存价值",
        "author": "YourName"
        },
        "parameters": [],
        "steps": [
        {
            "name": "warehouse_total_value",
            "type": "query",
            "config": {
            "data_source": "inventory",
            "joins": [
                {
                "type": "INNER",
                "table": "products",
                "on": "inventory.product_id = products.product_id"
                },
                {
                "type": "INNER",
                "table": "warehouses",
                "on": "inventory.warehouse_id = warehouses.warehouse_id"
                }
            ],
            "dimensions": [
                "warehouses.warehouse_name"
            ],
            "metrics": [
                {
                "expression": "SUM(inventory.quantity_on_hand * products.unit_price)",
                "alias": "total_inventory_value"
                }
            ],
            "group_by": [
                "warehouses.warehouse_name"
            ]
            }
        }
        ],
        "output": "warehouse_total_value"
    },
    "options": {
        "cache_enabled": true,
        "timeout": 60
    }
    }
    ```
    * 找出已经停产 (`discontinued` = TRUE) 但仍有库存的商品。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "停产但有库存商品查询",
        "description": "找出已经停产但仍有库存的商品，以便处理冗余库存",
        "author": "YourName"
        },
        "parameters": [],
        "steps": [
        {
            "name": "discontinued_products_with_stock",
            "type": "query",
            "config": {
            "data_source": "products",
            "joins": [
                {
                "type": "INNER",
                "table": "inventory",
                "on": "products.product_id = inventory.product_id"
                }
            ],
            "filters": [
                {
                "field": "products.discontinued",
                "operator": "=",
                "value": true
                },
                {
                "field": "inventory.quantity_on_hand",
                "operator": ">",
                "value": 0
                }
            ],
            "dimensions": [
                "products.product_name",
                "products.category",
                "inventory.quantity_on_hand",
                "inventory.warehouse_id"
            ]
            }
        }
        ],
        "output": "discontinued_products_with_stock"
    },
    "options": {
        "cache_enabled": true,
        "timeout": 60
    }
    }
    ------------------------------------------------------------------------------
    {
        "success": true,
        "data": [],
        "metadata": {
            "name": "停产但有库存商品查询",
            "description": "找出已经停产但仍有库存的商品，以便处理冗余库存",
            "version": "1.0",
            "author": "YourName",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.02515888214111328,
            "row_count": 0,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "discontinued_products_with_stock",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 0,
                "execution_time": 0.02515888214111328,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

* **供应商分析**:
    * 统计每个供应商提供的产品种类数量。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "供应商产品种类统计",
        "description": "统计每个供应商提供的产品种类数量，以便分析供应商多样性",
        "author": "YourName"
        },
        "parameters": [],
        "steps": [
        {
            "name": "supplier_category_count",
            "type": "query",
            "config": {
            "data_source": "products",
            "joins": [
                {
                "type": "INNER",
                "table": "suppliers",
                "on": "products.supplier_id = suppliers.supplier_id"
                }
            ],
            "dimensions": [
                "suppliers.supplier_name"
            ],
            "metrics": [
                {
                "expression": "COUNT(DISTINCT products.category)",
                "alias": "product_category_count"
                }
            ],
            "group_by": [
                "suppliers.supplier_name"
            ],
            "order_by": [
                {
                "field": "product_category_count",
                "direction": "DESC"
                }
            ]
            }
        }
        ],
        "output": "supplier_category_count"
    },
    "options": {
        "cache_enabled": true,
        "timeout": 60
    }
    }
    -----------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "supplier_name": "京都纺织株式会社",
                "product_category_count": 2
            },
            {
                "supplier_name": "珠三角智能制造",
                "product_category_count": 2
            },
            {
                "supplier_name": "长三角服装集团",
                "product_category_count": 2
            },
            {
                "supplier_name": "黑森林精密仪器",
                "product_category_count": 1
            },
            {
                "supplier_name": "华南电子配件厂",
                "product_category_count": 1
            },
            {
                "supplier_name": "硅谷创新科技",
                "product_category_count": 1
            }
        ],
        "metadata": {
            "name": "供应商产品种类统计",
            "description": "统计每个供应商提供的产品种类数量，以便分析供应商多样性",
            "version": "1.0",
            "author": "YourName",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.029512405395507812,
            "row_count": 6,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "supplier_category_count",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 6,
                "execution_time": 0.029512405395507812,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 找出为“电子产品”类别供货的所有中国供应商。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "中国电子产品供应商查询",
        "description": "找出为“电子产品”类别供货的所有中国供应商",
        "author": "YourName"
        },
        "parameters": [],
        "steps": [
        {
            "name": "chinese_electronics_suppliers",
            "type": "query",
            "config": {
            "data_source": "products",
            "joins": [
                {
                "type": "INNER",
                "table": "suppliers",
                "on": "products.supplier_id = suppliers.supplier_id"
                }
            ],
            "filters": [
                {
                "field": "products.category",
                "operator": "=",
                "value": "电子产品"
                },
                {
                "field": "suppliers.country",
                "operator": "=",
                "value": "中国"
                }
            ],
            "dimensions": [
                "suppliers.supplier_name"
            ],
            "group_by": [
                "suppliers.supplier_name"
            ],
            "order_by": [
                {
                "field": "suppliers.supplier_name",
                "direction": "ASC"
                }
            ]
            }
        }
        ],
        "output": "chinese_electronics_suppliers"
    },
    "options": {
        "cache_enabled": true,
        "timeout": 60
    }
    }
    -----------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "supplier_name": "华南电子配件厂"
            }
        ],
        "metadata": {
            "name": "中国电子产品供应商查询",
            "description": "找出为“电子产品”类别供货的所有中国供应商",
            "version": "1.0",
            "author": "YourName",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.05653715133666992,
            "row_count": 1,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "chinese_electronics_suppliers",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 1,
                "execution_time": 0.05653715133666992,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

### **五、 综合跨模块分析 (Complex Scenarios)**

这类查询通常需要连接三张或更多表，代表了更复杂的业务洞察需求。

* **员工业绩与销售关联分析**:
    * 查询某个销售代表（employee）在指定季度内完成的所有订单的总金额，用于计算提成。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "员工业绩销售总金额查询",
        "description": "查询某个销售代表在指定季度内完成的所有订单的总金额，用于计算提成。",
        "author": "YourName"
        },
        "parameters": [
        {
            "name": "employeeId",
            "type": "integer",
            "required": true,
            "description": "要查询的销售代表的员工ID。"
        },
        {
            "name": "quarterStartDate",
            "type": "string",
            "description": "查询季度的开始日期（格式：YYYY-MM-DD）。",
            "required": true
        },
        {
            "name": "quarterEndDate",
            "type": "string",
            "description": "查询季度的结束日期（格式：YYYY-MM-DD）。",
            "required": true
        }
        ],
        "steps": [
        {
            "name": "sales_commission_calculation",
            "type": "query",
            "config": {
            "data_source": "order_items",
            "joins": [
                {
                "type": "INNER",
                "table": "orders",
                "on": "order_items.order_id = orders.order_id"
                },
                {
                "type": "INNER",
                "table": "employees",
                "on": "orders.employee_id = employees.employee_id"
                }
            ],
            "filters": [
                {
                "field": "employees.employee_id",
                "operator": "=",
                "value": "$employeeId"
                },
                {
                "field": "orders.order_date",
                "operator": "BETWEEN",
                "value": ["$quarterStartDate", "$quarterEndDate"]
                },
                {
                "field": "orders.status",
                "operator": "=",
                "value": "已完成"
                }
            ],
            "dimensions": [
                "employees.employee_id",
                "employees.first_name",
                "employees.last_name"
            ],
            "metrics": [
                {
                "expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))",
                "alias": "total_sales_amount"
                }
            ],
            "group_by": [
                "employees.employee_id",
                "employees.first_name",
                "employees.last_name"
            ]
            }
        }
        ],
        "output": "sales_commission_calculation"
    },
    "parameters": { 
        "employeeId": 6,
        "quarterStartDate": "2024-01-01",
        "quarterEndDate": "2024-03-31"
    },
    "options": {
        "cache_enabled": true,
        "timeout": 120
    }
    }
    ----------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "employee_id": 6,
                "first_name": "杨",
                "last_name": "静",
                "total_sales_amount": "835.0500"
            }
        ],
        "metadata": {
            "name": "员工业绩销售总金额查询",
            "description": "查询某个销售代表在指定季度内完成的所有订单的总金额，用于计算提成。",
            "version": "1.0",
            "author": "YourName",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.01703333854675293,
            "row_count": 1,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "sales_commission_calculation",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 1,
                "execution_time": 0.01703333854675293,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

* **客户偏好与产品关联分析**:
    * 分析来自不同国家的客户最喜欢购买的商品类别是什么。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "每个国家最受欢迎商品类别分析",
        "description": "通过聚合、排名和过滤，找出每个国家销售额最高的商品类别，以识别客户偏好。",
        "version": "1.0",
        "author": "UQM Team"
        },
        "steps": [
        {
            "name": "aggregate_country_category_metrics",
            "type": "query",
            "config": {
            "data_source": "order_items",
            "joins": [
                {
                "type": "INNER",
                "table": "products",
                "on": "order_items.product_id = products.product_id"
                },
                {
                "type": "INNER",
                "table": "orders",
                "on": "order_items.order_id = orders.order_id"
                },
                {
                "type": "INNER",
                "table": "customers",
                "on": "orders.customer_id = customers.customer_id"
                }
            ],
            "dimensions": [
                {"expression": "customers.country", "alias": "country"},
                {"expression": "products.category", "alias": "category"}
            ],
            "metrics": [
                {"expression": "SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount))", "alias": "total_sales_amount"}
            ],
            "group_by": ["country", "category"]
            }
        },
        {
            "name": "rank_categories_per_country",
            "type": "query",
            "config": {
            "data_source": "aggregate_country_category_metrics",
            "dimensions": ["country", "category", "total_sales_amount"],
            "calculated_fields": [
                {
                "alias": "rank_by_sales",
                "expression": "ROW_NUMBER() OVER (PARTITION BY country ORDER BY total_sales_amount DESC)"
                }
            ],
            "order_by": [
                {"field": "country", "direction": "ASC"},
                {"field": "rank_by_sales", "direction": "ASC"}
            ]
            }
        },
        {
            "name": "select_top_rank_per_country",
            "type": "query",
            "config": {
            "data_source": "rank_categories_per_country",
            "dimensions": ["country", "category", "total_sales_amount"],
            "filters": [
                {
                "field": "rank_by_sales",
                "operator": "=",
                "value": 1
                }
            ],
            "order_by": [
                {"field": "country", "direction": "ASC"},
                {"field": "total_sales_amount", "direction": "DESC"}
            ]
            }
        }
        ],
        "output": "select_top_rank_per_country"
    },
    "parameters": {},
    "options": {
        "cache_enabled": true,
        "timeout": 300
    }
    }
    --------------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "country": "中国",
                "category": "电子产品",
                "total_sales_amount": "1334.0500"
            },
            {
                "country": "加拿大",
                "category": "图书",
                "total_sales_amount": "267.0000"
            },
            {
                "country": "德国",
                "category": "家居用品",
                "total_sales_amount": "799.0000"
            },
            {
                "country": "意大利",
                "category": "服装",
                "total_sales_amount": "516.0000"
            },
            {
                "country": "新加坡",
                "category": "电子产品",
                "total_sales_amount": "639.0000"
            },
            {
                "country": "日本",
                "category": "电子产品",
                "total_sales_amount": "1570.3500"
            },
            {
                "country": "法国",
                "category": "家居用品",
                "total_sales_amount": "1519.0500"
            },
            {
                "country": "美国",
                "category": "电子产品",
                "total_sales_amount": "1677.2000"
            }
        ],
        "metadata": {
            "name": "每个国家最受欢迎商品类别分析",
            "description": "通过聚合、排名和过滤，找出每个国家销售额最高的商品类别，以识别客户偏好。",
            "version": "1.0",
            "author": "UQM Team",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.0010297298431396484,
            "row_count": 8,
            "cache_hit": false,
            "steps_executed": 3
        },
        "step_results": [
            {
                "step_name": "aggregate_country_category_metrics",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 10,
                "execution_time": 0.0,
                "cache_hit": true,
                "error": null
            },
            {
                "step_name": "rank_categories_per_country",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 10,
                "execution_time": 0.0,
                "cache_hit": true,
                "error": null
            },
            {
                "step_name": "select_top_rank_per_country",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 8,
                "execution_time": 0.0010297298431396484,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```
    * 找出购买了“机械键盘”的客户，还同时购买了哪些其他商品（购物篮分析）。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "购买机械键盘的客户还购买了哪些商品",
        "description": "分析购买了“机械键盘”的客户，他们同一订单中还同时购买了哪些其他商品，并统计这些商品的出现次数。这是典型的购物篮分析场景。",
        "version": "1.0",
        "author": "UQM Team"
        },
        "steps": [
        {
            "name": "co_purchased_items_analysis",
            "type": "query",
            "config": {
            "data_source": "order_items AS oi1", // 将 order_items 表别名为 oi1
            "joins": [
                {
                "type": "INNER",
                "table": "products AS p1", // 第一个 products 表，用于筛选“机械键盘”
                "on": "oi1.product_id = p1.product_id"
                },
                {
                "type": "INNER",
                "table": "order_items AS oi2", // 第二个 order_items 表，用于获取同一订单中的其他商品
                "on": "oi1.order_id = oi2.order_id" // 在 order_id 上自连接
                },
                {
                "type": "INNER",
                "table": "products AS p2", // 第二个 products 表，用于获取其他商品的产品名
                "on": "oi2.product_id = p2.product_id"
                },
                {
                "type": "INNER",
                "table": "orders AS o", // 连接 orders 表获取客户ID
                "on": "oi1.order_id = o.order_id"
                },
                {
                "type": "INNER",
                "table": "customers AS c", // 连接 customers 表获取客户姓名
                "on": "o.customer_id = c.customer_id"
                }
            ],
            "dimensions": [
                {"expression": "c.customer_name", "alias": "customer_name"},
                {"expression": "p2.product_name", "alias": "co_purchased_product_name"}
            ],
            "metrics": [
                {"expression": "COUNT(DISTINCT oi2.order_item_id)", "alias": "purchase_count"} // 统计共同购买的商品在订单中出现的次数
            ],
            "filters": [
                {
                "field": "p1.product_name",
                "operator": "=",
                "value": "机械键盘" // 筛选包含“机械键盘”的订单
                },
                {
                "field": "p2.product_name",
                "operator": "!=",
                "value": "机械键盘" // 排除“机械键盘”本身
                }
            ],
            "group_by": ["c.customer_name", "p2.product_name"], // 按客户和共同购买的商品分组
            "order_by": [
                {"field": "customer_name", "direction": "ASC"},
                {"field": "purchase_count", "direction": "DESC"},
                {"field": "co_purchased_product_name", "direction": "ASC"}
            ],
            "limit": 100 // 可选：限制结果数量
            }
        }
        ],
        "output": "co_purchased_items_analysis"
    },
    "parameters": {},
    "options": {
        "cache_enabled": true,
        "timeout": 300
    }
    }
    -------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "customer_name": "Chen Wei",
                "co_purchased_product_name": "高精度光学鼠标",
                "purchase_count": 1
            },
            {
                "customer_name": "孙悟空",
                "co_purchased_product_name": "超高速SSD 1TB",
                "purchase_count": 1
            }
        ],
        "metadata": {
            "name": "购买机械键盘的客户还购买了哪些商品",
            "description": "分析购买了“机械键盘”的客户，他们同一订单中还同时购买了哪些其他商品，并统计这些商品的出现次数。这是典型的购物篮分析场景。",
            "version": "1.0",
            "author": "UQM Team",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.057001352310180664,
            "row_count": 2,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "co_purchased_items_analysis",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 2,
                "execution_time": 0.05600118637084961,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

* **供应链与销售关联分析**:
    * 分析来自不同供应商的产品的平均销售额和销量，评估供应商价值。
    ```json
    {
    "uqm": {
        "metadata": {
        "name": "按供应商分析产品销售额和销量",
        "description": "分析来自不同供应商的产品的总销售额和总销量，以评估供应商的价值。总销售额定义为订单项中数量与成交单价的乘积之和，销量定义为订单项中数量之和。",
        "version": "1.0",
        "author": "UQM Team"
        },
        "steps": [
        {
            "name": "supplier_sales_performance",
            "type": "query",
            "config": {
            "data_source": "order_items AS oi", // 以订单详情表作为起点，并使用别名oi
            "joins": [
                {
                "type": "INNER",
                "table": "products AS p", // 连接产品表，获取产品与供应商信息
                "on": "oi.product_id = p.product_id" // 连接条件：订单项的产品ID等于产品ID
                },
                {
                "type": "INNER",
                "table": "suppliers AS s", // 连接供应商表，获取供应商名称
                "on": "p.supplier_id = s.supplier_id" // 连接条件：产品的供应商ID等于供应商ID
                }
            ],
            "dimensions": [
                {"expression": "s.supplier_name", "alias": "supplier_name"} // 维度：供应商名称
            ],
            "metrics": [
                {
                "expression": "SUM(oi.quantity * oi.unit_price)", // 计算总销售额
                "alias": "total_sales_amount"
                },
                {
                "expression": "SUM(oi.quantity)", // 计算总销量
                "alias": "total_sales_volume"
                }
            ],
            "group_by": ["s.supplier_name"], // 按供应商名称进行分组聚合
            "order_by": [
                {"field": "total_sales_amount", "direction": "DESC"}, // 按总销售额降序排列
                {"field": "total_sales_volume", "direction": "DESC"} // 然后按总销量降序排列
            ],
            "limit": 50 // 可选：限制返回的结果数量，例如显示Top 50供应商
            }
        }
        ],
        "output": "supplier_sales_performance"
    },
    "parameters": {},
    "options": {
        "cache_enabled": true,
        "timeout": 300
    }
    }
    --------------------------------------------------------------------
    {
        "success": true,
        "data": [
            {
                "supplier_name": "珠三角智能制造",
                "total_sales_amount": "2716.00",
                "total_sales_volume": "14"
            },
            {
                "supplier_name": "黑森林精密仪器",
                "total_sales_amount": "2076.00",
                "total_sales_volume": "4"
            },
            {
                "supplier_name": "硅谷创新科技",
                "total_sales_amount": "1797.00",
                "total_sales_volume": "3"
            },
            {
                "supplier_name": "华南电子配件厂",
                "total_sales_amount": "1758.00",
                "total_sales_volume": "4"
            },
            {
                "supplier_name": "长三角服装集团",
                "total_sales_amount": "1202.00",
                "total_sales_volume": "8"
            },
            {
                "supplier_name": "京都纺织株式会社",
                "total_sales_amount": "799.00",
                "total_sales_volume": "1"
            }
        ],
        "metadata": {
            "name": "按供应商分析产品销售额和销量",
            "description": "分析来自不同供应商的产品的总销售额和总销量，以评估供应商的价值。总销售额定义为订单项中数量与成交单价的乘积之和，销量定义为订单项中数量之和。",
            "version": "1.0",
            "author": "UQM Team",
            "created_at": null,
            "updated_at": null,
            "tags": []
        },
        "execution_info": {
            "total_time": 0.05584096908569336,
            "row_count": 6,
            "cache_hit": false,
            "steps_executed": 1
        },
        "step_results": [
            {
                "step_name": "supplier_sales_performance",
                "step_type": "query",
                "status": "completed",
                "data": null,
                "row_count": 6,
                "execution_time": 0.05584096908569336,
                "cache_hit": false,
                "error": null
            }
        ]
    }
    ```

以上这些场景几乎涵盖了从简单查询、多表连接、聚合分组到复杂的业务洞察。每一个场景都可以通过组合使用您系统中的 `query`, `enrich`, `pivot` 等步骤，用 JSON Schema 的形式来实现。
```json
{
  "uqm": {
    "metadata": {
      "name": "EmployeeDepartmentDetailsEnrichment",
      "description": "通过部门ID关联员工和部门表，以获取员工的详细部门信息。",
      "version": "1.0",
      "author": "UQM User"
    },
    "steps": [
      {
        "name": "query_employees_data",
        "type": "query",
        "config": {
          "data_source": "employees",
          "dimensions": [
            "employee_id", 
            {
              "expression": "CONCAT(first_name, last_name)",
              "alias": "name"
            },
            "department_id", 
            "job_title", 
            "hire_date", 
            "salary"
          ],
          "filters": []
        }
      },
      {
        "name": "enrich_with_department_info",
        "type": "enrich",
        "config": {
          "source": "query_employees_data",
          "lookup": {
            "table": "departments",
            "columns": ["department_id", "name", "location"]
          },
          "on": {
            "left": "department_id",
            "right": "department_id"
          },
          "join_type": "left"
        }
      }
    ],
    "output": "enrich_with_department_info"
  },
  "parameters": {},
  "options": {
    "cache_enabled": false
  }
}
---------------------------------------------------------------------
{
    "success": true,
    "data": [
        {
            "employee_id": 1,
            "name": "张伟",
            "department_id": 2,
            "job_title": "IT总监",
            "hire_date": "2022-01-10",
            "salary": "35000.00",
            "name_1": "信息技术部",
            "location": "上海"
        },
        {
            "employee_id": 2,
            "name": "王芳",
            "department_id": 1,
            "job_title": "HR经理",
            "hire_date": "2022-03-15",
            "salary": "25000.00",
            "name_1": "人力资源部",
            "location": "北京"
        },
        {
            "employee_id": 3,
            "name": "李强",
            "department_id": 2,
            "job_title": "软件工程师",
            "hire_date": "2022-02-20",
            "salary": "18000.00",
            "name_1": "信息技术部",
            "location": "上海"
        },
        {
            "employee_id": 4,
            "name": "刘娜",
            "department_id": 1,
            "job_title": "人事专员",
            "hire_date": "2023-05-30",
            "salary": "12000.00",
            "name_1": "人力资源部",
            "location": "北京"
        },
        {
            "employee_id": 5,
            "name": "陈军",
            "department_id": 5,
            "job_title": "销售总监",
            "hire_date": "2021-09-01",
            "salary": "38000.00",
            "name_1": "销售部",
            "location": "北京"
        },
        {
            "employee_id": 6,
            "name": "杨静",
            "department_id": 5,
            "job_title": "销售代表",
            "hire_date": "2023-01-20",
            "salary": "15000.00",
            "name_1": "销售部",
            "location": "北京"
        },
        {
            "employee_id": 7,
            "name": "MingLi",
            "department_id": 3,
            "job_title": "高级财务分析师",
            "hire_date": "2020-08-11",
            "salary": "28000.00",
            "name_1": "财务部",
            "location": "深圳"
        },
        {
            "employee_id": 8,
            "name": "PeterSchmidt",
            "department_id": 6,
            "job_title": "欧洲区销售经理",
            "hire_date": "2022-11-01",
            "salary": "42000.00",
            "name_1": "欧洲销售部",
            "location": "德国-柏林"
        },
        {
            "employee_id": 9,
            "name": "YukiTanaka",
            "department_id": 4,
            "job_title": "市场专员",
            "hire_date": "2024-02-19",
            "salary": "14000.00",
            "name_1": "市场营销部",
            "location": "广州"
        },
        {
            "employee_id": 10,
            "name": "EmilyJones",
            "department_id": 2,
            "job_title": "高级软件工程师",
            "hire_date": "2024-04-08",
            "salary": "22000.00",
            "name_1": "信息技术部",
            "location": "上海"
        },
        {
            "employee_id": 11,
            "name": "CarlosGarcia",
            "department_id": 7,
            "job_title": "运营经理",
            "hire_date": "2025-01-15",
            "salary": "31000.00",
            "name_1": "研发中心",
            "location": "成都"
        },
        {
            "employee_id": 12,
            "name": "SophiaMüller",
            "department_id": 6,
            "job_title": "销售助理",
            "hire_date": "2025-03-20",
            "salary": "16000.00",
            "name_1": "欧洲销售部",
            "location": "德国-柏林"
        }
    ],
    "metadata": {
        "name": "EmployeeDepartmentDetailsEnrichment",
        "description": "通过部门ID关联员工和部门表，以获取员工的详细部门信息。",
        "version": "1.0",
        "author": "UQM User",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.04099893569946289,
        "row_count": 12,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "query_employees_data",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.02195286750793457,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "enrich_with_department_info",
            "step_type": "enrich",
            "status": "completed",
            "data": null,
            "row_count": 12,
            "execution_time": 0.018010377883911133,
            "cache_hit": false,
            "error": null
        }
    ]
}
```

```json
{
  "uqm": {
  "metadata": {
    "name": "OrderItemProductCategoryEnrichment",
    "description": "将订单商品项数据与产品表关联，丰富产品类别信息，用于销售和品类分析。",
    "version": "1.0",
    "author": "UQM User"
  },
  "steps": [
    {
      "name": "query_order_items",
      "type": "query",
      "config": {
        "data_source": "order_items",
        "dimensions": ["order_item_id", "order_id", "product_id", "quantity", "unit_price"],
        "filters": []
      }
    },
    {
      "name": "enrich_with_product_details",
      "type": "enrich",
      "config": {
        "source": "query_order_items",
        "lookup": {
          "table": "products",
          "columns": ["product_id AS id", "product_name", "category"]
        },
        "on": {
          "left": "product_id",
          "right": "id"
        },
        "join_type": "inner"
      }
    }
  ],
  "output": "enrich_with_product_details"
},
  "parameters": {},
  "options": {
    "cache_enabled": false
  }
}
---------------------------------------------------------------------------
{
    "success": true,
    "data": [
        {
            "order_item_id": 1,
            "order_id": 1,
            "product_id": 1,
            "quantity": 1,
            "unit_price": "499.00",
            "id": 1,
            "product_name": "超高速SSD 1TB",
            "category": "电子产品"
        },
        {
            "order_item_id": 13,
            "order_id": 10,
            "product_id": 1,
            "quantity": 1,
            "unit_price": "499.00",
            "id": 1,
            "product_name": "超高速SSD 1TB",
            "category": "电子产品"
        },
        {
            "order_item_id": 2,
            "order_id": 1,
            "product_id": 2,
            "quantity": 1,
            "unit_price": "380.00",
            "id": 2,
            "product_name": "机械键盘",
            "category": "电子产品"
        },
        {
            "order_item_id": 14,
            "order_id": 11,
            "product_id": 2,
            "quantity": 1,
            "unit_price": "380.00",
            "id": 2,
            "product_name": "机械键盘",
            "category": "电子产品"
        },
        {
            "order_item_id": 3,
            "order_id": 2,
            "product_id": 3,
            "quantity": 2,
            "unit_price": "129.00",
            "id": 3,
            "product_name": "潮流印花T恤",
            "category": "服装"
        },
        {
            "order_item_id": 11,
            "order_id": 8,
            "product_id": 3,
            "quantity": 5,
            "unit_price": "129.00",
            "id": 3,
            "product_name": "潮流印花T恤",
            "category": "服装"
        },
        {
            "order_item_id": 4,
            "order_id": 3,
            "product_id": 5,
            "quantity": 1,
            "unit_price": "599.00",
            "id": 5,
            "product_name": "AI智能音箱",
            "category": "电子产品"
        },
        {
            "order_item_id": 16,
            "order_id": 12,
            "product_id": 5,
            "quantity": 2,
            "unit_price": "599.00",
            "id": 5,
            "product_name": "AI智能音箱",
            "category": "电子产品"
        },
        {
            "order_item_id": 5,
            "order_id": 4,
            "product_id": 4,
            "quantity": 1,
            "unit_price": "299.00",
            "id": 4,
            "product_name": "商务休闲裤",
            "category": "服装"
        },
        {
            "order_item_id": 7,
            "order_id": 5,
            "product_id": 7,
            "quantity": 2,
            "unit_price": "259.00",
            "id": 7,
            "product_name": "高精度光学鼠标",
            "category": "电子产品"
        },
        {
            "order_item_id": 15,
            "order_id": 11,
            "product_id": 7,
            "quantity": 1,
            "unit_price": "259.00",
            "id": 7,
            "product_name": "高精度光学鼠标",
            "category": "电子产品"
        },
        {
            "order_item_id": 8,
            "order_id": 5,
            "product_id": 11,
            "quantity": 1,
            "unit_price": "1299.00",
            "id": 11,
            "product_name": "蓝牙降噪耳机",
            "category": "电子产品"
        },
        {
            "order_item_id": 9,
            "order_id": 6,
            "product_id": 8,
            "quantity": 1,
            "unit_price": "799.00",
            "id": 8,
            "product_name": "日式和风床品四件套",
            "category": "家居用品"
        },
        {
            "order_item_id": 10,
            "order_id": 7,
            "product_id": 10,
            "quantity": 1,
            "unit_price": "1599.00",
            "id": 10,
            "product_name": "智能升降学习桌",
            "category": "家居用品"
        },
        {
            "order_item_id": 12,
            "order_id": 9,
            "product_id": 9,
            "quantity": 3,
            "unit_price": "89.00",
            "id": 9,
            "product_name": "《SQL从入门到大神》",
            "category": "图书"
        },
        {
            "order_item_id": 17,
            "order_id": 13,
            "product_id": 9,
            "quantity": 10,
            "unit_price": "85.00",
            "id": 9,
            "product_name": "《SQL从入门到大神》",
            "category": "图书"
        }
    ],
    "metadata": {
        "name": "OrderItemProductCategoryEnrichment",
        "description": "将订单商品项数据与产品表关联，丰富产品类别信息，用于销售和品类分析。",
        "version": "1.0",
        "author": "UQM User",
        "created_at": null,
        "updated_at": null,
        "tags": []
    },
    "execution_info": {
        "total_time": 0.04099702835083008,
        "row_count": 16,
        "cache_hit": false,
        "steps_executed": 2
    },
    "step_results": [
        {
            "step_name": "query_order_items",
            "step_type": "query",
            "status": "completed",
            "data": null,
            "row_count": 16,
            "execution_time": 0.021997690200805664,
            "cache_hit": false,
            "error": null
        },
        {
            "step_name": "enrich_with_product_details",
            "step_type": "enrich",
            "status": "completed",
            "data": null,
            "row_count": 16,
            "execution_time": 0.018999338150024414,
            "cache_hit": false,
            "error": null
        }
    ]
}
```