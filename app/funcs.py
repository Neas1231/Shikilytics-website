from flask import Blueprint, render_template, jsonify, redirect, url_for, request
import asyncio
import asyncpg
import json

from .cache import cache_user_data, r
from .utils import profile_fetch, anime_fetch, search_anime, fetch_poster, truncate_sentence, recommend_anime,history_fetch,watched_anime

funcs = Blueprint('funcs', __name__)

PROFILE_NAME = "Профиль"
DEFAULT_FUNCS = ['Поиск по описанию']
PROFILE_FUNCS = ['Поиск по описанию', 'Аналитика профиля', 'Индивидуальные рекомендации']

anime = anime_fetch()
genres = anime.loc[(anime['genres'] != 'unk'),'genres'].str.split(' ').explode()
GENRES = sorted(list(genres[genres.str.strip() != ''].unique()))
STUDIOS = list(anime.loc[anime['studio'] != 'unk','studio'].sort_values().unique())
# Пример списка аниме
# animes = [
#     {
#         "id": 1,
#         "title": "Attack on Titan",
#         "image": "https://shikimori.one/uploads/poster/animes/52991/preview_alt-f180ae801fddf9551e27aff2d96f2112.jpeg",
#         "description": "A story about humanity's fight against giant humanoid creatures."
#     },
#     {
#         "id": 2,
#         "title": "My Hero Academia",
#         "image": "https://shikimori.one/uploads/poster/animes/5114/preview_alt-ba65e789c26d848f95418b3f8718b525.jpeg",
#         "description": "A story about a world where people have superpowers."
#     },
#     {
#         "id": 3,
#         "title": "Demon Slayer",
#         "image": "https://example.com/demon_slayer.jpg",
#         "description": "A story about a boy who becomes a demon slayer to save his sister."
#     }
# ]


def get_search(description, genre, studio):
    df = anime_fetch()
    df = df[df['rating'] != 'unk']
    # Filters
    if genre != 'default':
        df = df.loc[df['genres'].str.contains(genre)]
    if studio != 'default':
        df = df.loc[df['studio'] == studio]
    
    df = df.sort_values(by=["rating"], ascending=False).reset_index()
    # By description
    if description:
        # Жосски ML
        df = search_anime(description, df)
        df = df.sort_values(by=["similarity","rating"], ascending=False).reset_index(drop=True)
    
    df = df.loc[:,['link','name','description','poster']].iloc[:20,:]
    df.loc[:,'description'] = df.description.apply(lambda x: truncate_sentence(x,8))


    return df.to_dict(orient='records')


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
            search_output = get_search(request.form['search_text'], request.form["genre_filter"], request.form["studio_filter"])
            return render_template('search.html',
                                   profile_name=PROFILE_NAME, profile_pic=None, 
                                   funcs=DEFAULT_FUNCS, 
                                   search_output=search_output, 
                                   genres=GENRES, studios=STUDIOS)
    return render_template('search.html',
                           profile_name=PROFILE_NAME, profile_pic=None,
                           funcs=DEFAULT_FUNCS, 
                           search_output=search_output,
                           genres=GENRES, studios=STUDIOS)

# PROFILE SEARCH OUTPUT
@funcs.route('/<profile_id>/funcs/function1', methods=['GET', 'POST'])
def search_profile(profile_id, search_output = None):
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
        
    if request.method == 'POST':
        if 'profile_id' in request.form:
            profile_id = request.form["profile_id"]
            return redirect(url_for('main.confirm_profile_id', profile_id=profile_id))
        elif "search_text" in request.form:
            search_output = get_search(request.form['search_text'], request.form["genre_filter"], request.form["studio_filter"])
            return render_template('search.html',
                                    profile_id=profile_id,
                                    profile_name=profile_name, profile_pic=profile_pic,
                                    funcs=PROFILE_FUNCS, 
                                    search_output=search_output,
                                    genres=GENRES, studios=STUDIOS)
    return render_template('search.html', 
                           profile_id=profile_id, profile_name=profile_name, profile_pic=profile_pic, 
                           funcs=PROFILE_FUNCS, 
                           search_output=search_output,
                           genres=GENRES, studios=STUDIOS)

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

    df = anime_fetch()
    df['name'] = df['name'].str.split(' / ').str.get(0)
    animes_for_select = df.loc[:,['index','name','poster']].to_dict(orient='records')
    return render_template('recommendation.html', 
                           profile_id=profile_id, profile_name=profile_name, profile_pic=profile_pic, 
                           funcs=PROFILE_FUNCS,
                           animes=animes_for_select)



@funcs.route('/recommendations/sim', methods=['POST'])
async def recommend_by_similarity():
    data = request.get_json()
    
    anime_id = int(data.get('animeId'))
    profile_id = data.get('profile_id')
    print(profile_id)

    user_data = r.get(profile_id)
    if not user_data:
        base_url = f"https://shikimori.one/{profile_id}/history"
        # profile fetch
        profile, count_list = profile_fetch(profile_id), profile_fetch(profile_id, kind='count_list')
        # profile name
        if type(profile) != type(tuple()) or not count_list:
            return redirect(url_for('main.render_main', error=True))
        profile_name, profile_pic = profile
        # history fetch
        parsed_history = await history_fetch(base_url)
        if not parsed_history:
            return redirect(url_for('main.render_main', error=True))
        watched = watched_anime(parsed_history)
        cache_user_data(profile_name, profile_pic, count_list, watched)
    else:
        user_data = json.loads(user_data)
        profile_name, profile_pic, count_list, watched = user_data['username'], user_data['avatar_path'], user_data['counts'], user_data['watched']

    
    response = {
        'animeId': anime_id,
        'recommendations': recommend_anime(user_animeId = anime_id, watched = watched, num_recommendations=10)
    }
    
    return jsonify(response)


