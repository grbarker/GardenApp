from flask import render_template, flash, redirect, url_for, request, jsonify
from datetime import datetime
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Plant, Garden, Post
from app import app
from app import db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, PlantFormDropDown, GardenForm, PlantFormFromGardenPage
import sys

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form1 = PostForm()
    form2 = PlantFormDropDown()
    form2.garden.choices = [(g.id, g.name) for g in current_user.gardens]
    posts = current_user.followed_posts().all()
    plants = current_user.followed_plants().all()
    gardens = current_user.usergardens()
    return render_template("index.html", title='Home Page', form1=form1, form2=form2, posts=posts, plants=plants, gardens=gardens)

@app.route('/post_from_index', methods=['POST'])
def post():
    form1 = PostForm()
    form2 = PlantFormDropDown()
    form2.garden.choices = [(g.id, g.name) for g in current_user.gardens]
    if form1.validate_on_submit():
        post = Post(body=form1.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))


@app.route('/plant_from_index', methods=['POST'])
def plant():
    form1 = PostForm()
    form2 = PlantFormDropDown()
    form2.garden.choices = [(g.id, g.name) for g in current_user.gardens]
    if form2.submit.data:
        id = form2.garden.data
        garden = Garden.query.filter_by(id=id).first()
    if form2.validate_on_submit():
        plant = Plant(name=form2.plant.data,
            grower=current_user,
            garden=garden)
        db.session.add(plant)
        db.session.commit()
        flash('Your plant is now live!')
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)




@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



@app.route('/registerGarden', methods=['GET', 'POST'])
@login_required
def registerGarden():
    form = GardenForm()
    if form.validate_on_submit():
        garden = Garden(name=form.name.data)
        print(garden)
        garden.users.append(current_user)
        print(garden.users)
        db.session.add(garden)
        db.session.commit()
        flash('Congratulations, you have registered a new garden!')
        return redirect(url_for('index'))
    return render_template('registerGarden.html', title='Register Garden', form=form)



@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    plants = current_user.followed_plants().all()
    return render_template('user.html', user=user, plants=plants)


@app.route('/user/<garden_name>, <garden_id>', methods=['GET', 'POST'])
@login_required
def garden(garden_name, garden_id):
    garden = Garden.query.filter_by(id=garden_id).first_or_404()
    plants = garden.plants
    form = PlantFormFromGardenPage()
    if form.validate_on_submit():
        plant = Plant(name=form.plant.data, grower=current_user, garden=garden)
        db.session.add(plant)
        db.session.commit()
        flash('Your plant is now live!')
        return redirect(url_for('index'))
    return render_template('garden.html', form=form, garden=garden, plants=plants)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    plants = Plant.query.order_by(Plant.timestamp.desc()).all()
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    gardens = current_user.usergardens()
    return render_template("index.html", title='Explore', plants=plants, posts=posts, gardens=gardens)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()