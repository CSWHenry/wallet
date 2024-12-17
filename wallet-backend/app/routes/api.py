from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, verify_jwt_in_request
from app.models.user import User, Email, Phone
from app.models.bank import BankAccount
from app.models.transaction import Transaction, PaymentRequest, TransactionStatus, TransactionType
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from functools import wraps
import random
import string
import traceback

bp = Blueprint('api', __name__)

# 管理员权限装饰器
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # 先验证JWT
        verify_jwt_in_request()
        
        # 然后获取用户身份
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({
                'status': 'error',
                'message': 'Admin privileges required'
            }), 403
            
        return fn(*args, **kwargs)
    return wrapper

# 用户认证相关路由
@bp.route('/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response

    try:
        data = request.get_json()
        print("Register request data:", data)
        
        # 验证必要字段
        required_fields = ['name', 'ssn', 'email', 'phone', 'password']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': 'Registration failed',
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # 检查SSN是否已存在
        if User.query.filter_by(ssn=data['ssn']).first():
            return jsonify({
                'status': 'error',
                'message': 'Registration failed',
                'error': 'SSN already registered'
            }), 400
            
        # 检查邮箱是否已存在
        if Email.query.filter_by(email=data['email']).first():
            return jsonify({
                'status': 'error',
                'message': 'Registration failed',
                'error': 'Email already registered'
            }), 400
            
        # 检查电话是否已存在
        if Phone.query.filter_by(phone=data['phone']).first():
            return jsonify({
                'status': 'error',
                'message': 'Registration failed',
                'error': 'Phone already registered'
            }), 400
        
        # 创建用户
        user = User(
            name=data['name'], 
            ssn=data['ssn'],
            balance=round(random.uniform(800, 1200), 2)
        )
        user.set_password(data['password'])
        db.session.add(user)
        print("User created:", user.id)
        
        # 添加邮箱
        email = Email(email=data['email'], verification_code=''.join(random.choices(string.digits, k=6)))
        user.emails.append(email)
        print("Email added:", email.email)
        
        # 添加电话
        phone = Phone(phone=data['phone'], verification_code=''.join(random.choices(string.digits, k=6)))
        user.phones.append(phone)
        print("Phone added:", phone.phone)
        
        # 提交事务
        try:
            db.session.commit()
            print("Database commit successful")
        except Exception as e:
            db.session.rollback()
            print("Database error during registration:", str(e))
            print("Traceback:", traceback.format_exc())
            return jsonify({
                'status': 'error',
                'message': 'Registration failed',
                'error': 'Database error during registration'
            }), 400
        
        # 生成访问令牌
        access_token = create_access_token(identity=user.id)
        print("Access token generated")
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': email.email,
                'phone': phone.phone,
                'balance': user.balance
            }
        }), 201
    except Exception as e:
        print("Register error:", str(e))
        print("Traceback:", traceback.format_exc())
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Registration failed',
            'error': str(e)
        }), 400

@bp.route('/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response, 200

    try:
        data = request.get_json()
        print("Login request data:", data)
        
        if not all(k in data for k in ('identifier', 'password')):
            return jsonify({
                'status': 'error',
                'message': 'Both identifier and password are required'
            }), 400
            
        # 通过邮箱或电话查找用户
        user = None
        if '@' in data['identifier']:
            email = Email.query.filter_by(email=data['identifier']).first()
            if email:
                user = email.user
        else:
            phone = Phone.query.filter_by(phone=data['identifier']).first()
            if phone:
                user = phone.user
                
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 401
            
        if not user.check_password(data['password']):
            return jsonify({
                'status': 'error',
                'message': 'Invalid password'
            }), 401
            
        # 生成访问令牌
        access_token = create_access_token(identity=str(user.id))
        
        # 准备用户信息
        user_info = user.to_dict()
        
        # 准备响应数据
        response_data = {
            'data': {
                'access_token': access_token,
                'user': user_info
            },
            'message': 'Login successful'
        }
        
        response = jsonify(response_data)
        return response, 200
        
    except Exception as e:
        print("Login error:", str(e))
        print("Traceback:", traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# 验证邮箱
@bp.route('/verify/email', methods=['POST'])
@jwt_required()
def verify_email():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    email = Email.query.filter_by(user_id=user_id, email=data['email']).first()
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    if email.verification_code != data['code']:
        return jsonify({'error': 'Invalid verification code'}), 400
    
    email.is_verified = True
    db.session.commit()
    
    return jsonify({'message': 'Email verified successfully'})

# 验证电话
@bp.route('/verify/phone', methods=['POST'])
@jwt_required()
def verify_phone():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    phone = Phone.query.filter_by(user_id=user_id, phone=data['phone']).first()
    if not phone:
        return jsonify({'error': 'Phone not found'}), 404
    
    if phone.verification_code != data['code']:
        return jsonify({'error': 'Invalid verification code'}), 400
    
    phone.is_verified = True
    db.session.commit()
    
    return jsonify({'message': 'Phone verified successfully'})

# 添加银行账户
@bp.route('/bank-accounts', methods=['POST'])
@jwt_required()
def add_bank_account():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    # 验证必要字段
    required_fields = ['bank_id', 'account_number']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # 检查账户是否已存在
    bank_account = BankAccount.query.filter_by(
        bank_id=data['bank_id'],
        account_number=data['account_number']
    ).first()
    
    if not bank_account:
        bank_account = BankAccount(
            bank_id=data['bank_id'],
            account_number=data['account_number'],
            verification_amount=round(random.uniform(0.01, 0.99), 2)
        )
        db.session.add(bank_account)
    
    user = User.query.get(user_id)
    if bank_account not in user.bank_accounts:
        user.bank_accounts.append(bank_account)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Bank account added successfully',
        'verification_amount': bank_account.verification_amount
    })

