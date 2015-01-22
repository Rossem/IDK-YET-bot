from image import *

import praw
import bot
import sqlite3

import urllib
import requests
import shutil 

import imgurpython
from imgurpython import ImgurClient
import imgurcredentials

import subprocess
from subprocess import call

import time


USERNAME = bot.username
PASSWORD = bot.password
USERAGENT = "/u/" + bot.username + " QUAD Tree image bot"
SUBREDDIT = "pics"
MAXPOSTS = 25

WAIT = 300

HOT_SUBM = True

#-------------------------------------------------------
#Database

print "Opening database"
sql = sqlite3.connect("sql.db")
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
sql.commit()

#-------------------------------------------------------
#Reddit login things

print "Logging in to reddit"
r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD)

#-------------------------------------------------------
#Imgur things

print "Authenticating imgur"
CLIENT_ID = imgurcredentials._id
CLIENT_SECRET = imgurcredentials.secret
client = ImgurClient(CLIENT_ID, CLIENT_SECRET)

#-------------------------------------------------------

def main():

    #filename = raw_input("enter file: ")
    print "Fetching subreddit"
    subreddit = r.get_subreddit(SUBREDDIT)
    print "Fetching 25 hot/new submissions"

    if HOT_SUBM:
        submissions = subreddit.get_hot(limit=MAXPOSTS)
    else:
        submissions = subreddit.get_new(limit=MAXPOSTS)

    for submission in submissions:

        sid = submission.id
        cur.execute('SELECT * FROM oldposts WHERE ID=?', [sid])

        if not cur.fetchone():
            print "Fetching url"
            img_url = submission.url

            if "imgur" in img_url:

                k = img_url.rfind("/")
                img_name = img_url[k+1:]
                #data = urllib.urlretrieve(img_url, img_name)

                response = requests.get(img_url, stream=True)
                with open(img_name, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response

                img = ImageModel(img_name)
                previous = None

                for i in range(ITERATIONS):
                    error = img.average_error()

                    if previous is None or previous - error > ERROR_RATE:
                        print i, error
                        
                        if SAVE_FRAMES:
                            img.render('frames/%06d.png' % i)

                        previouse = error 
                    
                    img.split()
                
                img.render('QUAD' + img_name)

                new_img_url = client.upload_from_path('QUAD' + img_name)

                nl = "\n\n"
                comment = "[Converted to Quad Tree](" + new_img_url['link'] + ")" + nl*3 + "---" + nl*2 + "Info: this message was submitted by a bot" #+ nl*2 + "Feedback/comments/problems greatly appreciated: AskeeBot@gmail.com"

                #if i cant comment due to overlimiting requests
                cant_comment = True

                while cant_comment:
                    try:
                        submission.add_comment(comment)
                        cant_comment = False

                    except praw.errors.RateLimitExceeded as error:
                        print "\tSleeping for %d seconds" % error.sleep_time
                        time.sleep(error.sleep_time)

                print "Done submission: " + submission.title

            else:
                print "Not an imgur image"

            cur.execute('INSERT INTO oldposts VALUES(?)', [sid])
            sql.commit()
                    
                    


"""

    model = ImageModel(filename)
    previous = None
    
    for i in range(ITERATIONS):
        error = model.average_error()
        if previous is None or previous - error > ERROR_RATE:
            print i, error
            if SAVE_FRAMES:
                model.render('frames/%06d.png' % i)
            previous = error
        model.split()
    model.render('QUAD' + filename)

run()
"""        

while True:
    main()
    print "Waiting " + str(WAIT) + " seconds"
    #time.sleep(WAIT)

