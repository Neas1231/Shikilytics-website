from flask import Blueprint, render_template, jsonify, redirect, url_for, request
import asyncio
import asyncpg
import json

from .cache import cache_user_data, r
from .utils import profile_fetch

funcs = Blueprint('funcs', __name__)

PROFILE_NAME = "Профиль"
DEFAULT_FUNCS = ['Поиск по описанию']
PROFILE_FUNCS = ['Поиск по описанию', 'Аналитика профиля', 'Индивидуальные рекомендации']

# FETCH DATA
# async def fetch_data():
#     conn = asyncpg.connect(user='user', password='password', database='dbname', host='127.0.0.1')
#     rows = conn.fetch('SELECT * FROM your_table')
#     conn.close()
#     return rows

# Пример списка аниме
animes = [
    {
        "id": 1,
        "title": "Attack on Titan",
        "image": "https://shikimori.one/uploads/poster/animes/52991/preview_alt-f180ae801fddf9551e27aff2d96f2112.jpeg",
        "description": "A story about humanity's fight against giant humanoid creatures."
    },
    {
        "id": 2,
        "title": "My Hero Academia",
        "image": "https://shikimori.one/uploads/poster/animes/5114/preview_alt-ba65e789c26d848f95418b3f8718b525.jpeg",
        "description": "A story about a world where people have superpowers."
    },
    {
        "id": 3,
        "title": "Demon Slayer",
        "image": "https://example.com/demon_slayer.jpg",
        "description": "A story about a boy who becomes a demon slayer to save his sister."
    }
]

# @funcs.route('/api/animes', methods=['GET'])
def get_animes():
    # asyncio.sleep(5)
    return animes
    # return jsonify(animes)

# DEFAULT SEARCH OUTPUT
@funcs.route('/funcs/function1', methods=['GET', 'POST'])
def search(search_output = None):
    if request.method == 'POST':
        if 'profile_id' in request.form:
            profile_id = request.form["profile_id"]
            return redirect(url_for('main.confirm_profile_id', profile_id=profile_id))
        elif "search_text" in request.form:
            # data = fetch_data()  # Асинхронный вызов к базе данных
            # return jsonify(data)
            search_output = get_animes()
            return render_template('search.html',profile_name=PROFILE_NAME, profile_pic=None, funcs=DEFAULT_FUNCS, search_output=search_output)
    return render_template('search.html',profile_name=PROFILE_NAME, profile_pic=None, funcs=DEFAULT_FUNCS, search_output=search_output)

# PROFILE SEARCH OUTPUT
@funcs.route('/<profile_id>/funcs/function1', methods=['GET', 'POST'])
def search_profile(profile_id, search_output = None):
    if request.method == 'POST':
        if 'profile_id' in request.form:
            profile_id = request.form["profile_id"]
            return redirect(url_for('main.confirm_profile_id', profile_id=profile_id))
        elif "search_text" in request.form:
            # data = fetch_data()  # Асинхронный вызов к базе данных
            # return jsonify(data)
            search_output = get_animes()
            return render_template('search.html',profile_name=PROFILE_NAME, profile_pic=None, funcs=DEFAULT_FUNCS, search_output=search_output)
    # profile fetch
    user_data = r.get(profile_id)
    if not user_data:
        profile, count_list = profile_fetch(profile_id), profile_fetch(profile_id, kind='count_list')
        # profile name
        if type(profile) != type(tuple()):
            return profile
        profile_name, profile_pic = profile
        cache_user_data(profile_name, profile_pic, count_list)
    else:
        user_data = json.loads(user_data)
        profile_name, profile_pic, = user_data['username'],user_data['avatar_path']
    return render_template('search.html', profile_id=profile_id, profile_name=profile_name, profile_pic=profile_pic, funcs=PROFILE_FUNCS, search_output=search_output)

@funcs.route('/<profile_id>/funcs/function2', methods=['GET', 'POST'])
def analytic(profile_id):
    return redirect(url_for('main.confirm_profile_id', profile_id=profile_id))

@funcs.route('/<profile_id>/funcs/function3', methods=['GET', 'POST'])
def recommendation(profile_id):
    if request.method == 'POST':
        if 'profile_id' in request.form:
                profile_id = request.form["profile_id"]
                return redirect(url_for('main.confirm_profile_id', profile_id=profile_id))
    # profile fetch
    profile_id = profile_id.replace(' ', '+')
    user_data = r.get(profile_id)
    
    if not user_data:
        profile, count_list = profile_fetch(profile_id), profile_fetch(profile_id, kind='count_list')
        # profile name
        if type(profile) != type(tuple()):
            return profile
        profile_name, profile_pic = profile
        cache_user_data(profile_name, profile_pic, count_list)
    else:
        user_data = json.loads(user_data)
        profile_name, profile_pic, = user_data['username'],user_data['avatar_path']
    return render_template('recommendation.html', profile_id=profile_id, profile_name=profile_name, profile_pic=profile_pic, funcs=PROFILE_FUNCS)