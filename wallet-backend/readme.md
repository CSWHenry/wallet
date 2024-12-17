确保你的本地MySQL服务已经启动，并且可以使用以下凭据连接：
主机：localhost
端口：3306
用户名：root
密码：123456

初始化数据库：
python create_db.py && python init_db.py && python create_admin.py

启动应用(DEBUG模式)：
set FLASK_APP=app.py && set FLASK_ENV=development && set FLASK_DEBUG=1 && flask run --host=0.0.0.0 --port=5000