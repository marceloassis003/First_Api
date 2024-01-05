from flask import Flask



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bd.sqlite"
app.config['JSON_SORT_KEYS'] = False
secret = app.config['SECRET_KEY'] = 'e749a4fd0e4104136484b269a125ddfb'
alg = app.config['JWT_ALGORITHM'] = 'HS256'



@app.route("/")
def home():
    return "hello world from api "


@app.route("/about")
def about():
    return "hello abou from this"



if __name__ == "__main__":   
    with app.app_context():
        app.run( debug=True)

