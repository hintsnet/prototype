from flask import render_template
from webapp import flask_obj
from webapp.forms import LoginForm

@flask_obj.route('/')
@flask_obj.route('/index')
def index():
    my_users = { 'username': 'pimgeek' }
    my_posts = [
        {
            'author': { 'username': 'pimgeek' },
            'body': '一切有为法，皆梦幻泡影。'
        },
        {
            'author': { 'username': 'ceciliapple' },
            'body': 'Smelly Cat, Smelly Cat, What Do They Feed You?'
        }
    ]
    page_view = render_template('index.html', users=my_users, posts=my_posts)
    return page_view

@flask_obj.route('/login')
def login():
    my_form = LoginForm()
    page_view = render_template('login.html', title='登录', form=my_form)
    return page_view
