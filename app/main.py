from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
import os
import pymongo
import requests
import feedparser
from datetime import datetime, timedelta, timezone
import isodate
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s', level=logging.INFO)

MONGODB_HOST = os.getenv('MONGODB_HOST')
MONGODB_PORT = os.getenv('MONGODB_PORT')
MONGODB_DB = os.getenv('MONGODB_DB', 'youtube')
G_API_KEY = os.getenv('G_API_KEY')

YT_API = "https://www.googleapis.com/youtube/v3"
RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id="
KEEP_DAYS = 30

mongo_client = pymongo.MongoClient(f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}")
db = mongo_client[MONGODB_DB]
channelsDB = db['channels']
videosDB = db['videos']
randomDB = db['random']


# static_url_path='' serves the single-page UI and its assets from the site root.
app = Flask(__name__, static_folder='static', static_url_path='')


def ok(message, data=None):
    return jsonify({'status': 'OK', 'message': message, 'data': data})


def error(message, code):
    return jsonify({'status': 'ERROR', 'message': message}), code


@app.errorhandler(Exception)
def handle_error(e):
    if isinstance(e, HTTPException):
        return error(e.description, e.code)
    if isinstance(e, requests.HTTPError):
        logging.warning(f"{e}: {e.response.text}")
        return error(f"YouTube refused the request ({e.response.status_code}), check the API key and the daily quota.", 502)
    logging.exception(e)
    return error('Unexpected server error, check the logs.', 500)


def now():
    return datetime.now(timezone.utc)


def youtube(endpoint, **params):
    r = requests.get(f"{YT_API}/{endpoint}", params={**params, 'key': G_API_KEY}, timeout=10)
    r.raise_for_status()
    return r.json().get('items', [])


def batches(items, size=50):
    # The YouTube API accepts at most 50 ids per call.
    for i in range(0, len(items), size):
        yield items[i:i + size]


def channel_data(item):
    snippet, stats = item['snippet'], item['statistics']
    return {
        "title": snippet['title'],
        "description": snippet['description'],
        "created": snippet['publishedAt'],
        "logo": snippet['thumbnails']['medium']['url'],
        "viewCount": int(stats.get('viewCount', 0)),
        "videoCount": int(stats.get('videoCount', 0)),
        # Missing when the channel hides its subscriber count.
        "subscriberCount": int(stats.get('subscriberCount', 0)),
    }


def is_short(video_id: str) -> bool:
    try:
        r = requests.get(f"https://www.youtube.com/shorts/{video_id}", allow_redirects=True, timeout=5)
        return "shorts" in r.url
    except Exception:
        return False


def set_last_update(key):
    randomDB.update_one({"_id": key}, {"$set": {"time": now().strftime('%d/%m/%Y %H:%M')}}, upsert=True)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/get/videos')
def get_videos():
    return ok('Videos list returned.', list(videosDB.find({"hidden": 0}).sort('published', -1)))


@app.route('/watch/video/<id>')
def watch_video(id):
    videosDB.update_one({"_id": id}, {"$set": {"viewed": 1, "watched_at": now().isoformat()}})
    return ok('Video marked as watched.')


@app.route('/tbwatch/video/<id>')
def tbwatch_video(id):
    videosDB.update_one({"_id": id}, {"$set": {"viewed": 0}, "$unset": {"watched_at": ""}})
    return ok('Video marked as to be watched.')


@app.route('/get/channels')
def get_channels():
    return ok('Channels list returned.', {c['_id']: c for c in channelsDB.find({})})


@app.route('/add/channel', methods=['POST'])
def add_channel():
    channel_id = (request.get_json(silent=True) or {}).get('channel_id')
    if not channel_id:
        return error('Missing channel_id.', 400)
    items = youtube('channels', part='snippet,statistics', id=channel_id)
    if not items:
        return error(f"Channel {channel_id} not found on YouTube.", 404)
    try:
        channelsDB.insert_one({"_id": items[0]['id'], **channel_data(items[0])})
    except pymongo.errors.DuplicateKeyError:
        return error(f"Channel {channel_id} is already added.", 409)
    return ok(f"Channel {channel_id} added.")


