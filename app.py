from flask import Flask, render_template, request, redirect, jsonify
from flask_restful import abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Recipes.db'
db = SQLAlchemy(app)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    preptime = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    portions = db.Column(db.Integer, nullable=False)
    ingredients = db.Column(db.String(2000), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    # img_url = db.Column(db.String(200), nullable=True)
    # author = db.Column(db.String(200), nullable=False)

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
    'url': fields.String
}


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        pass

    else:
        return "hello index"

@app.route('/recipe', methods=['POST'])
@marshal_with(resource_fields)
def recipePOST():
    try:
        data = request.form
        recipe = Recipe(name=data['name'], preptime=data['preptime'], likes=data['likes'], portions=data['portions'], ingredients=data['ingredients'], url=data['url'])
    except:
        abort(404, message="Faltou dados no form")

    try:
        db.session.add(recipe)
        db.session.commit()
    except:
        abort(404, message="Algma coisa deu errado durante o commit")
    return recipe, 201

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