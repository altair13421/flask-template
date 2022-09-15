from wsgiref.util import request_uri
from app import app, db, ma
import random
from flask import render_template, redirect, url_for, current_app, flash, request
from flask_bootstrap import Bootstrap
from flask_mdbootstrap import MDBootstrap
from flask_login import LoginManager, login_required, login_user, current_user, logout_user, UserMixin
from flask_wtf import FlaskForm
from werkzeug.urls import url_parse
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, ValidationError

mdbootstrap = MDBootstrap(app)
bootstrap = Bootstrap(app)
login = LoginManager(app=app)
login.login_view = 'admin_login'
login_messages = (
    "You must Be logged in",
    "Are you sure you're Logged in",
    "Drunks should Log in",
    "Login or Gimme your Soul",
    "Soul accepted, now You may Login",
    "BRING ME THEIR SOULS, or just login",
    "WE LIVE IN THE FUTURE, But you still have to login",
)

# Admin Model
class Admins(db.Model, UserMixin):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    admin_username = db.Column(db.String, unique=True)
    admin_password = db.Column(db.String)
    admin_token = db.Column(db.String)
    
    @login.user_loader
    def load_user(id):
        return Admins.query.get(int(id))
    
    def change_username(self, username):
        self.admin_username = username
    
    def change_password(self, password):
        self.admin_password = password
    
    def check_password(self, password):
        return self.admin_password == password
    
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
class Admin_Login_Form(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Enter the Panel")
    pass

# THE SHITTER
@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_home'))
    if request.method == "POST":
        # flash(form_data)
        user = Admins.query.filter_by(admin_username=request.form.get("username")).first()
        if user is None or not user.check_password(request.form.get("password")):
            flash('Invalid Username or Password')
            return redirect(url_for('admin_login'))
        login_user(user)
        flash("Login Successful")
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('admin_home')
        return redirect(next_page)
    return render_template(
        'admin_login.html', 
        title="Login",
        name_form='Admin Login',
        # form = form,
    )

@app.route("/admin/home", methods=["GET"])
@login_required
def admin_home():
    return render_template("admin.html")

@app.route('/admin/tables')
@login_required
def tables():
    engine_inspector = db.inspect(db.engine)
    table_names = engine_inspector.get_table_names()
    return render_template(
        "admin_tables.html", 
        table_names=table_names,
    )

@app.route('/admin/table/<table_name>')
@login_required
def view_table(table_name: str):
    if table_name == "alembic_version":
        flash(f"No Table Data For {table_name}, as it is a default Table")
        return redirect(url_for('tables'))
    engine_inspector = db.inspect(db.engine)
    # DB QUERY
    table_data = db.engine.execute(f"SELECT * FROM {table_name}").all()
    table_columns = engine_inspector.get_columns(table_name)
    if not table_name == "admin":
        table_columns = table_columns[0:3]
        table_data = [item[0:3] for item in table_data]
    flash(f"Table Data Get Successful for {table_name}")
    return render_template(
        "raw_table.html",
        table_name=table_name,
        table_columns=table_columns,
        table_data=table_data,
    )

@app.route("/admin/table/<table_name>/<id>")
def view_item(table_name:str, id: int):    
    if table_name == "alembic_version":
        flash(f"No Table Data For {table_name}, as it is a default Table")
        return redirect(url_for('tables'))
    engine_inspector = db.inspect(db.engine)
    # DB QUERY
    table_data = db.engine.execute(f"SELECT * FROM {table_name} WHERE id={int(id)}").all()[0]
    table_columns = engine_inspector.get_columns(table_name)
    return render_template(
        "raw_data.html",
        table_name=table_name,
        length = len(table_columns),
        table_columns=table_columns,
        table_data=table_data,
    )

@app.route('/admin/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.before_request
def before_request():
    login.login_message = login_messages[random.randint(0, len(login_messages)-1)]