# -*- coding: UTF-8 -*-

from app.Model import db, get_user
from flask import redirect


def authorize():
    return get_user() is not None

if __name__ == "__main__":
    authorize()