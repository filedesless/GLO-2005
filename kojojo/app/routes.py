from app import app
from flask import render_template, flash, redirect, make_response, session
from app.forms import LoginForm
from werkzeug.security import check_password_hash
from uuid import uuid4 as guid
import pymysql.cursors


db = pymysql.connect(host='localhost',
                     user='kojojo',
                     password='kojojo',
                     db='KOJOJO',
                     charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def hello_world():
    return render_template('base.html')

@app.route('/User/SignIn', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(session)
    if form.validate_on_submit():
        with db.cursor() as cursor:
            cursor.execute("SELECT UserId, PasswordHash FROM User WHERE Email = %s", (form.email.data,))
            row = cursor.fetchone()
            if row is not None and check_password_hash(row["PasswordHash"], form.password.data):
                session_id = guid().hex
                cursor.execute("INSERT INTO Session (SessionId, UserId) VALUES (%s, %s)", (session_id, row["UserId"]))
                db.commit()
                session["session_id"] = session_id
                flash('Login requested for user {}'.format(form.email.data))
                return redirect('/')
            else:
                flash('Tentative de connection incorrecte')

    return render_template('login.html', title='Connexion', form=form)

@app.route('/User/SignOut', methods=['GET'])
def logout():
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM Session WHERE SessionId = %s", (session["session_id"],))
    db.commit()
    del session["session_id"]
    flash('Déconnexion réussie')
    return redirect('/')