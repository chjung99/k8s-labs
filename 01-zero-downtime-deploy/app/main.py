import asyncio
import os
import signal
import socket
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

# MODE=A : SIGTERM을 받으면 즉시 종료 (실패 재현용)
# MODE=B : uvicorn 기본 동작 사용 -> 새 연결은 닫고, 진행 중 요청만 마무리 후 종료
MODE = os.getenv("MODE", "B").upper()
HOST = socket.gethostname()


def log(msg: str) -> None:
    print(f"{time.strftime('%H:%M:%S')} [{HOST}] {msg}", flush=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if MODE == "A":
        def die(signum, frame):
            log("SIGTERM received -> exit immediately (MODE A)")
            os._exit(1)

        signal.signal(signal.SIGTERM, die)
    log(f"started (MODE {MODE})")
    yield
    log("graceful shutdown finished")


app = FastAPI(lifespan=lifespan)


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.get("/slow")
async def slow():
    await asyncio.sleep(5)  # 요청 하나당 처리 시간 5초
    return {"pod": HOST, "mode": MODE}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")