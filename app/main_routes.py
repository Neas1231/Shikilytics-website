from flask import Blueprint, render_template, request, redirect, url_for
import redis
import json

from .utils import profile_fetch, history_fetch, watched_anime, watched_todf
from .cache import cache_user_data, r
from .graphs import (pie_count_chart, bar_count_chart, 
                     hist_watched_genres,
                     hist_watched_type,
                     hist_watched_pegi,
                     hist_watched_studio
                    )

main = Blueprint('main', __name__)


PROFILE_NAME = "Профиль"
DEFAULT_FUNCS = ['Поиск по описанию']
PROFILE_FUNCS = ['Поиск по описанию', 'Аналитика профиля', 'Индивидуальные рекомендации']


@main.route("/")
def render_main(profile_name=PROFILE_NAME, profile_pic=None, funcs = DEFAULT_FUNCS):
    error = request.args.get('error')
    return render_template("main.html", profile_name=profile_name, profile_pic=profile_pic, funcs=funcs, error=error)

@main.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        profile_id = request.form["profile_id"]
        return redirect(url_for('main.confirm_profile_id', profile_id=profile_id))
    return render_main

def render_profile(profile_id, profile_name, profile_pic, funcs = PROFILE_FUNCS, error=None, count_figures=None, watched_figures=None,watched_metrics=None):
    return render_template("profile.html", 
                           profile_id=profile_id, 
                           profile_name=profile_name, 
                           profile_pic=profile_pic, 
                           funcs=funcs, 
                           error=error, 
                           count_figures=count_figures,
                           watched_names = ['Жанры', 'Тип сериала', 'Возрастное ограничение', 'Студии'],
                           watched_figures=watched_figures,
                           watched_metrics=watched_metrics
                           )

@main.route("/<profile_id>", methods=['GET', 'POST'])
async def confirm_profile_id(profile_id):
    if request.method == 'POST':
        profile_id = request.form["profile_id"]
        return redirect(url_for('main.confirm_profile_id', profile_id=profile_id))
    # profile fetch
    profile_id = profile_id.replace(' ', '+')
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
    
    watched_df = watched_todf(watched)
    # Graphs
    # count
    count_figs = []
    count_figs.append(pie_count_chart(count_list))
    count_figs.append(bar_count_chart(count_list))
    # watched
    watched_figs = []
    watched_figs.append(hist_watched_genres(watched_df))
    watched_figs.append(hist_watched_type(watched_df))
    watched_figs.append(hist_watched_pegi(watched_df))
    watched_figs.append(hist_watched_studio(watched_df))
    # metrics
    watched_metrics = []
    watched_metrics.append(['Средний рейтинг просмотренных', str(watched_df.loc[watched_df.rating != 'unk','rating'].astype(float).mean().round(3)) + '⭐'])
    watched_metrics.append(['Среднее количество эпизодов у сериала', watched_df.loc[watched_df.episodes != 'unk','episodes'].astype(int).mean().round(3)])
    watched_metrics.append(['Средняя продолжительность эпизода', float(watched_df.duration.mean().round(3))])
    watched_metrics.append(['Наиболее популярный год', int(watched_df.loc[watched_df.date != 'unk','date'].astype(float).mode().values[0])])
    return render_profile(profile_id, profile_name=profile_name, profile_pic=profile_pic, 
                          count_figures=count_figs,
                          watched_figures=watched_figs, watched_metrics=watched_metrics)