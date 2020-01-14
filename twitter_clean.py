#!/usr/bin/env python

"""
https://www.karambelkar.info/2015/01/how-to-use-twitters-search-rest-api-most-effectively./
"""

import sys
import time
import tweepy
from datetime import datetime, timedelta
from auth import consumer_key, consumer_secret, \
        access_token_key, access_token_secret, screen_name


sleeptime = 0.1
exception_sleeptime = 60

do_delete = True
verbose = True

match_by_date = True
days_to_keep = 30
cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

keep_last_n_tweets = 7
delete_matching = 'me // automatically checked by'
keep_matching = '#keep'
keybase_matching = 'GF-1BjCID_I45YXm_UIqknVq0gjbAvKhGLOC'


def vprint(msg):
    if verbose:
        print(msg)


def make_twapi():
    appauth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    appauth.set_access_token(access_token_key, access_token_secret)
    return tweepy.API(appauth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def get_tweet_list(pages):
    pnum = 0
    tweet_list = []
    while True:
        try:
            page = next(pages)
            time.sleep(sleeptime)
        except tweepy.TweepError:  # rate limit exceeded (180 queries per 15m)
            vprint('Sleeping...')
            time.sleep(exception_sleeptime)
            page = next(pages)
        except StopIteration: # no more pages
            vprint('Done')
            break
        pnum += 1
        vprint('### Page number: %d ####' % pnum)
        for entry in page:
            tweet_list.append(entry)
    return tweet_list


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


def last_tweets_manage(api, tweet_list, do_delete):
    print('tweet_list: ' + str(len(tweet_list)))
    print('cutoff_date: ', cutoff_date)
    tweet_list_subset = []
    if delete_matching:
        tweet_list_subset += [tweet for tweet in tweet_list if delete_matching in tweet.text]
    if match_by_date:
        tweet_list_subset += [tweet for tweet in tweet_list if tweet.created_at < cutoff_date]
    print('tweet_list_subset: ', len(tweet_list_subset))
    if len(tweet_list) <= keep_last_n_tweets:
        print('Too few tweets to delete')
        return
    for item in tweet_list_subset:
        if item.favorite_count >= 1000:
            print_tweet(item, 'KEEP favourite')
        elif keep_matching in item.text:
            print_tweet(item, 'KEEP match')
        elif keybase_matching in item.text:
            print_tweet(item, 'KEEP keybase')
        else:
            print_tweet(item, 'DELETE')
            if do_delete:
                api.destroy_status(item.id)


def lambda_handler(event, context):
    api = make_twapi()
    pages = tweepy.Cursor(api.user_timeline, screen_name=screen_name).pages()
    tweet_list = get_tweet_list(pages)
    last_tweets_manage(api, tweet_list, do_delete)
