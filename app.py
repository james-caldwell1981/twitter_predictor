from flask import Flask, render_template, request, jsonify
from twitter_data_model import DB
from twitter_database_functions import upsert_user, get_user_names
import spacy
from predict import get_most_likely_author
import tweepy
from os import environ

def create_app():

    twitter_auth = tweepy.OAuthHandler(environ['TWITTER_API_KEY'], environ['TWITTER_API_KEY_SECRET'])
    twitter_api = tweepy.API(twitter_auth)

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    DB.init_app(app)

    nlp = spacy.load('../../lectures/module2-consuming-data-from-an-api/twitter_app/my_model')

    @app.route('/')
    def main_page():
        welcome = 'Welcome to Tweet Predictor'
        return render_template('base.html', welcome=welcome)


    @app.route('/add_author', methods=['GET', 'POST'])
    def add_author():
        twitter_handle = request.args['twitter_handle']
        new_user = upsert_user(twitter_handle, nlp, twitter_api)

        if new_user == 'No new tweets.':
            response_body = 'No new tweets.'

        elif 'Tweets' in dir(new_user):
            response_body = f'@{new_user.name}\'s tweets added to the database\n'.format(
                ', '.join([t.text for t in new_user.Tweets])
            )

        else:
            response_body = f'@{new_user.name}\'s tweets added to the database\n'

        return jsonify(response_name=twitter_handle, response_body=response_body)


    @app.route('/predict_author', methods=['GET', 'POST'])
    def predict_author():
        usernames = [i[0] for i in get_user_names()]
        tweet_to_classify = request.args['tweet_to_classify']

        author_prediction = get_most_likely_author(
            usernames,
            tweet_to_classify
        )

        return jsonify(response_name=author_prediction, response_body=f'@{author_prediction} would tweet this.')

    return app
