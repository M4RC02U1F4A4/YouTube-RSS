import pymongo
import os
import requests
import feedparser
import isodate
from datetime import datetime, timezone
import schedule
import time

MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
MONGODB_HOST = os.getenv('MONGODB_HOST')
MONGODB_PORT = os.getenv('MONGODB_PORT')
G_API_KEY = os.getenv('G_API_KEY')


mongo_client = pymongo.MongoClient(f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}")
db = mongo_client.youtube
channelsDB = db['channels']
videosDB = db['videos']


def update_video():
    rss_link = "https://www.youtube.com/feeds/videos.xml?channel_id="
    for x in channelsDB.find():
        feed = feedparser.parse(f"{rss_link}{x['_id']}")

        if not videosDB.find_one({"channel":x['_id']}):
            first_time = 1
        else:
            first_time = 0
        
        for entry in feed.entries:
            try:
                if not videosDB.find_one({"_id":f"{entry.yt_videoid}"}) and (datetime.now(timezone.utc) - datetime.fromisoformat(entry.published).replace(tzinfo=timezone.utc)).days < 30:
                    print(entry.yt_videoid)
                    r = requests.get(f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id={entry.yt_videoid}&key={G_API_KEY}").json()
                                        
                    if "maxres" in r['items'][0]['snippet']['thumbnails']:
                        thumbnail = r['items'][0]['snippet']['thumbnails']['maxres']['url']
                    else:
                        thumbnail = r['items'][0]['snippet']['thumbnails']['standard']['url']
                    
                    dur = isodate.parse_duration(r['items'][0]['contentDetails']['duration'])
                    if dur.total_seconds() > 62:
                        if first_time == 1:
                            viewed = 1
                        else:
                            viewed = 0
                        hidden = 0
                    else:
                        viewed = 1
                        hidden = 1

                    videosDB.insert_one({
                        "_id": entry.yt_videoid,
                        "thumbnail": thumbnail,
                        "published": entry.published,
                        "title": entry.title,
                        "viewed": viewed,
                        "channel": x['_id'],
                        "duration": dur.total_seconds(),
                        "hidden": hidden
                    })
            except Exception as e:
                print(e)


def delete_video():
    videos = videosDB.find({"viewed":1})
    for video in videos:
        if (datetime.now(timezone.utc) - datetime.fromisoformat(video['published']).replace(tzinfo=timezone.utc)).days > 30:
            videosDB.delete_one({"_id":video['_id']})


def update_channel():
    channels = channelsDB.find({})
    for c in channels:
        print(c)
        result = requests.get(f"https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={c['_id']}&key={G_API_KEY}").json()
        data = {
            "title":f"{result['items'][0]['snippet']['title']}",
            "description":f"{result['items'][0]['snippet']['description']}",
            "created":f"{result['items'][0]['snippet']['publishedAt']}",
            "logo":f"{result['items'][0]['snippet']['thumbnails']['high']['url']}",
            "viewCount":int(f"{result['items'][0]['statistics']['viewCount']}"),
            "videoCount":int(f"{result['items'][0]['statistics']['videoCount']}"),
            "subscriberCount":int(f"{result['items'][0]['statistics']['subscriberCount']}"),
        }
        channelsDB.update_one({"_id":f"{c['_id']}"}, {"$set": data})

print('RSS STARTED')

schedule.every().day.at("00:00").do(update_channel)
schedule.every().hour.do(update_video)
schedule.every().day.at("06:00").do(delete_video)

while True:
    schedule.run_pending()
    time.sleep(1)