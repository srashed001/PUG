from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
db = SQLAlchemy()



class Follows(db.Model):
    
    __tablename__ = 'follows'

    user_being_followed_id = db.Column(db.Integer,db.ForeignKey('users.id', ondelete="cascade"), primary_key=True,)
    user_following_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True )

class User_Game(db.Model):
    
    __tablename__ = 'user_games'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='cascade'), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())


class Game(db.Model):
    
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text)
    city = db.Column(db.Text, nullable=False)
    state = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    messages = db.relationship('Messages' )


class User(db.Model):
    """User class model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    city = db.Column(db.Text, nullable=False)
    state = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.Text, nullable=False, default= 'default.jpg')

    games_created = db.relationship('Game', backref="game_creator")

    games = db.relationship('Game', secondary='user_games')

    followers = db.relationship('User', secondary='follows', primaryjoin=(Follows.user_being_followed_id == id), secondaryjoin=(Follows.user_following_id == id))

    following = db.relationship('User', secondary='follows', primaryjoin=(Follows.user_following_id == id), secondaryjoin=(Follows.user_being_followed_id == id))

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"
    
    def get_fullname(self):
        """return full name"""
        return f"{self.first_name} {self.last_name}"
    
    def get_location(self):
        """return user location as a string """
        return f"{self.city}, {self.state}"

    def is_followed_by(self, other_user):
        """Is this user followed by 'other_user'"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1 
    
    def is_following(self, other_user):
        """Is this user following 'other_user"""

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1

    @classmethod
    def signup(cls, first_name, last_name, username, email, password, city, state):
        """sign up user
        hashes password and adds user to system"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            first_name=first_name, 
            last_name=last_name, 
            username=username, 
            email=email, 
            password=hashed_pwd, 
            city=city, 
            state=state
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """attempts to authenticate user credentials 
        If a authentication successful, it returns that user object. 
        
        If authentication fails it returns false"""

        user = cls.query.filter_by(username=username).first()

        if user: 
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user 

        return False 





class Messages(db.Model):

    __tablename__ = 'message_boards'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    






def connect_db(app):
    """connect to this database to provided flask app"""

    db.app = app 
    db.init_app(app)
