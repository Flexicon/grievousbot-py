import os
import praw
import sentry_sdk
import random

from praw import models
from dotenv import load_dotenv

REQUIRED_ENV_VARS = [
    "CLIENT_USERNAME",
    "CLIENT_SECRET",
    "CLIENT_ID",
    "CLIENT_PASSWORD",
    "USER_AGENT",
]

REPLY_QUOTES = [
    "That wasn't much of a rescue.",
    "I will deal with this Jedi slime myself.",
    "Jedi slime - Your comment will make a fine addition to my collection!",
    "Time to abandon ship.",
    "Army or not, you must realize, you are doomed.",
    "Your comment will make a fine addition to my collection!",
    "Your lightsabers will make a fine addition to my collection!",
]

load_dotenv()

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

    debug_print(
        "Received reply [%s] by [%s] - Link: https://reddit.com%s"
        % (comment, comment.author.name, comment.permalink)
    )

    if is_bot_reply(comment):
        new_reply = comment.reply(random.choice(REPLY_QUOTES))
        print(
            "Reply to [%s] sent successfully - Link: https://reddit.com%s"
            % (comment, new_reply.permalink)
        )
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


def ensure_env_vars_present(vars: list[str]):
    for v in vars:
        if not os.getenv(v):
            raise Exception(f"Missing environment variable '{v}'")


def setup_sentry():
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        print("Skipping Sentry setup - SENTRY_DSN is not set")
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=app_env(),
        attach_stacktrace=True,
        traces_sample_rate=1.0,
        ignore_errors=[KeyboardInterrupt],
    )


def app_env() -> str:
    env = os.getenv("APP_ENV")
    return env if env else "development"


def debug_print(msg: str):
    if os.getenv("DEBUG") == "true":
        print(f"[DEBUG] {msg}")


if __name__ == "__main__":
    ensure_env_vars_present(REQUIRED_ENV_VARS)
    setup_sentry()
    run_bot()
