from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///anime.db"
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

def create_database():
    with app.app_context():
        ...

create_database()

@app.route("/")
def home():
    result = db.session.execute(db.select(Anime).order_by(Anime.ranking))
    all_anime = result.scalars().all()
    return render_template("index.html", anime=all_anime)

@app.route("/edit", methods=["GET", "POST"])
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

if __name__ == '__main__':
    app.run(debug=True)
