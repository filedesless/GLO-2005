import os
from uuid import uuid4

from werkzeug.utils import secure_filename

from app import app
from flask import render_template, flash, redirect, session, request, url_for
from app.Model import db, get_user
from app.forms import NewProductForm
from app.authorize import authorize


def View(template, **kwargs):
    with db.cursor() as cursor:
        cursor.execute("SELECT CategoryId, Type FROM Category")
        categories = cursor.fetchall()
    return render_template(template, categories=categories, **kwargs)

@app.route('/Product/Add', methods=['GET', 'POST'])
def add_product():
    if not authorize():
        return redirect('/User/SignIn')

    form = NewProductForm()

    with db.cursor() as cursor:
        cursor.execute("SELECT CategoryId, Type FROM Category")
        form.category.choices = [('--', '-- Veuillez sélectionner une catégorie --')] + [
            (str(row["CategoryId"]), row["Type"]) for row in cursor.fetchall()]

    if form.validate_on_submit():
        if form.category.data != '--':
            with db.cursor() as cursor:
                town = form.town.data
                cursor.execute("SELECT TownId FROM Town "
                               "WHERE TownName = %s", (town, ))
                row = cursor.fetchone()
                if row is None:
                    cursor.execute("INSERT INTO Town (TownName) VALUES (%s)", (town,))

                filename = ""
                if form.image.data is not None:
                    u = uuid4().hex
                    filename = "{}.{}".format(u, secure_filename(form.image.data.filename).split('.')[-1])
                    form.image.data.save(os.path.join(
                        app.static_folder, app.config["UPLOAD_FILE"], filename
                    ))
                    cursor.execute("INSERT INTO Image (FileName) "
                                   "VALUES (%s)", (filename,))


                user = get_user()
                cursor.execute("INSERT INTO Product (ProductName, Price, Description, Date, CategoryId, UserId, TownId, ImageId) "
                               "VALUES (%s, %s, %s, NOW(), %s, %s, "
                               "(SELECT TownId FROM Town WHERE TownName = %s), "
                               "(SELECT ImageId FROM Image WHERE FileName = %s))", (form.name.data,
                                                                                     form.price.data,
                                                                                     form.description.data,
                                                                                     form.category.data,
                                                                                     user["UserId"],
                                                                                     town,
                                                                                     filename))
                db.commit()
                return redirect('/')
        else:
            flash('Veuillez choisir une catégorie')

    return View('add_product.html', title='Nouveau produit', form=form)

@app.route('/Product/Search/<query>', methods=['GET'])
def search_product(query: str):
    with db.cursor() as cursor:
        cursor.execute("SELECT ProductId, ProductName, Price FROM Product "
                       "WHERE ProductName LIKE %s "        
                       "ORDER BY Date DESC", ("%{}%".format(query),))
        products = cursor.fetchall()

    return View('list_product.html', products=products, title="Liste des correspondant à la recherche")

@app.route('/Product/FromCategory/<id>', methods=['GET'])
def product_by_category(id: int):
    with db.cursor() as cursor:
        cursor.execute("SELECT ProductId, ProductName, Price FROM Product "
                       "WHERE Product.CategoryId = %s "        
                       "ORDER BY Date DESC", (id,))
        products = cursor.fetchall()

    return View('list_product.html', products=products, title="Liste des correspondant à la recherche")


@app.route('/Product/List', methods=['GET'])
def list_products():
    with db.cursor() as cursor:
        cursor.execute("SELECT Product.ProductId, ProductName, Price, FileName FROM Product "
                       "LEFT JOIN Image ON Image.ImageId = Product.ImageId "
                       "ORDER BY Date DESC")
        products = cursor.fetchall()

    return View('list_product.html', products=products, title="Liste des articles publiés")

