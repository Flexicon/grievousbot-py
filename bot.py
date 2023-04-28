import os
import praw

from praw import models
from dotenv import load_dotenv

load_dotenv()

# TODO: ensure environment variables are set: https://github.com/Flexicon/grievousbot/blob/master/main.go#L18-L22
# TODO: setup sentry: https://github.com/Flexicon/grievousbot/blob/master/main.go#L104

ua = os.getenv("USER_AGENT")
bot_id = os.getenv("CLIENT_BOT_ID")


def run_bot():
    reddit = praw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        password=os.getenv("CLIENT_PASSWORD"),
        user_agent=ua,
        username=os.getenv("CLIENT_USERNAME"),
    )
    subreddit = reddit.subreddit(monitored_subreddits())

    print("General Grievous standing by...")
    for comment in subreddit.stream.comments(skip_existing=True):
        process_comment(comment)


def process_comment(comment: models.Comment):
    if is_bot_comment(comment):
        return

    debug_print(f'received comment: [{comment}]\n"{comment.body}"\n')

    if is_bot_reply(comment):
        # TODO: send a random reply comment: https://github.com/Flexicon/grievousbot/blob/master/bot.go#L20-L28
        # comment.reply("You dare address me directly, filth?!")
        pass
    else:
        # TODO: send the standard reply if comment is in "Hello There" format: https://github.com/Flexicon/grievousbot/blob/master/bot.go#L15-L16
        # comment.reply("Got you know, Jedi scum!")
        pass


def is_bot_reply(comment: models.Comment):
    parent = comment.parent()
    return isinstance(parent, models.Comment) and is_bot_comment(parent)


def is_bot_comment(comment: models.Comment):
    return comment.author.id == bot_id


def monitored_subreddits() -> str:
    default = "flexicondev"
    additional = os.getenv("SUBREDDITS")
    return f"{default}+{additional}" if additional else default


def debug_print(msg: str):
    if os.getenv("DEBUG") == "true":
        print(f"[DEBUG] {msg}")


if __name__ == "__main__":
    run_bot()
