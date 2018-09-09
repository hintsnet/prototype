from flask import Flask
from config import Config

flask_app = Flask(__name__)
flask_app.config.from_object(Config)

# 网站的各个路由及其处理函数定义，都包含在 routes.py 中
from webapp import routes
