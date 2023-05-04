import os
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from contextlib import asynccontextmanager
import asyncio

from bot import ensure_env_vars_present, run_bot


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(run_bot())
    yield


load_dotenv()
ensure_env_vars_present()

app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return Response(
        "General Grievous Bot - https://www.reddit.com/user/gen_grievous_bot\n"
        + f"{os.getenv('USER_AGENT')}"
    )
