from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from app import db

bp = Blueprint('dashboard', __name__)

@bp.route('/overview', methods=['GET'])
@jwt_required()
def get_overview():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({
                'error': 'Not Found',
                'message': 'User not found'
            }), 404

        # 获取总余额
        total_balance = user.balance

        # 获取待处理余额（未完成的交易总额）
        pending_balance = db.session.query(func.sum(Transaction.amount))\
            .filter(Transaction.sender_id == current_user_id)\
            .filter(Transaction.status == TransactionStatus.PENDING)\
            .scalar() or 0.0

        # 获取本月活动金额
        first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_activity = db.session.query(func.sum(func.abs(Transaction.amount)))\
            .filter(
                (Transaction.sender_id == current_user_id) | (Transaction.receiver_id == current_user_id),
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.created_at >= first_day_of_month
            ).scalar() or 0.0

        return jsonify({
            'data': {
                'total_balance': round(float(total_balance), 2),
                'pending_balance': round(float(pending_balance), 2),
                'monthly_activity': round(float(monthly_activity), 2)
            },
            'message': 'success'
        })

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@bp.route('/recent-transactions', methods=['GET'])
@jwt_required()
def get_recent_transactions():
    try:
        current_user_id = get_jwt_identity()
        limit = request.args.get('limit', default=5, type=int)

        # 获取用户的最近交易
        transactions = Transaction.query\
            .filter(
                ((Transaction.sender_id == current_user_id) | (Transaction.receiver_id == current_user_id)) &
                (Transaction.status == TransactionStatus.COMPLETED)
            )\
            .order_by(desc(Transaction.created_at))\
            .limit(limit)\
            .all()

        transaction_list = []
        for tx in transactions:
            is_sender = tx.sender_id == current_user_id
            transaction_list.append({
                'date': tx.created_at.isoformat(),
                'type': 'Sent' if is_sender else 'Received',
                'description': tx.description,
                'amount': round(-float(tx.amount), 2) if is_sender else round(float(tx.amount), 2)
            })

        return jsonify({
            'data': {
                'transactions': transaction_list
            },
            'message': 'success'
        })

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500

@bp.route('/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'error': 'Not Found',
                'message': 'User not found'
            }), 404

        # 获取用户的主要邮箱和电话
        primary_email = user.emails[0].email if user.emails else None
        primary_phone = user.phones[0].phone if user.phones else None

        return jsonify({
            'data': {
                'name': user.name,
                'email': primary_email,
                'phone': primary_phone,
                'is_admin': user.is_admin
            },
            'message': 'success'
        })

    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500 