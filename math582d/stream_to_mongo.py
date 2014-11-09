#!/usr/bin/python

import json
import pymongo
import tweepy

consumer_key = ''
consumer_secret = ''
access_key = ''
access_secret = ''
    
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)


class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()

        self.db = pymongo.MongoClient().twitter

    def on_data(self, tweet):
    	decoded = json.loads(tweet)
    	try:
    		self.db.lines.insert({'text': decoded['text'].encode('ascii', 'ignore'), 'id_str': decoded['id_str']})
        except KeyError: pass
        

    def on_error(self, status_code):
        return True # Don't kill the stream

    def on_timeout(self):
        return True # Don't kill the stream


if __name__ == '__main__':
	sapi = tweepy.streaming.Stream(auth, CustomStreamListener(api))
	sapi.filter(track=['a','e','i','o','u'],languages=['en']) 
	#sapi.sample(languages=['en'])  
