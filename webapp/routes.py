from flask import render_template
from webapp import flask_obj

@flask_obj.route('/')
@flask_obj.route('/index')
def index():
    users = { 'username': 'pimgeek' }
    return render_template('index.html', title='首页', users=users)
