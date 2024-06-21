import matplotlib.pyplot as plt
import sqlite3
import json
from datetime import timedelta
from dateutil import parser
from pprint import pprint


def print_top_channels(videos, other_threshold=20):
    channels = {}
    for vid_id, duration, channel_id, name, tags, title, likeCount, viewCount, short in videos:
        if channel_id in channels:
            channels[channel_id][0] += 1
        else:
            channels[channel_id] = [1, name]

    total = 0
    sorted_channels = sorted(channels.items(), reverse=True, key=lambda x: x[1][0])
    for index, (channel, (count, name)) in enumerate(sorted_channels):
        total += count
        print(f"{index + 1}. {name}: {count}\t|\t{channel}")

    channel_ids, channel_tally = zip(*sorted_channels[:other_threshold])
    values, labels = zip(*channel_tally)
    # add 'Other'
    values = list(values)
    labels = list(labels)
    values.append(total - sum(values))
    labels.append("Other")

    plt.pie(values, labels=labels)
    plt.show()


def print_top_videos(videos):
    vids = {}
    for vid_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short in videos:
        if title in vids:
            vids[title][0] += 1
        else:
            vids[title] = [1, vid_id]

    sorted_videos = sorted(vids.items(), reverse=True, key=lambda x: x[1][0])
    # print(sorted_videos[:500])
    print("length:" + str(len(vids)))
    len(videos)
    # print(sorted_videos.reverse())
    for index, (vid_title, (count, video_id)) in enumerate(sorted_videos[:100]):
        print(f"{index + 1}. {vid_title}: {count}\t|\thttps://www.youtube.com/watch?v={video_id}")


def print_top_tags(videos):
    top_tags = {}
    for vid_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short in videos:
        decoded_tags = json.loads(tags)
        if not decoded_tags:
            continue
        for tag in decoded_tags:
            if tag in top_tags:
                top_tags[tag] += 1
            else:
                top_tags[tag] = 1

    top_tags = sorted(top_tags.items(), reverse=True, key=lambda x: x[1])
    for index, (tag, count) in enumerate(top_tags[:100]):
        print(f"{index + 1}. {tag}: {count}")


def print_avg_like_view_count(videos):
    likes_views = [(likeCount, viewCount) for
                   vid_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short in videos]

    likes, views = zip(*likes_views)
    total_likes = sum(likes)
    total_views = sum(views)

    avg_likes = total_likes / len(videos)
    avg_views = total_views / len(videos)
    print(f"Avg like count: {avg_likes:,.2f}")
    print(f"Median like count: {likes[len(likes) // 2]:,}")
    print(f"Max like count: {max(likes):,}")
    print()
    print(f"Avg view count: {avg_views:,.2f}")
    print(f"Median view count: {views[len(views) // 2]:,}")
    print(f"Max view count: {max(views):,}")


def print_avg_duration(videos):
    durations = [(video_id, title, int(duration))
                 for video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short in videos]

    durations.sort(reverse=True, key=lambda x: x[2])
    # remove 5 biggest TODO: be smarter
    for i in range(5):
        durations.pop(0)

    _, _, lengths = zip(*durations)
    avg_seconds = sum(lengths) / len(lengths)
    median_seconds = lengths[len(lengths) // 2]
    total_seconds = sum(lengths)
    average = timedelta(seconds=avg_seconds)
    median = timedelta(seconds=median_seconds)
    total = timedelta(seconds=total_seconds)

    print(f"Average duration is {average}")
    print(f"Median duration is {median}")
    print(f"Total duration is {total}")


if __name__ == '__main__':
    conn = sqlite3.connect('youtube_data.db')
    cursor = conn.cursor()
    # cursor.execute("SELECT * FROM video_data WHERE short = 0")
    cursor.execute("SELECT * FROM video_data")
    videos = cursor.fetchall()

    # get videos from specific year
    current_year_videos = []
    for video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short in videos:
        cursor.execute("SELECT date_watched FROM youtube_data WHERE video_url LIKE ?",
                       (f'%{video_id}%',))  # Assuming video_url contains the video_id
        date_watched = cursor.fetchone()[0]
        year = parser.parse(date_watched).year  # TODO: add tzinfos argument
        if year == 2024:
            current_year_videos.append(
                (video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short)
            )

    print("Calculating Stats...")
    print(len(videos))
    print(len(current_year_videos))
    # print_top_channels(videos)]
    print_top_videos(videos)
    print_top_tags(videos)
    print_avg_like_view_count(videos)
    print_avg_duration(videos)