@app.route('/Product/<int:id>', methods=['GET'])
def show_product(id):
    with db.cursor() as cursor:
        cursor.execute("SELECT ProductId, ProductName, Price, Description, Date, TownName, Type, Product.UserId, UserName, Email, Phone, FileName FROM Product "
                       "INNER JOIN User ON Product.UserId = User.UserId "
                       "INNER JOIN Town ON Product.TownId = Town.TownId "
                       "INNER JOIN Category ON Product.CategoryId = Category.CategoryId "
                       "LEFT JOIN Image ON Product.ImageId = Image.ImageId "
                       "WHERE ProductId = %s", (id,))
        product = cursor.fetchone()
        if product is not None:
            user = get_user()
            is_author = user is not None and user["UserId"] == product["UserId"]
        else:
            product = []
            is_author = False

    return View('show_product.html', title='Accueil', product=product, is_author=is_author)

@app.route('/Product/Edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    form = NewProductForm()
    user = get_user()

    with db.cursor() as cursor:
        cursor.execute("SELECT UserId, ProductName, Price, Description, TownName, Product.CategoryId, Type FROM Product "
                       "INNER JOIN Town ON Product.TownId = Town.TownId "
                       "INNER JOIN Category ON Product.CategoryId = Category.CategoryId "
                       "WHERE ProductId = %s", (id,))
        product = cursor.fetchone()
        if product is None:
            flash('Produit invalide')
            return redirect('/')

        if user is None:
            return redirect('/User/SignIn')
        elif user["UserId"] != product["UserId"]:
            return redirect('/')

        cursor.execute("SELECT CategoryId, Type FROM Category")
        form.category.choices = [(str(product["CategoryId"]), product["Type"])] + [
            (str(row["CategoryId"]), row["Type"]) for row in cursor.fetchall() if row["CategoryId"] != product["CategoryId"]]


    if form.validate_on_submit():
        town = form.town.data
        with db.cursor() as cursor:
            if product["TownName"] != town:
                cursor.execute("SELECT TownId FROM Town "
                               "WHERE TownName = %s", (town,))
                row = cursor.fetchone()
                if row is None:
                    cursor.execute("INSERT INTO Town (TownName) VALUES (%s)", (town,))

            cursor.execute("SELECT CategoryId FROM Category "
                           "WHERE CategoryId = %s", (form.category.data,))
            row = cursor.fetchone()
            if row is None:
                flash('Catégorie invalide')
                return redirect('/')

            if form.image.data is not None:
                u = uuid4().hex
                filename = "{}.{}".format(u, secure_filename(form.image.data.filename).split('.')[-1])
                form.image.data.save(os.path.join(
                    app.static_folder, app.config["UPLOAD_FILE"], filename
                ))
                cursor.execute("INSERT INTO Image (FileName) "
                               "VALUES (%s)", (filename,))

                cursor.execute("UPDATE PRODUCT "
                               "SET ProductName = %s, Price = %s, Description = %s, Date = NOW(), CategoryId = %s, "
                               "ImageId = (SELECT ImageId FROM Image WHERE FileName = %s), "
                               "TownId = (SELECT TownId FROM Town WHERE TownName = %s) "
                               "WHERE ProductId = %s", (form.name.data, form.price.data, form.description.data, form.category.data, filename, town, id))

            else:
                cursor.execute("UPDATE PRODUCT "
                               "SET ProductName = %s, Price = %s, Description = %s, Date = NOW(), CategoryId = %s, "
                               "TownId = (SELECT TownId FROM Town WHERE TownName = %s) "
                               "WHERE ProductId = %s", (form.name.data, form.price.data, form.description.data, form.category.data, town, id))
            db.commit()
            flash("L'annonce a bien été modifiée")
            return redirect('/')

    form.name.data = product["ProductName"]
    form.price.data = product["Price"]
    form.description.data = product["Description"]
    form.town.data = product["TownName"]
    form.category.data = product["Type"]

    return View('edit_product.html', title="Modifier l'annonce", form=form)


@app.route('/Product/Remove/<int:id>', methods=['GET'])
def remove_product(id):
    user = get_user()
    with db.cursor() as cursor:
        cursor.execute("SELECT UserId FROM Product "
                       "WHERE ProductId = %s", (id,))
        product = cursor.fetchone()
        if product is not None:
            if user is not None and user["UserId"] == product["UserId"]:
                cursor.execute("DELETE FROM Product "
                               "WHERE ProductId = %s", (id,))
                db.commit()
                flash("L'annonce a bien été supprimée")

    return redirect('/')

