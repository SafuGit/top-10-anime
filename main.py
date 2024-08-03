from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()
db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db.init_app(app)
Bootstrap5(app)

class Anime(db.Model): # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(250))
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250), nullable=False)

class EditForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField("Your Review")
    submit = SubmitField("Done")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")

class AddForm(FlaskForm):
    title = StringField("Anime Title", validators=[DataRequired()])
    year = StringField("Release Year", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    rating = StringField("Rating", validators=[DataRequired()])
    ranking = StringField("Ranking", validators=[DataRequired()])
    review = StringField("Review", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[DataRequired()])
    submit = SubmitField("Add")

def create_database():
    with app.app_context():
        db.create_all()

create_database()

@app.route("/")
def home():
    result = db.session.execute(db.select(Anime).order_by(Anime.ranking))
    all_anime = result.scalars().all()
    return render_template("index.html", anime=all_anime)

@app.route(os.getenv("EDIT_TOKEN"), methods=["GET", "POST"]) #type: ignore
def edit():
    form = EditForm()
    id = request.args.get('id')
    if request.method == "POST":
        if form.validate_on_submit(): 
            anime_to_update = db.get_or_404(Anime, id)
            anime_to_update.rating = form.rating.data
            anime_to_update.review = form.review.data
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("edit.html", form=form)

@app.route(os.getenv("DELETE_TOKEN"), methods=["GET", "POST"]) #type: ignore
def delete():
    id = request.args.get('id')
    anime_to_delete = db.get_or_404(Anime, id)
    db.session.delete(anime_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    method = request.args.get("method")
    id = request.args.get("id")
    if request.method == "POST":
        if form.validate_on_submit() and form.username.data == os.getenv("USERNAME") and form.password.data == os.getenv("PASSWORD"): 
            if method == "update":
                return redirect(url_for('edit', id=id))
            elif method == "delete":
                return redirect(url_for('delete', id=id))
            elif method == "add":
                return redirect(url_for('add'))
    return render_template("login.html", form=form)

@app.route(os.getenv("ADD_TOKEN"), methods=["GET", "POST"]) #type: ignore
def add():
    form = AddForm()
    if request.method == "POST":
        if form.validate_on_submit():
            new_anime = Anime(
                title = form.title.data,
                year = form.year.data,
                description = form.description.data,
                rating = form.rating.data,
                ranking = form.ranking.data,
                review = form.review.data,
                img_url = form.img_url.data
            )
            db.session.add(new_anime)
            db.session.commit()
    return render_template('add.html', form=form)

if __name__ == "__main__":
    app.run()
