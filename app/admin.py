from app import app, db, ma
import random

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
        while True:
            for _ in range(16):
                random_integer = random.randint(97, 97 + 26 - 1)
                flip_bit = random.randint(0, 1)
                random_integer = random_integer - 32 if flip_bit == 1 else random_integer
                random_string += (chr(random_integer))
            user = Admins.query.filter_by(token=random_string).first()
            if not user:
                break
        self.admin_token = random_string
    
    def __repr__(self) -> str:
        return f"Admin {self.admin_username}"

class Admin_schema(ma.Schema):
    class Meta:
        fields = ("username", "password")

@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    pass

@app.route("/admin/home", methods=["GET"])
def admin_home():
    pass
