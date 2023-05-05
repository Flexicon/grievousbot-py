import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from contextlib import asynccontextmanager
from sentry_sdk import capture_exception
import asyncio

from bot import ensure_env_vars_present, run_bot, setup_sentry


async def kickstart_bot(count: int = 1):
    try:
        await run_bot()
    except Exception as e:
        capture_exception(e)
        print(f"❌ Bot crashed: {e}")
        if count > 5:
            sys.exit(1)

        print("🪫 Reloading Grievous Bot in 5s...")
        await asyncio.sleep(5)
        await kickstart_bot(count + 1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(kickstart_bot())
    yield


load_dotenv()
ensure_env_vars_present()
setup_sentry()

app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return Response(
        "General Grievous Bot - https://www.reddit.com/user/gen_grievous_bot\n"
        + f"{os.getenv('USER_AGENT')}"
    )
