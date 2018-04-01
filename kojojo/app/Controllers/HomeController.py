from flask import render_template, flash, session
from app import app


@app.route('/')
def index():
    flash(session)
    return render_template('base.html', title='Index')
