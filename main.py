import pandas
from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
from releases import Releases

SPOTIFY_URL = "https://open.spotify.com/artist/3LFFf4EpKn2krneZ9vozyz"

app = Flask(__name__)

releases = Releases()

(upcoming_releases_ascending, upcoming_releases_descending, past_releases_ascending, past_releases_descending) = \
    releases.get_releases()


closest_releases = releases.get_closest_releases()

image_dict = releases.get_images()

@app.route('/')
def home():
    return render_template("index.html", releases=closest_releases, images=image_dict)


@app.route('/releases/ascending')
def releases():
    return render_template("releases.html", releases=upcoming_releases_ascending, p_releases=past_releases_ascending, images=image_dict,
                           ascending=True)

@app.route('/releases/descending')
def releases_descending():
    return render_template("releases.html", releases=upcoming_releases_descending, p_releases=past_releases_descending, images=image_dict,
                           ascending=False)

@app.route('/artist_profile/<str: artist>')

@app.route('/private/testing')
def test_page():
    return render_template("artist_image_check.html", releases=past_releases_ascending, images=image_dict,
                           ascending=False)


if __name__ == "__main__":
    app.run(debug=True)
