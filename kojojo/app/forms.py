from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, length
from wtforms.fields.html5 import TelField, EmailField


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Connexion')

class RegisterForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[
        DataRequired(),
        length(max=45, min=4, message='Le nom d\'utilisateur doit faire entre 4 et 45 caractères')
    ])
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(),
        length(max=45, message='Le courriel ne peut pas faire plus de 45 caractères'),
        EqualTo('confirm_email', message='La confirmation doit être identique au courriel')
    ])
    confirm_email = EmailField('Confirmation email', validators=[
        DataRequired()
    ])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(),
        EqualTo('confirm_password', message='La confirmation doit être identique au mot de passe'),
        length(min=6, message='Le mot de passe doit faire au moins 6 caractère')
    ])
    confirm_password = PasswordField('Confirmation mot de passe')
    phone = TelField('Téléphone', validators=[
        length(max=45, message='Le numéro de téléphone ne peut pas faire plus de 45 caractères')
    ])
    submit = SubmitField('Inscription')