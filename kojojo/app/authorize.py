from app.Model import db, get_user
from flask import redirect


def authorize() -> bool:
    return get_user() is not None

if __name__ == "__main__":
    authorize()