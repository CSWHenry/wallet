from app import db
from datetime import datetime
import enum

class TransactionType(enum.Enum):
    TRANSFER = "transfer"
    REQUEST = "request"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # 正数表示收入，负数表示支出
    description = db.Column(db.String(200))
    status = db.Column(db.Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    type = db.Column(db.Enum(TransactionType), nullable=False)
    sender_account=db.Column(db.String(30)) #如果type是transfer 则需要填发送者的银行账户 接收方默认是primary账户
    recipient_identifier=db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))

class PaymentRequest(db.Model):
    __tablename__ = 'payment_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payer_identifier = db.Column(db.String(120), nullable=False)  # email or phone
    payer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # 关联
    transaction = db.relationship('Transaction', backref=db.backref('payment_requests', lazy=True))
    requester = db.relationship('User', foreign_keys=[requester_id], backref=db.backref('requested_payments', lazy=True))
    payer = db.relationship('User', foreign_keys=[payer_id], backref=db.backref('pending_payments', lazy=True))
    