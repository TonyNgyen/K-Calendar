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


class Releases:

    def __init__(self):
        self.all_releases = None
        self.upcoming_releases = []
        self.past_releases = []

    def get_releases(self, date, url, request_headers):
        response = requests.get(url=url, headers=request_headers)
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
            # if datetime.datetime.strptime(row[0], "%Y-%m-%d") < date:
            #     length = len(self.past_releases)
            #     self.past_releases.loc[length] = row
            # else:
            #     length = len(self.upcoming_releases)
            #     self.upcoming_releases.loc[length] = row
        self.all_releases = self.all_releases.values.tolist()


        for i in range(len(self.all_releases)):
            if self.all_releases[i][0] != "":
                self.all_releases[i][0] = f"10-{self.all_releases[i][0][:-2]}-2022"
            else:
                self.all_releases[i][0] = self.all_releases[i - 1][0]

            if self.all_releases[i][1] == "" or self.all_releases[i][1] == "?":
                self.all_releases[i][1] = "N/A"

            if datetime.datetime.strptime(self.all_releases[i][0], "%m-%d-%Y") < date:
                self.past_releases.append(self.all_releases[i])
            else:
                self.upcoming_releases.append(self.all_releases[i])

    def get_closest_releases(self):
        return self.upcoming_releases[0:3]
