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

fmt = "INSERT INTO KOJOJO.User (UserName, PasswordHash, RegistrationDate) VALUES ('{}', '{}', '{}');"

lines = [line.strip() for line in open('usernames.txt').readlines()]

try:
    with connection.cursor() as cursor:
        for line in lines:
            h = pwhash('changeme')
            t = datetime.date(2017, randint(1, 12), randint(1, 28))
            stmt = fmt.format(line, h, t)
            print("Inserting:", stmt)
            cursor.execute(stmt)
    connection.commit()
finally:
    cursor.close()
