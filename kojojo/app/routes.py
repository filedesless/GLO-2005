from flask_wtf.csrf import CSRFError

from app import app
from flask import render_template, flash, redirect, make_response, session
from app.forms import LoginForm, RegisterForm
from werkzeug.security import check_password_hash, generate_password_hash
from uuid import uuid4 as guid
import pymysql.cursors


db = pymysql.connect(host='localhost',
                     user='kojojo',
                     password='kojojo',
                     db='KOJOJO',
                     charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor)

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash(e.description)
    return redirect('/')

@app.route('/')
def index():
    flash(session)
    return render_template('base.html', title='Index')

@app.route('/User/SignIn', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with db.cursor() as cursor:
            cursor.execute("SELECT UserId, PasswordHash FROM User WHERE Email = %s", (form.email.data,))
            row = cursor.fetchone()
            if row is not None and check_password_hash(row["PasswordHash"], form.password.data):
                session_id = guid().hex
                cursor.execute("INSERT INTO Session (SessionId, UserId) VALUES (%s, %s)", (session_id, row["UserId"]))
                db.commit()
                session["session_id"] = session_id
                flash('Connexion réussie pour l\'utilisateur {}'.format(form.email.data))
                return redirect('/')
            else:
                flash('Tentative de connection incorrecte')

    return render_template('login.html', title='Connexion', form=form)

@app.route('/User/SignOut', methods=['GET'])
def logout():
    if 'session_id' in session:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM Session WHERE SessionId = %s", (session["session_id"],))
        db.commit()
        del session['session_id']

    flash('Déconnexion réussie')
    return redirect('/')

@app.route('/User/Register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email, usr, pwd, phone = form.email.data, form.username.data, form.password.data, form.phone.data
        valid = True
        if len(email) > 45:
            flash('Le courriel ne peut pas faire plus de 45 caractères')
            valid = False
        if len(usr) < 4 or len(usr) > 45:
            flash('Le nom d\'utilisateur doit être entre 4 et 45 caractères')
            valid = False
        if len(pwd) < 6:
            flash('Le mot de passe doit faire plus de 6 caractères')
            valid = False
        if len(phone) > 45:
            flash('Le téléphone doit faire moins de 45 caractères')
            valid = False

        if valid:
            pw_hash = generate_password_hash(pwd)
            with db.cursor() as cursor:
                cursor.execute("INSERT INTO User (UserName, PasswordHash, RegistrationDate, Email, Phone) "
                               "VALUES (%s, %s, CURRENT_DATE(), %s, %s)",
                               (usr, pw_hash, email, phone))
            db.commit()
            flash('Inscription réussie, vous pouvez maintenant vous connecter')
            return redirect('/')

    return render_template('register.html', title='Inscription', form=form)

