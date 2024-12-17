#!/bin/bash

# 激活虚拟环境
source venv/bin/activate

# 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# 启动应用
flask run --host=0.0.0.0 --port=5000 