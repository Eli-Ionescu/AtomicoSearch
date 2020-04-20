import os
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import requests
import json

# TODO: This should be secure ;)
AUTH_KEY = os.environ.get("AUTH_KEY")

from urllib.parse import urlparse

app = Flask(__name__)
# Local setting
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:atomico123@localhost/atomico'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # So that we don't get a warning

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

uri = "postgres+pg8000://{}:{}@/{}?unix_sock=/cloudsql/{}".format(db_user, db_pass, db_name, cloud_sql_connection_name)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # So that we don't get a warning

db = SQLAlchemy(app)


class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    url = db.Column(db.String(253), unique=True)
    twitter = db.Column(db.String(100), unique=True)

    def __init__(self, name, url, twitter=''):
        self.name = name
        self.url = url
        self.twitter = twitter

    def __repr__(self):
        return "<User(name='%s', url='%s', twitter='%s')>" % (self.name, self.url, self.twitter)


def get_screen_name(twitter_url):
    path = urlparse(twitter_url).path
    handler = path.split('/')[-1]
    return handler


def get_nr_twitter_followers(screen_name):
    headers = {
        'Authorization': 'Bearer ' + AUTH_KEY,
    }
    next_cursor_str = '-1'
    nr_followers = 0
    while True:
        params = (
            ('cursor', next_cursor_str),
            ('screen_name', screen_name),
            ('skip_status', 'true'),
            ('include_user_entities', 'false'),
            ('count', '200')
        )
        response = requests.get('https://api.twitter.com/1.1/followers/list.json', headers=headers, params=params)

        if response.status_code == 200:
            response_data = response.json()
            nr_followers += len(response_data['users'])
            next_cursor = response_data['next_cursor']

            if next_cursor == 0:
                return str(nr_followers)

        else:
            print("Bad request")
            print(response.json())
            break

    return str(-1)


def fast_get_nr_twitter_followers(screen_name):
    url = 'https://cdn.syndication.twimg.com/widgets/followbutton/info.json?screen_names=' + screen_name
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()  # Returns a list with the info about all the screen names passed
        return data[0]['followers_count']
    return -1


@app.route('/search/<path:search_field>')
def search(search_field):
    company = db.session.query(Company).filter(Company.name == search_field).first()
    if company is None:
        # Try to look up after the url
        company = db.session.query(Company).filter(Company.url == search_field).first()

    if company is None:
        company_not_in_db = {
            'name': -1,
            'url': -1,
            'twitter': -1,
            'nr_followers': -1
        }
        return company_not_in_db

    if company.twitter is None:
        url = company.url if company.url is not None else ''

        if company.url is not None:
            url = company.url

        twitter_not_found = {
            'name': company.name,
            'url': url,
            'twitter': -1,
            'nr_followers': -1
        }
        return twitter_not_found

    screen_name = get_screen_name(company.twitter)
    company_nr_followers = fast_get_nr_twitter_followers(screen_name)
    param_company = {
        'name': company.name,
        'url': company.url,
        'twitter': company.twitter,
        'nr_followers':  company_nr_followers
    }
    return param_company

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(500)
def server_error(e):
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
