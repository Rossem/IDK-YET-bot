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
#SUBREDDIT = "pics" welp i got banned from /r/pics o well
SUBREDDIT = "images"
MAXPOSTS = 150 

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
        print "Fetching submission"

        sid = submission.id
        cur.execute('SELECT * FROM oldposts WHERE ID=?', [sid])

        "checking if already commented"

        if not cur.fetchone():
            print "Fetching url"
            img_url = submission.url

            if "imgur" in img_url and (".jpg" in img_url or ".jpeg" in img_url or ".png" in img_url):


                k = img_url.rfind("/")
                img_name = img_url[k+1:]

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
                comment = "[Converted to Quad Tree](" + new_img_url['link'] + ")" + nl*3 + "---" + nl*2 + "Info: this message was submitted by a bot" 
                #if i cant comment due to overlimiting requests
                cant_comment = True

                while cant_comment:
                    try:
                        submission.add_comment(comment)
                        cant_comment = False

                    except praw.errors.RateLimitExceeded as error:
                        t = round(error.sleep_time) + 1
                        _t = int(t)
                        countdown(_t)

                print "Done submission: " + submission.title

            else:
                print "Not an imgur image/gallery"

            cur.execute('INSERT INTO oldposts VALUES(?)', [sid])
            sql.commit()
            cleanup()
                    
                    
def cleanup():
    subprocess.call(["rm", "*.png"])
    subprocess.call(["rm", "*.jpg"])
    subprocess.call(["rm", "*.jpeg"])

def countdown(t):
    for i in range(t, 0, -1):
        time.sleep(1)
        sys.stdout.write(str(i) + ' ')
        sys.stdout.flush()

while True:
    main()
    #print "Waiting " + str(WAIT) + " seconds"
    #time.sleep(WAIT)

