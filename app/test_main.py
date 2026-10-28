"""Self-check for the API, with YouTube faked out. Needs a throwaway MongoDB:

    docker run -d --rm -p 27017:27017 --name ytrss-test mongo
    MONGODB_HOST=localhost MONGODB_PORT=27017 python test_main.py
"""
import os
os.environ['MONGODB_DB'] = 'youtube_test'

from datetime import timedelta
import main

main.mongo_client.drop_database('youtube_test')
c = main.app.test_client()


def iso(days_ago):
    return (main.now() - timedelta(days=days_ago)).isoformat()


FEED = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns="http://www.w3.org/2005/Atom">
<entry><yt:videoId>upcoming</yt:videoId><title>Premiere</title><published>{iso(0)}</published></entry>
<entry><yt:videoId>long</yt:videoId><title>Long</title><published>{iso(1)}</published></entry>
<entry><yt:videoId>tiny</yt:videoId><title>Tiny</title><published>{iso(2)}</published></entry>
<entry><yt:videoId>short</yt:videoId><title>Short</title><published>{iso(3)}</published></entry>
<entry><yt:videoId>old</yt:videoId><title>Old</title><published>{iso(40)}</published></entry>
</feed>"""
DURATIONS = {'upcoming': None, 'premiere001': None, 'premiere002': 'PT20M', 'long': 'PT10M', 'tiny': 'PT45S', 'short': 'PT2M', 'spotvideo01': 'PT20S', 'spotvideo02': 'PT5M'}
# Premieres added by link: scheduled in two days, not out yet.
SCHEDULE = {'premiere001': iso(-2), 'premiere002': iso(-2)}
SNIPPETS = {**{i: {'publishedAt': iso(1), 'title': 'Premiere', 'channelId': 'UC1', 'channelTitle': 'One',
                   'liveBroadcastContent': 'upcoming'} for i in SCHEDULE},
            'spotvideo01': {'publishedAt': '2020-01-01T00:00:00Z', 'title': 'Spot', 'channelId': 'UC2', 'channelTitle': 'Two'},
            'spotvideo02': {'publishedAt': '2020-01-01T00:00:00Z', 'title': 'Spot', 'channelId': 'UC1', 'channelTitle': 'One'}}
CHANNEL = {'id': 'UC1', 'snippet': {'title': 'One', 'description': 'd', 'publishedAt': 'x',
           'thumbnails': {'medium': {'url': 'logo'}}}, 'statistics': {'viewCount': '10', 'videoCount': '2'}}
calls = []


def fake_youtube(endpoint, **params):
    calls.append((endpoint, params.get('id')))
    if endpoint == 'channels':
        return [{**CHANNEL, 'id': i} for i in params['id'].split(',') if i in ('UC1', 'UC2')]
    if endpoint == 'videos':
        # A scheduled premiere has no duration yet.
        return [{'id': i, 'contentDetails': {'duration': DURATIONS[i]} if DURATIONS[i] else {}, 'snippet': SNIPPETS.get(i),
                 'liveStreamingDetails': {'scheduledStartTime': SCHEDULE[i]} if i in SCHEDULE else {}}
                for i in params['id'].split(',') if i in DURATIONS]
    return [{'id': {'channelId': 'UC1'}, 'snippet': {}}]


class FakeResponse:
    content = FEED.encode()
    def raise_for_status(self): pass


main.youtube = fake_youtube
main.requests.get = lambda url, **kw: FakeResponse()
main.is_short = lambda video_id: video_id == 'short'

# Channels
assert c.post('/add/channel', json={}).status_code == 400
assert c.post('/add/channel', json={'channel_id': 'UCx'}).status_code == 404
assert c.post('/add/channel', json={'channel_id': 'UC1'}).status_code == 200
assert c.post('/add/channel', json={'channel_id': 'UC1'}).status_code == 409
assert c.get('/get/channels').json['data']['UC1']['subscriberCount'] == 0, 'hidden subscriber count'

# Import: recent videos only, shorts hidden, known videos not looked up again,
# videos without a duration yet skipped and looked up again on the next run
assert c.get('/update/videos').status_code == 200
videos = {v['_id']: v for v in main.videosDB.find()}
assert set(videos) == {'long', 'tiny', 'short'}, videos
assert (videos['long']['hidden'], videos['tiny']['hidden'], videos['short']['hidden']) == (0, 1, 1)
calls.clear()
c.get('/update/videos')
assert [x for x in calls if x[0] == 'videos'] == [('videos', 'upcoming')], calls
DURATIONS['upcoming'] = 'PT1H'
c.get('/update/videos')
assert main.videosDB.find_one({'_id': 'upcoming'})['hidden'] == 0
main.videosDB.delete_one({'_id': 'upcoming'})
DURATIONS['upcoming'] = None
assert [v['_id'] for v in c.get('/get/videos').json['data']] == ['long']

stats = c.get('/stats').json['data']
assert (stats['n_of_videos_to_watch'], stats['time_to_watch'], stats['last_channels_update']) == (1, 600, None), stats
assert stats['last_videos_update']

# Watch, then cleanup: watched videos stay 30 days from when they were watched
c.get('/watch/video/long')
assert main.videosDB.find_one({'_id': 'long'})['watched_at']
c.get('/clean/videos')
assert main.videosDB.find_one({'_id': 'long'}), 'just watched, must stay'
c.get('/tbwatch/video/long')
assert 'watched_at' not in main.videosDB.find_one({'_id': 'long'})
main.videosDB.update_one({'_id': 'long'}, {'$set': {'viewed': 1, 'watched_at': iso(31)}})
main.videosDB.insert_many([
    {'_id': 'legacy-old', 'viewed': 1, 'hidden': 0, 'published': iso(40)},
    {'_id': 'legacy-new', 'viewed': 1, 'hidden': 0, 'published': iso(5)},
    {'_id': 'short-old', 'viewed': 0, 'hidden': 1, 'published': iso(40)},
    {'_id': 'unwatched-old', 'viewed': 0, 'hidden': 0, 'published': iso(400)},
])
c.get('/clean/videos')
assert {v['_id'] for v in main.videosDB.find()} == {'tiny', 'short', 'legacy-new', 'unwatched-old'}

# Single videos: any link shape, shorts kept, old dates kept, channel shown even if not followed
assert c.post('/add/video', json={}).status_code == 400
assert c.post('/add/video', json={'url': 'https://example.com/watch?v=short'}).status_code == 400
assert c.post('/add/video', json={'url': 'missingvid1'}).status_code == 404
assert c.post('/add/video', json={'url': 'https://youtu.be/spotvideo01?t=3'}).status_code == 200
assert c.post('/add/video', json={'url': 'https://www.youtube.com/watch?v=spotvideo01'}).status_code == 409
spot = main.videosDB.find_one({'_id': 'spotvideo01'})
assert (spot['hidden'], spot['duration'], spot['published']) == (0, 20, '2020-01-01T00:00:00Z'), spot
assert (spot['channel'], spot['channel_title'], spot['channel_logo']) == ('UC2', 'Two', 'logo'), spot
calls.clear()
assert c.post('/add/video', json={'url': 'https://www.youtube.com/shorts/spotvideo02'}).status_code == 200
assert 'channel_title' not in main.videosDB.find_one({'_id': 'spotvideo02'}) and ('channels', 'UC1') not in calls
main.videosDB.insert_one({'_id': 'hiddenshort', 'viewed': 0, 'hidden': 1, 'published': iso(1)})
calls.clear()
assert c.post('/add/video', json={'url': 'hiddenshort'}).status_code == 200 and not calls
assert main.videosDB.find_one({'_id': 'hiddenshort'})['hidden'] == 0
main.videosDB.delete_many({'_id': {'$in': ['spotvideo01', 'spotvideo02', 'hiddenshort']}})

# Premieres added by link: kept on top under their schedule until out, dropped if they disappear
for i in SCHEDULE:
    assert c.post('/add/video', json={'url': i}).status_code == 200
    v = main.videosDB.find_one({'_id': i})
    assert (v['upcoming'], v['duration'], v['published']) == (1, 0, SCHEDULE[i]), v
assert c.get('/get/videos').json['data'][0]['_id'] in SCHEDULE
SCHEDULE['premiere001'] = iso(-3)
del DURATIONS['premiere002']
c.get('/update/videos')
assert main.videosDB.find_one({'_id': 'premiere001'})['published'] == SCHEDULE['premiere001']
assert not main.videosDB.find_one({'_id': 'premiere002'}), 'gone from YouTube, must be dropped'
DURATIONS['premiere001'] = 'PT30M'
SNIPPETS['premiere001']['liveBroadcastContent'] = 'none'
c.get('/update/videos')
v = main.videosDB.find_one({'_id': 'premiere001'})
assert (v['duration'], v['hidden'], 'upcoming' in v) == (1800, 0, False), v
main.videosDB.delete_one({'_id': 'premiere001'})

# Search, channel refresh, UI, errors
assert c.get('/search').status_code == 400
assert c.get('/search?q=a/b c').json['data'][0]['id']['channelId'] == 'UC1'
assert c.get('/update/channels').status_code == 200 and c.get('/stats').json['data']['last_channels_update']
assert b'YouTube RSS' in c.get('/').data
assert c.get('/nope').status_code == 404 and c.get('/nope').json['status'] == 'ERROR'
main.youtube = lambda *a, **k: 1 / 0
r = c.get('/update/channels')
assert r.status_code == 500 and r.json['status'] == 'ERROR'
assert c.delete('/remove/channel', json={'channel_id': 'UC1'}).status_code == 200
assert main.videosDB.count_documents({'channel': 'UC1'}) == 0

main.mongo_client.drop_database('youtube_test')
print('OK')
