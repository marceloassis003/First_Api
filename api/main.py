from flask import Flask
app = Flask(__name__)


@app.route("/")
def home():
    return "hello world from api "


@app.route("/about")
def about():
    return "hello abou from this"