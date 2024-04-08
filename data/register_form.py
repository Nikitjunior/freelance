from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Электронная почта', validators=[DataRequired()])
    password = PasswordField('Пороль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пороль', validators=[DataRequired()])
    surname = StringField("Фамилия", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    speciality = StringField("Профессия", validators=[DataRequired()])
    phone_number = StringField("Номер телефона", validators=[DataRequired()])
    submit = SubmitField('Submit')
