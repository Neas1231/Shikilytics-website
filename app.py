from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests

from generate import generate_random_header

app = Flask(__name__, template_folder='templates')
PROFILE_NAME = "Профиль"
PROFILE_PIC = "static/imgs/profile_default.png"


@app.route("/")
def render_main(profile_name=PROFILE_NAME, profile_pic=PROFILE_PIC, error=None):
    return render_template("index.html", profile_name=profile_name, profile_pic=profile_pic, error=error)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        profile_id = request.form["profile_id"]
        return redirect(url_for('confirm_profile_id', profile_id=profile_id))
    return render_main

@app.route("/<profile_id>", methods=['GET', 'POST'])
def confirm_profile_id(profile_id):
    print(request)
    if request.method == 'POST':
        profile_id = request.form["profile_id"]
        return redirect(url_for('confirm_profile_id', profile_id=profile_id))
    # profile name
    profile_name = profile_id
    profile_id = profile_id.replace(' ', '+')
    # profile pic
    page = requests.get(
        f"https://shikimori.one/{profile_id}", headers=generate_random_header())
    if page.status_code != 200:
        return render_main(error=True)
    soup = BeautifulSoup(page.text, 'html.parser')
    profile_pic = soup.find('div', class_="avatar").find("img")['src']
    return render_template("index.html", profile_name=profile_name, profile_pic=profile_pic)


if __name__ == "__main__":
    app.run(debug=True)


