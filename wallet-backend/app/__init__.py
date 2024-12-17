from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "expose_headers": ["Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    
    # JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Token has expired'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Invalid token'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Missing authorization token'
        }), 401
        
    @jwt.user_lookup_error_loader
    def user_lookup_error_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Not Found',
            'message': 'User not found'
        }), 404
    
    # 注册蓝图
    from app.routes import api, dashboard,transactions
    app.register_blueprint(api.bp, url_prefix='/api')
    app.register_blueprint(dashboard.bp, url_prefix='/api/dashboard')
    app.register_blueprint(transactions.bp, url_prefix='/api/transactions')


    @app.route('/')
    def index():
        return 'Hello World!'
    return app 