import json
import tweepy
import re
from flask import Flask
from flask import render_template, request

app = Flask(__name__)
app.config.from_pyfile('settings.py')

# Function is called when the homepage of the website
# is accessed by user. It loads the html for the homepage.
@app.route("/")
def test():
    return render_template("index.html")

# Function is called when html sends the user to the 
# /handle_data page on the website after searching a term.
# This function sends the hashtag typed into the webpage
# to be used in the interaction with Twitters API.
@app.route('/handle_data', methods=['POST'])
def handle_data():
    projectpath = request.form['projectFilepath'] #stores the hashtag term in projectpath

    results = search_for_hashtags(projectpath)
    
    #gets a string and numeric value to show the results on the webpage
    percentGood = results[0]/(results[0]+results[1])*100
    feedbackString = ""
    if percentGood < 20.0:
        feedbackString = "Overwhelmingly Negative"
    elif percentGood < 40.0:
        feedbackString = "Negative"
    elif percentGood < 60.0:
        feedbackString = "Neutral"
    elif percentGood < 80.0:
        feedbackString = "Positive"
    else:
        feedbackString = "Overwhelmingly Positive"

    #returns all the variables needed to populate the webpage to the html template
    return render_template("results.html", goodcount=results[0], badcount=results[1], neutralcount=results[2], hashtagTerm=projectpath, resultString=feedbackString, percGood=round(percentGood,2))


# Uses the hashtag_phrase to search for tweets and insert them into a list.
def search_for_hashtags(hashtag_phrase):
    
    #create authentication for accessing Twitter
    auth = tweepy.OAuthHandler("hUaPAmZv01BIgcgluEbjpfwYu", "mZIzW6p8Oyjd6tVA9P5uOkalshEPeVCr8V5atrbHZ1Y9p2eEmJ")
    auth.set_access_token("1208515781815877633-JkecI77hGZ1QdAsGw4RZqPfItCCTKG", "XfSuHsgDrif8uIVKjgQZ9ERbf5kLpgJ3pC5DDAryDxVKJ")

    #initialize Tweepy API
    api = tweepy.API(auth)

    #declare list to store tweets from Tweepy
    tweets = []

    #Loop searches last 100 tweets with the hashtag_phrase and stores them in list
    for tweet in tweepy.Cursor(api.search, q=hashtag_phrase+' -filter:retweets', \
                                lang="en", tweet_mode='extended').items(100):
        individualtweet = str([tweet.full_text.replace('\n',' ').encode('utf-8')])
        tweets.append(individualtweet)

    return reviewTweets(tweets)

# Takes a list of tweets and returns a list with index 0 being
# the number of neutral tweets, index 1 being the number of good tweets
# and index 2 being the number of bad tweets.
def reviewTweets(tweetList):
    goodTweets = 0
    badTweets = 0
    neutralTweets = 0
    for tweet in tweetList:
        tweetType = isGoodTweet(stringCleaner(tweet)) #cleans the string before determining its tweet type
        if tweetType == 0:
            neutralTweets = neutralTweets+1
        elif tweetType == 1:
            goodTweets = goodTweets+1
        else:
            badTweets = badTweets+1
    goodVBad = []
    goodVBad.append(goodTweets)
    goodVBad.append(badTweets)
    goodVBad.append(neutralTweets)
    return goodVBad

# Compares the words present in the tweet against a text file of 
# good and bad words in order to give it a tweet type(0=neutral,1=good,2=bad)
def isGoodTweet(wordArr):
    badWords = open('badWords.txt', 'r')
    badCount = 0
    badText = badWords.read().strip().split()
    goodWords = open('goodWords.txt', 'r')
    goodCount = 0
    goodText = goodWords.read().strip().split()
    for word in wordArr:
        if word in badText:
            badCount = badCount + 1
        if word in goodText:
            goodCount = goodCount + 1
    badWords.close()
    goodWords.close()
    if goodCount == badCount:
        return 0
    elif goodCount > badCount:
        return 1
    else:
        return 2

# Takes a string, sets it to lowercase, removes symbols, and returns
# a string array containing the individual words of the tweet separated
# by spaces.
def stringCleaner(tweet):
    tweet = tweet.lower()
    symbols = ['.','/',',','?','"','!','@','#','$','%','^','&','*','(',')','-','_','=','+','`','~','<','>',';',':','[',']',"'"]

    for char in symbols:
        tweet = tweet.replace(char,'')

    wordArr = tweet.split(' ')
    return wordArr