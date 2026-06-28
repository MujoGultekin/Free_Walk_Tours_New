# app.py
from flask import Flask, render_template, request, flash
from flask_login import LoginManager
from datetime import datetime
from models import User

# Importing DAO functions and Blueprints for modularity
from dao.users_dao import get_user_by_id
from dao.tours_dao import search_tours
from routes.auth_routes import auth_bp
from routes.guide_routes import guide_bp
from routes.participant_routes import participant_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "RomaFreeWalkingToursSecretKey2026"

# Configuring LoginManager for authentication
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    """
    Callback to reload the user object from the user ID stored in the session.
    """
    db_user = get_user_by_id(user_id)
    if db_user:
        return User(
            id=db_user["id"], name=db_user["name"], surname=db_user["surname"],
            email=db_user["email"], role=db_user["role"], languages=db_user["languages"]
        )
    return None

# Registering blueprints to organize routes
app.register_blueprint(auth_bp)
app.register_blueprint(guide_bp)
app.register_blueprint(participant_bp)

@app.route("/roma-tours")
def roma_tours():
    return render_template("roma_tours.html")

@app.route("/")
def home():
    """
    Home route: Handles filtering of tours based on language, duration, and date.
    """
    lang = request.args.get("language")
    duration = request.args.get("duration")
    date_input = request.args.get("date")
    
    day_name = None
    if date_input:
        try:
            # Converting date string to day name to match weekly schedule
            day_name = datetime.strptime(date_input, "%Y-%m-%d").strftime("%A")
        except ValueError:
            flash("Invalid date format.", "danger")
            
    tours = search_tours(day_name, duration, lang)
    return render_template("index.html", tours=tours)

if __name__ == "__main__":
    app.run(debug=True)