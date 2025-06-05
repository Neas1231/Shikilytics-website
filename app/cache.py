import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()
REDIS_HOST = os.getenv("REDIS_HOST")

r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

def cache_user_data(username, avatar_path, counts, watched):
    user_data = {
        'username': username,
        'avatar_path': avatar_path,
        'counts': counts,
        'watched': watched
    }
    
    r.set(username, json.dumps(user_data))
    
