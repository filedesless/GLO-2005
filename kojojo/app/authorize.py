from app.Model import db, get_user
from flask import redirect


def authorize(action_method):
    def wrapper():
        return action_method() if get_user() is not None else redirect('/User/SignIn')

    return wrapper

if __name__ == "__main__":
    authorize()