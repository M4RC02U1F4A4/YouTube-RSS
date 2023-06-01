from flask import Flask, render_template, redirect, request
import os
import pymongo
import requests
import re
from numerize import numerize
import datetime

MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
MONGODB_HOST = os.getenv('MONGODB_HOST')
MONGODB_PORT = os.getenv('MONGODB_PORT')
G_API_KEY = os.getenv('G_API_KEY')

mongo_client = pymongo.MongoClient(f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}")
db = mongo_client.youtube
channelsDB = db['channels']
videosDB = db['videos']
randomDB = db['random']


app = Flask(__name__)

@app.template_filter('get_logo')
def get_logo(id):
    channel = channelsDB.find_one({"_id":id})
    return channel['logo']

@app.template_filter('get_title')
def get_title(id):
    channel = channelsDB.find_one({"_id":id})
    return channel['title']

@app.template_filter('get_subscriberCount')
def get_subscriberCount(id):
    channel = channelsDB.find_one({"_id":id})
    return numerize.numerize(int(channel['subscriberCount']))

@app.template_filter('convert_time')
def convert_time(time):
    return str(datetime.timedelta(seconds=time))

@app.template_filter('beautify_time')
def beautify_time(time):
    time = time.split(":")
    return f"{time[0]}h {time[1]}min {time[2]}sec"

def calc_len():
    videos_len = videosDB.count_documents({"viewed":0})
    all_videos_len = videosDB.count_documents({"hidden":0})
    channels_len = channelsDB.count_documents({})
    return videos_len, all_videos_len, channels_len

def last_update():
    try:
        return randomDB.find_one({"_id":"last_update"})['time']
    except:
        return 'NA'
    
def time_to_watch():
    total_time = 0
    videos = videosDB.find({"viewed":0})
    for v in videos:
        total_time += v['duration']
    return total_time

@app.route('/')
def home():
    videos = videosDB.find({"viewed":0}).sort('published', -1)
    videos_len, all_videos_len, channels_len = calc_len()
    
    return render_template('home.html',
                           videos=videos,
                           videos_len=videos_len,
                           all_videos_len=all_videos_len,
                           channels_len=channels_len,
                           active='home',
                           last_update=last_update(),
                           time = time_to_watch())

@app.route('/channels')
def channels():
    channels = channelsDB.find({}).sort('subscriberCount', -1)
    videos_len, all_videos_len, channels_len = calc_len()
    return render_template('channels.html',
                           channels=channels,
                           videos_len=videos_len,
                           all_videos_len=all_videos_len,
                           channels_len=channels_len,
                           active='channels',
                           last_update=last_update(),
                           time = time_to_watch())

@app.route('/videos')
def videos():
    all_videos = videosDB.find({"hidden":0}).sort('published', -1)
    videos_len, all_videos_len, channels_len = calc_len()
    return render_template('videos.html',
                           videos=all_videos,
                           videos_len=videos_len,
                           all_videos_len=all_videos_len,
                           channels_len=channels_len,
                           active='videos',
                           last_update=last_update(),
                           time = time_to_watch())

@app.route('/manage')
def manage():
    videos_len = videosDB.count_documents({"viewed":0})
    videos_len, all_videos_len, channels_len = calc_len()
    return render_template('manage.html',
                           videos_len=videos_len,
                           all_videos_len=all_videos_len,
                           channels_len=channels_len,
                           active='manage',
                           last_update=last_update(),
                           time = time_to_watch())

@app.route('/read/<id>')
def read(id):
    videosDB.update_one({"_id":f"{id}"}, {"$set": {"viewed":1}})
    return "OK", 200

@app.route('/unread/<id>')
def unread(id):
    videosDB.update_one({"_id":f"{id}"}, {"$set": {"viewed":0}})
    return redirect('/')


@app.route('/add', methods = ['POST'])
def add():
    search = request.form['search']
    result = requests.get(f"https://www.googleapis.com/youtube/v3/search?part=id%2Csnippet&q={search}&type=channel&key={G_API_KEY}&maxResults=12").json()
    
    videos_len = videosDB.count_documents({"viewed":0})
    videos_len, all_videos_len, channels_len = calc_len()
    return render_template('manage.html',
                           result=result,
                           videos_len=videos_len,
                           all_videos_len=all_videos_len,
                           channels_len=channels_len,
                           active='manage',
                           last_update=last_update(),
                           time = time_to_watch())

@app.route('/add/<id>', methods = ['GET'])
def add_id(id):
    result = requests.get(f"https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={id}&key={G_API_KEY}").json()
    data = {
        "_id":f"{result['items'][0]['id']}",
        "title":f"{result['items'][0]['snippet']['title']}",
        "description":f"{result['items'][0]['snippet']['description']}",
        "created":f"{result['items'][0]['snippet']['publishedAt']}",
        "logo":f"{result['items'][0]['snippet']['thumbnails']['high']['url']}",
        "viewCount":int(f"{result['items'][0]['statistics']['viewCount']}"),
        "videoCount":int(f"{result['items'][0]['statistics']['videoCount']}"),
        "subscriberCount":int(f"{result['items'][0]['statistics']['subscriberCount']}")
    }
    try:
        channelsDB.insert_one(data)
    except:
        pass

    return redirect("/")

@app.route('/remove', methods = ['POST'])
def remove():
    id = request.form['id']

    channelsDB.delete_one({"_id":id})
    videosDB.delete_many({"channel":id})
    return redirect('/manage')


# app.run(debug=True, port=5001, host='0.0.0.0')