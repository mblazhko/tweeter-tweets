import uvicorn
from app import app


if __name__ == "__main__":
    uvicorn.run("main:app", workers=65, host="0.0.0.0", port=80)