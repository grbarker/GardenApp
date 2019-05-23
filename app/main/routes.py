from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from datetime import datetime
from flask_login import current_user, login_user, logout_user, login_required
from flask_googlemaps import Map
from werkzeug.urls import url_parse
from app.models import User, Plant, Garden, Post
from app import db
from app.main import bp
from app.main.forms import EditProfileForm, PostForm, WallPostForm, PlantFormDropDown, GardenForm, PlantFormFromGardenPage, DeleteGardenForm
import sys
import requests
from sqlalchemy import desc



@bp.route('/location/<address>', methods=['GET', 'POST'])
@login_required
def location(address):
    gardens = Garden.query.filter_by(address=address).all()
    lat = gardens[0].lat
    lon = gardens[0].lon
    plants = []
    users = []
    for gdn in gardens:
        plants.extend(gdn.plants.all())
        users.extend(gdn.users.all())
    GardenAppKeyNew = "AIzaSyB_6lIcM2n0ZtT9Zrex8gOGaNJOMwpLecs"

    return render_template('location.html', users=users, gardens=gardens, plants=plants, lat=lat, lon=lon, key=GardenAppKeyNew)




@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form1 = PostForm()
    form2 = PlantFormDropDown()
    form2.garden.choices = [(g.id, g.name) for g in current_user.gardens]
    if form1.submit1.data and form1.validate_on_submit():
        post = Post(body=form1.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    if form2.submit2.data and form2.validate_on_submit():
        id = form2.garden.data
        garden = Garden.query.filter_by(id=id).first()
        plant = Plant(name=form2.plant.data,
            grower=current_user,
            garden=garden)
        db.session.add(plant)
        db.session.commit()
        flash('Your plant is now live!')
        return redirect(url_for('main.index'))
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
    gardens = current_user.gardens
    coords = []
    locations_for_markers = []
    markers = []
    for garden in gardens:
        if garden.lat and garden.lon:
            lat = garden.lat
            lon = garden.lon
            coord = (lat, lon)
            garden_plants = garden.plants.all()
            #handle the case where two markers would be placed in hte exact same spot, where only one would be visible and usable in the google maps once rendered
            if coord in coords:
                #find the index of the first garden for a given coord
                index = coords.index(coord)
                #use index of given coord to select the corresponding location_for_markers in its list and extend the plants list
                locations_for_markers[index][2].extend(garden_plants)
            elif coord not in coords:
                coords.append(coord)
                location_for_markers = (lat, lon, garden_plants)
                locations_for_markers.append(location_for_markers)
    for location_for_markers in locations_for_markers:
        location_plants = location_for_markers[2]
        infobox_plants = ''
        for location_plant in location_plants:
            infobox_plants = infobox_plants + '<li style="list-style-type: none;">' + location_plant.name + '</li>'
        lat = location_for_markers[0]
        lon =location_for_markers[1]
        icon = str(url_for('static', filename='agriculture_map_icons/iboga.png'))
        infobox = '<h3 style="strong">{}&#39;s plants at this location</h3><ul>{}</ul>'.format(current_user.username, infobox_plants)
        marker = {'icon': icon, 'lat': lat, 'lng': lon, 'infobox': infobox}
        markers.append(marker)
    mymap = Map(
        identifier="mymap",
        lat=45.487292,
        lng=-122.635435,
        style="height:500px;width:100%;margin-bottom=:20px;",
        markers= markers,
    )
    return render_template("index.html", title='Home Page', form1=form1, form2=form2, posts=posts.items,
        posts_next_url=posts_next_url, posts_prev_url=posts_prev_url, plants=plants.items,
        plants_next_url=plants_next_url, plants_prev_url=plants_prev_url, mymap=mymap, gardens=gardens)


@bp.route('/explore')
@login_required
def explore():
    posts_page = request.args.get('posts_page', 1, type=int)
    plants_page = request.args.get('plants_page', 1, type=int)
    plants = Plant.query.order_by(desc(Plant.timestamp)).paginate(
        plants_page, current_app.config['PLANTS_PER_PAGE'], False)
    posts = Post.query.order_by(desc(Post.timestamp)).paginate(
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
    all_gardens = Garden.query.all()
    addresses = []
    coords = []
    locations_for_markers = []
    markers = []
    for garden in all_gardens:
        if garden.lat and garden.lon:
            lat = garden.lat
            lon = garden.lon
            coord = (lat, lon)
            address = garden.address
            garden_plants = garden.plants.all()
            garden_users = garden.users.all()
            #Handle the case where two markers would be placed in the exact same spot, where only
            #one would be visible and usable in the google maps once rendered
            if coord in coords:
                #Find the index of the first garden for a given coord
                index = coords.index(coord)
                #Use index of given coord to select the corresponding location_for_markers in its
                #list and extend the plants list
                locations_for_markers[index][3].append(garden)
                locations_for_markers[index][4].extend(garden_plants)
                locations_for_markers[index][5].extend(garden_users)
            elif coord not in coords:
                coords.append(coord)
                addresses.append(addresses)
                gardens = [garden]
                location_for_markers = (lat, lon, address, gardens, garden_plants, garden_users)
                locations_for_markers.append(location_for_markers)
    for location_for_markers in locations_for_markers:
        response = requests.get('http://maps.googleapis.com/maps/api/streetview?size=200x200&location={}&pitch=-25&key=AIzaSyDhPSBWrhJwAnF7awFAIq2fzba7AWM8AuQ'.format(location_for_markers[2]))
        #responseJSON = response.get_json()
        location_gardens = location_for_markers[3]
        #gslength = len(location_gardens)
        location_plants = location_for_markers[4]
        location_users = location_for_markers[5]
        #infobox_gardens1 = ''
        #infobox_gardens2 = ''
        #infobox_gardens_users = ''
        #infobox_gardens_plants = ''
        infobox_plants = ''
        infobox_gardens_grid = ''
        grid_plants=''
        infobox_gardens_list = ''
        list_plants=''
        for location_garden in location_gardens:
            for plant in location_garden.plants.all():
                list_plants = list_plants + "<p><span style='color: green;background-color: white;''>{}</span> --- {}</p>".format(plant.name, plant.grower.username)
            infobox_gardens_list = infobox_gardens_list + "<div class='row'><div class='col-md-12'><h5>{}</h5>{}</div></div></div'>".format(location_garden.name, list_plants)
            list_plants = ''
        #for location_garden in location_gardens:
        #    for plant in location_garden.plants.all():
        #        grid_plants = grid_plants + "<p><span style='color: green;background-color: white;''>{}</span> --- {}</p>".format(plant.name, plant.grower.username)
        #    if (location_gardens.index(location_garden) + 1) % 4 == 0:
        #        infobox_gardens_grid = infobox_gardens_grid + "<div class='col-md-3'><h4>{}</h4>{}</div></div><div class='row'>".format(location_garden.name, grid_plants)
        #    else:
        #        infobox_gardens_grid = infobox_gardens_grid + "<div class='col-md-3'><h4>{}</h4>{}</div>".format(location_garden.name, grid_plants)
        #for location_garden in location_gardens:
        #    for user in location_garden.users.all():
        #        infobox_gardens_users = infobox_gardens_users +'<li style="list-style-type: none;"><p style="color: blue;background-color: white;"><strong>{}</strong></p></li>'.format(user.username)
        #    infobox_gardens1 = infobox_gardens1 + '<li style="list-style-type: none;"><strong>{}</strong> --- Users: <ul>{}</ul></li>'.format(location_garden.name, infobox_gardens_users)
        #    infobox_gardens_users = ''
        #for location_garden in location_gardens:
        #    for plant in location_garden.plants.all():
        #        infobox_gardens_plants = infobox_gardens_plants +'<li style="list-style-type: none;"><p style="color: green;background-color: white;"><strong>{}</strong></p> -- planted by {}</li>'.format(plant.name, plant.grower.username)
        #    infobox_gardens2 = infobox_gardens2 + '<li style="list-style-type: none;"><strong>{}</strong><ul>{}</ul></li>'.format(location_garden.name, infobox_gardens_plants)
        #    infobox_gardens_plants = ''
        #for location_plant in location_plants:
        #    infobox_plants = infobox_plants + '<li style="list-style-type: none;"><p style="color: green;background-color: white;"><strong>{}</strong></p>- planted by {}</li>'.format(location_plant.name, location_plant.grower.username)
        GardenAppKeyNew = "AIzaSyB_6lIcM2n0ZtT9Zrex8gOGaNJOMwpLecs"
        GoogleMapsAPIKeyOld ="AIzaSyDhPSBWrhJwAnF7awFAIq2fzba7AWM8AuQ"
        lat = location_for_markers[0]
        lon =location_for_markers[1]
        address = location_for_markers[2]
        icon = str(url_for('static', filename='agriculture_map_icons/iboga.png'))
        location_stats = "<p>{} Gardens,  {} Plants,  {} Users</p>".format(len(location_gardens), len(location_plants), len(location_users))
        #streetview_url = "https://maps.googleapis.com/maps/api/streetview?size=275x275&location={}&pitch=-25&key=AIzaSyDhPSBWrhJwAnF7awFAIq2fzba7AWM8AuQ".format(address)
        embed_img = '<iframe width="280" height="300" frameborder="0" style="border:0" src="https://www.google.com/maps/embed/v1/streetview?location={},{}&key=AIzaSyB_6lIcM2n0ZtT9Zrex8gOGaNJOMwpLecs" allowfullscreen></iframe>'.format(lat, lon)
        #streetview = '<img src="{}" style="max-width:300px;max-height:300px;width:auto;height:auto;" alt="A Google Streetview image of the selected location">'.format(streetview_url)
        location_url = url_for('main.location', address=address)
        location_link = '<a href="{}">Go to Location</a>'.format(location_url)
        garden_list_column = "<div class='col-md-6'>{}{}</div>".format(infobox_gardens_list, location_link)
        streetview_column = "<div class='col-md-6'><div class='row'><div class='col-md-12'>{}</div></div><div class='row'><div class='col-md-12'>{}</div></div></div>".format(embed_img, location_stats)
        #rows = "<div class='row'>{}</div>".format(infobox_gardens_grid)
        #column1 = '<div class="col-md-6" style="border-style: groove;border-color: green;border-width: 5px;"><ul>{}</ul></div>'.format(infobox_gardens1)
        #column2 = '<div class="col-md-12" style="border-style: groove;border-color: red;border-width: 5px;"><ul>{}</ul></div>'.format(infobox_gardens2)
        container = '<div class="row" style="border-style: solid;border-color: blue;border-width: 5px;">{}{}</div>'.format(garden_list_column, streetview_column)
        #infobox = '<div class="container" style="width: 500px; height: auto;"><h3 style="strong">Plants at this location</h3><ul>{}</ul><h4>{} gardens: </h4>{}</div>'.format(infobox_plants, gslength, infobox_gardens2)
        #infobox2 = '<div class="container" style="width: 500px; height: auto;"><h3 style="strong"> Gardens and Plants at this location</h3>{}</div>'.format(container)
        infobox3 = '<div class="container" style="width: 600px; height: 600px;">{}</div>'.format(container)
        marker = {'icon': icon, 'lat': lat, 'lng': lon, 'infobox': infobox3}
        markers.append(marker)
    mymap = Map(
        identifier="mymap",
        lat=45.487292,
        lng=-122.635435,
        zoom=12,
        maptype="HYBRID",
        style="height:700px;width:100%;",
        markers= markers,
        center_on_user_location=True,
        streetview_control=True,
        fullscreen_control=True,
        rotate_control=True,
        scale_control=True,
        maptype_control=True,
        zoom_control=True,
        varname="explore",
    )
    return render_template("index.html", title='Explore', plants=plants.items, plants_next_url=plants_next_url,
        plants_prev_url=plants_prev_url, posts=posts.items, posts_next_url=posts_next_url,
        posts_prev_url=posts_prev_url, mymap=mymap, gardens=gardens)


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
        id = form2.garden.data
        garden = Garden.query.filter_by(id=id).first()
        plant = Plant(name=form2.plant.data,
            grower=current_user,
            garden=garden)
        db.session.add(plant)
        db.session.commit()
        flash('Your plant is now live!')
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('main.index'))


@bp.route('/placementMap', methods=['GET', 'POST'])
@login_required
def placementMap():
    lat = request.args.get('lat', None, type=int)
    lng = request.args.get('lng', None, type=int)
    placementmap = Map(
        identifier="placementmap",
        varname="placementmap",
        lat=45.487292,
        lng=-122.635435,
        report_clickpos=True,
        clickpos_uri=url_for('main.placementMap'),
        zoom=10,
        maptype="HYBRID",
        style="height:700px;width:100%;",
        center_on_user_location=True,
        collapsible=False,
    )
    return render_template("placementMap.html", placementmap=placementmap, lat=lat, lng=lng)

#Note: the Google API address might/will change in the future
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

@bp.route('/registerGardenFromMap/<address>', methods=['GET', 'POST'])
@login_required
def registerGardenFromMap(address):
    address = address
    form = GardenForm()
    form.address.data=address
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
    return render_template('registerGarden.html', title='Register Garden From Map', form=form, address=address)

#Note: add post and plant pagination for user page
@bp.route('/user/<username>', methods =['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = WallPostForm()
    if form.validate_on_submit():
        post = Post(body=form.wall_post.data, author=current_user, wall_post=True, wall_owner_id=user.id)
        db.session.add(post)
        db.session.commit()
        flash("You posted to {}'s wall!".format(username))
        return redirect(url_for('main.user', username=user.username))

    posts_page = request.args.get('posts_page', 1, type=int)
    wall_posts_page = request.args.get('wall_posts_page', 1, type=int)
    plants_page = request.args.get('plants_page', 1, type=int)

    posts = user.posts.order_by(desc(Post.timestamp)).paginate(
        posts_page, current_app.config['POSTS_PER_PAGE'], False)
    wall_posts = Post.query.filter_by(wall_owner_id=user.id).order_by(desc(Post.timestamp)).paginate(
        wall_posts_page, current_app.config['POSTS_PER_PAGE'], False)
    plants = user.plants.order_by(desc(Plant.timestamp)).paginate(
        plants_page, current_app.config['PLANTS_PER_PAGE'], False)

    plants_next_url = url_for('main.index', plants_page=plants.next_num, posts_page=posts_page) \
        if plants.has_next else None
    plants_prev_url = url_for('main.index', plants_page=plants.prev_num, posts_page=posts_page) \
        if plants.has_prev else None

    posts_next_url = url_for('main.index', plants_page=plants_page, posts_page=posts.next_num) \
        if posts.has_next else None
    posts_prev_url = url_for('main.index', plants_page=plants_page, posts_page=posts.prev_num) \
        if posts.has_prev else None

    wall_posts_next_url = url_for('main.index', plants_page=plants_page, wall_posts_page=wall_posts.next_num) \
        if wall_posts.has_next else None
    wall_posts_prev_url = url_for('main.index', plants_page=plants_page, wall_posts_page=wall_posts.prev_num) \
        if wall_posts.has_prev else None
    return render_template('user.html', user=user, plants=plants.items, posts=posts.items, wall_posts=wall_posts.items, form=form)


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

@bp.route('/user/<garden_name>, <garden_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_garden(garden_name, garden_id):
    garden = Garden.query.filter_by(id=garden_id).first_or_404()
    form = DeleteGardenForm()
    if form.validate_on_submit():
        db.session.delete(garden)
        db.session.commit()
        flash('Your garden has been removed!')
        return redirect(url_for('main.index'))
    return render_template('delete_garden.html', form=form, garden=garden)


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