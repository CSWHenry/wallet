from app import create_app, db
from app.models.user import User, Email, Phone
from app.models.bank import BankAccount, UserBankAccount
from app.models.transaction import Transaction, PaymentRequest
import pymysql

def init_db():
    # 首先创建数据库
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='20021203csw',
        port=3306
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute('CREATE DATABASE IF NOT EXISTS wallet CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        connection.commit()
    finally:
        connection.close()

    # 然后创建表
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database and tables created successfully!")

if __name__ == '__main__':
    init_db() 