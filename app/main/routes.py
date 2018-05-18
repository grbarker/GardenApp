from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from datetime import datetime
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Plant, Garden, Post
from app import db
from app.main import bp
from app.main.forms import EditProfileForm, PostForm, PlantFormDropDown, GardenForm, PlantFormFromGardenPage
import sys
import requests

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form1 = PostForm()
    form2 = PlantFormDropDown()
    form2.garden.choices = [(g.id, g.name) for g in current_user.gardens]
    posts_page = request.args.get('posts_page', 1, type=int)
    plants_page = request.args.get('plants_page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        posts_page, current_app.config['POSTS_PER_PAGE'], False)
    plants = current_user.followed_plants().paginate(
        plants_page, current_app.config['PLANTS_PER_PAGE'], False)
    plants_next_url = url_for('main.index', plants_page=plants.next_num, posts_page=posts_page) \
        if plants.has_next else None
    plants_prev_url = url_for('main.index', plants_page=plants.prev_num, posts_page=posts_page) \
        if plants.has_prev else None
    posts_next_url = url_for('main.index', plants_page=plants_page, posts_page=posts.next_num) \
        if posts.has_next else None
    posts_prev_url = url_for('main.index', plants_page=plants_page, posts_page=posts.prev_num) \
        if posts.has_prev else None
    gardens = current_user.usergardens()
    return render_template("index.html", title='Home Page', form1=form1, form2=form2, posts=posts.items,
        posts_next_url=posts_next_url, posts_prev_url=posts_prev_url, plants=plants.items,
        plants_next_url=plants_next_url, plants_prev_url=plants_prev_url, gardens=gardens)


@bp.route('/explore')
@login_required
def explore():
    posts_page = request.args.get('posts_page', 1, type=int)
    plants_page = request.args.get('plants_page', 1, type=int)
    plants = Plant.query.order_by(Plant.timestamp.desc()).paginate(
        plants_page, current_app.config['PLANTS_PER_PAGE'], False)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        posts_page, current_app.config['POSTS_PER_PAGE'], False)
    plants_next_url = url_for('main.explore', plants_page=plants.next_num, posts_page=posts_page) \
        if plants.has_next else None
    plants_prev_url = url_for('main.explore', plants_page=plants.prev_num, posts_page=posts_page) \
        if plants.has_prev else None
    posts_next_url = url_for('main.explore', plants_page=plants_page, posts_page=posts.next_num) \
        if posts.has_next else None
    posts_prev_url = url_for('main.explore', plants_page=plants_page, posts_page=posts.prev_num) \
        if posts.has_prev else None
    gardens = current_user.usergardens()
    return render_template("index.html", title='Explore', plants=plants.items, plants_next_url=plants_next_url,
        plants_prev_url=plants_prev_url, posts=posts.items, posts_next_url=posts_next_url,
        posts_prev_url=posts_prev_url, gardens=gardens)


@bp.route('/post_from_index', methods=['POST'])
def post():
    form1 = PostForm()
    form2 = PlantFormDropDown()
    form2.garden.choices = [(g.id, g.name) for g in current_user.gardens]
    if form1.validate_on_submit():
        post = Post(body=form1.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))


@bp.route('/plant_from_index', methods=['POST'])
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
        return redirect(url_for('main.index'))



@bp.route('/registerGarden', methods=['GET', 'POST'])
@login_required
def registerGarden():
    form = GardenForm()
    if form.validate_on_submit():
        response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCyX0uZDxs4ekWQz-uSuhvhpABMOFf8QfI'.format(form.address.data))
        responseJSON = response.json()
        lat = responseJSON['results'][0]['geometry']['location']['lat']
        lon = responseJSON['results'][0]['geometry']['location']['lng']
        garden = Garden(name=form.name.data, address=form.address.data, lat=lat, lon=lon)
        print(garden)
        garden.users.append(current_user)
        print(garden.users)
        db.session.add(garden)
        db.session.commit()
        flash('Congratulations, you have registered a new garden!')
        return redirect(url_for('main.index'))
    return render_template('registerGarden.html', title='Register Garden', form=form)

#Note: add post and plant pagination for user page
@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    plants = current_user.followed_plants().all()
    return render_template('user.html', user=user, plants=plants)


@bp.route('/user/<garden_name>, <garden_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('main.index'))
    return render_template('garden.html', form=form, garden=garden, plants=plants)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()