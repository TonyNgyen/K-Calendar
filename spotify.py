import base64
import datetime
import requests
import json
from urllib.parse import urlencode

with open("spotify_client.txt", "r") as data_file:
    data = json.load(data_file)
    CLIENT_ID = data["CLIENT ID"]
    CLIENT_SECRET = data["CLIENT SECRET"]


class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        # Returns a base64 encoded string
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(url=token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client")
        data = r.json()
        now = datetime.datetime.now()
        access_token = data["access_token"]
        self.access_token = access_token
        expires_in = data["expires_in"]  # seconds
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token is None:
            return self.get_access_token()
        return token

    def base_search(self, query_params, search_type='artist'):
        headers = self.get_resource_headers()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        r = requests.get(url=lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def search(self, query=None, operator=None, operator_query=None, search_type="artist"):
        if query is None:
            raise Exception("A query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k, v in query.items()])
        if operator is not None and operator_query is not None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": search_type.lower()})
        return self.base_search(query_params)

    def get_resource_headers(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def get_resource(self, lookup_id, resource_type="albums", version="v1"):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_headers()
        r = requests.get(url=endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def get_artist(self, _id):
        return self.get_resource(lookup_id=_id, resource_type="artists")

    def get_release(self, artist_id, search_type):
        headers = self.get_resource_headers()
        album_endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/albums?limit=50&include_groups={search_type}"
        r = requests.get(url=album_endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        albums_data = r.json()["items"]
        albums_list = []
        for element in albums_data:
            if len(element["available_markets"]) > 1:
                albums_dict = {"album name": element["name"], "album release date": element["release_date"],
                               "album link": element["external_urls"]["spotify"],
                               "album length": element["total_tracks"],
                               "album id": element["id"], "album image": element["images"][0]["url"],
                               "album_tracks": self.get_release_tracks(element["id"])}
                albums_list.append(albums_dict)
        return albums_list

    def get_albums(self, artist_id):
        return self.get_release(artist_id=artist_id, search_type="album")

    def get_singles(self, artist_id):
        return self.get_release(artist_id=artist_id, search_type="single")

    def get_release_tracks(self, album_id):
        headers = self.get_resource_headers()
        endpoint = f"https://api.spotify.com/v1/albums/{album_id}/tracks?limit=50"
        r = requests.get(url=endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        album_data = r.json()["items"]
        album_tracks = []
        for track in album_data:
            albums_tracks_dict = {"track name": track["name"], "track id": track["id"],
                                  "track link": track["external_urls"]["spotify"],
                                  "track preview": track["preview_url"]}
            album_tracks.append(albums_tracks_dict)
        return album_tracks

    def get_all_data(self, artist_list):
        data_dict = {}
        for artist in artist_list:
            try:
                artist_id = self.search(artist)["artists"]["items"][0]["id"]
                artist_image = self.search(artist)["artists"]["items"][0]["images"][0]["url"]
                albums = self.get_all_releases(artist_id)
                data_dict[artist] = {"artist_id": artist_id, "artist_image": artist_image, "releases": albums}
            except IndexError:
                data_dict[artist] = {"artist_id": "NOT FOUND", "artist_image": "NOT FOUND", "releases": "NOT FOUND"}
        try:
            with open("Data.json", "r") as data_file:
                data = json.load(data_file)
                data.update(data_dict)
        except FileNotFoundError:
            with open("Data.json", "w") as data_file:
                json.dump(data, data_file, indent=4)
        else:
            data.update(data_dict)
            with open("Data.json", "w") as data_file:
                json.dump(data, data_file, indent=4)
        return True

    def update_data_file(self, artist_list):
        try:
            with open("Data.json", "r") as data_file:
                data = json.load(data_file)
                add_list = []
                for artist in artist_list:
                    if artist not in data:
                        add_list.append(artist)
                self.get_all_data(add_list)
        except FileNotFoundError:
            return False
        return True


    def get_all_releases(self, artist_id):
        all_releases = {"albums": self.get_albums(artist_id), "singles": self.get_singles(artist_id)}
        return all_releases


# EXAMPLE CODE IF NOT SURE HOW THE CLASS WORKS
# spotify = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)
# artist_list = ["BTS", "ENHYPEN", "IVE", "LE SSERAFIM", "TXT", "NewJeans", "aespa", "STAYC"]
# print(spotify.update_data_file(artist_list))
# print(spotify.search(query='BTS', search_type='artist')['artists']['items'][0]['images'][0]['url'])
# albums = spotify.get_artist_albums(artist_id)
# album_tracks = spotify.get_album_tracks(album_id="6al2VdKbb6FIz9d7lU7WRB")
# print(spotify.search(query="Danger", operator="NOT", operator_query="Zone", search_type="track"))
