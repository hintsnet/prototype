from flask import render_template, flash, redirect, url_for, g
from webapp import flask_app
from webapp.forms import LoginForm
from neo4j import GraphDatabase

neo4j_drv = GraphDatabase.driver(flask_app.config['NEO4J_DB_URI'], \
	auth=(flask_app.config['NEO4J_DB_USR'], flask_app.config['NEO4J_DB_KEY']))

def get_db():
	if not hasattr(g, 'neo4j_db'):
		g.neo4j_db = neo4j_drv.session()
	return g.neo4j_db
	
@flask_app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'neo4j_db'):
		g.neo4j_db.close()
		
@flask_app.route('/')
@flask_app.route('/index')
def index():
	my_user = { 'username': 'pimgeek' }
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
	page_view = render_template('index.html', user=my_user, posts=my_posts)
	return page_view

@flask_app.route('/cards')
def cards():
	my_user = { 'username': 'pimgeek' }
	my_cards = get_cards()
	page_view = render_template('cards.html', user=my_user, cards=my_cards)
	return page_view

def get_cards():
	db = get_db()
	results = db.run("match (c)" "RETURN c.title as title, c.content as content")
	cards = []
	for record in results:
		cards.append({'title': record['title'], 'content': record['content']})
	return cards
	
@flask_app.route('/login', methods=['GET','POST'])
def login():
	my_form = LoginForm()
	if my_form.validate_on_submit():
		flash('用户 %s 尝试登录，是否要求记忆登录信息？%s' % \
			(my_form.username.data, my_form.remember.data))
		page_view = redirect(url_for('index'))
	else:
		if (my_form.username.data or my_form.password.data or my_form.remember.data):
			flash('用户输入内容有误，请重新输入...')
		else:
			pass
		page_view = render_template('login.html', title='登录', form=my_form)
	return page_view