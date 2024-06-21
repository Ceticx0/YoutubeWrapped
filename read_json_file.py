import sqlite3
import random
import json

conn = sqlite3.connect('youtube_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS youtube_data (
                    video_url TEXT,
                    date_watched TEXT,
                    channel_url TEXT
                )''')

file_path = "C:\\Users\\Gavin\\Downloads\\takeout-20240620T224529Z-001\\Takeout\\YouTube and YouTube Music\\history\\watch-history.json"
seen_channels = {}

with open(file_path, encoding='utf8') as json_file:
    watch_history = json.load(json_file)
    print(watch_history[1122])
    try:
        for index, video in enumerate(watch_history):
            if not video.get("subtitles") or not video.get("titleUrl"):
                continue  # skip deleted channels, etc

            video_url = video["titleUrl"]
            date_watched = video["time"]
            channel_url = video["subtitles"][0]["url"]
            channel_id = channel_url[channel_url.rindex('/')+1:]

            if random.random() > 0.994:
                print(f"{index}: adding {video_url}")

            cursor.execute('INSERT INTO youtube_data (video_url, date_watched, channel_url) VALUES (?, ?, ?)',
                           (video_url, date_watched, channel_url))

        print(f"{index} videos in total since {date_watched}")

    except KeyError as e:
        print("KeyError found at json index {}".format(index))
        print(e)
    except Exception as e:
        conn.commit()
        conn.close()
        raise e
    conn.commit()
    conn.close()
