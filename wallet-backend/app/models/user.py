from app import db
from datetime import datetime
import bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ssn = db.Column(db.String(11), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联
    emails = db.relationship('Email', backref='user', lazy=True)
    phones = db.relationship('Phone', backref='user', lazy=True)
    bank_accounts = db.relationship('BankAccount', secondary='user_bank_accounts', back_populates='users')
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        
    def to_dict(self):
        """返回用户的字典表示"""
        primary_email = self.emails[0] if self.emails else None
        primary_phone = self.phones[0] if self.phones else None
        return {
            'id': f"ACC{self.id}",
            'name': self.name,
            'email': primary_email.email if primary_email else None,
            'phone': primary_phone.phone if primary_phone else None,
            'is_admin': self.is_admin,
            'balance': self.balance
        }

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 