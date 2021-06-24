import os
import datetime
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/homepage")
def homepage():
    # get all forum posts
    posts = mongo.db.forum_posts.find()
    return render_template("homepage.html", posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # checks if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username Already Exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        # if username doesn't exist adds new username to db
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration Successful")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # checks if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # if username exists check if password matches
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))

            else:
                flash("Incorrect password")
                return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/new_post", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        # grabs the date and time of submission for display
        date_time = datetime.datetime.now()
        post = {
            "post_title": request.form.get("post_title"),
            "post_description": request.form.get("post_description"),
            "created_by": session["user"],
            "creation_date": date_time.strftime("%x"),
            "creation_time": date_time.strftime("%X")
        }
        mongo.db.forum_posts.insert_one(post)
        flash("Post Successful")
        return redirect(url_for("homepage"))

    return render_template("new_post.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grabs username of current session
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/view_replies/<post_id>")
def view_replies(post_id):
    post = mongo.db.forum_posts.find_one({"_id": ObjectId(post_id)})
    return render_template("view_replies.html", post=post)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
