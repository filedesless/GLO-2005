from app import app
from flask_wtf.csrf import CSRFProtect


if __name__ == '__main__':
    csrf = CSRFProtect()
    csrf.init_app(app)
    app.run()
