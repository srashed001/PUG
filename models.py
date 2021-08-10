from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask import g


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

    game = db.relationship('Game')


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

    users = db.relationship('User', secondary='user_games')

    def serialize(self):
        return {
        'id': self.id, 
        'title': self.title,
        'description': self.description,
        'city': self.city,
        'state': self.state,
        'creator_id': self.creator_id,
        'creator_img_file':self.game_creator.image_file if self.creator_id else "default.jpg", 
        'creator_username':self.game_creator.username if self.creator_id else None, 
        'members':len(self.users), 
        'creator_img_file':self.game_creator.image_file if self.creator_id else "default.jpg", 
        'date': self.date.strftime('%B %d'),
        'time': self.time.strftime('%H:%M%p'),
    }


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


class Message(db.Model):

    __tablename__ = 'message_boards'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    user = db.relationship('User', backref='messages')
    game = db.relationship('Game', backref='messages')

    def __repr__(self):
        return f"<Message #{self.id}: user_id:{self.user_id}, game_id:{self.game_id}>"

    def serialize(self):
        return {
        'id': self.id, 
        'game_id': self.game_id,
        'user_id': self.user_id,
        'text': self.text,
        'timestamp': self.timestamp,
        'user_name': self.user.get_fullname(),
    }


class Court(db.Model):

    __tablename__ = 'courts'

    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float)
    address = db.Column(db.Text, unique=True)
    city = db.Column(db.Text, nullable = False)
    state = db.Column(db.Text, nullable = False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    url = db.Column(db.Text)

    games = db.relationship('Game', secondary='game_courts', backref='court')

class GameCourt(db.Model):

    __tablename__ = 'game_courts'

    court_id = db.Column(db.Text, db.ForeignKey('courts.id', ondelete='cascade'), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='cascade'), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

class Invite(db.Model):

    __tablename__= 'invites'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id", ondelete='cascade'))
    inviter_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='cascade'))
    invitee_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='cascade'))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False, default='pending')
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    

def connect_db(app):
    db.app = app
    db.init_app(app)