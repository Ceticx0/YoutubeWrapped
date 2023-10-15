import sqlite3

conn = sqlite3.connect('youtube_data.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM youtube_data")
videos = cursor.fetchall()

channels = {}
for video, date, channel, name in videos:
# for vid_id, duration, channel, name, tags, title, likeCount, viewCount, short in videos:
    if channel in channels:
        channels[channel][0] += 1
    else:
        channels[channel] = [1, name]

sorted_channels = sorted(channels.items(), reverse=True, key=lambda x: x[1][0])
for index, (channel, (count, name)) in enumerate(sorted_channels):
    print(f"{index+1}. {name}: {count}\t|\t{channel}")

print(len(videos))
