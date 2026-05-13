#!/usr/bin/env python
"""
数据库迁移脚本 - 添加token相关字段
"""

import pymysql
import os
from config import Config

def migrate_database():
    """执行数据库迁移"""
    try:
        # 解析数据库连接信息
        uri = Config.SQLALCHEMY_DATABASE_URI
        # mysql+pymysql://user:pass@host/dbname
        
        # 提取用户名、密码、主机和数据库名
        # 移除 mysql+pymysql:// 前缀
        uri_without_prefix = uri.replace('mysql+pymysql://', '')
        
        # 分割用户名密码和主机数据库
        user_pass, host_db = uri_without_prefix.split('@')
        username, password = user_pass.split(':')
        host, db_name = host_db.split('/')
        
        # 连接数据库
        connection = pymysql.connect(
            host=host,
            user=username,
            password=password,
            database=db_name,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 检查token字段是否存在
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = '{db_name}' 
                AND TABLE_NAME = 'user' 
                AND COLUMN_NAME = 'token'
            """)
            
            token_exists = cursor.fetchone()[0] > 0
            
            if not token_exists:
                print("正在添加token字段...")
                # 添加token字段
                cursor.execute("""
                    ALTER TABLE user 
                    ADD COLUMN token VARCHAR(255) NULL,
                    ADD COLUMN token_expires DATETIME NULL,
                    ADD UNIQUE KEY uk_token (token)
                """)
                print("token字段添加成功")
            else:
                print("token字段已存在")
            
            # 检查其他可能需要的字段
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = '{db_name}' 
                AND TABLE_NAME = 'user' 
                AND COLUMN_NAME = 'token_expires'
            """)
            
            expires_exists = cursor.fetchone()[0] > 0
            
            if not expires_exists:
                print("正在添加token_expires字段...")
                cursor.execute("""
                    ALTER TABLE user 
                    ADD COLUMN token_expires DATETIME NULL
                """)
                print("token_expires字段添加成功")
            
            connection.commit()
            print("数据库迁移完成")
            
    except Exception as e:
        print(f"迁移失败: {e}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    migrate_database()