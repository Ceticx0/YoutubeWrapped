import sqlite3
from pprint import pprint
import googleapiclient.discovery
import requests
import json


def is_short(vid):
    url = 'https://www.youtube.com/shorts/' + vid
    ret = requests.head(url)
    # whether 303 or other values, it's not short
    return ret.status_code == 200


with open('apiKey.json', 'r') as keyFile:
    apikey = json.load(keyFile)[0]

yt = googleapiclient.discovery.build("youtube", "v3", developerKey=apikey)

conn = sqlite3.connect('youtube_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS video_data (
                    video_id TEXT PRIMARY KEY,
                    duration TEXT,
                    channel_id TEXT,
                    channel_name TEXT,
                    tags TEXT,
                    title TEXT,
                    likeCount INTEGER,
                    viewCount INTEGER,
                    short INTEGER
                )''')

cursor.execute("SELECT video_url FROM youtube_data")
videos = cursor.fetchall()
videos = set(videos)


all_ids = [url[0][url[0].rindex('=') + 1:] for url in videos]

api_video_limit = 50
iterations = (len(all_ids) // api_video_limit) + 1 if len(all_ids) % api_video_limit != 0 else len(all_ids) // api_video_limit
used_ids = []
current_id = 0
for i in range(iterations):
    current_ids = set(all_ids[current_id:current_id + api_video_limit])
    request = yt.videos().list(
        part="snippet,contentDetails,statistics",
        id=",".join(current_ids)
    )
    response = request.execute()

    for video in response['items']:
        snippet = video['snippet']

        id = video['id']
        short = is_short(id)
        duration = video['contentDetails']['duration']
        channel_id = snippet['channelId']
        channel_name = snippet['channelTitle']
        title = snippet['title']
        tags = json.dumps(snippet.get('tags'))
        likeCount = video['statistics'].get('likeCount')
        viewCount = video['statistics']['viewCount']

        cursor.execute('INSERT INTO video_data '
                       '(video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short) '
                       'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short))
        used_ids.append(id)
    print(f"Video number {current_id + api_video_limit} | {(len(all_ids) / (current_id + api_video_limit)):5.2f}% complete, saving...")
    conn.commit()
    current_id += api_video_limit


conn.commit()
conn.close()
