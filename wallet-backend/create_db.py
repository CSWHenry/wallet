import pymysql

def create_database():
    # 连接到MySQL服务器
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='20021203csw',
        port=3306
    )
    
    try:
        with connection.cursor() as cursor:
            # 删除已存在的数据库
            cursor.execute('DROP DATABASE IF EXISTS wallet')
            # 创建新数据库
            cursor.execute('CREATE DATABASE wallet CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
            print("Database created successfully!")
    finally:
        connection.close()

if __name__ == '__main__':
    create_database() 