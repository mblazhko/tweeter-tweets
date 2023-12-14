import uvicorn
import logging
from app import app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("main:app",workers=10, host="0.0.0.0", port=80)