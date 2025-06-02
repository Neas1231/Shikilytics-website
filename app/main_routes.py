from flask import Blueprint, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests

from generate import generate_random_header

main = Blueprint('main', __name__)

PROFILE_NAME = "Профиль"
DEFAULT_FUNCS = ['Поиск по описанию']
PROFILE_FUNCS = ['Поиск по описанию', 'Аналитика профиля', 'Индивидуальные рекомендации']


@main.route("/")
def render_main(profile_name=PROFILE_NAME, profile_pic=None, funcs = DEFAULT_FUNCS, error=None):
    return render_template("main.html", profile_name=profile_name, profile_pic=profile_pic, funcs=funcs, error=error)

@main.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        profile_id = request.form["profile_id"]
        return redirect(url_for('main.confirm_profile_id', profile_id=profile_id))
    return render_main

def render_profile(profile_id, profile_name=PROFILE_NAME, profile_pic=None, funcs = PROFILE_FUNCS, error=None):
    return render_template("profile.html", profile_name=profile_name, profile_pic=profile_pic, funcs=funcs, error=error, profile_id=profile_id)

@main.route("/<profile_id>", methods=['GET', 'POST'])
def confirm_profile_id(profile_id):
    if request.method == 'POST':
        profile_id = request.form["profile_id"]
        return redirect(url_for('main.confirm_profile_id', profile_id=profile_id))
    # profile name
    profile_name = profile_id
    profile_id = profile_id.replace(' ', '+')
    # profile pic
    page = requests.get(
        f"https://shikimori.one/{profile_id}", headers=generate_random_header())
    if page.status_code != 200:
        return render_main(error=True)
    soup = BeautifulSoup(page.text, 'html.parser')
    profile_pic = soup.find('div', class_="avatar")
    if profile_pic is not None:
        profile_pic = profile_pic.find("img")['src']
    else:
        return render_main(error=True)
    return render_profile(profile_id, profile_name=profile_name, profile_pic=profile_pic)