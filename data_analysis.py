import matplotlib.pyplot as plt
import sqlite3
import json
from datetime import timedelta
from dateutil import parser
from pprint import pprint


def print_top_channels(videos, other_threshold=20):
    channels = {}
    for video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short, watchCount in videos:
        if channel_id in channels:
            channels[channel_id][0] += watchCount
        else:
            channels[channel_id] = [watchCount, channel_name]

    total = 0
    sorted_channels = sorted(channels.items(), reverse=True, key=lambda x: x[1][0])
    for index, (channel, (count, name)) in enumerate(sorted_channels):
        total += count
        print(f"{index + 1}. {name}: {count}\t|\thttps://www.youtube.com/channel/{channel}")

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
    sorted_videos = sorted(videos, reverse=True, key=lambda x: x[9])
    for index, (video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short, watchCount) in enumerate(sorted_videos[:100]):
        print(f"{index + 1}. {title}: {watchCount}\t|\thttps://www.youtube.com/watch?v={video_id}")


def print_top_tags(videos):
    top_tags = {}
    for video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short, watchCount in videos:
        decoded_tags = json.loads(tags)
        if not decoded_tags:
            continue
        for tag in decoded_tags:
            if tag in top_tags:
                top_tags[tag] += watchCount
            else:
                top_tags[tag] = watchCount

    top_tags = sorted(top_tags.items(), reverse=True, key=lambda x: x[1])
    for index, (tag, count) in enumerate(top_tags[:100]):
        print(f"{index + 1}. {tag}: {count}")


def print_avg_like_view_count(videos):
    total_likes = sum(likeCount for
                      video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short, watchCount
                      in videos)

    total_views = sum(viewCount for
                      video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short, watchCount
                      in videos)

    likes = []
    views = []
    for video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short, watchCount in videos:
        likes.extend([likeCount] * watchCount)
        views.extend([viewCount] * watchCount)

    # Calculate averages
    avg_likes = total_likes / len(likes)
    avg_views = total_views / len(views)

    # Sorting the likes and views for median calculation
    sorted_likes = sorted(likes)
    sorted_views = sorted(views)

    # Calculate medians
    median_likes = sorted_likes[len(sorted_likes) // 2] if sorted_likes else 0
    median_views = sorted_views[len(sorted_views) // 2] if sorted_views else 0
    print(f"Avg like count: {avg_likes:,.2f}")
    print(f"Median like count: {median_likes:,}")
    print(f"Max like count: {max(likes):,}")
    print()
    print(f"Avg view count: {avg_views:,.2f}")
    print(f"Median view count: {median_views:,}")
    print(f"Max view count: {max(views):,}")


# im js gonna like comment this out bc its dumb anyway
# def print_avg_duration(videos):
#     durations = [(video_id, title, int(duration))
#                  for video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short, watchCount in videos]
#
#     durations.sort(reverse=True, key=lambda x: x[2])
#     # remove 5 biggest TODO: be smarter
#     for i in range(5):
#         durations.pop(0)
#
#     _, _, lengths = zip(*durations)
#     avg_seconds = sum(lengths) / len(lengths)
#     median_seconds = lengths[len(lengths) // 2]
#     total_seconds = sum(lengths)
#     average = timedelta(seconds=avg_seconds)
#     median = timedelta(seconds=median_seconds)
#     total = timedelta(seconds=total_seconds)
#
#     print(f"Average duration is {average}")
#     print(f"Median duration is {median}")
#     print(f"Total duration is {total}")


if __name__ == '__main__':
    conn = sqlite3.connect('youtube_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM video_data WHERE short = 0")
    # cursor.execute("SELECT * FROM video_data")
    vid_entries = cursor.fetchall()

    # get videos from specific year
    current_year_vid_entries = []
    for video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short, watchCount in vid_entries:
        cursor.execute("SELECT date_watched FROM youtube_data WHERE video_url LIKE ?",
                       (f'%{video_id}%',))  # Assuming video_url contains the video_id
        date_watched = cursor.fetchone()[0]
        year = parser.parse(date_watched).year  # TODO: add tzinfos argument
        if year == 2024:
            current_year_vid_entries.append(
                (video_id, duration, channel_id, channel_name, tags, title, likeCount, viewCount, short, watchCount)
            )

    print("Calculating Stats...")
    cursor.execute("SELECT min(date_watched) from youtube_data")
    print("Data starts at: " + ''.join(cursor.fetchone()))
    print(sum(vid[9] for vid in vid_entries), " videos clicked on since data start")
    print(sum(vid[9] for vid in current_year_vid_entries), " videos clicked on in 2024")
    print_top_channels(vid_entries)
    # print_top_videos(vid_entries)
    # print_top_tags(vid_entries)
    # print_avg_like_view_count(vid_entries)
