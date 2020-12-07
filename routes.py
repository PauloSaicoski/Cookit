from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask_restful import abort, fields, marshal_with
from app import app, db, bcrypt
from flask_login import login_user, current_user, logout_user
import re
from werkzeug.datastructures import ImmutableMultiDict
import random

from forms import ResistrationForm, LoginForm
from models import Recipe, User, Favorite, Preference

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

@app.route('/preferences/<int:id>', methods=['POST', 'GET'])
def preferences(id):

    if not current_user.is_authenticated:
        flash('Você ainda não está logado para usar as Preferências', 'info')
        return redirect(url_for('login'))

    if id == 6:
        flash('Prefêrencias salvas com sucesso!', 'success')
        return redirect(url_for('index'))

    
    cat_names = ['Carnes', 'Legumes', 'Frutas', 'Cereais e Grãos', 'Outros']
    cat1 = ['Carne', 'Frango', 'Porco','Carne Moída', 'Picanha', 'Costela','Linguiça', 'Pato', 'Filé']
    cat2 = ['Alface', 'Couve','Repolho', 'Brócolis', 'Couve-flor','Pepino', 'Tomate', 'Batata']
    cat3 = ['Abacate', 'Abacaxi', 'Açaí', 'Banana', 'Cereja', 'Coco', 'Maça', 'Manga', 'Laranja', 'Uva']
    cat4 = ['Arroz', 'Feijão', 'Aveia', 'Milho', 'Soja']
    cat5 = ['Leite', 'Queijo', 'Requeijão', 'Doce de Leite', 'Chocolate', 'Manteiga']
    catIng = list()
    catIng.append(cat1)
    catIng.append(cat2)
    catIng.append(cat3)
    catIng.append(cat4)
    catIng.append(cat5)

    p = Preference.query.filter_by(user_id=current_user.id).first()
    userpref = ''
    if p:
        if id == 1:
            userpref = p.category1
        elif id == 2:
            userpref = p.category2
        elif id == 3:
            userpref = p.category3
        elif id == 4:
            userpref = p.category4
        elif id == 5:
            userpref = p.category5
    if not userpref:
        userpref = ''

    
    if request.method == 'GET':
        return render_template('preferences.html', id=id, cat=catIng[id-1], catname=cat_names[id-1], userpref=userpref)
    else:
        data = request.form['pref']

        try:
            p = Preference.query.filter_by(user_id=current_user.id).first()
            if p:
                if id == 1:
                    p.category1 = data
                elif id == 2:
                    p.category2 = data
                elif id == 3:
                    p.category3 = data
                elif id == 4:
                    p.category4 = data
                elif id == 5:
                    p.category5 = data
                db.session.commit()
            else:
                if id == 1:
                    p = Preference(user_id=current_user.id, category1=data)
                elif id == 2:
                    p = Preference(user_id=current_user.id, category2=data)
                elif id == 3:
                    p = Preference(user_id=current_user.id, category3=data)
                elif id == 4:
                    p = Preference(user_id=current_user.id, category4=data)
                elif id == 5:
                    p = Preference(user_id=current_user.id, category5=data)

                db.session.add(p)
                db.session.commit()
        except:
            abort(404, message="Ocorreu um erro")

        print(data, flush=True)
        return "deu certo", 201


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
            # print(data, flush=True)
            favorites = Favorite.query.filter_by(user_id=data).order_by(Favorite.recipe_id).all()
            rec = list()
            for f in favorites:
                r = Recipe.query.filter_by(id=f.recipe_id).first()
                rec.append(r)
            if(len(rec)==0):
                flash("Você ainda não tem nenhum favorito, tente adicionar alguns!", 'info')
            return render_template("favorites.html", recipes = rec)
        except:
            abort(404, message="Algma coisa deu errado durante a busca")
        return "ola"
       

    


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            # Transforma as tags em uma lista
            data = request.form.to_dict(flat=False)        
            data = data['ingredient'][1]
            data = re.split(r"\s*,\s*", data)

            recipe = searchRecipesByList(data).all()
            recipe.sort(key=sortByLikes, reverse = True)
            rec = recipe
          
            favorites = list()
            recipePref = list()
            if current_user.is_authenticated:
                try:
                    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
                    preferences = Preference.query.filter_by(user_id=current_user.id).first()
                    if preferences:
                        userpref = list()
                        if preferences.category1:
                            userpref.append(re.split(r"\s*,\s*", preferences.category1))
                        if preferences.category2:
                            userpref.append(re.split(r"\s*,\s*", preferences.category2))
                        if preferences.category3:
                            userpref.append(re.split(r"\s*,\s*", preferences.category3))
                        if preferences.category4:
                            userpref.append(re.split(r"\s*,\s*", preferences.category4))
                        if preferences.category5:
                            userpref.append(re.split(r"\s*,\s*", preferences.category5))
                        # print(userpref)
                        recipePref = applyPreferences(data, userpref)
                    else:
                        recipePref = rec
                                 
                except:
                    abort(404, message="Faltou dados no form")
                return render_template("index.html", recipes = recipePref, recipespref=recipePref, favorites=favorites, method=2)
            else:
                return render_template("index.html", recipes = rec, recipespref=recipePref, favorites=favorites, method=2)
            # return recipe
        except:
            abort(404, message="Faltou dados no form")
    else:
        recipes = Recipe.query.all()
        favorites = list()
        if current_user.is_authenticated:
            favorites = Favorite.query.filter_by(user_id=current_user.id).all()
        return render_template('index.html', recipes=recipes, favorites=favorites, method=1)

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
                flash('Já existe uma conta com esse Nome ou Email!', 'danger')
                return render_template("register.html", form=form)

            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Houve um problema!', 'danger')
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
                flash('Logado com Sucesso!', 'success')
                p = Preference.query.filter_by(user_id=current_user.id).first()
                if not p:
                    flash('Parece que você ainda não configurou as Preferências!', 'info')
                return redirect(url_for('index'))

        flash('Erro ao autenticar, verifique seu email ou senha!', 'danger')
        return render_template("login.html", form=form)
    else:
        return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('Saiu com Sucesso!', 'success')
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

