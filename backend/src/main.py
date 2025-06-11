# main.py

from fastapi import FastAPI
from auth.routers import router as auth_router

app = FastAPI()

app.include_router(auth_router)

if __name__ == "__main__":
    import uvicorn
    import logging

    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="127.0.0.1", port=8000)
