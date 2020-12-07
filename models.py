from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def loadUser(id):
    return User.query.get(int(id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True,nullable=False)
    password = db.Column(db.String(200), nullable=False)
    preferences = db.relationship('Preference', backref='user', lazy=True)
    
    def __repr__(self):
        return '<Username %r>' % self.username

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    preptime = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    portions = db.Column(db.Integer, nullable=False)
    ingredients = db.Column(db.String(2000), nullable=False)
    url = db.Column(db.String(200), unique=True, nullable=False)
    imgUrl = db.Column(db.String(200), nullable=True)
    author = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Recipe %r>' % self.id

class Preference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category1 = db.Column(db.String(200), nullable=True)
    category2 = db.Column(db.String(200), nullable=True)
    category3 = db.Column(db.String(200), nullable=True)
    category4 = db.Column(db.String(200), nullable=True)
    category5 = db.Column(db.String(200), nullable=True)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
