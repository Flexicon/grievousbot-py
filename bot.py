import os
import random
import re

import sentry_sdk
from dotenv import load_dotenv
from praw import Reddit, models

REQUIRED_ENV_VARS = [
    "CLIENT_ID",
    "CLIENT_SECRET",
    "CLIENT_BOT_ID",
    "CLIENT_USERNAME",
    "CLIENT_PASSWORD",
    "USER_AGENT",
    "SUBREDDITS",
]

HELLO_THERE_MSG = "General Kenobi. You are a bold one."
HELLO_THERE_PATTERN = "^(hello there)[!]*$"
REPLY_QUOTES = [
    "That wasn't much of a rescue.",
    "I will deal with this Jedi slime myself.",
    "Jedi slime - Your comment will make a fine addition to my collection!",
    "Time to abandon ship.",
    "Army or not, you must realize, you are doomed.",
    "Your comment will make a fine addition to my collection!",
    "Your lightsabers will make a fine addition to my collection!",
]


def run_bot():
    print("🔋 Powering up Grievous Bot...")
    reddit = reddit_client()
    subreddits = reddit.subreddit(monitored_subreddits())

    print("🤖 General Grievous standing by...")
    for comment in subreddits.stream.comments(skip_existing=True):
        process_comment(comment)


def reddit_client() -> Reddit:
    return Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        password=os.getenv("CLIENT_PASSWORD"),
        user_agent=os.getenv("USER_AGENT"),
        username=os.getenv("CLIENT_USERNAME"),
    )


def process_comment(comment: models.Comment):
    if is_bot_comment(comment):
        return

    debug_print(
        "Received comment [%s] by [%s] - Link: https://reddit.com%s"
        % (comment, comment.author.name, comment.permalink)
    )

    if is_bot_reply(comment):
        new_reply = comment.reply(random.choice(REPLY_QUOTES))

        if new_reply:
            print_reply_successful(comment, new_reply)
    elif is_hello_comment(comment):
        new_reply = comment.reply(HELLO_THERE_MSG)

        if new_reply:
            print_reply_successful(comment, new_reply)
    else:
        debug_print("Comment [%s] did not match any pattern - moving on" % (comment))


def is_bot_reply(comment: models.Comment) -> bool:
    parent = comment.parent()
    return isinstance(parent, models.Comment) and is_bot_comment(parent)


def is_bot_comment(comment: models.Comment) -> bool:
    try:
        return comment.author.id == os.getenv("CLIENT_BOT_ID")
    except:
        return False


def is_hello_comment(comment: models.Comment) -> bool:
    return bool(re.match(HELLO_THERE_PATTERN, comment.body, re.IGNORECASE))


def print_reply_successful(original_comment: models.Comment, reply: models.Comment):
    print(
        "Reply to [%s] sent successfully - Link: https://reddit.com%s"
        % (original_comment, reply.permalink)
    )


def monitored_subreddits() -> str:
    default = "flexicondev"
    configured = os.getenv("SUBREDDITS")
    return configured if configured else default


def ensure_env_vars_present():
    for v in REQUIRED_ENV_VARS:
        if not os.getenv(v):
            raise Exception(f"Missing environment variable '{v}'")
    print("✅ Environment verified")


def setup_sentry():
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        print("🤷 Skipping Sentry setup - SENTRY_DSN is not set")
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=app_env(),
        attach_stacktrace=True,
        traces_sample_rate=1.0,
        ignore_errors=[KeyboardInterrupt],
    )
    print("🎯 Sentry setup")


def app_env() -> str:
    env = os.getenv("APP_ENV")
    return env if env else "development"


def check_debug_mode():
    if is_debug():
        print("🐞 Debug mode enabled")


def is_debug() -> bool:
    return os.getenv("DEBUG") == "true"


def debug_print(msg: str):
    if is_debug():
        print(f"[DEBUG] {msg}")


if __name__ == "__main__":
    load_dotenv()
    ensure_env_vars_present()
    setup_sentry()
    check_debug_mode()

    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n😴 Shutting down")
