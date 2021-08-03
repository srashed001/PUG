import os 
from PIL import Image

from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from sqlalchemy.exc import IntegrityError 

from models import db, connect_db, User, Game, Messages, User_Game, Follows
from forms import UserAddForm, LoginForm, UpdatePhoto, EditProfileForm, AddGameForm

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
            first_name=form.first_name.data,
            last_name=form.last_name.data, 
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            city=form.city.data, 
            state=form.city.data
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
    games_created = [g.id for g in Game.query.filter_by(creator_id = user_id)]
    # need to fix this

    games = (User_Game.query.filter(User_Game.user_id == user_id).order_by(User_Game.timestamp.desc()).all())
    print('******************************************')
    print('******************************************')
    print(games)
    print(user.games)
    print('******************************************')
    print('******************************************')

    return render_template('users/profile.html', user=user, games = games, games_created = games_created)

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

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")

@app.route('/users/edit_profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    # IMPLEMENT THIS
    if not g.user: 
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user 
    form = EditProfileForm(obj=user)

    if form.validate_on_submit():
        user = User.authenticate(g.user.username, form.password.data)

        if user:
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.username = form.username.data
            user.email = form.email.data 
            user.city = form.city.data
            user.state = form.state.data
       
            db.session.commit()
            return redirect(f'/users/{user.id}')
        flash("Access unauthorized.", "danger")
        return redirect("/")
    return render_template('/users/edit.html', form = form, user = user)


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
    form = EditProfileForm(obj=user)

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

@app.route('/games/new', methods=["GET", "POST"])
def create_game():
    """Create new Game 
    Show form if GET. if valid submission, create new Game instance"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user 
    form = AddGameForm()

    if form.validate_on_submit():
        game = Game(
        title = form.title.data,
        description = form.description.data,
        address = form.address.data,
        city = form.city.data,
        state = form.state.data,
        creator_id = user.id,
        date = form.date.data,
        time = form.time.data,
        )
        user.games.append(game)
        db.session.commit()
        
        return redirect(f'/users/{user.id}')
    
    return render_template("games/new.html", form = form, user=user)


















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