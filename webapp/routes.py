from flask import render_template
from webapp import flask_obj

@flask_obj.route('/')
@flask_obj.route('/index')
def index():
    myusers = { 'username': 'pimgeek' }
    myposts = [
        {
            'author': { 'username': 'pimgeek' },
            'body': '一切有为法，皆梦幻泡影。'
        },
        {
            'author': { 'username': 'ceciliapple' },
            'body': 'Smelly Cat, Smelly Cat, What Do They Feed You?'
        }
    ]
    return render_template('index.html', users=myusers, posts=myposts)
