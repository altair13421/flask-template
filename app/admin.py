from app import app, db, ma
import random
from flask import render_template, redirect, url_for, current_app
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError

bootstrap = Bootstrap(app)
login = LoginManager(app=app)
login.login_view = 'admin_login'

# Admin Model
class Admins(db.Model):
    __tablename__ = "admin"
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_username = db.Column(db.String, unique=True)
    admin_password = db.Column(db.String)
    admin_token = db.Column(db.String)
    
    def change_username(self, username):
        self.admin_username = username
    
    def change_password(self, password):
        self.admin_password = password
        
    def get_token(self):
        return self.admin_token
    
    def set_token(self):
        random_string = ''
        for _ in range(16):
            random_integer = random.randint(97, 97 + 26 - 1)
            flip_bit = random.randint(0, 1)
            random_integer = random_integer - 32 if flip_bit == 1 else random_integer
            random_string += (chr(random_integer))
        self.admin_token = random_string
    
    def __repr__(self) -> str:
        return f"Admin {self.admin_username}"

class Admin_schema(ma.Schema):
    class Meta:
        fields = ("username", "password")

# FORMS
class Admin_Login(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Enter the Panel")
    pass


@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    return render_template('admin_login.html')

@login.login_required
@app.route("/admin/home", methods=["GET"])
def admin_home():
    pass
