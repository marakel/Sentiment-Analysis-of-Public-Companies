import praw
import tweepy
import webbrowser
import time
import flair
import json 
import os
import pandas as pd
from pygooglenews import GoogleNews
from collections import Counter
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from datetime import datetime
from dotenv import load_dotenv


#API Keys/Username Information imported from env file
load_dotenv()
reddit_client_id = os.getenv("reddit_client_id")
reddit_client_secret = os.getenv("reddit_client_secret")
reddit_username = os.getenv("reddit_username")
reddit_password = os.getenv("reddit_password")
twitter_consumer_key = os.getenv("twitter_consumer_key")
twitter_consumer_secret = os.getenv("twitter_consumer_secret")


def reddit_data(subreddit_name):
    """Using the reddit api to grab the most recent 100 post titles in the given subreddit. 
    
    Args: 
    subreddit_name (string): The name of the subreddit that is being searched.

    Return:
    reddit_df: A dataframe of the most recent 100 post titles.
    """
    reddit = praw.Reddit(client_id= reddit_client_id, 
                        client_secret= reddit_client_secret,
                        username= reddit_username,
                        password= reddit_password,
                        user_agent= 'prawscraper')

    subreddit = reddit.subreddit(subreddit_name) 
    new_posts = subreddit.new(limit=100)
    reddit_df = []
    for submission in new_posts:
        if not submission.stickied:
            reddit_df.append(submission.title)
    reddit_df = pd.DataFrame(reddit_df)
    reddit_df.rename(columns={0:'Text'}, inplace=True)
    return reddit_df


def google_data(headline_keyword):
    """Using the pygooglenews package to grab the most recent 100 headlines related to the keyword.
    
    Args: 
    headline_keyword (string): The keyword that is being searched on Google News.

    Return:
    google_df: A dataframe of the most recent 100 related headlines.
    """
    gn = GoogleNews()
    search = gn.search(headline_keyword)

    google_df = []
    for item in search['entries']:
        google_df.append(item['title'])

    google_df= pd.DataFrame(google_df)
    google_df.rename(columns={0:'Text'}, inplace=True)
    return google_df


def twitter_data(tweet_query):
    """Using the twitter api and the tweepy package to grab recent tweets containing the keyword.
    
    Args: 
    tweet_query (string): The keyword that is being searched for on twitter.

    Return:
    twitter_df: A dataframe of the 100 most recent tweets containing the keyword.
    """
    consumer_key = twitter_consumer_key
    consumer_secret = twitter_consumer_secret
    callback_uri = 'oob'
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback_uri)
    redirect_url = auth.get_authorization_url()
    webbrowser.open(redirect_url)
    user_pin_input = input("What's the pin value? ")
    auth.get_access_token(user_pin_input)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    verify = api.verify_credentials()
    cursor = tweepy.Cursor(api.search_tweets, q=tweet_query, tweet_mode = 'extended').items(900)

    twitter_df = []
    for i in cursor:
        tweets = i.full_text
        try:
            if detect(tweets) == 'en':
                twitter_df.append(tweets)
        except LangDetectException:
            pass

    twitter_df = pd.DataFrame(twitter_df)
    twitter_df.rename(columns={0:'Text'}, inplace=True)

    #Removing Retweets and mentions then taking the most recent 100 tweets
    twitter_df = twitter_df[~twitter_df.Text.str.contains("RT")]
    twitter_df = twitter_df[~twitter_df.Text.str.contains("@")]
    twitter_df = twitter_df.reset_index(drop=True)
    twitter_df = twitter_df[:100]
    return twitter_df


def sentiment_model(keyword):
    """Calling the 3 data functions, combining the 3 dataframes into one, 
    and passing all the data through the flair sentiment model. Percentage 
    of positive/negative sentiment is calculated and the positive value is 
    considered the sentiment value. The final result is written to a json file.
    
    Args: 
    keyword (string): The keyword that is passed to the 3 scraper functions.
    """
    reddit_df = reddit_data(keyword)
    google_df = google_data(keyword)
    twitter_df = twitter_data(keyword)
    all_data = pd.concat([reddit_df, google_df, twitter_df], axis=0)

    #Passing data through flair sentiment model.
    sentiment_model = flair.models.TextClassifier.load('en-sentiment')
    sentiment = []
    confidence = []
    for sentence in all_data['Text']:
        if sentence.strip() == "":
            sentiment.append("")
            confidence.append("")
        else:
            sample = flair.data.Sentence(sentence)
            sentiment_model.predict(sample)
            sentiment.append(sample.labels[0].value)
            confidence.append(sample.labels[0].score)

    #Calculating the percentage of negative/positive sentiment.
    count = Counter(sentiment).items()
    percentages = {x: int(float(y) / len(sentiment) * 100) for x, y in count}

    #Write results to a file
    filename = 'sentimentvalue.json'
    with open(filename, 'w') as outfile:
        json.dump(percentages, outfile)


enter_keyword = str(input("Enter company name: "))
sentiment_model(enter_keyword)
