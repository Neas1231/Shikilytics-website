from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests
import random
app = Flask(__name__,template_folder='templates')

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        profile_id = request.form["profile_id"]
        print(profile_id)
        return redirect(url_for('confirm_profile_id', profile_id=profile_id))
    profile_name = "Профиль" 
    profile_pic = "static/imgs/profile_default.png"
    return render_template("index.html", profile_name = profile_name, profile_pic = profile_pic)

@app.route("/<profile_id>")
def confirm_profile_id(profile_id):
    profile_name = profile_id
    profile_id = profile_id.replace(' ','+')
    page = requests.get(f"https://shikimori.one/{profile_id}", headers=generate_random_header()).text
    soup = BeautifulSoup(page, 'html.parser')
    profile_pic = soup.find('div',class_="avatar").find("img")['src']
    return render_template("index.html", profile_name = profile_name, profile_pic = profile_pic)




def generate_random_header():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 11; SM-G991B Build/RP1A.200720.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36"
    ]

    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": random.choice(["en-US,en;q=0.9", "fr-FR,fr;q=0.9", "es-ES,es;q=0.9"]),
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    
    return headers


if __name__ == "__main__":
    app.run(debug=True)