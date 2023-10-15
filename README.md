# Youtube Wrapped

This project takes in the html watch history file you get from google takeout,
and then saves it into an sqlite3 database, it then uses the youtube api to save additional information
about it and runs some analysis to show interesting statistics. <br>

The data it saves after the api calls:
1. Video id (for each video in your watch history)
2. Video duration (for each video in your watch history)
3. Id of channel that uploaded each video
4. Name of channel that uploaded each video
5. The tags on each video
6. The title of each video
7. The like number on each video
8. The view count on each video
9. Whether the video is a short

The results it can output include:
1. The top channels (channels you clicked on the most videos from)
2. Top videos (videos you watched the most times)
3. Most common tags in the videos in your watch history
4. The average, median, and max like and view count of the videos
5. The average, median, and total duration of all the videos <br>

Although it's pretty easy to add more.

## Usage
1. Create apiKey.json file with ["Your api key here"] inside
2. Change the location of your watch history html file in main.py and run it
to save the info to youtube_data.db (warning this uses like a billion api credits to get channel names which ill fix soon)
3. Run add_api_data.py to get all the info from the youtube api and add it to youtube_data.db again
4. Uncomment whatever you want to see at the bottom of data_analysis.py and run it

## Additional info

To avoid outliers like 356 day livestreams the duration deletes the top 5 longest videos, if
anyone is smart and wants to make that actually do something reliable be my guest

Download google takeout data here, https://takeout.google.com/settings/takeout?pli=1  
you only need to check youtube and youtube music at the bottom