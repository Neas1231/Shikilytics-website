from flask import redirect, url_for
from bs4 import BeautifulSoup
import requests
import random
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


load_dotenv()
HOST = os.getenv("HOST")
DATABASE = os.getenv("DATABASE")
USER = os.getenv("USER")
PASS = os.getenv("PASS")


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

def search_anime(user_description, df):
    vectorizer = TfidfVectorizer()

    descriptions = df['description'].tolist()
    descriptions.append(user_description)

    tfidf_matrix = vectorizer.fit_transform(descriptions)

    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    df['similarity'] = cosine_similarities.flatten()
    
    return df

def truncate_sentence(sentence, word_count):
    words = sentence.split()

    if len(words) <= word_count:
        return sentence  
    
    truncated = ' '.join(words[:word_count - 1]) + '...'
    
    return truncated

def fetch_poster(link):
    page = requests.get(link, headers=generate_random_header())
    if page.status_code != 200:
        return None
    soup = BeautifulSoup(page.text, 'html.parser')
    poster_div = soup.find('div',class_="b-db_entry-poster")
    if not poster_div:
        return None
    return poster_div.find('img')['src']


def profile_fetch(profile_id, kind='header'):
    profile_name = profile_id.replace('+', ' ')
    # profile pic
    page = requests.get(
        f"https://shikimori.one/{profile_id}", headers=generate_random_header())
    if page.status_code != 200:
        return redirect(url_for('main.render_main', error=True))
    soup = BeautifulSoup(page.text, 'html.parser')
    
    if kind == 'header':
        profile_pic = soup.find('div', class_="avatar")
        if profile_pic is not None:
            profile_pic = profile_pic.find("img")['src']
        else:
            return redirect(url_for('main.render_main', error=True))
        return profile_name, profile_pic
    
    if kind == 'count_list':
        result = []
        watching_soup = soup.find("div",class_='b-stats_bar anime')
        if not watching_soup:
            return None
        for watch_type in ['Запланировано', 'Смотрю','Просмотрено','Отложено','Брошено']:
            selected_info = watching_soup.select(f"[data-type]:-soup-contains('{watch_type}') span")
            if selected_info:
                result.append([watch_type,selected_info[0].text])
        return result

# History fetch
async def fetch(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.text()
        else:
            return None

async def parse_page(html):
    soup_history = BeautifulSoup(html, "html.parser")
    history_lines = soup_history.find_all('div',class_="b-user_history-line")
    
    if history_lines:
        return [[line.find('span',class_= "name-ru").text, line.find('span').get_text().split('\xa0')[1]] for line in history_lines if line.find('span',class_= "name-ru")]
    return None

async def history_fetch(base_url):
    parsed_history = []
    async with aiohttp.ClientSession() as session:
        retry_times = 0
        page_number = 1
        while True:
            url = f"{base_url}?page={page_number}"
            html = await fetch(session, url)
            if not bool(html):
                retry_times += 1
                if retry_times > 10:
                    return None
                await asyncio.sleep(3)
                continue
            result = await parse_page(html)
            if result:
                parsed_history += result
            else:
                break
            page_number += 1
    return parsed_history

# Pg anime fetch
def anime_fetch():
    try:
        engine = create_engine(f"postgresql+psycopg2://{USER}:{PASS}@{HOST}/{DATABASE}", echo=False)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM anime")).fetchall()
        anime_df = pd.DataFrame(result)
        return anime_df
    except Exception as e:
        print("Ошибка:", e)
        return None

# History process

def watched_todf(watched):
    anime_df = anime_fetch()
    # Кеширование просмотренных аниме
    watched_df = anime_df[anime_df['name'].str.split(' / ').str[0].isin(watched)]
    return watched_df

def watched_anime(parsed_history):
    history_df = pd.DataFrame(parsed_history, columns=["Название", "Действие"])
    temp = {}
    for action_type in ['добавлено в список', 'просмотрено', 'смотрю']:
        temp[action_type] = history_df[history_df['Действие'] == action_type]['Название'].values
    anime_df = anime_fetch()
    watched = list(set(anime_df['name'].str.split(' / ').apply(lambda x:x[0])).intersection(set(temp['просмотрено'])))
    return watched