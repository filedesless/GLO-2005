from flask import render_template, flash, session
from app import app
from app.Model import db


@app.route('/')
def index():
    products = []

    with db.cursor() as cursor:
        cursor.execute("SELECT ProductId, ProductName, Price FROM Product ORDER BY Date DESC LIMIT 10")
        products = cursor.fetchall()

    return render_template('accueil.html', title='Accueil', products=products)