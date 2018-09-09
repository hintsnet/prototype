# 导入 webapp 子目录中的 flask_app 对象
# 需要查看 webapp/__init__.py 了解该对象的详细情况
from webapp import flask_app
print(" * 运行环境中预设的 APP 密钥为：%s" % flask_app.config['SECRET_KEY'])
