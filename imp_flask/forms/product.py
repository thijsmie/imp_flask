from flask_wtf import FlaskForm
from wtforms import Field, StringField, PasswordField, IntegerField, BooleanField, FieldList
from wtforms.validators import DataRequired, ValidationError



class Product(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    group = StringField('group', validators=[DataRequired()])
    amount = IntegerField('amount')
    value = IntegerField('value')
    allow_negative = BooleanField('allow_negative')
    value_constant = BooleanField('value_constant')
    losemods = FieldList(IntegerField('losemods'))
    gainmods = FieldList(IntegerField('gainmods'))
