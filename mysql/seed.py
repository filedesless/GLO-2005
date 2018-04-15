#!/usr/bin/env python3

from werkzeug.security import generate_password_hash as pwhash
from random import choice
import pymysql.cursors
import csv

connection = pymysql.connect(host='localhost',
                             user='kojojo',
                             db='KOJOJO',
                             password='kojojo',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

user_stmt = "INSERT INTO KOJOJO.User (UserName, PasswordHash, RegistrationDate, Email, Phone) VALUES (%s, %s, %s, %s, %s);"
cat_stmt  = "INSERT INTO KOJOJO.Category (Type) VALUES (%s);"
town_stmt = "INSERT INTO KOJOJO.Town (TownName) VALUES (%s);"
product_stmt = "INSERT INTO KOJOJO.Product (ProductName, Price, Description, Date, CategoryId, UserId, TownId) VALUES (%s, %s, %s, %s, %s, %s, %s);"
image_stmt = "INSERT INTO KOJOJO.Image (ImageId, FileName) VALUES (%s, %s);"
new_products_stmt = "INSERT INTO KOJOJO.Product (ProductName, Price, Description, Date, CategoryId, UserId, TownId, ImageId) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);"

def users():
    for line in open('usernames.csv').readlines():
        arr = line.strip().split(',')
        arr[1] = pwhash(arr[1])
        yield tuple(arr)

def products(users, towns, categories):
    with open('products.csv') as csvfile:
        for line in csv.reader(csvfile):
            line.append(choice(categories))
            line.append(choice(users))
            line.append(choice(towns))
            yield tuple(line)

def new_products(users, towns, categories):
    with open('new_products.csv') as csvfile:
        for line in csv.reader(csvfile):
            line[4] = choice(categories)
            line[5] = choice(users)
            line[6] = choice(towns)
            yield tuple(line)

categories = [line.strip() for line in open('categories.csv').readlines()]
towns = [line.strip() for line in open('towns.csv').readlines()] 
images = [tuple(line.strip().split(',')) for line in open('images.csv').readlines()]

try:
    with connection.cursor() as cursor:
        print("Inserting users")
        cursor.executemany(user_stmt, users())
        print("Inserting categories")
        cursor.executemany(cat_stmt, categories)
        print("Inserting towns")
        cursor.executemany(town_stmt, towns)
        print("Inserting images")
        cursor.executemany(image_stmt, images)
        cursor.execute("SELECT UserId FROM User")
        users = [row['UserId'] for row in cursor.fetchall()]
        cursor.execute("SELECT TownId FROM Town")
        towns = [row['TownId'] for row in cursor.fetchall()]
        cursor.execute("SELECT CategoryId FROM Category")
        categories = [row['CategoryId'] for row in cursor.fetchall()]
        print("Inserting products")
        cursor.executemany(product_stmt, products(users, towns, categories))
        cursor.executemany(new_products_stmt, new_products(users, towns, categories))

    connection.commit()
finally:
    cursor.close()
