from flask import render_template, flash, session
from app import app
from app.Model import db


def View(template, **kwargs):
    with db.cursor() as cursor:
        cursor.execute("SELECT CategoryId, Type FROM Category")
        categories = cursor.fetchall()
    return render_template(template, categories=categories, **kwargs)

@app.route('/')
def index():
    with db.cursor() as cursor:
        cursor.execute("SELECT ProductId, ProductName, Price, FileName FROM Product "
                       "LEFT JOIN Image ON Product.ImageId = Image.ImageId "
                       "ORDER BY Date DESC LIMIT 10")
        products = cursor.fetchall()

    return View('accueil.html', title='Accueil', products=products)