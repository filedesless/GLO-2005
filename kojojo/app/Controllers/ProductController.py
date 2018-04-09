from app import app
from flask import render_template, flash, redirect, session
from app.Model import db, get_user
from app.forms import NewProductForm
from app.authorize import authorize


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
                user = get_user()
                cursor.execute("INSERT INTO Product (ProductName, Price, Description, Date, CategoryId, UserId, TownId) "
                               "VALUES (%s, %s, %s, NOW(), %s, %s, "
                               "(SELECT TownId FROM Town WHERE TownName = %s))", (form.name.data,
                                                                                  form.price.data,
                                                                                  form.description.data,
                                                                                  form.category.data,
                                                                                  user["UserId"],
                                                                                  town))
                db.commit()
                return redirect('/')
        else:
            flash('Veuillez choisir une catégorie')

    return render_template('add_product.html', title='Nouveau produit', form=form)

@app.route('/Product/Search/<query>', methods=['GET'])
def search_product(query: str):
    products = []

    with db.cursor() as cursor:
        cursor.execute("SELECT ProductId, ProductName, Price FROM Product "
                       "WHERE ProductName LIKE %s "        
                       "ORDER BY Date DESC", ("%{}%".format(query),))
        products = cursor.fetchall()

    return render_template('list_product.html', products=products, title="Liste des correspondant à la recherche")

@app.route('/Product/List', methods=['GET'])
def list_products():
    products = []

    with db.cursor() as cursor:
        cursor.execute("SELECT ProductId, ProductName, Price FROM Product ORDER BY Date DESC")
        products = cursor.fetchall()

    return render_template('list_product.html', products=products, title="Liste des articles publiés")

@app.route('/Product/<int:id>', methods=['GET'])
def show_product(id):
    with db.cursor() as cursor:
        cursor.execute("SELECT ProductId, ProductName, Price, Description, Date, TownName, Type, Product.UserId, UserName, Email, Phone FROM Product "
                       "INNER JOIN User ON Product.UserId = User.UserId "
                       "INNER JOIN Town ON Product.TownId = Town.TownId "
                       "INNER JOIN Category ON Product.CategoryId = Category.CategoryId "
                       "WHERE ProductId = %s", (id,))
        product = cursor.fetchone()
        if product is not None:
            user = get_user()
            is_author = user is not None and user["UserId"] == product["UserId"]
        else:
            product = []
            is_author = False

    return render_template('show_product.html', title='Accueil', product=product, is_author=is_author)

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

    return render_template('edit_product.html', title="Modifier l'annonce", form=form)


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

