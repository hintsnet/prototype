from webapp import flask_obj

@flask_obj.route('/')
@flask_obj.route('/index')
def index():
    return '你好，世界！\n'
