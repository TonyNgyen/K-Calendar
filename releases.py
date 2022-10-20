from bs4 import BeautifulSoup
import requests
import pandas
import datetime


class Releases:

    def __init__(self):
        self.upcoming_releases = None
        self.past_releases = None

    def get_releases(self, date, url):
        response = requests.get(url=url)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table")
        headers = []

        for i in table.find_all("th"):
            title = i.text
            headers.append(title)

        self.upcoming_releases = pandas.DataFrame(columns=headers)
        self.past_releases = pandas.DataFrame(columns=headers)

        for j in table.find_all("tr")[1:]:
            row_data = j.find_all("td")
            row = [i.text for i in row_data]
            if datetime.datetime.strptime(row[0], "%Y-%m-%d") < date:
                length = len(self.past_releases)
                self.past_releases.loc[length] = row
            else:
                length = len(self.upcoming_releases)
                self.upcoming_releases.loc[length] = row

    def get_closest_releases(self):
        return self.upcoming_releases.iloc[0:3]

