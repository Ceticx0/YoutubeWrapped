import concurrent.futures
import json
import datetime

import httplib2
import requests
import sqlite3
from googleapiclient import discovery
from dataclasses import dataclass
from tqdm import tqdm

with open('apiKey.json', 'r') as keyFile:
    apikey = json.load(keyFile)[0]
yt = discovery.build("youtube", "v3", developerKey=apikey)


@dataclass
class Video:
    is_short: bool = False
    vid_id: str = None
    duration: int = -1
    channel_id: str = None
    channel_name: str = None
    title: str = None
    tags: str = None
    likeCount: int = -1
    viewCount: int = -1


def is_short(vid_id: str, i):
    url = 'https://www.youtube.com/shorts/' + vid_id
    ret = requests.head(url)
    # whether 303 or other values, it's not short
    return ret.status_code == 200, i

def get_isosplit(s, split):
    if split in s:
        n, s = s.split(split)
    else:
        n = 0
    return n, s


def parse_isoduration(s):
    # Remove prefix
    s = s.split('P')[-1]

    # Step through letter dividers
    days, s = get_isosplit(s, 'D')
    _, s = get_isosplit(s, 'T')
    hours, s = get_isosplit(s, 'H')
    minutes, s = get_isosplit(s, 'M')
    seconds, s = get_isosplit(s, 'S')

    # Convert all to seconds
    dt = datetime.timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds))
    return int(dt.total_seconds())


def fetch_video_info(api, video_ids, http_lib):
    response = api.videos().list(
        part="snippet,contentDetails,statistics",
        id=",".join(video_ids)
    ).execute(http=http_lib)
    return response


def get_video_info(video_ids) -> list[Video]:
    completed_videos: list[Video] = []
    http = httplib2.Http()  # Makes YouTube api work multithreaded

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        f = []
        for (i, id) in enumerate(video_ids):
            f.append(executor.submit(is_short, id, i))

        api_task = executor.submit(fetch_video_info, yt, video_ids, http)
        concurrent.futures.wait(f + [api_task])
        is_short_results = [task.result() for task in f]
        response = api_task.result()
        is_short_results.sort(key=lambda x: x[1])

    for (i, video) in enumerate(response['items']):
        snippet = video['snippet']
        completed_videos.insert(i, Video())
        completed_videos[i].vid_id = video['id']
        completed_videos[i].duration = parse_isoduration(video['contentDetails']['duration'])
        completed_videos[i].channel_id = snippet['channelId']
        completed_videos[i].channel_name = snippet['channelTitle']
        completed_videos[i].title = snippet['title']
        completed_videos[i].tags = json.dumps(snippet.get('tags'))
        completed_videos[i].likeCount = int(video['statistics'].get('likeCount') or -1)
        completed_videos[i].viewCount = int(video['statistics'].get('viewCount') or -1)
        completed_videos[i].is_short = is_short_results[i][0]

    return completed_videos


conn = sqlite3.connect('youtube_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS video_data (
                    video_id TEXT,
                    duration TEXT,
                    channel_id TEXT,
                    channel_name TEXT,
                    tags TEXT,
                    title TEXT,
                    likeCount INTEGER,
                    viewCount INTEGER,
                    short INTEGER
                )''')
cursor.execute("DELETE FROM video_data")
conn.commit()

cursor.execute("SELECT video_url FROM youtube_data")
videos = cursor.fetchall()

all_ids = list([url[0][url[0].rindex('=') + 1:] for url in videos])
# all_ids] = []
# try:
#     for url in videos:
#         all_ids.append(url[0][url[0].rindex('=') + 1:])
# except AttributeError as e:
#     print(url)
#     print(url[0])]
#     breakpoint()


api_fetch_limit = 50

num_batches = (len(all_ids) // api_fetch_limit) + 1 if len(all_ids) % api_fetch_limit != 0 else len(
    all_ids) // api_fetch_limit
current_id = 0
skipped_vids = 0

with concurrent.futures.ThreadPoolExecutor() as executor, tqdm(total=len(all_ids)) as progress:
    print("Running...")
    f = []
    for i in range(num_batches):
        current_ids = list(set(all_ids[current_id:current_id + api_fetch_limit]))
        f.append(executor.submit(get_video_info, current_ids))
        current_id += api_fetch_limit

    for future in concurrent.futures.as_completed(f):
        result = future.result()
        try:
            for video in result:
                if not video.vid_id:
                    skipped_vids += 1
                    continue

                cursor.execute('INSERT INTO video_data '
                               '(video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short) '
                               'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)',
                               (video.vid_id, video.duration, video.channel_id, video.channel_name, video.tags,
                                video.title, video.likeCount, video.viewCount, video.is_short))
                progress.update()
            conn.commit()
        except Exception as e:
            print("Error occurred, Failed this batch")
            print(e)
            print(e.with_traceback(e.__traceback__))

print("skipped {} deleted/broken vids".format(skipped_vids))
conn.commit()
conn.close()
