import numpy as np
from twitter_data_model import DB, Tweet, User
from functools import partial


"""
The heroku library via pip also installs python-dateutil 1.5 regardless of what is already installed,
which is outdated and breaks pandas. The solution was to uninstall heroku and python-dateutil,
reinstalling the correct version of python-dateutil.

The updated version of heroku via pip is heroku3, which does not work on windows. Instead,
a windows user must download and run an installer, then restart the computer. After this,
the library will not work unil the user deletes the buildpacks and reinstalls them in
the correct order because heroku does not do this automatically. Only then  can the user
initialize a web dyno, which is required to handle the application requests.

(venv) C:\Repositories\unit3\lambda33\heroku>heroku ps:scale web=2 -a lambda33
Scaling dynos... !
 !    Couldn't find that process type (web).


Also, gunicorn does not work on windows due to the library fcntl not supporting windows.
This means the only way to test the application is by deploying to heroku, which has eaten
a lot of time.

The above is my understanding of the issues encountered with deployment to heroku from windows.
I may be mistaken and have missed a setting or function call, but so far the internet trail
has led me here but I don't have the time to finish it due to the sprint challenge being due.
"""

def upsert_user(twitter_handle, nlp, twitter_api):

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
