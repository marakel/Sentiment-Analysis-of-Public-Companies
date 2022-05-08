# Sentiment-Analysis-of-Public-Companies
---
The SentAnalysis.py file contains the main code which involves scraping data from three sources, passing the data to a sentiment model, calculating the percent of positive sentiment, and writing the result to a file. The pre-trained sentiment analysis model from the Flair package is being used. In a future version I will be training the model with labelled social media data.

The three main sources of data that are being utilized are from Reddit, Google News, and Twitter. I am accessing the Reddit and Twitter APIs using the packages praw and tweepy. This data consists of the most recent 100 post titles submitted to the bitcoin subreddit and the most recent 100 tweets that contain the word "bitcoin". The pygooglenews package is also being used for obtaining the most recent 100 news headlines on Google News that contain the word "bitcoin".

Due to API request limits, I am only scraping 100 posts/headlines/tweets from each source. The sentiment_model function combines this data into a 300 row dataframe and outputs a list with values of either "Positive" or "Negative". The percentage of positive sentiment (a value between 0 and 100) is the sentiment value.
