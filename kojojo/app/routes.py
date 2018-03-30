from flask_wtf.csrf import CSRFError

from app import app
from flask import render_template, flash, redirect, make_response, session
from app.forms import LoginForm, RegisterForm, EditAccountForm, ChangePassword
from werkzeug.security import check_password_hash, generate_password_hash
from uuid import uuid4 as guid
import pymysql.cursors


db = pymysql.connect(host='localhost',
                     user='kojojo',
                     password='kojojo',
                     db='KOJOJO',
                     charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor)

def get_user():
    if "session_id" in session:
        with db.cursor() as cursor:
            cursor.execute("SELECT UserId FROM Session WHERE SessionId = %s", (session["session_id"],))
            row = cursor.fetchone()
            if row is not None:
                cursor.execute("SELECT UserId, UserName, Email, Phone, PasswordHash, RegistrationDate FROM User WHERE UserId = %s", (row["UserId"],))
                row = cursor.fetchone()
                return row
    return None

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
        email, user, pwd, phone = form.email.data, form.username.data, form.password.data, form.phone.data

        pw_hash = generate_password_hash(pwd)
        with db.cursor() as cursor:
            cursor.execute("INSERT INTO User (UserName, PasswordHash, RegistrationDate, Email, Phone) "
                           "VALUES (%s, %s, CURRENT_DATE(), %s, %s)",
                           (user, pw_hash, email, phone))
        db.commit()
        flash('Inscription réussie, vous pouvez maintenant vous connecter')
        return redirect('/')

    return render_template('register.html', title='Inscription', form=form)

@app.route('/User/Profile', methods=['GET', 'POST'])
def edit_account():
    form = EditAccountForm()
    row = get_user()

    if form.validate_on_submit() and row is not None:
        user, email, phone = form.username.data, form.email.data, form.phone.data
        with db.cursor() as cursor:
            cursor.execute("UPDATE User "
                           "SET UserName = %s, Email = %s, Phone = %s "
                           "WHERE UserId = %s",
                           (user, email, phone, row["UserId"]))
        db.commit()
        flash('Mise à jour du profile réussie')
        return redirect('/')

    if row is not None:
        form.username.data = row["UserName"]
        form.email.data = row["Email"]
        form.confirm_email.data = row["Email"]
        form.phone.data = row["Phone"]
        return render_template('edit_account.html', title='Profile', form=form)

    return render_template('edit_account.html', title='Profile', form=form)

@app.route('/User/Password', methods=['GET', 'POST'])
def change_password():
    form = ChangePassword()
    row = get_user()

    if form.validate_on_submit():
        old_pwd, new_pwd = form.old_password.data, form.password.data
        if check_password_hash(row["PasswordHash"], old_pwd):
            with db.cursor() as cursor:
                cursor.execute("UPDATE User "
                               "SET PasswordHash = %s "
                               "WHERE UserId = %s",
                               (generate_password_hash(new_pwd), row["UserId"]))
            db.commit()
            flash('Mise à jour du mot de passe réussie')
            return redirect('/')
        flash('Mot de passe actuel incorrect')

    return render_template('change_password.html', title='Modifier son mot de passe', form=form)

@app.route('/User/Delete', methods=['GET'])
def delete_account():
    row = get_user()
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM User "
                       "WHERE UserId = %s",
                       (row["UserId"]),)
    db.commit()
    if 'session_id' in session:
        del session['session_id']

    return redirect('/')