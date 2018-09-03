from flask import render_template, flash, redirect
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

@flask_obj.route('/login', methods=['GET','POST'])
def login():
	my_form = LoginForm()
	if my_form.validate_on_submit():
		flash('用户 %s 尝试登录，是否要求记忆登录信息？%s' % \
			(my_form.username.data, my_form.remember.data))
		page_view = redirect('/index')
	else:
		if (my_form.username.data or my_form.password.data or my_form.remember.data):
			flash('用户输入内容有误，请重新输入...')
		else:
			pass
		page_view = render_template('login.html', title='登录', form=my_form)
	return page_view
