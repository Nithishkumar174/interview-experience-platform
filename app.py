from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)

jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    experiences = db.relationship("Experience", backref="user", lazy=True)

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100))
    role = db.Column(db.String(100))
    round_type = db.Column(db.String(100))
    difficulty = db.Column(db.String(50))
    experience_text = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    upvotes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/clear")
def clear():
    return """
    <script>
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        window.location.href = '/';
    </script>
    """

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register_page")
def register_page():
    return render_template("register.html")


@app.route("/login_page")
def login_page():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/register", methods=["POST"])
def register():

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")


    new_user = User(
        username=username,
        email=email,
        password=generate_password_hash(password)
    )

    db.session.add(new_user)
    db.session.commit()

    return {"message": "User Registered Successfully"}, 201


@app.route("/login", methods=["POST"])
def login():

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):

       access_token = create_access_token(identity=str(user.id))

       return {
        "token": access_token,
        "username": user.username
         }

    return "Invalid Email or Password"

@app.route("/add_experience", methods=["POST"])
@jwt_required()
def add_experience():

    company_name = request.form.get("company_name")
    role = request.form.get("role")
    round_type = request.form.get("round_type")
    difficulty = request.form.get("difficulty")
    experience_text = request.form.get("experience_text")
    current_user = get_jwt_identity()

    new_experience = Experience(
        company_name=company_name,
        role=role,
        round_type=round_type,
        difficulty=difficulty,
        experience_text=experience_text,
        user_id=current_user

    )

    db.session.add(new_experience)
    db.session.commit()

    return "Experience Added Successfully"


@app.route("/experiences")
def get_experiences():

    company = request.args.get("company")
    role = request.args.get("role")
    difficulty = request.args.get("difficulty")

    query = Experience.query

    if company:
        query = query.filter_by(company_name=company)

    if role:
        query = query.filter_by(role=role)

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    experiences = query.all()

    return {
    "experiences": [
        {
            "id": e.id,
            "company_name": e.company_name,
            "role": e.role,
            "round_type": e.round_type,
            "difficulty": e.difficulty,
            "experience_text": e.experience_text,
            "upvotes": e.upvotes,
            "username": e.user.username,
            "created_at":
            e.created_at.strftime("%d-%m-%Y %H:%M")
        }
        for e in experiences
    ]
    }


@app.route("/update_experience/<int:id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_experience(id):

    exp = Experience.query.get(id)

    if not exp:
        return {"error": "Experience not found"}, 404

    data = request.get_json()

    # update only fields that are provided
    if "company_name" in data:
        exp.company_name = data["company_name"]

    if "role" in data:
        exp.role = data["role"]

    if "round_type" in data:
        exp.round_type = data["round_type"]

    if "difficulty" in data:
        exp.difficulty = data["difficulty"]

    if "experience_text" in data:
        exp.experience_text = data["experience_text"]

    db.session.commit()

    return {
        "message": "Experience updated successfully",
        "updated_data": {
            "id": exp.id,
            "company_name": exp.company_name,
            "role": exp.role,
            "round_type": exp.round_type,
            "difficulty": exp.difficulty,
            "experience_text": exp.experience_text
        }
    }, 200

@app.route("/delete_experience/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_experience(id):

    exp = Experience.query.get(id)

    if not exp:
        return {"error": "Not found"}, 404

    db.session.delete(exp)
    db.session.commit()

    return {"message": "Deleted successfully"}, 200


@app.route("/upvote/<int:id>", methods=["POST"])
@jwt_required()
def upvote(id):

    exp = Experience.query.get(id)

    if not exp:
        return {"error": "Not found"}, 404

    exp.upvotes += 1
    db.session.commit()

    return {
      "message": "Upvoted successfully",
       "upvotes": exp.upvotes
    }


with app.app_context():
    db.create_all()

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )