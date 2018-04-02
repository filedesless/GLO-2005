from app import app
from flask import render_template, flash, redirect, session
from app.Model import db, get_user
from app.forms import NewProductForm
from app.authorize import authorize


@authorize
@app.route('/Product/Add', methods=['GET', 'POST'])
def add_product():
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
                    flash('hourra!')
                    return redirect('/')
        else:
            flash('Veuillez choisir une catégorie')

    return render_template('add_product.html', title='Nouveau produit', form=form)
