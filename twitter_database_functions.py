import numpy as np
from twitter_data_model import DB, Tweet, User
from functools import partial


"""
Cannot connect to heroku due to the following errors and I cannot afford more time than already spent
or risk being unable to complete the sprint challenge.

(venv) C:\Repositories\unit3\lambda33\heroku>git push origin
Enumerating objects: 10, done.
Counting objects: 100% (10/10), done.
Delta compression using up to 4 threads
Compressing objects: 100% (5/5), done.
Writing objects: 100% (6/6), 645 bytes | 322.00 KiB/s, done.
Total 6 (delta 3), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (3/3), completed with 3 local objects.
To https://github.com/james-caldwell1981/twitter_predictor.git
   a3151ba..384343e  main -> main
   
(venv) C:\Repositories\unit3\lambda33\heroku>heroku ps:scale web=1 -a lambda33
Scaling dynos... !
 !    Couldn't find that process type (web).


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
