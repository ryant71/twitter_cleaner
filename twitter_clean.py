#!/usr/bin/env python3

import sys
import time
import tweepy
import boto3
from datetime import datetime, timedelta

SLEEPTIME = 0.2
EXCEPTION_SLEEPTIME = 60

DO_DELETE = True
VERBOSE = True

MATCH_BY_DATE = True
DAYS_TO_KEEP = 7
KEEP_LAST_N_TWEETS = 7
DELETE_MATCHING = 'me // automatically checked by'
KEEP_MATCHING = ['#keep', '#thread', '#Thread']

cutoff_date = datetime.utcnow() - timedelta(days=DAYS_TO_KEEP)

ssm = boto3.client('ssm')
keybase_matching = ssm.get_parameter(Name='/lambda/twitter_cleaner/keybase_id', WithDecryption=True)['Parameter']['Value']
bearer_token = ssm.get_parameter(Name='/lambda/twitter_cleaner/shi/bearer_token', WithDecryption=True)['Parameter']['Value']
consumer_key = ssm.get_parameter(Name='/lambda/twitter_cleaner/shi/consumer_key', WithDecryption=True)['Parameter']['Value']
consumer_secret = ssm.get_parameter(Name='/lambda/twitter_cleaner/shi/consumer_secret', WithDecryption=True)['Parameter']['Value']
access_token = ssm.get_parameter(Name='/lambda/twitter_cleaner/shi/access_token', WithDecryption=True)['Parameter']['Value']
access_token_secret = ssm.get_parameter(Name='/lambda/twitter_cleaner/shi/access_token_secret', WithDecryption=True)['Parameter']['Value']

client = tweepy.Client(bearer_token=bearer_token,
                       consumer_key=consumer_key,
                       consumer_secret=consumer_secret,
                       access_token=access_token,
                       access_token_secret=access_token_secret)


def print_tweet(entry, msg=""):
    try:
        media_url = entry.entities['media'][0]['media_url']
    except KeyError:
        media_url = ''
    output = '[%d][%s](%s)fc=%-3d,rc=%-4d %s %s' % (
        entry.id,
        entry.created_at,
        msg,
        entry.favorite_count,
        entry.retweet_count,
        entry.text,
        media_url)
    print(output)


def text_in_tweet(item_list, tweet_text):
    for item in item_list:
        if item in tweet_text:
            return True
    return False


def get_tweet_timeline(id, from_date, to_date):
    timeline = tweepy.Paginator(client.get_users_tweets, id=me.data.id,
                                max_results=10, limit=1).flatten()
    response = client.get_tweet(id)

def timeline_verbosifier(func):
    def wrapper():
        if VERBOSE:
        i = 1
        for tweet in timeline:
            print(f'{i}: {tweet.text}\n---')
            i+=1
            tweet_details = get_tweet(tweet.id)


def lambda_handler(event, context):
    me = client.get_me()
    tweets = get_tweet_timeline(id)
    #favourites_pages = tweepy.Paginator(client.get_liked_tweets)

if __name__=="__main__":
    lambda_handler(False, False)
