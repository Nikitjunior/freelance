from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired


class OrdersCreationForm(FlaskForm):
    order_title = StringField('Заголовок заказа', validators=[DataRequired()])
    description = TextAreaField("Описание заказа", validators=[DataRequired()])
    submit = SubmitField('Разместить')
    readonly = False
