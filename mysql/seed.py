#!/usr/bin/env python3

from werkzeug.security import generate_password_hash as pwhash
from random import randint
import pymysql.cursors
import datetime

connection = pymysql.connect(host='localhost',
                             user='kojojo',
                             password='kojojo',
                             db='KOJOJO',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

user_fmt = "INSERT INTO KOJOJO.User (UserName, PasswordHash, RegistrationDate) VALUES ('{}', '{}', '{}');"
cat_fmt  = "INSERT INTO KOJOJO.Category (Type) VALUES (%s);"

usernames = [line.strip() for line in open('usernames.txt').readlines()]
categories = [line.strip() for line in open('categories.txt').readlines()]

try:
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM KOJOJO.User;")
        cursor.execute("DELETE FROM KOJOJO.Category;")
        for username in usernames:
            h = pwhash('changeme')
            t = datetime.date(2017, randint(1, 12), randint(1, 28))
            stmt = user_fmt.format(username, h, t)
            print("Inserting:", stmt)
            cursor.execute(stmt)
        for category in categories:
            arr = category.split('>')
            cat = arr[-1].strip()
            print("Inserting:", cat)
            cursor.execute(cat_fmt, (cat,))
    connection.commit()
finally:
    cursor.close()
