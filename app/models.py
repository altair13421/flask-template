from app import app, db, ma
from datetime import datetime as dt

"""
follows = db.Table(
    'follows',
    db.metadata,
    db.Column('follower_id', db.Integer, db.ForeignKey("user.user_id")),
    db.Column('followed_id', db.Integer, db.ForeignKey("user.user_id")),
)
"""
import random
# Tables
class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, nullable=False, unique=True)
    email = db.Column(db.String, index=True, nullable=False, unique=True)
    password = db.Column(db.String, index=False, nullable=False)
    name = db.Column(db.String, index=True, nullable=False)
    date_of_birth = db.Column(db.String)
    is_deleted = db.Column(db.Boolean, default=False)
    about_user = db.Column(db.String, default=f"Hi I am User {username}")
    token = db.Column(db.String, unique=True)

    posts = db.relationship("Posts", backref="writer", lazy="dynamic")
    comments_by_user = db.relationship("Comments", backref="comment_by_user", lazy='dynamic')

    def set_about_user(self, about):
        self.about_user = about

    def get_token(self):
        return self.token
    
    def delete_user(self):
        self.is_deleted = True
        
    def set_token(self):
        random_string = ''
        while True:
            for _ in range(16):
                random_integer = random.randint(97, 97 + 26 - 1)
                flip_bit = random.randint(0, 1)
                random_integer = random_integer - 32 if flip_bit == 1 else random_integer
                random_string += (chr(random_integer))
            user = User.query.filter_by(token=random_string).first()
            if not user:
                break
        self.token = random_string

    def __repr__(self) -> str:
        return f"User {self.username}"


class Posts(db.Model):
    __tablename__ = "posts"
    post_id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String, index=True, nullable=False)
    post_body = db.Column(db.String, index=True)
    date_added = db.Column(db.DateTime, default=dt.now())
    author_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    comments = db.relationship("Comments", backref="comment_post", lazy="dynamic")
    is_deleted = db.Column(db.Boolean, default=False)
        
    def delete_post(self):
        self.is_deleted = True
    def __repr__(self) -> str:
        return f"Post {self.post_title} || User_id {self.author_id}"

class Comments(db.Model):
    __tablename__="comments"
    comment_id = db.Column(db.Integer, primary_key=True)
    comment_body = db.Column(db.String, nullable=False, index=True)
    time_added = db.Column(db.DateTime, default=dt.now())
    on_post = db.Column(db.Integer, db.ForeignKey("posts.post_id"))
    by_user = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    is_deleted = db.Column(db.Boolean, default=False)
        
    def delete_comment(self):
        self.is_deleted = True
    
    def __repr__(self) -> str:
        return f"Comment {self.comment_body} || On {self.on_post} || By {self.by_user}"