# 转账
@bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    data = request.get_json()
    sender_id = get_jwt_identity()
    
    # 验证必要字段
    required_fields = ['recipient_identifier', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # 创建交易
    transaction = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=data['amount'],
        note=data.get('note'),
        sender_id=sender_id,
        recipient_identifier=data['recipient_identifier']
    )
    
    # 查找接收者
    recipient = None
    if '@' in data['recipient_identifier']:
        email = Email.query.filter_by(email=data['recipient_identifier'], is_verified=True).first()
        if email:
            recipient = email.user
    else:
        phone = Phone.query.filter_by(phone=data['recipient_identifier'], is_verified=True).first()
        if phone:
            recipient = phone.user
    
    if recipient:
        transaction.recipient_id = recipient.id
        transaction.status = TransactionStatus.COMPLETED
        transaction.completed_at = datetime.utcnow()
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Transfer initiated successfully', 'transaction_id': transaction.id})

# 请求付款
@bp.route('/request-payment', methods=['POST'])
@jwt_required()
def request_payment():
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

# 获取交易历史
@bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
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

# Dashboard相关路由
@bp.route('/dashboard/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    try:
        # 获取用户ID并打印日志
        current_user_id = get_jwt_identity()
        print(f"Accessing dashboard for user ID: {current_user_id}")
        
        # 获取用户信息
        user = User.query.get(current_user_id)
        if not user:
            print(f"User not found for ID: {current_user_id}")
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
            
        print(f"Found user: {user.name} (ID: {user.id})")
            
        # 获取待处理交易的总额
        pending_balance = db.session.query(func.sum(Transaction.amount)).\
            filter(
                Transaction.user_id == current_user_id,
                Transaction.status == TransactionStatus.PENDING
            ).scalar() or 0.0
            
        # 获取本月交易总额
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        monthly_activity = db.session.query(func.sum(func.abs(Transaction.amount))).\
            filter(
                Transaction.user_id == current_user_id,
                Transaction.created_at >= month_start,
                Transaction.status == TransactionStatus.COMPLETED
            ).scalar() or 0.0
        
        # 准备响应数据
        response_data = {
            'status': 'success',
            'data': {
                'total_balance': float(user.balance),
                'pending_balance': float(pending_balance),
                'monthly_activity': float(monthly_activity)
            }
        }
        print(f"Dashboard data: {response_data}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error getting dashboard overview: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/dashboard/recent-transactions', methods=['GET'])
@jwt_required()
def get_recent_transactions():
    current_user_id = get_jwt_identity()
    
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 限制每页最大条数
        per_page = min(per_page, 50)
        
        # 查询交易记录
        query = Transaction.query.\
            filter(Transaction.user_id == current_user_id).\
            order_by(desc(Transaction.created_at))
            
        # 执行分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        transactions = pagination.items
            
        response = make_response(jsonify({
            'status': 'success',
            'data': {
                'transactions': [{
                    'id': f"TX{tx.id}",
                    'date': tx.created_at.isoformat(),
                    'type': 'Received' if tx.amount > 0 else 'Sent',
                    'description': tx.description or '',
                    'amount': round(float(tx.amount), 2),
                    'status': tx.status.value
                } for tx in transactions],
                'pagination': {
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'current_page': page,
                    'per_page': per_page,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        }))
        
        # 添加缓存控制
        response.headers['Cache-Control'] = 'no-cache'  # 不缓存交易记录
        return response
        
    except Exception as e:
        print(f"Error getting recent transactions: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return jsonify({
            'error': 'Failed to get recent transactions',
            'message': str(e)
        }), 500

@bp.route('/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    current_user_id = get_jwt_identity()
    
    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'message': 'The requested user does not exist'
            }), 404
            
        # 获取主要邮箱和电话
        primary_email = user.emails[0] if user.emails else None
        primary_phone = user.phones[0] if user.phones else None
            
        response = make_response(jsonify({
            'status': 'success',
            'data': {
                'id': user.id,
                'name': user.name,
                'email': primary_email.email if primary_email else None,
                'phone': primary_phone.phone if primary_phone else None,
                'email_verified': primary_email.is_verified if primary_email else False,
                'phone_verified': primary_phone.is_verified if primary_phone else False,
                'avatar': None  # 暂时不支持头像
            }
        }))
        
        # 添加缓存控制
        response.headers['Cache-Control'] = 'private, max-age=300'  # 5分钟缓存
        return response
        
    except Exception as e:
        print(f"Error getting user profile: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return jsonify({
            'error': 'Failed to get user profile',
            'message': str(e)
        }), 500

# 错误处理
@bp.errorhandler(401)
def unauthorized(e):
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication is required to access this resource'
    }), 401

