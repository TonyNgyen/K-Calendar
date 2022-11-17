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

    def search_id(self, artist_id):
        headers = self.get_resource_headers()
        endpoint = f"https://api.spotify.com/v1/artists/{artist_id}"
        r = requests.get(url=endpoint, headers=headers)
        return r.json()

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

    def get_artist_data(self, artist):
        artist_info = {}
        try:
            artist_information = self.search(query=artist)["artists"]["items"][0]
            artist_name = artist_information["name"]
            artist_id = artist_information["id"]
            artist_image = artist_information["images"][0]["url"]
            related_artists = self.get_related_artists(artist_id)
            albums = self.get_releases(artist_id)
            artist_info[artist_name] = {"artist_id": artist_id, "artist_image": artist_image,
                                      "releases": albums, "related artists": related_artists}
        except IndexError:
            artist_info[artist_name] = {"artist_id": "NOT FOUND", "artist_image": "NOT FOUND", "releases": "NOT FOUND"}
        return artist_info

    def get_all_data_name(self, name_list):
        data_dict = {}
        for artist in name_list:
            try:
                artist_information = self.search(query=artist)["artists"]["items"][0]
                artist_name = artist_information["name"]
                artist_id = artist_information["id"]
                try:
                    artist_image = artist_information["images"][0]["url"]
                except IndexError:
                    artist_image = "https://i.scdn.co/image/ab6761610000e5ebb1a15fd3e7c1b375dea2637a"
                related_artists = self.get_related_artists(artist_id)
                albums = self.get_releases(artist_id)
                data_dict[artist_name] = {"artist_id": artist_id, "artist_image": artist_image,
                                          "releases": albums, "related artists": related_artists}
            except IndexError:
                data_dict[artist] = {"artist_id": "NOT FOUND", "artist_image": "NOT FOUND",
                                     "releases": "NOT FOUND", "related artists": "NOT FOUND"}
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

    def get_all_data_id(self, id_list):
        data_dict = {}
        for id_ in id_list:
            artist_information = self.search_id(artist_id=id_)
            artist_name = artist_information["name"]
            artist_id = artist_information["id"]
            try:
                artist_image = artist_information["images"][0]["url"]
            except IndexError:
                artist_image = "https://i.scdn.co/image/ab6761610000e5ebb1a15fd3e7c1b375dea2637a"
            related_artists = self.get_related_artists(artist_id)
            releases = self.get_releases(artist_id)
            data_dict[artist_name] = {"artist_id": artist_id, "artist_image": artist_image,
                                      "releases": releases, "related artists": related_artists}
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
                self.get_all_data_name(add_list)
        except FileNotFoundError:
            return False
        return True

    def get_related_artists(self, artist_id):
        headers = self.get_resource_headers()
        endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
        r = requests.get(url=endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        related_artists = r.json()["artists"][0:6]
        related_artists_dict = {}
        for artist in related_artists:
            try:
                related_artists_dict[artist["name"]] = {"id": artist["id"], "image": artist["images"][0]["url"]}
            except IndexError:
                related_artists_dict[artist["name"]] = {"id": artist["id"],
                                                        "image": "https://i.scdn.co/image/ab6761610000e5ebb1a15fd3e7c1b375dea2637a"}
        return related_artists_dict

    def update_related_artists(self):
        with open("Data.json", "r") as data_file:
            data = json.load(data_file)
            update_list = []
            for element in data.values():
                try:
                    related_artists = (element["related artists"])
                    for artist in related_artists:
                        if artist not in data and related_artists[artist]["id"] not in update_list:
                            update_list.append(related_artists[artist]["id"])
                except KeyError:
                    pass
            self.get_all_data_id(id_list=update_list)
        return True

    def get_releases(self, artist_id):
        headers = self.get_resource_headers()
        id_list = self.get_releases_id(artist_id)
        albums_list, singles_list, eps_list = [], [], []
        while len(id_list) >= 20 or len(id_list) > 0:
            current_list = id_list[0:20]
            del id_list[:20]
            query = ",".join(current_list)
            releases_endpoint = f"https://api.spotify.com/v1/albums?ids={query}"
            r = requests.get(url=releases_endpoint, headers=headers)
            if r.status_code not in range(200, 299):
                return {}
            releases = r.json()["albums"]
            is_single = True
            for release in releases:
                tracks = []
                album_length_ms = 0
                for track in release["tracks"]["items"]:
                    album_length_ms += track["duration_ms"]
                    if track["duration_ms"]/60000 > 10:
                        is_single = False
                    track = {"track name": track["name"], "track id": track["id"],
                             "track link": track["external_urls"]["spotify"], "track preview": track["preview_url"]}
                    tracks.append(track)
                release_dict = {"release name": release["name"], "release release date": release["release_date"],
                                "release link": release["external_urls"]["spotify"], "release type": release["album_type"],
                                "release length tracks": release["total_tracks"], "release image": release["images"][0]["url"],
                                "release tracks": tracks}
                if release_dict["release type"] == "single":
                    if album_length_ms/60000 < 30 and release_dict["release length tracks"] <= 3 and is_single:
                        singles_list.append(release_dict)
                    else:
                        eps_list.append(release_dict)
                else:
                    albums_list.append(release_dict)
        return {"albums": albums_list, "eps": eps_list, "singles": singles_list}

    def get_releases_id(self, artist_id):
        headers = self.get_resource_headers()
        album_endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/albums?limit=50&include_groups=album,single"
        r = requests.get(url=album_endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        albums_data = r.json()["items"]
        albums_list = []
        albums_tracker = 0
        while len(albums_data) == 50:
            for element in albums_data:
                if len(element["available_markets"]) > 5:
                    albums_list.append(element["id"])
            albums_tracker += len(albums_data)
            album_endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/albums?limit=50&include_groups=album,single&offset={albums_tracker}"
            r = requests.get(url=album_endpoint, headers=headers)
            albums_data = r.json()["items"]
        r = requests.get(url=album_endpoint, headers=headers)
        albums_data = r.json()["items"]
        for element in albums_data:
            if len(element["available_markets"]) > 1:
                albums_list.append(element["id"])
        return albums_list

    def update_entire_data(self):
        with open("Data.json", "r") as data_file:
            data = json.load(data_file)
            id_list = []
            for element in data:
                id_list.append(data[element]["artist_id"])
        self.get_all_data_id(id_list)


# EXAMPLE CODE IF NOT SURE HOW THE CLASS WORKS
    # spotify = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)
    # spotify.get_all_data_id(["2KC9Qb60EaY0kW4eH68vr3"])
    # print(spotify.get_releases(["6al2VdKbb6FIz9d7lU7WRB", "3u0ggfmK0vjuHMNdUbtaa9"]))
    # artist_list = ["BTS", "ENHYPEN", "IVE", "LE SSERAFIM", "TXT", "NewJeans", "aespa", "STAYC"]
    # spotify.get_all_data_name(artist_list)
    # spotify.get_all_data_id(["5R7AMwDeroq6Ls0COQYpS4"])
    # print(spotify.update_data_file(artist_list))
    # print(spotify.search(query='BTS')["artists"]["items"][0])
    # print(spotify.get_related_artists("3Nrfpe0tUJi4K4DXYWgMUX"))
    # albums = spotify.get_artist_albums(artist_id)
    # album_tracks = spotify.get_album_tracks(album_id="6al2VdKbb6FIz9d7lU7WRB")
    # print(spotify.search(query="Danger", operator="NOT", operator_query="Zone", search_type="track"))
