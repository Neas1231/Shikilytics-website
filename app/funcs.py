from flask import Blueprint, render_template, jsonify, redirect, url_for, request
import asyncio
import asyncpg  
from bs4 import BeautifulSoup
import requests

from generate import generate_random_header

funcs = Blueprint('funcs', __name__)

PROFILE_NAME = "Профиль"
DEFAULT_FUNCS = ['Поиск по описанию']
PROFILE_FUNCS = ['Поиск по описанию', 'Аналитика профиля', 'Индивидуальные рекомендации']

# FETCH DATA
# async def fetch_data():
#     conn = await asyncpg.connect(user='user', password='password', database='dbname', host='127.0.0.1')
#     rows = await conn.fetch('SELECT * FROM your_table')
#     await conn.close()
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
async def get_animes():
    # await asyncio.sleep(5)
    return animes
    # return jsonify(animes)

# DEFAULT SEARCH OUTPUT
@funcs.route('/funcs/function1', methods=['GET', 'POST'])
async def search(search_output = None):
    if request.method == 'POST':
        if 'profile_id' in request.form:
            profile_id = request.form["profile_id"]
            return redirect(url_for('main.confirm_profile_id', profile_id=profile_id))
        elif "search_text" in request.form:
            # data = await fetch_data()  # Асинхронный вызов к базе данных
            # return jsonify(data)
            search_output = await get_animes()
            return render_template('search.html',profile_name=PROFILE_NAME, profile_pic=None, funcs=DEFAULT_FUNCS, search_output=search_output)
    return render_template('search.html',profile_name=PROFILE_NAME, profile_pic=None, funcs=DEFAULT_FUNCS, search_output=search_output)

# PROFILE SEARCH OUTPUT
@funcs.route('/<profile_id>/funcs/function1', methods=['GET', 'POST'])
async def search_profile(profile_id, search_output = None):
    if request.method == 'POST':
        if 'profile_id' in request.form:
            profile_id = request.form["profile_id"]
            return redirect(url_for('main.confirm_profile_id', profile_id=profile_id))
        elif "search_text" in request.form:
            # data = await fetch_data()  # Асинхронный вызов к базе данных
            # return jsonify(data)
            search_output = await get_animes()
            return render_template('search.html',profile_name=PROFILE_NAME, profile_pic=None, funcs=DEFAULT_FUNCS, search_output=search_output)
    profile_name = profile_id
    profile_id = profile_id.replace(' ', '+')
    # profile pic
    page = requests.get(
        f"https://shikimori.one/{profile_id}", headers=generate_random_header())
    if page.status_code != 200:
        return redirect(url_for('main.render_main', error=True))
    soup = BeautifulSoup(page.text, 'html.parser')
    profile_pic = soup.find('div', class_="avatar")
    if profile_pic is not None:
        profile_pic = profile_pic.find("img")['src']
    else:
        return redirect(url_for('main.render_main', error=True))
    return render_template('search.html', profile_id=profile_id, profile_name=profile_name, profile_pic=profile_pic, funcs=PROFILE_FUNCS, search_output=search_output)

@funcs.route('/<profile_id>/funcs/function2', methods=['GET', 'POST'])
def analytic(profile_id):
    return redirect(url_for('main.confirm_profile_id', profile_id=profile_id))