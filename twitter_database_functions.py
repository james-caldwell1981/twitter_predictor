import numpy as np
import tweepy
from os import environ
from twitter_data_model import DB, Tweet, User
from functools import partial


twitter_auth = tweepy.OAuthHandler(environ['TWITTER_API_KEY'], environ['TWITTER_API_KEY_SECRET'])
twitter_api = tweepy.API(twitter_auth)


def upsert_user(twitter_handle, nlp):

    try:
        twitter_user = twitter_api.get_user(twitter_handle)
        if User.query.get(twitter_user.id):
            db_user = User.query.get(twitter_user.id)
        else:
            db_user = User(id=twitter_user.id, name=twitter_handle)
            DB.session.add(db_user)

        user_tweet_ids = [tweet.id for tweet in Tweet.query.filter(Tweet.user_id == db_user.id).all()]
        user_tweets_func = partial(twitter_user.timeline, count=500, exclude_replies=True, include_trs=False,
                                                tweet_mode='extended')
        if len(user_tweet_ids) > 0:
            last_tweet_stored_id = np.max(user_tweet_ids)
            user_tweets = user_tweets_func(sinc_id=last_tweet_stored_id)

            if last_tweet_stored_id >= max(user_tweet_ids):
                return 'No new tweets.'
        else:
            user_tweets = user_tweets_func()

        for tweet in user_tweets:
            vectorized_tweet = nlp(tweet.full_text).vector
            db_tweet = Tweet(id=tweet.id, text=tweet.full_text, vect=vectorized_tweet)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)

    except Exception as e:
        raise e
    else:
        DB.session.commit()

    return db_user


def get_user_names():
    return User.query.with_entities(User.name)
