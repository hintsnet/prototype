from webapp import flask_obj

@flask_obj.route('/')
@flask_obj.route('/index')
def index():
    users = { 'username': 'pimgeek' }
    return '''
<html>
    <head>
        <title>首页 - 引思网卡片库</title>
    </head>
    <body>
        <h1>你好，''' + users['username'] + '''！</h1>
    </body>
</html>
    '''
