import sqlite3
from dateutil import parser

conn = sqlite3.connect('youtube_data.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM youtube_data")
videos = cursor.fetchall()

channels = {}

for video, date, channel in videos:
    parsed_date = parser.parse(date)
    print(f"{video}: {parsed_date.year}")
    if channel in channels:
        channels[channel] += 1
    else:
        channels[channel] = 1

sorted_channels = sorted(channels.items(), reverse=True, key=lambda x: x[1])
for index, (channel, count) in enumerate(sorted_channels):
    print(f"{index+1}. {channel}: {count}")

print(len(videos))
