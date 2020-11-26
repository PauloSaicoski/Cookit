from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True,nullable=False)
    password = db.Column(db.String(200), nullable=False)
    def __repr__(self):
        return '<Username %r>' % self.username

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    preptime = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    portions = db.Column(db.Integer, nullable=False)
    ingredients = db.Column(db.String(2000), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    imgUrl = db.Column(db.String(200), nullable=True)
    author = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Recipe %r>' % self.id