def applyPreferences(lista, preferencias):
    resultNormais = searchRecipesByList(lista).all()
    resultPref = list()
    for categoria in preferencias:
        rand = random.randrange(0, len(categoria))
        ingredients = lista.copy()
        ingredients.append(categoria[rand]) # seleciona um elemento aleatório de cada lista de preferencias
        resultPref.append(searchRecipesByList(ingredients).all()) # procura as receitas que utilizam aquele ingrediente além dos informados pelo usuário
        resultNormais = list(set(resultNormais) - set(resultPref[-1])) # remove os resultados da lista original para evitar duplicacao
    for i in range(1, len(resultPref)):
        for j in range(0, i):
            resultPref[i] = list(set(resultPref[i]) - set(resultPref[j])) # evita duplicacao de receitas
            resultPref[i].sort(key=sortByLikes)
    # resultNormais.sort(key=sortByLikes)
    resultFinal = list()
    i=-1
    while (len(resultPref) > 0 or len(resultNormais) > 0):
        if (len(resultNormais) > 0):
            resultFinal.append(resultNormais.pop())
        if(len(resultPref) > 0):
            i = (i+1)%len(resultPref)
            if (len(resultPref[i]) > 0):
                resultFinal.append(resultPref[i].pop())
            else:
                del resultPref[i]
                i-=1
            
    return resultFinal
    

def sortByLikes(e):
    return e.likes
    

@app.route('/recipe', methods=['GET'])
@marshal_with(resource_fields)
def recipeGET():  
    try:
        data = request.form
        recipe = Recipe.query.filter_by(id=data['id']).first()
        return recipe
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
