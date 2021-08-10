import os 
from PIL import Image
import pprint

from flask import Flask, render_template, request, flash, redirect, session, g, url_for, jsonify
from sqlalchemy.exc import IntegrityError 

from models import db, connect_db, User, Game, User_Game, Follows, Message, Court, GameCourt
from forms import UserAddForm, LoginForm, UpdatePhoto, EditProfileForm, GameForm, EditGameForm, AddMessage, FindCourtForm, FindGame, InviteFriendsForm
from maps_api import get_courts, get_courts_next_or_previous, get_court_details, get_geocode

CURR_USER_KEY = 'curr_user'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///PUG'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")



connect_db(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        user = User.signup(
            first_name=form.first_name.data.title(),
            last_name=form.last_name.title(), 
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            city=form.city.data.title(), 
            state=form.state.data
        )
        db.session.commit()

        do_login(user)


        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""


    # IMPLEMENT THIS
    if not g.user:
        flash("You have not been logged in as a user.", "danger")
        return redirect("/login")
    
    do_logout()
    flash("Logged out successfully", "success")
    return redirect('/login')

# =========== User Routes ========================================================

@app.route('/users')
def list_users():
    """"Page listing all users
    
    Can take a 'q' param in querystring to search by that username"""

    search = request.args.get('q')

    if not search: 
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()
    
    return render_template('users/index.html')

@app.route('/users/<int:user_id>')
def users_profile(user_id):
    """show users profile"""

    user = User.query.get_or_404(user_id)
    curr_user = g.user
    games_created = [g.id for g in Game.query.filter_by(creator_id = user_id)]
    form = InviteFriendsForm()
    # need to fix this

    games = (User_Game.query.filter(User_Game.user_id == user_id).order_by(User_Game.timestamp.desc()).all())
    games = [game.game for game in games]

    return render_template('users/profile.html', form=form, curr_user=curr_user, user=user, games = games, games_created = games_created)

@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)

@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(request.referrer)


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(request.referrer)

