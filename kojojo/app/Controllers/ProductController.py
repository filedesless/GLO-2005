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
    pass

@app.route('/Product/List', methods=['GET'])
def list_products():
    products = []

    with db.cursor() as cursor:
        cursor.execute("SELECT ProductId, ProductName, Price FROM Product ORDER BY Date DESC")
        products = cursor.fetchall()

    return render_template('list_product.html', title='Accueil', products=products)

@app.route('/Product/<int:id>', methods=['GET'])
def show_product(id):
    pass

@app.route('/Product/Edit/<int:id>', methods=['GET'])
def edit_product(id):
    pass

@app.route('/Product/Remove/<int:id>', methods=['GET'])
def remove_product(id):
    pass

