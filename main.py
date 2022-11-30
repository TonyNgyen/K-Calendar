import pandas
from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
from releases import Releases

app = Flask(__name__)

releases = Releases()

(upcoming_releases_ascending, upcoming_releases_descending, past_releases_ascending, past_releases_descending) = \
    releases.get_releases()

closest_releases = releases.get_closest_releases()

data_dict = releases.get_images()

@app.route('/')
def home():
    return render_template("index.html", releases=closest_releases, images=data_dict)


@app.route('/releases/ascending')
def releases():
    return render_template("releases.html", releases=upcoming_releases_ascending, p_releases=past_releases_ascending, images=data_dict,
                           ascending=True)

@app.route('/releases/descending')
def releases_descending():
    return render_template("releases.html", releases=upcoming_releases_descending, p_releases=past_releases_descending, images=data_dict,
                           ascending=False)

@app.route('/artist_profile/<string:artist>')
def artist_profile(artist):
    return render_template("artist_profile.html", artist_name=artist, data=data_dict)

@app.route('/artist_profile/<string:artist>/<string:release_type>/<string:release>')
def release(artist, release, release_type):
    return render_template("release.html", release_name=release, artist_name=artist, release_data=data_dict[artist]["releases"][release_type][release])

@app.route('/private/testing')
def test_page():
    return render_template("test.html", artist_name="BTS", data=data_dict)


if __name__ == "__main__":
    app.run(debug=True)
