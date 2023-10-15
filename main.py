from pyquery import PyQuery
import sqlite3
import googleapiclient.discovery
import random
import json

with open('apiKey.json', 'r') as keyFile:
    apikey = json.load(keyFile)[0]

yt = googleapiclient.discovery.build("youtube", "v3", developerKey=apikey)

conn = sqlite3.connect('youtube_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS youtube_data (
                    video_url TEXT,
                    date_watched TEXT,
                    channel_url TEXT,
                    channel_name TEXT
                )''')

html_file = "D:\\tmd\\youtubehist\\Takeout\\YT\\history\\watch-history.html"
seen_channels = {}

with open(html_file, encoding='utf8') as html:
    pq = PyQuery(html.read())

    try:
        for index, outer_cell in enumerate(pq('div.outer-cell.mdl-cell.mdl-cell--12-col.mdl-shadow--2dp')):
            video_url = pq(outer_cell)('a[href^="https://www.youtube.com/watch?v="]').attr('href')
            date_watched = pq(outer_cell)('div.mdl-typography--body-1').text().split('\n')[-1]
            channel_url = pq(outer_cell)('a[href^="https://www.youtube.com/channel/"]').attr('href')

            if not channel_url:
                continue  # skip deleted channels, etc
            channel_id = channel_url[channel_url.rindex('/')+1:]
            channel_name = seen_channels.get(channel_id)

            if not channel_name:
                request = yt.channels().list(
                    part="snippet",
                    id=channel_id
                )
                response = request.execute()
                if response.get('items'):
                    channel_name = response['items'][0]['snippet']['localized']['title']
                else:
                    print("No items")
                    channel_name = None

                seen_channels[channel_id] = channel_name

            if random.random() > 0.994:
                print(f"{index}: adding {video_url}")
            cursor.execute('INSERT INTO youtube_data (video_url, date_watched, channel_url, channel_name) VALUES (?, ?, ?, ?)',
                           (video_url, date_watched, channel_url, channel_name))
    except Exception as e:
        conn.commit()
        conn.close()
        raise e
    conn.commit()
    conn.close()
