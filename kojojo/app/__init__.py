from flask import Flask, flash, redirect
from flask_wtf.csrf import CSRFError

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash(e.description)
    return redirect('/')

from app.Controllers import HomeController, UserController