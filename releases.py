from bs4 import BeautifulSoup
import requests
import pandas
import datetime

TODAY_DATE = datetime.datetime.today()
UPCOMING_RELEASES_URL = "https://www.reddit.com/r/kpop/wiki/upcoming-releases/2022/october/"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
FILTER_RELEASES_URL = "https://dbkpop.com/2022/09/01/october-2022-k-pop-comebacks-and-debuts/"

class Releases:

    def __init__(self):
        self.all_releases = None
        self.upcoming_releases = []
        self.past_releases = []
        self.filter = []
        self.filtered_releases = []
        self.upcoming_releases_ascending = []
        self.upcoming_releases_descending = []
        self.past_releases_ascending = []
        self.past_releases_descending = []

    def get_releases(self):
        self.get_filter()
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

            if self.all_releases[i][2].casefold() in self.filter:
                self.filtered_releases.append(self.all_releases[i])
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

        self.filter = pandas.DataFrame(columns=headers)

        for j in table.find_all("tr")[1:]:
            row_data = j.find_all("td")
            row = [i.text for i in row_data]
            row[1] = row[1].casefold()
            length = len(self.filter)
            self.filter.loc[length] = row

        self.filter = self.filter.loc[:, "Artist"].tolist()
