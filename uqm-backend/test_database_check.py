"""
检查数据库中的实际数据，了解为什么查询返回空结果
"""

import sys
import os
import sqlite3
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database_data():
    """检查数据库中的实际数据"""
    print("=" * 70)
    print("检查数据库中的实际数据")
    print("=" * 70)
    
    db_path = "uqm.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        print("📋 检查表结构:")
        
        # 检查employees表
        cursor.execute("PRAGMA table_info(employees)")
        emp_columns = cursor.fetchall()
        print(f"\n📊 employees表结构 ({len(emp_columns)}列):")
        for col in emp_columns:
            print(f"   • {col[1]} ({col[2]})")
        
        # 检查departments表
        cursor.execute("PRAGMA table_info(departments)")
        dept_columns = cursor.fetchall()
        print(f"\n📊 departments表结构 ({len(dept_columns)}列):")
        for col in dept_columns:
            print(f"   • {col[1]} ({col[2]})")
        
        # 检查数据内容
        print("\n📋 检查数据内容:")
        
        # 检查employees表的数据
        cursor.execute("SELECT COUNT(*) FROM employees")
        emp_count = cursor.fetchone()[0]
        print(f"\n📊 employees表总记录数: {emp_count}")
        
        if emp_count > 0:
            # 查看前几条employees数据
            cursor.execute("SELECT * FROM employees LIMIT 5")
            emp_data = cursor.fetchall()
            print("   前5条记录:")
            for i, row in enumerate(emp_data, 1):
                print(f"     {i}. {row}")
            
            # 检查职位分布
            cursor.execute("SELECT job_title, COUNT(*) as count FROM employees GROUP BY job_title ORDER BY count DESC")
            job_titles = cursor.fetchall()
            print(f"\n📊 职位分布 (共{len(job_titles)}种职位):")
            for job, count in job_titles:
                print(f"   • {job}: {count}人")
            
            # 检查部门分布
            cursor.execute("SELECT department_id, COUNT(*) as count FROM employees GROUP BY department_id ORDER BY count DESC")
            dept_ids = cursor.fetchall()
            print(f"\n📊 部门ID分布:")
            for dept_id, count in dept_ids:
                print(f"   • 部门ID {dept_id}: {count}人")
            
            # 检查薪资范围
            cursor.execute("SELECT MIN(salary) as min_salary, MAX(salary) as max_salary, AVG(salary) as avg_salary FROM employees")
            salary_stats = cursor.fetchone()
            print(f"\n📊 薪资统计:")
            print(f"   • 最低薪资: {salary_stats[0]}")
            print(f"   • 最高薪资: {salary_stats[1]}")
            print(f"   • 平均薪资: {salary_stats[2]:.2f}")
            
            # 检查入职日期范围
            cursor.execute("SELECT MIN(hire_date) as min_date, MAX(hire_date) as max_date FROM employees WHERE hire_date IS NOT NULL")
            date_stats = cursor.fetchone()
            print(f"\n📊 入职日期范围:")
            print(f"   • 最早入职: {date_stats[0]}")
            print(f"   • 最晚入职: {date_stats[1]}")
            
            # 检查活跃状态
            cursor.execute("SELECT is_active, COUNT(*) as count FROM employees GROUP BY is_active")
            active_stats = cursor.fetchall()
            print(f"\n📊 员工状态:")
            for status, count in active_stats:
                status_text = "活跃" if status else "非活跃"
                print(f"   • {status_text}: {count}人")
        
        # 检查departments表的数据
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        print(f"\n📊 departments表总记录数: {dept_count}")
        
        if dept_count > 0:
            cursor.execute("SELECT * FROM departments")
            dept_data = cursor.fetchall()
            print("   所有部门:")
            for i, row in enumerate(dept_data, 1):
                print(f"     {i}. {row}")
        
        # 测试联表查询
        print("\n📋 测试联表查询:")
        query = """
        SELECT d.name as department_name, e.job_title, e.salary, e.hire_date, e.is_active
        FROM employees e
        INNER JOIN departments d ON e.department_id = d.id
        WHERE e.is_active = 1
        LIMIT 10
        """
        cursor.execute(query)
        join_data = cursor.fetchall()
        print(f"📊 联表查询结果 (前10条):")
        for i, row in enumerate(join_data, 1):
            print(f"   {i}. 部门: {row[0]}, 职位: {row[1]}, 薪资: {row[2]}, 入职: {row[3]}, 活跃: {row[4]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        import traceback
        traceback.print_exc()

def analyze_user_query_problem():
    """分析用户查询问题"""
    print("\n" + "=" * 70)
    print("分析用户查询问题")
    print("=" * 70)
    
    print("🔍 用户查询分析:")
    print("参数:")
    print("  - target_departments: ['信息技术部', '销售部', '人力资源部']")
    print("  - min_salary_threshold: 15000")
    print("  - job_title: 'HR经理'")
    print("  - hire_date_from: '2025-01-15'")
    print("  - hire_date_to: '2025-06-15'")
    
    print("\n🚨 可能的问题:")
    print("1. 日期范围问题:")
    print("   - 查询日期: 2025-01-15 到 2025-06-15")
    print("   - 这是未来日期，数据库中可能没有这个时间段的数据")
    
    print("\n2. 条件表达式逻辑问题:")
    print("   - 过滤器: job_title = 'HR经理'")
    print("   - 条件: $job_title != 'HR经理'")
    print("   - 矛盾: 当job_title='HR经理'时，条件为false，过滤器被跳过")
    
    print("\n3. 部门名称匹配问题:")
    print("   - 查询部门: ['信息技术部', '销售部', '人力资源部']")
    print("   - 需要检查数据库中的实际部门名称是否匹配")

if __name__ == "__main__":
    print("🚀 开始数据库数据检查...")
    
    # 检查数据库数据
    check_database_data()
    
    # 分析查询问题
    analyze_user_query_problem()
    
    print("\n" + "=" * 70)
    print("🎉 数据库检查完成!")
    print("=" * 70)