@app.route('/remove/channel', methods=['DELETE'])
def remove_channel():
    channel_id = (request.get_json(silent=True) or {}).get('channel_id')
    if not channel_id:
        return error('Missing channel_id.', 400)
    channelsDB.delete_one({"_id": channel_id})
    videosDB.delete_many({"channel": channel_id})
    return ok('Channel removed.')


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return error('Missing search query.', 400)
    return ok('Search results returned.', youtube('search', part='snippet', q=query, type='channel', maxResults=6))


@app.route('/update/channels')
def update_channels():
    ids = [c['_id'] for c in channelsDB.find({}, {"_id": 1})]
    for batch in batches(ids):
        for item in youtube('channels', part='snippet,statistics', id=','.join(batch), maxResults=50):
            channelsDB.update_one({"_id": item['id']}, {"$set": channel_data(item)})
    set_last_update('last_channels_update')
    return ok('Channels updated.')


@app.route('/update/videos')
def update_videos():
    cutoff = now() - timedelta(days=KEEP_DAYS)
    new = {}
    for channel_id in [c['_id'] for c in channelsDB.find({}, {"_id": 1})]:
        try:
            r = requests.get(f"{RSS_URL}{channel_id}", timeout=10)
            r.raise_for_status()
            feed = feedparser.parse(r.content)
        except Exception as e:
            logging.warning(f"Feed of channel {channel_id} skipped: {e}")
            continue
        for entry in feed.entries:
            if datetime.fromisoformat(entry.published).astimezone(timezone.utc) >= cutoff:
                new[entry.yt_videoid] = {"published": entry.published, "title": entry.title, "channel": channel_id}

    known = {v['_id'] for v in videosDB.find({"_id": {"$in": list(new)}}, {"_id": 1})}
    for batch in batches([i for i in new if i not in known]):
        for item in youtube('videos', part='contentDetails', id=','.join(batch), maxResults=50):
            duration = isodate.parse_duration(item['contentDetails']['duration']).total_seconds()
            # Shorts last at most 3 minutes, so only those need the (slow) redirect check.
            hidden = 1 if duration <= 62 or (duration <= 180 and is_short(item['id'])) else 0
            videosDB.update_one(
                {"_id": item['id']},
                {"$setOnInsert": {**new[item['id']], "duration": duration, "viewed": 0, "hidden": hidden}},
                upsert=True,
            )
    set_last_update('last_videos_update')
    return ok('Videos updated.')


@app.route('/clean/videos')
def clean_videos():
    # Watched videos stay KEEP_DAYS after being watched, so they can still be moved back.
    # Videos watched before 2.0 have no watched_at and fall back to their publish date.
    # Hidden shorts are never shown, they only need to outlive the import window.
    cutoff = (now() - timedelta(days=KEEP_DAYS)).isoformat()
    result = videosDB.delete_many({"$or": [
        {"viewed": 1, "watched_at": {"$lt": cutoff}},
        {"viewed": 1, "watched_at": {"$exists": False}, "published": {"$lt": cutoff}},
        {"hidden": 1, "published": {"$lt": cutoff}},
    ]})
    return ok(f"Removed {result.deleted_count} old videos.")


@app.route('/stats')
def stats():
    to_watch = {"viewed": 0, "hidden": 0}
    total = list(videosDB.aggregate([{"$match": to_watch}, {"$group": {"_id": None, "s": {"$sum": "$duration"}}}]))
    last = {d['_id']: d['time'] for d in randomDB.find({})}
    return ok('Stats returned.', {
        "last_videos_update": last.get('last_videos_update'),
        "last_channels_update": last.get('last_channels_update'),
        "n_of_videos": videosDB.count_documents({}),
        "n_of_channels": channelsDB.count_documents({}),
        "n_of_videos_to_watch": videosDB.count_documents(to_watch),
        "time_to_watch": int(total[0]['s']) if total else 0,
    })


if __name__ == "__main__":
    app.run(debug=True, port=8080, host='0.0.0.0')
