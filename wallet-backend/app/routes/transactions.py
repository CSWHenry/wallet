from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models.bank import BankAccount, UserBankAccount
from app.models.transaction import Transaction, TransactionType, TransactionStatus, PaymentRequest
from app.models.user import Email, Phone, User

bp = Blueprint('transactions', __name__)


# 转账
@bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({
                'error': 'Not Found',
                'message': 'User not found'
            }), 404


        data = request.get_json()
        sender_id = get_jwt_identity()

        # 验证必要字段
        required_fields = ['recipient_identifier', 'amount','source_account']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # 创建交易
        transaction = Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=data['amount'],
            note=data.get('note'),
            sender_id=sender_id,
            recipient_identifier=data['recipient_identifier'],
            sender_account=data['source_account'],
            created_at = datetime.utcnow()
        )

        # 查找接收者
        recipient_id = None
        if '@' in data['recipient_identifier']:
            email = Email.query.filter_by(email=data['recipient_identifier'], is_verified=True).first()
            if email:
                recipient_id = email.user_id
        else:
            phone = Phone.query.filter_by(phone=data['recipient_identifier'], is_verified=True).first()
            if phone:
                recipient_id = phone.user_id

        if recipient_id:
            transaction.recipient_id = recipient_id
            # 对双方银行账户进行操作
            account=BankAccount.query.filter_by(account_number=transaction.sender_account).first()
            if account:
                account.balance-=transaction.amount
            account=BankAccount.query.filter_by(account_number=UserBankAccount.query.filter_by(user_id=recipient_id).first().bank_account_id).first()
            if account:
                account.balance+=transaction.amount

            transaction.status = TransactionStatus.COMPLETED
            transaction.completed_at = datetime.utcnow()

        else:
            transaction.recipient_id=None
            transaction.status=TransactionStatus.PENDING
            #这里应该还有超过十五分钟 交易状态为 EXPIRE 的逻辑

        db.session.add(transaction)
        db.session.commit()

        return jsonify({'message': 'Transfer initiated successfully', 'transaction_id': transaction.id})
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

# 请求付款
@bp.route('/request', methods=['POST'])
@jwt_required()
def request_payment():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({
                'error': 'Not Found',
                'message': 'User not found'
            }), 404
        data = request.get_json()
        requester_id = get_jwt_identity()

        # 验证必要字段
        if not all(key in data for key in ['payers', 'total_amount']):
            return jsonify({'error': 'Missing required fields'}), 400

        # 创建交易
        transaction = Transaction(
            transaction_type=TransactionType.REQUEST,
            amount=data['total_amount'],
            note=data.get('note'),
            sender_id=requester_id

        )
        db.session.add(transaction)

        # 创建付款请求
        for payer in data['payers']:
            payment_request = PaymentRequest(
                transaction_id=transaction.id,
                requester_id=requester_id,
                payer_identifier=payer['identifier'],
                amount=payer['amount']
            )
            db.session.add(payment_request)

        db.session.commit()

        return jsonify({'message': 'Payment request created successfully', 'transaction_id': transaction.id})
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

# 获取交易历史
@bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():

    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({
                'error': 'Not Found',
                'message': 'User not found'
            }), 404

        user_id = get_jwt_identity()

        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        transaction_type = request.args.get('type')
        status = request.args.get('status')

        # 构建查询
        query = Transaction.query.filter(
            (Transaction.sender_id == user_id) | (Transaction.recipient_id == user_id)
        )

        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        if status:
            query = query.filter(Transaction.status == status)

        transactions = query.order_by(Transaction.created_at.desc()).all()

        return jsonify({
            'transactions': [{
                'id': t.id,
                'type': t.transaction_type.value,
                'status': t.status.value,
                'amount': t.amount,
                'note': t.note,
                'created_at': t.created_at.isoformat(),
                'completed_at': t.completed_at.isoformat() if t.completed_at else None
            } for t in transactions]
        })
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


#特定时间内取消转账
@bp.route('/transactions/cancel', methods=['GET'])
@jwt_required()
def cancel_transaction():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({
                'error': 'Not Found',
                'message': 'User not found'
            }), 404
        #逻辑是 根据交易id查询具体的转账双方 并恢复对应的账户数额
        transfer_id = request.args.get('transactionId')
        query=Transaction.query.filter_by(id=transfer_id,type='transfer').first()
        if query :
            #查看交易目前状态
            status=query.status
            if status == TransactionStatus.PENDING or status == TransactionStatus.EXPIRED:
                query.status=TransactionStatus.CANCELLED
            if status==TransactionStatus.COMPLETED:
                sender_account=query.sender_account
                # 查找接收者
                recipient_id = None
                if '@' in query.recipient_identifier:
                    email = Email.query.filter_by(email=query.recipient_identifier, is_verified=True).first()
                    if email:
                        recipient_id = email.user_id
                else:
                    phone = Phone.query.filter_by(phone=query.recipient_identifier, is_verified=True).first()
                if phone:
                    recipient_id = phone.user_id
                    # 对双方银行账户进行回退操作
                account = BankAccount.query.filter_by(account_number=sender_account).first()
                if account:
                    account.balance += query.amount
                    account = BankAccount.query.filter_by(account_number=UserBankAccount.query.filter_by(user_id=recipient_id).first().bank_account_id).first()
                    account.balance -= query.amount
                query.status = TransactionStatus.CANCELLED
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500