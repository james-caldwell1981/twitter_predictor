import spacy
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from twitter_data_model import User
import pandas as pd
import numpy as np

transformer = spacy.load('../my_model')

def get_most_likely_author(usernames, tweet_to_classify):

    df_dataset = pd.DataFrame()

    for i, author in enumerate(usernames):
        author = User.query.filter(User.name == author).one()
        author_features = np.array([transformer(tweet.text).vector for tweet in author.tweets])
        author_target = np.zeros(len(author.tweets)) + i
        author_dataset = pd.DataFrame(author_features)
        author_dataset['target'] = author_target
        df_dataset = pd.concat([df_dataset, author_dataset])

    model = LogisticRegression(max_iter=1000)
    model.fit(df_dataset[[c for c in df_dataset.columns if c is not 'target']], df_dataset['target'])
    most_likely_author_index = model.predict([transformer(tweet_to_classify).vector])

    return usernames[int(most_likely_author_index)]