@app.route('/users/edit_profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    # IMPLEMENT THIS
    if not g.user: 
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user 

 
    pwd_form = UpdatePhoto()
    form = EditProfileForm(obj=user)

    if pwd_form.validate_on_submit():
        if pwd_form.image.data:
            image_file = save_profile_picture(pwd_form.image.data)
            user.image_file = image_file
        db.session.commit()
        flash('Your profile picture has been updated!', 'success')
        return redirect(request.referrer)


    if form.validate_on_submit():
        user = User.authenticate(g.user.username, form.password.data)

        if user:
            user.first_name = form.first_name.data.uppercase()
            user.last_name = form.last_name.data.uppercase()
            user.username = form.username.data
            user.email = form.email.data 
            user.city = form.city.data.uppercase()
            user.state = form.state.data
          
        
       
            db.session.commit()
            return redirect(f'/users/{user.id}')
        flash("Access unauthorized.", "danger")
        return redirect(request.referrer)
    return render_template('/users/edit.html', pwd_form=pwd_form, form = form, user = user)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")

# for image upload 
def save_profile_picture(form_image):
    image_id = str(g.user.id)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = image_id + f_ext
    image_path = os.path.join(app.root_path, 'static/profile_pics', image_fn)

    output_size = (125, 125)
    i = Image.open(form_image)
    i.thumbnail(output_size)

    i.save(image_path)

    return image_fn


@app.route('/users/profile_pic', methods=["GET", "POST"])
def image_upload(): 

    if not g.user: 
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user 

    form = UpdatePhoto()
    if form.validate_on_submit():
        if form.image.data:
            image_file = save_profile_picture(form.image.data)
            user.image_file = image_file
        db.session.commit()
        flash('Your profile picture has been updated!', 'success')
        return redirect(url_for('image_upload'))
    
    image_file = url_for('static', filename='profile_pics/' + g.user.image_file)
    return render_template('users/profile_pic.html', form=form, image = image_file, user=user)

# ==================== Game Routes ===================================================

@app.route('/games')
def find_games():
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = FindGame()

    return render_template('games/games.html', form = form, user=user)

@app.route('/api/games', methods=['POST'])
def get_games():
    
    city = request.json['city'].title()
    state = request.json['state']

    if city:
        games = Game.query.filter(Game.city.like(f"%{city}%"), Game.state == state).all()
        games = [game.serialize() for game in games]
        return jsonify(games = games )
        
    
    games = Game.query.filter_by(state=state).all()
    games = [game.serialize() for game in games]
    return jsonify(games = games )


@app.route('/games/new', methods=["GET", "POST"])
def create_game():
    """Create new Game 
    Show form if GET. if valid submission, create new Game instance"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user 
    form = GameForm()

    if form.validate_on_submit():
        game = Game(
        title = form.title.data,
        description = form.description.data,
        address = form.address.data.title(),
        city = form.city.data.title(),
        state = form.state.data,
        creator_id = user.id,
        date = form.date.data,
        time = form.time.data,
        )
        user.games.append(game)
        db.session.commit()
        
        return redirect(f'/users/{user.id}')
    
    return render_template("games/new.html", form = form, user=user)

@app.route('/games/<int:game_id>', methods=['GET'])
def game_details(game_id):

    user = g.user

    game = Game.query.get_or_404(game_id)
    address = game.address if game.address else None
    city = game.city
    state = game.state
    form = AddMessage()

    resp = get_geocode(address, city, state)
    lat = resp['lat']
    lng = resp['lng']

    return render_template('games/details.html', lat=lat, lng=lng, game = game, user=user, form=form)

@app.route('/games/<int:game_id>', methods=['POST'])
def join_game(game_id):

    game = Game.query.get_or_404(game_id)
    user = g.user

    if not g.user:
        flash("You must be a PUG member to join. Please signup!.", "danger")
        return jsonify(message="Access Unauthorized, Please register to join game")

    if user.id != game.creator_id:
        user.games.append(game)
        db.session.commit()
        flash("You have joined this PUG!", "success")
        
        return jsonify(message="Game added")

    flash("You created this pug, you are already a member!")
    return jsonify(message="You are creator of this PUG")

@app.route('/games/<int:game_id>', methods=['DELETE'])
def leave_game(game_id):

    game = Game.query.get_or_404(game_id)
    user = g.user

    if not g.user:
        flash("You must be a PUG member to join. Please signup!.", "danger")
        return jsonify(message="Access Unauthorized, Please register to join game")

    if user.id != game.creator_id:
        user.games.remove(game)
        db.session.commit()
        flash("You have left this PUG!", "success")
        
        return jsonify(message="User removed from PUG")

    flash("You created this pug, you are already a member!")
    return jsonify(message="You are creator of this PUG")
 

@app.route('/games/<int:game_id>/edit', methods=["GET", "POST"])
def edit_game(game_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    game = Game.query.get_or_404(game_id)
    user = g.user

    address = game.address if game.address else None
    city = game.city
    state =game.state
    form = AddMessage()

    resp = get_geocode(address, city, state)
    lat = resp['lat']
    lng = resp['lng']


    form = EditGameForm(obj=game)
    if form.validate_on_submit():
        user = User.authenticate(g.user.username, form.password.data)

        if user:
            game.title = form.title.data.capitalize()
            game.description = form.description.data
            game.address = form.address.data.title()
            game.city = form.city.data.title()
            game.state = form.state.data
            game.date = form.date.data
            game.time = form.time.data
       
            db.session.commit()
            return redirect(f'/users/{user.id}')
        flash("Access unauthorized.", "danger")
        return redirect("/")
    return render_template('games/edit.html', form = form, user = user, game=game, lat=lat, lng=lng)


@app.route('/users/<int:user_id>/games')
def show_user_games(user_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(user_id)
    games = user.games_created

    return render_template('games/user.html', user = user, games = games)


@app.route('/games/<int:game_id>/delete', methods=["POST"])
def delete_game(game_id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    game = Game.query.get_or_404(game_id)
    if game.creator_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    db.session.delete(game)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")

# =========================== Message Routes=================================

@app.route('/messages/<int:game_id>', methods=['POST'])
def create_message(game_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    message = Message(
        game_id = int(request.json['game_id']),
        user_id = int(request.json['user_id']),
        text = request.json['text']
    )
    db.session.add(message)
    db.session.commit()

    return (jsonify(message=message.serialize()), 201)

@app.route('/messages/<int:game_id>', methods=['GET'])  
def get_messages(game_id):

    game = Game.query.get_or_404(game_id)

    messages = (Message.query.filter(Message.game_id == game.id).order_by(Message.timestamp.desc()).all())
    messages = [msg.serialize() for msg in messages]

    return jsonify(messages=messages)

@app.route('/messages/<int:msg_id>', methods=['DELETE'])  
def delete_messages(msg_id):

    msg = Message.query.get_or_404(msg_id)

    db.session.delete(msg)
    db.session.commit()
    return jsonify(message='Deleted')

# ===================== Court Routes ===========================================

@app.route('/courts')
def look_up_courts():

    form = FindCourtForm()
    return render_template('find_court.html', form=form)


@app.route('/api/courts', methods=["POST"])
def get_court():

    city = request.json['city']
    state = request.json['state']

    try:
        data = get_courts(city,state)
    except:
        return jsonify(error="currently unable to find courts in your area")
    
    return jsonify(data=data)

@app.route('/api/courts/next', methods=["POST"])
def next_page_court():

    pg_token = request.json['pageToken']

    try:
        data = get_courts_next_or_previous(pg_token)
    except:
        return jsonify(error="currently unable to find courts in your area")
    
    return jsonify(data=data)

@app.route('/courts/game/<court_id>', methods=["GET", "POST"])
def create_game_with_court_info(court_id):

    user = g.user
    court_place_details = get_court_details(court_id)
    court_details = court_place_details["result"]

    address = court_details["formatted_address"]
    lat = court_details["geometry"]["location"]['lat']
    lng = court_details["geometry"]["location"]['lng']
    name = court_details["name"]
    rating = court_details.get("rating", None)
    url = court_details.get("url", None)

    address_list = address.split(",")

    if len(address_list) == 3:
        city, state_zip, country = [ add.strip() for add in address_list]
        address = None
        state, zip_code = state_zip.split()
        flash("Since there is no address for this location, include one in the description", 'danger')
    
    else:
        address, city, state_zip, country = [ add.strip() for add in address_list]
        state, zip_code = state_zip.split()

    data = {
        "state": state,
        "city": city,
        "title": f'PUG @ {name}',
        "address": address
    }

    form = GameForm(data=data)

    if form.validate_on_submit():
        court = Court.query.filter_by(id = court_id).first()
        if court is None:
            court = Court(
                id=court_id,
                name = name, 
                rating = rating,
                address = address.title(),
                city = city.title(), 
                state = state, 
                lat = lat, 
                lng = lng, 
                url = url
            )
            db.session.add(court)
            db.session.commit()
        game = Game(
            title = form.title.data.capitalize(),
            description = form.description.data,
            address = form.address.data.title(),
            city = form.city.data.title(),
            state = form.state.data,
            creator_id = user.id,
            date = form.date.data,
            time = form.time.data,
            )
        game.court.append(court)
        user.games.append(game)
        db.session.commit()

        return redirect(f'games/{game.id}')
    
    else:
        return render_template('court_details.html', 
                                id = court_id, 
                                form=form, 
                                add = address, 
                                city=city, 
                                state=state, 
                                st_zip = state_zip, 
                                name = name, 
                                rating = rating, 
                                url=url, 
                                lat = lat, 
                                lng = lng)




@app.route('/')
def homepage():

    return render_template('home-anon.html')












@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req