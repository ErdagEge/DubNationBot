import praw
import json

# Load the configuration from the JSON file
with open('config.json') as config_file:
    config = json.load(config_file)

# Initialize the Reddit instance with the configuration data
reddit_instance = praw.Reddit(
    username=config['username'],
    password=config['password'],
    client_id=config['client_id'],
    client_secret=config['client_secret'],
    user_agent=config['user_agent']
)

# print(reddit_instance.user.me())

# HOW TO GET TOP 25 POSTS IN THE LAST WEEK
# subreddit = reddit_instance.subreddit("warriors")
# top_25_submissions = subreddit.top(limit=25, time_filter="week")
# for submission in top_25_submissions:
#    print(submission.title)

# HOW TO POST A POST
# subreddit = reddit_instance.subreddit("testingground4bots")
# subreddit.submit(title="This is a test post", selftext="Hello Test.")

submission = reddit_instance.submission("1e9ghv0")
comments = submission.comments

# HOW TO COMMENT
for comment in comments:
    if "test my stuff" in comment.body:
        comment.reply("reply.")
