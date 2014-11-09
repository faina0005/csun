# -*- coding: utf-8 -*-


import os
import sys
import time
import json
import twitter
import re
import pymongo
import exceptions

from twitter.api import Twitter, TwitterError
from twitter.oauth import OAuth, write_token_file , read_token_file
from twitter.oauth_dance import oauth_dance
from urllib2 import URLError
from httplib import BadStatusLine

#import any other natual processing libs


# go to http://twitter.com/apps/new to create an app and get values
# for these credentials that you'll need to provide in place of these
# empty string values that are defined as placeholders.
    
def oauth_login():
    CONSUMER_KEY = '0lJsvdGOaFrnLeRfNMtbiqI8o'
    CONSUMER_SECRET ='3UJwpgbNRpYFzvpj9GVyMWJIYdQzxzqfyslsuwre0naCHVS7AW'
    OAUTH_TOKEN = '2880116101-qyhIBwI5ogbRcD3wUdYf2wWSBL97jqKgWo8zFBD'
    OAUTH_TOKEN_SECRET = 'dzf41CNJh9lLtDjvGsXaWfN1rBjPgJcwa1vpXUqkA3PN7'
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
    
    twitter_api = Twitter(auth=auth)
    return twitter_api

# nested helper function that handles common HTTPErrors. Return an updated
# value for wait_period if the problem is a 500 level error. Block until the
# rate limit is reset if it's a rate limiting issue (429 error). Returns None
# for 401 and 404 errors, which requires special handling by the caller.
    
    
def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw): 
    
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e
    
        # See https://dev.twitter.com/docs/error-codes-responses for common codes
        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429: 
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e
    # End of nested helper function
    
    wait_period = 2 
    error_count = 0 

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0 
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
                

# all of your project code can be wrapped inside of this function
# right now response just parrots the message back at the sender


def response(message):
    return message


def get_id_str_list(name_list, collection, limit=10):
    to_respond=[searchMongo(name, collection, limit) for name in name_list]
    print to_respond
    id_str_list=[tweet['id_str'] for name in to_respond for tweet in name]
    return id_str_list

# Connection to Mongo DB
def connectMongo():
    try:
        conn=pymongo.MongoClient()
        print "Connected successfully!!!"
    except pymongo.errors.ConnectionFailure, e:
       print "Could not connect to MongoDB: %s" % e 
    return conn




def searchMongo(name,collection, limit=10):
    name=name.split(' ')
    if(len(name)>1):
        first=name[0]
        last=name[1]
    else:
        first=name[0]
        last=''
    line1=r'love.*'+first+' ?'+last
    line2=first+' ?'+last+r'.*love'
    re_exp=re.compile(r'('+line1+r')|('+line2+r')', re.IGNORECASE)
    
    query={'$and':
              [ {'text':re_exp},
                {'text':{'$not':re.compile(r'^.?@'+first+last, re.IGNORECASE)}}]
        }
    
    return list(collection.find(query).limit(limit))

#bot=oauth_login()
def deletePosts(bot): #mass delete the posts
    
    statuses=bot.statuses.user_timeline()
    print len(statuses)
    for status in statuses:
        try:
            print 'deleting ', status['id']
            bot.statuses.destroy(id=status['id'])
        except exceptions.BaseException, e: #in case of some error/exception - just skipping that post
                        print e






name_list=['katy perry',
'britney spears',
'taylor swift',
'kim kardashian',
'justin bieber',
'justin timberlake',
 'chris brown',
 'nicki minaj',
 'lady gaga',
 'miley cyrus',
 'selena gomez',
 'rihanna',
 'beyonce knowles',
 'ashton kutcher',
 'ellen gegeneres',
 'cristian oronaldo',
 'oprah winfrey',
 'jennifer lopez',
 'shakira']



if __name__ == "__main__":
    
    conn=connectMongo()
    db=conn.twitter
    collection=db.lines

    last_id=None

    bot = oauth_login()
    bot_name = '@'+bot.account.verify_credentials()['screen_name'] #put your actual bot's name here
    print bot_name
    bot_id=2880116101 #gina's bot
    bot_id_GRC= 2878685726 #GetRealCeleb bot
    #bot_id=bot.account.verify_credentials()['id']
    print bot_id
    
    #main loop. Just keep searching anyone talking to us
    while True:
        try:
            id_list_str=get_id_str_list(name_list[:12], collection, limit=3)
            print id_list_str
            for id_str in id_list_str:
                try:
                    status = make_twitter_request(bot.statuses.user_timeline)
                    if len(status) > 0:
                        last_id = status[0]['id']
                        print 'last_id', last_id    
                    
                    
                    # reply to one of the users pulled out from DB
                   #======================================================== 
                    mention=make_twitter_request(bot.statuses.show,_id=int(id_str))
                    message = mention['text']
                    speaker = mention['user']['screen_name']
                    _id=mention['id']
                    print "[+] " + speaker + " is saying " + message
                    reply = '@GetRealCeleb get on earth(c) ' +speaker
                    #reply = 'get on earth(c) ' +speaker+' forget '+ message
                    if len(reply)>140: #in case message is more than 140 characters
                        reply=reply[:140]
                    print "[+] Replying " , reply 
                    _id=531012911473258497 #would need to comment out once we have a real message
                    make_twitter_request(bot.statuses.update, status=reply,in_reply_to_status_id=_id)
                   
               #===================================                 
                
                
                #then respond to all the mentions (based on the last reply)
                #===========================================
                    if last_id!=None:
                        mentions = make_twitter_request(bot.statuses.mentions_timeline, since_id=last_id)
                    else:
                        mentions = make_twitter_request(bot.statuses.mentions_timeline)

                    if not mentions:
                        print "No one talking to us now...", time.ctime()
                
                    mentions=[mentions[(len(mentions)-i-1)] for i in xrange(len(mentions))] #reverse the list
            
                    for mention in mentions: 
                        if mention['id'] > last_id and mention['user']['id']!=bot_id: #does not respond to itself
                            print 'current mention_id ',mention['id']
                            message = mention['text'].replace(bot_name, '')
                            speaker = mention['user']['screen_name']
                            _id = mention['id']
                            speaker_id = str(mention['id'])

                            print "[+] " + speaker + " is saying " + message
                            reply = '@%s %s' % (speaker, response(message)) 
                            print "[+] Replying " , reply
                            make_twitter_request(bot.statuses.update, status=reply,in_reply_to_status_id=_id)
                           
                except exceptions.BaseException, e: #in case of some error/exception - just skipping that post
                        print e
                    
                    
                sleep_int = 60 #downtime interval in seconds
                print "Sleeping...\n"
                time.sleep(sleep_int)
        

            
        except KeyboardInterrupt:
                print"[!] Cleaning up. last_id was ", last_id
                sys.exit()
            



