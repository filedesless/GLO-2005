import pymysql
from flask import session
from app import Config

db = pymysql.connect(host= Config.DB_HOST,
                     user= Config.DB_USER,
                     password= Config.DB_PASS,
                     db= Config.DB_NAME,
                     charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor)

def get_user():
    if "session_id" in session:
        with db.cursor() as cursor:
            cursor.execute("SELECT UserId FROM Session WHERE SessionId = %s", (session["session_id"],))
            row = cursor.fetchone()
            if row is not None:
                cursor.execute("SELECT UserId, UserName, Email, Phone, PasswordHash, RegistrationDate "
                               "FROM User WHERE UserId = %s", (row["UserId"],))
                row = cursor.fetchone()
                return row
            del session["session_id"]
    return None