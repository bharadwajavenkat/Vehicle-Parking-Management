from flask import Flask
from models.models import db
app = None

def create_app():
    app = Flask(__name__)
    app.secret_key = "vehicle-parking"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.sqlite3"
    db.init_app(app)
    app.app_context().push()
    app.debug = True
    return app


def initialize_database():
    db.create_all()
    
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        u = User(username="admin",email="admin@parking.com",password="admin123",role="admin")
        db.session.add(u)
        db.session.commit()
        print("Admin Details:\nusername:admin\npassword:admin123")



app = create_app()
from controllers.controller import *

if __name__ == '__main__':

    initialize_database()
    app.run()

