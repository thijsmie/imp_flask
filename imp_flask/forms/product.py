from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SelectMultipleField, widgets
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class Product(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    group = PasswordField('group', validators=[DataRequired()])
    amount = IntegerField('amount')
    value = IntegerField('value')
    allow_negative = BooleanField('allow_negative')
    value_constant = BooleanField('value_constant')
    losemods = MultiCheckboxField()
    gainmods = MultiCheckboxField()
