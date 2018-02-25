from app import app
from flask import render_template, flash, redirect
from app.forms import LoginForm


@app.route('/')
def hello_world():
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}'.format(form.username.data))
        return redirect('/')
    return render_template('login.html', title='Connexion', form=form)