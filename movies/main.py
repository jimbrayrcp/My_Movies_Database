import os
from datetime import datetime
import sqlalchemy.exc
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask import send_from_directory
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, TextAreaField
from wtforms.validators import DataRequired
import webbrowser
from config_control import ConfigJson
from database import db_session, init_db
from model import Movie
from movie_api import MovieList

config = ConfigJson()

app = Flask(__name__)
app.config['SECRET_KEY'] = config.read(item_to_read="APP_SECRET_KEY")
Bootstrap(app)
init_db()
now = datetime.now()
year = now.strftime("%Y")


class ApiForm(FlaskForm):
    """
    Flask constructor for the api entry form
    """
    er_key = "Must have an API Key to save"
    er_placeholder = "enter your api key here"
    key = StringField("Your API Key",
                      validators=[DataRequired(er_key)],
                      render_kw={"placeholder": er_placeholder})
    submit = SubmitField(label="Save Key")


class MovieEdit(FlaskForm):
    """
    Flask constructor for the edit form
    """
    er_rating = "a value with a decimal > 0.0 must be included ex. '4.2'"
    ds_rating = "Enter a value from 0.1 to 10.0 (""include decimal)"
    er_review = "Please add a word or two for your review"
    rating_m = FloatField("Movie Rating", validators=[DataRequired(er_rating)], description=ds_rating)
    review_m = TextAreaField("Movie Review", validators=[DataRequired(er_review)])
    submit_m = SubmitField(label="Save Movie")


class MovieSearch(FlaskForm):
    """
    Flask constructor for the api search form
    """
    er_title = "The movie must have a title"
    title_m = StringField("Movie Title", validators=[DataRequired(er_title)], description="Enter a Movie Title")
    submit_m = SubmitField(label="Find Movie")


@app.route('/favicon.ico')
def favicon():
    """
    gets the favicon for the app
    :return: favicon file
    """
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.teardown_appcontext
def shutdown_session(exception=None):
    """
    shuts down the database session
    :param exception:
    :return:
    """
    db_session.remove()


@app.route("/")
def home():
    """
    index page
    :return: index file
    """
    pictures = db_session.query(Movie).order_by(Movie.rating.desc())
    for count, row in enumerate(pictures):
        row.ranking = count + 1
        db_session.commit()
    movies = db_session.query(Movie).order_by(Movie.rating.asc())
    return render_template("index.html", movies=movies)


@app.route("/account", methods=["GET"])
def account_get():
    """
    account get for opening the page
    :return: account file
    """
    keys = config.read(item_to_read="MOVIE_API_KEY")
    form = ApiForm(request.form, obj=keys)
    if keys:
        form = ApiForm()
        form.key.data = config.read(item_to_read="MOVIE_API_KEY")
        form.submit.label.text = 'Update Key'
    return render_template("account.html", action="Add", form=form)


@app.route("/account", methods=["POST"])
def account_post():
    """
    account post data processing
    :return: the index file if successful entry otherwise the account file
    """
    keys = config.read(item_to_read="MOVIE_API_KEY")
    form = ApiForm(request.form, obj=keys)
    if not keys:
        if form.validate_on_submit():
            key = form.key.data
            config.edit(key="MOVIE_API_KEY", new_value=key)
            return redirect(url_for('home'))
    elif form.validate_on_submit():
        new_key = form.key.data
        config.edit(key="MOVIE_API_KEY", new_value=new_key)
        return redirect(url_for('home'))
    return render_template("account.html", action="Add", form=form)


@app.route("/search", methods=["GET", "POST"])
def search():
    """
    search page
    :return: add file
    """
    search = MovieSearch()
    if search.validate_on_submit():
        title = search.title_m.data,
        mlc = MovieList()
        try:
            mlc.poll_api_search(movie_title=title)
        except Exception as ex:
            template = "{0}: \n{1!r}"
            er_msg = template.format(type(ex).__name__, ex.args)
            message = f"Hey, did you get your API key yet?\n\n" \
                f"If yes, please ensure it was entered correctly!\n\n" \
                f"   App Error: {er_msg}"
            text_msg = message.split('\n')
            flash(text_msg, category="warning")
            return redirect(url_for('search'))
        else:
            movies = mlc.choice_from_list()
            session['movies_list'] = movies
            return redirect(url_for('select'))
    return render_template("add.html", action="Add", form=search)


@app.route("/select", methods=["GET", "POST"])
def select():
    """
    select page
    :return: select file
    """
    return render_template("select.html")


@app.route("/selected/<movie_id>", methods=["GET"])
def selected(movie_id):
    """
    adds the selected movie to the database
    :param movie_id: id to send to MovieList helper
    :return: the selected movie info to the database
    """
    sel = MovieList()
    sel.poll_api_id(movie_id)
    sel.get_results()
    date_time_str = sel.release_date
    date_time_obj = datetime.strptime(date_time_str, '%Y')
    new_movie = Movie(
        title=sel.original_title,
        year=date_time_obj,
        description=sel.overview,
        rating=0.0,
        ranking=None,
        review="",
        img_url=sel.image
    )
    db_session.add(new_movie)
    try:
        db_session.commit()
    except sqlalchemy.exc.IntegrityError:
        flash(f"The Movie {sel.original_title} is already in your collection", category="warning")
        return redirect(url_for('home'))
    else:
        new_movie = Movie.query.filter_by(title=sel.original_title).first()
        return redirect(url_for("edit", movie_id=new_movie.id))


@app.route("/edit/<int:movie_id>", methods=['GET', 'POST'])
def edit(movie_id):
    """
    edit page
    :param movie_id: movie id being edited
    :return: GET: edit file POST: index file
    """
    item = db_session.query(Movie).get(movie_id)
    edit = MovieEdit(request.form, obj=item)
    new_movie = Movie.query.filter_by(id=movie_id).first()
    if request.method == 'GET':
        edit.rating_m.data = item.rating
        edit.review_m.data = item.review
    if edit.validate_on_submit():
        item.rating = edit.rating_m.data
        item.review = edit.review_m.data
        db_session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", action="Edit", movie=new_movie.title, form=edit)


@app.route("/home/<int:movie_id>")
def delete(movie_id):
    """
    deletes the movie from the database
    :param movie_id: id to delete
    :return: index file
    """
    movie_to_delete_id = Movie.query.get(movie_id)
    db_session.delete(movie_to_delete_id)
    db_session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    """
    auto opens the users default browser
    """
    webbrowser.open_new("http://localhost:5000")
    app.run(debug=True)
