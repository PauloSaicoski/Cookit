from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask_restful import abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from forms import ResistrationForm, LoginForm
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Recipes.db'
app.config['SECRET_KEY'] ='ad18303111748e53cf13022d4daeddc8'
db = SQLAlchemy(app)

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

#serialize(Transforma para objeto json)
resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'preptime': fields.Integer,
    'likes': fields.Integer,
    'portions': fields.Integer,
    'ingredients': fields.String,
    'url': fields.String,
    'imgUrl': fields.String,
    'author': fields.String
}


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        pass
    else:
        recipes = Recipe.query.all()
        return render_template('index.html', recipes=recipes)

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = ResistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash(f'Conta criada com {form.username.data}!', 'sucess')
            return redirect(url_for('login'))
        else:
            flash(f'Houve um problema!', 'fail')
        return render_template("register.html", form=form)
    else:
        return render_template("register.html", form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        return redirect(url_for("index"))
    else:
        return render_template("login.html", form=form)



@app.route('/recipe', methods=['POST'])
@marshal_with(resource_fields)
def recipePOST():
    try:
        data = request.form
        recipe = Recipe(name=data['name'], preptime=data['preptime'], likes=data['likes'], portions=data['portions'], ingredients=data['ingredients'], url=data['url'], imgUrl=data['imgUrl'], author=data['author'])
    except:
        abort(404, message="Faltou dados no form")

    try:
        db.session.add(recipe)
        db.session.commit()
    except:
        abort(404, message="Algma coisa deu errado durante o commit")
    return recipe, 201

def searchRecipesByList(lista):
    if len(lista) > 1:
        return searchRecipesByList(lista[1:]).filter(Recipe.ingredients.contains(lista[0]))
    else:
        return Recipe.query.filter(Recipe.ingredients.contains(lista[0]))

@app.route('/search', methods=['GET', 'POST'])
# @marshal_with(resource_fields)
def search():
    if request.method == 'GET':
        return render_template("search.html")
    else:
        try:
            data = request.form
            recipe = searchRecipesByList(re.split(r"\s*,\s*", data['ingredients']))
            rec = list()
            for r in recipe:
                #print(r.id, flush=True)
                rec.append(r)
            #return jsonify({'data':re})
            return render_template("search.html", recipes = rec)
            # return recipe
        except:
            abort(404, message="Faltou dados no form")


@app.route('/recipe', methods=['GET'])
@marshal_with(resource_fields)
def recipeGET():  
    try:
        data = request.form
        recipe = Recipe.query.filter_by(id=data['id']).first()
        return recipe
    except:
        abort(404, message="Faltou dados no form")

@app.route('/all', methods=['GET'])
def recipeAll():  
    try:
        recipe = Recipe.query.all()
        re = list()
        for r in recipe:
            print(r.id, flush=True)
            re.append(r.id)
        return jsonify({'data':re})
    except:
        abort(404, message="Faltou dados no form")
    
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    to_delete = Recipe.query.get_or_404(id)

    try:
        db.session.delete(to_delete)
        db.session.commit()
        return "Deleted", 204
    except:
        abort(404, message="Something went wrong deleting the task")

if __name__ == "__main__":
    app.run(debug=True)