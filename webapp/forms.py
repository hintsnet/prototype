from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
	username = StringField('用户名', validators=[DataRequired()])
	password = PasswordField('密　码', validators=[DataRequired()])
	remember = BooleanField('记住我')
	submit = SubmitField('提交')

class CreateCardForm(FlaskForm):
	card_title = StringField('卡片标题', validators=[DataRequired()])
	card_content = TextAreaField('卡片文字', validators=[DataRequired()])
	submit = SubmitField('提交')