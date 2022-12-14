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
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, nullable=False)
    email = db.Column(db.String, index=True, nullable=False)
    password = db.Column(db.String, index=False, nullable=False)
    name = db.Column(db.String, index=True, nullable=False)
    date_of_birth = db.Column(db.String)
    about_user = db.Column(db.String, default=f"Hi I am User {username}")
    sign_up_time = db.Column(db.String, default= f"{dt.now().isoformat()}")
    token = db.Column(db.String, unique=True)

    posts = db.relationship("Posts", backref="writer", lazy="dynamic")
    comments_by_user = db.relationship("Comments", backref="comment_by_user", lazy='dynamic')
    
    is_deleted = db.Column(db.Boolean, default=False)

    def set_about_user(self, about):
        self.about_user = about

    def get_token(self):
        return self.token
    
    def delete_user(self):
        self.is_deleted = True
        self.username = f"{self.username}_[DELETED]"
        self.email = f"{self.email}_[DELETED]"
        self.about_user = f"[DELETED]"
    
    def change_password(self, password):
        self.password = password
        
    def change_name(self, name):
        self.name = name
    
    def change_email(self, email):
        self.email = email
        
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
    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String, index=True, nullable=False)
    post_body = db.Column(db.String, index=True)
    
    date_added = db.Column(db.String, default=f"{dt.now().isoformat()}")
    
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comments = db.relationship("Comments", backref="comment_post", lazy="dynamic")
    
    is_deleted = db.Column(db.Boolean, default=False)
        
    def delete_post(self):
        self.is_deleted = True
        for comment in self.comments:
            comment.delete_comment()
            db.session.commit()
    
    def __repr__(self) -> str:
        return f"Post {self.post_title} || User_id {self.author_id}"

class Comments(db.Model):
    __tablename__="comments"
    id = db.Column(db.Integer, primary_key=True)
    comment_body = db.Column(db.String, nullable=False, index=True)
    
    time_added = db.Column(db.String, default=f"{dt.now().isoformat()}")
    
    on_post = db.Column(db.Integer, db.ForeignKey("posts.id"))
    by_user = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    is_deleted = db.Column(db.Boolean, default=False)
        
    def delete_comment(self):
        self.is_deleted = True
    
    def __repr__(self) -> str:
        return f"Comment {self.comment_body} || On {self.on_post} || By {self.by_user}"
