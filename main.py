import pandas
from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
from releases import Releases

UPCOMING_RELEASES_URL = "https://dbkpop.com/2022/09/01/october-2022-k-pop-comebacks-and-debuts/"
SPOTIFY_URL = "https://open.spotify.com/artist/3LFFf4EpKn2krneZ9vozyz"
TODAY_DATE = datetime.datetime.today()

app = Flask(__name__)

releases = Releases()

releases.get_releases(date=TODAY_DATE, url=UPCOMING_RELEASES_URL)

response = requests.get(url=SPOTIFY_URL)
soup = BeautifulSoup(response.content, "html.parser")
meta = soup.find("meta", {"property": "og:image"})["content"]

upcoming_releases_ascending = releases.upcoming_releases.values.tolist()
upcoming_releases_ascending.sort(key=lambda x: x[0])
upcoming_releases_descending = upcoming_releases_ascending[::-1]

closest_releases = releases.get_closest_releases().values.tolist()

past_releases_descending = releases.past_releases.values.tolist()
past_releases_descending.sort(key=lambda x: x[0])
past_releases_ascending = past_releases_descending[::-1]


@app.route('/')
def home():
    return render_template("index.html", releases=closest_releases)


@app.route('/releases/ascending')
def releases():
    return render_template("releases.html", releases=upcoming_releases_ascending, p_releases=past_releases_ascending,
                           ascending=True)

@app.route('/releases/descending')
def releases_descending():
    return render_template("releases.html", releases=upcoming_releases_descending, p_releases=past_releases_descending,
                           ascending=False)


if __name__ == "__main__":
    app.run(debug=True)
