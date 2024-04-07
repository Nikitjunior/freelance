from flask import Flask
from data import db_session


app = Flask(__name__)
app.config['SECRET_KEY'] = '12qasdj6'


@app.route("/")
def index():
    return ""


def main():
    db_session.global_init("db/freelance.db")
    app.run()


if __name__ == '__main__':
    main()
