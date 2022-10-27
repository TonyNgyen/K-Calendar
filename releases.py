# from bs4 import BeautifulSoup
# import requests
# import pandas
# import datetime
#
#
# class Releases:
#
#     def __init__(self):
#         self.upcoming_releases = None
#         self.past_releases = None
#
#     def get_releases(self, date, url):
#         response = requests.get(url=url)
#         soup = BeautifulSoup(response.content, "html.parser")
#         table = soup.find("table")
#         headers = []
#
#         for i in table.find_all("th"):
#             title = i.text
#             headers.append(title)
#
#         self.upcoming_releases = pandas.DataFrame(columns=headers)
#         self.past_releases = pandas.DataFrame(columns=headers)
#
#         for j in table.find_all("tr")[1:]:
#             row_data = j.find_all("td")
#             row = [i.text for i in row_data]
#             if row[3] == "":
#                 row[3] = "N/A"
#             if datetime.datetime.strptime(row[0], "%Y-%m-%d") < date:
#                 length = len(self.past_releases)
#                 self.past_releases.loc[length] = row
#             else:
#                 length = len(self.upcoming_releases)
#                 self.upcoming_releases.loc[length] = row
#
#     def get_closest_releases(self):
#         return self.upcoming_releases.iloc[0:3]
#

from bs4 import BeautifulSoup
import requests
import pandas
import datetime

TODAY_DATE = datetime.datetime.today()
UPCOMING_RELEASES_URL = "https://www.reddit.com/r/kpop/wiki/upcoming-releases/2022/october/"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
FILTER_RELEASES_URL = "https://dbkpop.com/2022/09/01/october-2022-k-pop-comebacks-and-debuts/"

# TRY USING FILTER LINK TO MAKE A LIST OF NAME OF THE ARTISTS
# THEN USE THE REDDIT LINK TO GET ALL THE ARTISTS AND GO THROUGH THE LIST AND CHECK IF THE ARTIST IS IN THE FILTER LIST
# IF SO, APPEND ALL OF THAT INFORMATION TO A NEW LIST

class Releases:

    def __init__(self):
        self.all_releases = None
        self.upcoming_releases = []
        self.past_releases = []
        self.filter_releases = []
        self.upcoming_releases_ascending = []
        self.upcoming_releases_descending = []
        self.past_releases_ascending = []
        self.past_releases_descending = []

    def get_releases(self):
        response = requests.get(url=UPCOMING_RELEASES_URL, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table")
        headers = []

        for i in table.find_all("th"):
            title = i.text
            headers.append(title)

        self.all_releases = pandas.DataFrame(columns=headers)

        for j in table.find_all("tr")[1:]:
            row_data = j.find_all("td")
            row = [i.text for i in row_data]
            length = len(self.all_releases)
            self.all_releases.loc[length] = row
        self.all_releases = self.all_releases.values.tolist()

        for i in range(len(self.all_releases)):
            if self.all_releases[i][0] != "":
                self.all_releases[i][0] = f"10-{self.all_releases[i][0][:-2]}-2022"
            else:
                self.all_releases[i][0] = self.all_releases[i - 1][0]

            if self.all_releases[i][1] == "" or self.all_releases[i][1] == "?":
                self.all_releases[i][1] = "N/A"

            if datetime.datetime.strptime(self.all_releases[i][0], "%m-%d-%Y") < TODAY_DATE:
                self.past_releases.append(self.all_releases[i])
            else:
                self.upcoming_releases.append(self.all_releases[i])

        self.upcoming_releases_ascending = self.upcoming_releases
        self.upcoming_releases_ascending.sort(key=lambda x: x[0])
        self.upcoming_releases_descending = self.upcoming_releases_ascending[::-1]

        self.past_releases_descending = self.past_releases
        self.past_releases_descending.sort(key=lambda x: x[0])
        self.past_releases_ascending = self.past_releases_descending[::-1]

        return self.upcoming_releases_ascending, self.upcoming_releases_descending, \
               self.past_releases_ascending, self.past_releases_descending

    def get_closest_releases(self):
        return self.upcoming_releases[0:3]

    def get_filter(self):
        response = requests.get(url=FILTER_RELEASES_URL)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table")
        headers = []

        for i in table.find_all("th"):
            title = i.text
            headers.append(title)

        self.filter_releases = pandas.DataFrame(columns=headers)

        for j in table.find_all("tr")[1:]:
            row_data = j.find_all("td")
            row = [i.text for i in row_data]
            length = len(self.filter_releases)
            self.filter_releases.loc[length] = row
        self.filter_releases = self.filter_releases.values.tolist()

    def filter_all_releases(self):
        pass
