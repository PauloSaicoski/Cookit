from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Recipes.db'
app.config['SECRET_KEY'] ='ad18303111748e53cf13022d4daeddc8'
db = SQLAlchemy(app)
from routes import *

if __name__ == "__main__":
    app.run(debug=True)