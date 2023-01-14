from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    remember = BooleanField("Remember Me")
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password1 = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Register')


class HomeWorkForm(FlaskForm):
    date = DateField('date', validators=[DataRequired()])
    subject = StringField('subject', validators=[DataRequired()])
    task = TextAreaField('task', validators=[DataRequired()])
    submit = SubmitField('Добавить')
