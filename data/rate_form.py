from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired, NumberRange, ReadOnly


class RateForm(FlaskForm):
    rate = IntegerField("Оценка", validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Оценить')