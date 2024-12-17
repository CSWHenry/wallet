from app import create_app, db
from app.models.user import User, Email, Phone

def create_admin():
    app = create_app()
    with app.app_context():
        # 检查管理员是否已存在
        admin_email = "admin@wallet.com"
        email = Email.query.filter_by(email=admin_email).first()
        if email:
            print("Admin already exists!")
            return
            
        # 创建管理员用户
        admin = User(
            name="System Admin",
            ssn="000-00-0000",
            is_admin=True
        )
        admin.set_password("Admin@123")
        
        # 添加邮箱
        email = Email(
            email=admin_email,
            is_verified=True
        )
        admin.emails.append(email)
        
        # 添加电话
        phone = Phone(
            phone="0000000000",
            is_verified=True
        )
        admin.phones.append(phone)
        
        # 保存到数据库
        db.session.add(admin)
        db.session.commit()
        
        print("Admin account created successfully!")
        print("Email:", admin_email)
        print("Password: Admin@123")

if __name__ == '__main__':
    create_admin() 