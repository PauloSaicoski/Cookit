from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask_restful import abort, fields, marshal_with
from app import app, db, bcrypt
from flask_login import login_user, current_user, logout_user
import re

from forms import ResistrationForm, LoginForm
from models import Recipe, User, Favorite

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

resource_fields_fav={
    'id': fields.Integer,
    'user_id': fields.Integer,
    'recipe_id': fields.Integer
}

@app.route('/favorites', methods=['POST', 'GET'])
def favorites():
    if not current_user.is_authenticated:
        flash('Você ainda não está logado para usar os Favoritos', 'info')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            data = request.form
            # Verifica se a receita ja esta favoritada
            favorite = Favorite.query.filter_by(user_id=data['user_id'],recipe_id=data['recipe_id']).first()
            if favorite:
                # Se estiver, tenta remove-la
                try:
                    db.session.delete(favorite)
                    db.session.commit()
                    
                    return "deu certo", 201
                except:
                    abort(404, message="Ocorreu um erro deletando")
            else:
                # Se não estiver, tenta adiciona-la
                favorite = Favorite(user_id=data['user_id'], recipe_id=data['recipe_id'])
                try:
                    db.session.add(favorite)
                    db.session.commit()
                    
                    return "deu certo", 201

                except:
                    abort(404, message="Algma coisa deu errado durante o commit")
        except:
            abort(404, message="Faltou dados no form")
        return "deu certo", 201
    else:
        try:
            data = current_user.id
            print(data, flush=True)
            favorites = Favorite.query.filter_by(user_id=data).all()
            rec = list()
            for f in favorites:
                r = Recipe.query.filter_by(id=f.recipe_id).first()
                rec.append(r)
            return render_template("favorites.html", recipes = rec)
        except:
            abort(404, message="Algma coisa deu errado durante a busca")
        return "ola"
       

    


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        pass
    else:
        recipes = Recipe.query.all()
        favorites = list()
        if current_user.is_authenticated:
            favorites = Favorite.query.filter_by(user_id=current_user.id).all()
        return render_template('index.html', recipes=recipes, favorites=favorites)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_pw)

            try:
                db.session.add(user)
                db.session.commit()
            except:
                flash(f'Já existe uma conta com esse Nome ou Email!', 'fail')
                return render_template("register.html", form=form)

            flash(f'Conta criada com sucesso!', 'sucess')
            return redirect(url_for('login'))
        else:
            flash(f'Houve um problema!', 'fail')
        return render_template("register.html", form=form)
    else:
        return render_template("register.html", form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash(f'Logado com Sucesso!', 'sucess')
                return redirect(url_for('index'))

        flash(f'Erro ao autenticar, verifique seu usuário/email ou senha!', 'fail')
        return render_template("login.html", form=form)
    else:
        return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash(f'Saiu com Sucesso!', 'sucess')
    return redirect(url_for('index'))



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
