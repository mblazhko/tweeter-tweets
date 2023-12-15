import redis
from dateutil import parser


def transform_to_datetime(date: str) -> str:
    date_string = date.replace("·", "")
    timestamp = parser.parse(date_string)
    return str(timestamp)

def get_redis_client():
    return redis.StrictRedis(host='localhost', port=6379, db=0)