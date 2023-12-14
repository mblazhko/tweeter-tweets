import uvicorn
import logging
from app import app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="logs.log", filemode="w")
    uvicorn.run("main:app", host="0.0.0.0", port=80)