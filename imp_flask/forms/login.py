from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class Login(FlaskForm):
    username = StringField('name', validators=[DataRequired()])
    password = PasswordField('name', validators=[DataRequired()])