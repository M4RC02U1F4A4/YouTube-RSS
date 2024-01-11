from flask import Flask, render_template, redirect, request, jsonify
import os
import pymongo
import requests
from numerize import numerize
import feedparser
from datetime import datetime, timezone
import isodate
import logging
from flask_cors import CORS

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s', level=logging.DEBUG)

# MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
# MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
MONGODB_HOST = os.getenv('MONGODB_HOST')
MONGODB_PORT = os.getenv('MONGODB_PORT')
G_API_KEY = os.getenv('G_API_KEY')

# mongo_client = pymongo.MongoClient(f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}")
mongo_client = pymongo.MongoClient(f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}")
db = mongo_client.youtube
channelsDB = db['channels']
videosDB = db['videos']
randomDB = db['random']


app = Flask(__name__)
CORS(app)

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




@app.route('/unread/<id>')
def unread(id):
    videosDB.update_one({"_id":f"{id}"}, {"$set": {"viewed":0}})
    return redirect('/')



# ----------------------------------------
# Updated requests

@app.route('/get/videos', methods = ['GET'])
def get_videos():
    try:
        videos = videosDB.find({"hidden":0}).sort('published', -1)
        return jsonify({'staus': 'OK', 'message': 'Videos list returned.', 'data': list(videos)})
    except:
        return jsonify({'status': 'ERROR', 'message': 'Error getting videos.'})


@app.route('/watch/video/<id>')
def watch_video(id):
    try:
        videosDB.update_one({"_id":f"{id}"}, {"$set": {"viewed":1}})
        return jsonify({'staus': 'OK', 'message': 'Video marked as watched.'}), 200
    except:
        return jsonify({'status': 'ERROR', 'message': 'Error.'})
    

@app.route('/tbwatch/video/<id>')
def tbwatch_video(id):
    try:
        videosDB.update_one({"_id":f"{id}"}, {"$set": {"viewed":0}})
        return jsonify({'staus': 'OK', 'message': 'Video marked as to be watched.'}), 200
    except:
        return jsonify({'status': 'ERROR', 'message': 'Error.'})



@app.route('/get/channels', methods = ['GET'])
def get_channels():
    try:
        channels = channelsDB.find({}).sort('subscriberCount', -1)
        result_dict = {channel['_id']: channel for channel in channels}
        return jsonify({'staus': 'OK', 'message': 'Channels list returned.', 'data': result_dict})
    except:
        return jsonify({'status': 'ERROR', 'message': 'Error getting channels.'})


@app.route('/add/channel', methods = ['POST'])
def add_channel():
    if request.is_json:
        request_data = request.get_json()
        result = requests.get(f"https://www.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={request_data['channel_id']}&key={G_API_KEY}").json()
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
            return jsonify({'status': "OK", 'message': f"Channel with ID {request_data['channel_id']} added."}), 200
        except:
            return jsonify({'status': "ERROR", 'message': f"Failed to add channel with ID {request_data['channel_id']}."}), 500
    else:
        return jsonify({'status': 'ERROR', 'message': 'Channel not valid.'})


@app.route('/remove/channel', methods = ['DELETE'])
def remove():
    if request.is_json:
        request_data = request.get_json()
        channelsDB.delete_one({"_id": request_data['channel_id']})
        videosDB.delete_many({"channel": request_data['channel_id']})
        return jsonify({'status': 'OK', 'message': 'Channel removed.'})
    else:
        return jsonify({'status': 'ERROR', 'message': 'Channel not valid.'})


@app.route('/search/<query>', methods = ['GET'])
def search(query):
    logging.debug(f"Query: \"{query}\".")
    result = requests.get(f"https://www.googleapis.com/youtube/v3/search?part=id%2Csnippet&q={query}&type=channel&key={G_API_KEY}&maxResults=12").json()
    return jsonify({'status': "OK", 'message': f"Search result retuned.", 'data': result}), 200


@app.route('/update/channels', methods = ['GET'])
def update_channels():
    try:
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
        return jsonify({'status': 'OK', 'message': 'Successful update.'})
    except:
        return jsonify({'status': 'ERROR', 'message': 'Error during update.'})


@app.route('/update/videos', methods = ['GET'])
def update_videos():
    logging.debug("Updating video...")
    rss_link = "https://www.youtube.com/feeds/videos.xml?channel_id="
    for x in channelsDB.find():
        feed = feedparser.parse(f"{rss_link}{x['_id']}")
        
        for entry in feed.entries:
            logging.debug(entry.yt_videoid)
            try:
                if not videosDB.find_one({"_id":f"{entry.yt_videoid}"}) and (datetime.now(timezone.utc) - datetime.fromisoformat(entry.published).replace(tzinfo=timezone.utc)).days < 30:
                    logging.debug(entry.yt_videoid)
                    r = requests.get(f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id={entry.yt_videoid}&key={G_API_KEY}").json()
                                        
                    if "maxres" in r['items'][0]['snippet']['thumbnails']:
                        thumbnail = r['items'][0]['snippet']['thumbnails']['maxres']['url']
                    else:
                        thumbnail = r['items'][0]['snippet']['thumbnails']['standard']['url']
                    
                    dur = isodate.parse_duration(r['items'][0]['contentDetails']['duration'])
                    if dur.total_seconds() > 62:
                        viewed = 0
                        hidden = 0
                    else:
                        viewed = 0
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
                try:
                    randomDB.insert_one({"_id":"last_update", "time":f"{datetime.now().strftime('%d/%m/%y %H:%M')}"})
                except:
                    randomDB.update_one({"_id":"last_update"},{"$set":{"time":f"{datetime.now().strftime('%d/%m/%y %H:%M')}"}})
            except Exception as e:
                logging.debug(e)
    return jsonify({'status': 'OK', 'message': 'Successful update.'})


@app.route('/clean/videos', methods = ['GET'])
def clean_videos():
    try:
        videos = videosDB.find({"viewed":1})
        for video in videos:
            if (datetime.now(timezone.utc) - datetime.fromisoformat(video['published']).replace(tzinfo=timezone.utc)).days > 30:
                videosDB.delete_one({"_id":video['_id']})
        return jsonify({'status': 'OK', 'message': "Clean succesfull."})
    except:
        return jsonify({'status': 'OK', 'message': 'Error during video cleaning.'})

if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')