@bp.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404

@bp.errorhandler(500)
def server_error(e):
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

# 管理员API - 获取所有账户
@bp.route('/admin/accounts', methods=['GET', 'OPTIONS'])
def get_all_accounts():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
    
    # 使用装饰器验证权限
    @admin_required
    def handle_request():
        try:
            # 打印请求信息
            print("Request headers:", dict(request.headers))
            print("Authorization:", request.headers.get('Authorization'))
            
            current_user_id = get_jwt_identity()
            print("Current user ID:", current_user_id)
            
            # 获取所有用户
            users = User.query.all()
            accounts = []
            
            for user in users:
                account_info = user.to_dict()
                # 计算用户的总余额
                total_balance = db.session.query(func.sum(BankAccount.balance))\
                    .filter(BankAccount.users.any(id=user.id))\
                    .scalar() or 0.0
                account_info['balance'] = round(float(total_balance), 2)
                accounts.append(account_info)
                
            response = jsonify({
                'status': 'success',
                'data': {
                    'accounts': accounts
                }
            })
            
            # 设置响应头
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            return response
            
        except Exception as e:
            print("Error getting accounts:", str(e))
            print("Traceback:", traceback.format_exc())
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    return handle_request()

# 管理员API - 转账
@bp.route('/admin/transfer', methods=['POST'])
@jwt_required()
@admin_required
def admin_transfer():
    try:
        data = request.get_json()
        
        # 验证必要字段
        if not all(k in data for k in ('to_account', 'amount')):
            return jsonify({
                'error': 'Invalid request',
                'message': 'to_account and amount are required'
            }), 400
            
        # 解析账户ID
        to_account_id = int(data['to_account'].replace('ACC', ''))
        from_account_id = int(data['from_account'].replace('ACC', '')) if 'from_account' in data else None
        
        # 验证目标账户
        to_user = User.query.get(to_account_id)
        if not to_user:
            return jsonify({
                'error': 'Invalid account',
                'message': 'Target account not found'
            }), 404
            
        # 如果指定了源账户，验证源账户
        from_user = None
        if from_account_id:
            from_user = User.query.get(from_account_id)
            if not from_user:
                return jsonify({
                    'error': 'Invalid account',
                    'message': 'Source account not found'
                }), 404
        
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({
                'error': 'Invalid amount',
                'message': 'Amount must be positive'
            }), 400
            
        # 创建交易记录
        transaction = Transaction(
            user_id=to_user.id,
            amount=amount,
            description=data.get('note', 'Admin transfer'),
            type=TransactionType.TRANSFER,
            status=TransactionStatus.COMPLETED
        )
        
        # 更新账户余额
        if from_user:
            # 用户间转账
            from_account = from_user.bank_accounts[0] if from_user.bank_accounts else None
            if not from_account or from_account.balance < amount:
                return jsonify({
                    'error': 'Insufficient funds',
                    'message': 'Source account has insufficient funds'
                }), 400
            from_account.balance -= amount
            
        to_account = to_user.bank_accounts[0] if to_user.bank_accounts else None
        if not to_account:
            # 如果用户没有银行账户，创建一个
            to_account = BankAccount(
                bank_name='Default Bank',
                account_number=''.join(random.choices(string.digits, k=10)),
                balance=0
            )
            to_user.bank_accounts.append(to_account)
            
        to_account.balance += amount
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transfer completed successfully',
            'transaction_id': f"TX{transaction.id}"
        })
        
    except Exception as e:
        print("Transfer error:", str(e))
        print("Traceback:", traceback.format_exc())
        db.session.rollback()
        return jsonify({
            'error': 'Transfer failed',
            'message': str(e)
        }), 500 