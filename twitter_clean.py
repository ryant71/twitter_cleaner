#!/usr/bin/env python3

"""
https://www.karambelkar.info/2015/01/how-to-use-twitters-search-rest-api-most-effectively./
"""

import sys
import time
import tweepy
import boto3
from datetime import datetime, timedelta

sleeptime = 0.2
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

ssm = boto3.client('ssm')
consumer_key = ssm.get_parameter(Name='/lambda/twitter_cleaner/consumer_key', WithDecryption=True)
consumer_secret = ssm.get_parameter(Name='/lambda/twitter_cleaner/consumer_secret', WithDecryption=True)
access_token_key = ssm.get_parameter(Name='/lambda/twitter_cleaner/access_token_key', WithDecryption=True)
access_token_secret = ssm.get_parameter(Name='/lambda/twitter_cleaner/access_token_secret', WithDecryption=True)


def vprint(msg):
    if verbose:
        print(msg)


def make_twapi():
    appauth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    appauth.set_access_token(access_token_key, access_token_secret)
    return tweepy.API(appauth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def get_timeline_list(timeline_pages):
    pnum = 0
    timeline_list = []
    while True:
        try:
            page = next(timeline_pages)
            time.sleep(sleeptime)
        except tweepy.TweepError:  # rate limit exceeded (180 queries per 15m)
            vprint('Sleeping...')
            time.sleep(exception_sleeptime)
            page = next(timeline_pages)
        except StopIteration: # no more timeline_pages
            vprint('Done')
            break
        pnum += 1
        vprint('### timeline page number: %d ####' % pnum)
        for entry in page:
            timeline_list.append(entry)
    return timeline_list


def get_favorites_list(favourites_pages):
    fnum = 0
    favorites_list = []
    while True:
        try:
            page = next(favourites_pages)
            time.sleep(sleeptime)
        except tweepy.TweepError:
            vprint('Sleeping')
            time.sleep(exception_sleeptime)
            page = next(favourites_pages)
        except StopIteration:
            vprint('Done favorites')
            break
        fnum += 1
        vprint('### favorites page number: %d ####' % fnum)
        for entry in page:
            favorites_list.append(entry)
    return favorites_list


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


def delete_tweet_items(api, timeline_list, favorites_list, do_delete):
    print('timeline_list: ' + str(len(timeline_list)))
    print('cutoff_date: ', cutoff_date)
    timeline_list_subset = []
    favorites_list_subset = []
    if delete_matching:
        timeline_list_subset += [tweet for tweet in timeline_list if delete_matching in tweet.text]
    if match_by_date:
        timeline_list_subset += [tweet for tweet in timeline_list if tweet.created_at < cutoff_date]
        favorites_list_subset += [fav for fav in favorites_list if fav.created_at < cutoff_date]
    print('timeline_list_subset: ', len(timeline_list_subset))
    print('favorites_list_subset', len(favorites_list_subset))
    if len(timeline_list) <= keep_last_n_tweets:
        print('Too few tweets to delete')
        return
    for item in timeline_list_subset:
        if item.favorite_count >= 1000:
            print_tweet(item, 'KEEP favorited')
        elif keep_matching in item.text:
            print_tweet(item, 'KEEP matched')
        elif keybase_matching in item.text:
            print_tweet(item, 'KEEP keybase')
        else:
            print_tweet(item, 'DELETE TWEET')
            if do_delete:
                api.destroy_status(item.id)
    print('Finished timeline, Starting favorites')
    for item in favorites_list_subset:
        print_tweet(item, 'DELETE FAVORITE')
        if do_delete:
            api.destroy_favorite(item.id)


def lambda_handler(event, context):
    api = make_twapi()
    timeline_pages = tweepy.Cursor(api.user_timeline).pages()
    favourites_pages = tweepy.Cursor(api.favorites).pages()
    timeline_list = get_timeline_list(timeline_pages)
    favorites_list = get_favorites_list(favourites_pages)
    delete_tweet_items(api, timeline_list, favorites_list, do_delete)


if __name__=="__main__":

    lambda_handler(False, False)
