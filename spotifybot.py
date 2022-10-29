#https://selenium-python.readthedocs.io/locating-elements.html

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
import json
from releases import Releases


# class Releases:

#     def __init__(self):
#         self.all_releases = None
#         self.upcoming_releases = []
#         self.past_releases = []

#     def get_releases(self, date, url, request_headers):
#         response = requests.get(url=url, headers=request_headers)
#         soup = BeautifulSoup(response.content, "html.parser")
#         table = soup.find("table")
#         headers = []

#         for i in table.find_all("th"):
#             title = i.text
#             headers.append(title)

#         self.all_releases = pandas.DataFrame(columns=headers)

#         for j in table.find_all("tr")[1:]:
#             row_data = j.find_all("td")
#             row = [i.text for i in row_data]
#             length = len(self.all_releases)
#             self.all_releases.loc[length] = row
#             # if datetime.datetime.strptime(row[0], "%Y-%m-%d") < date:
#             #     length = len(self.past_releases)
#             #     self.past_releases.loc[length] = row
#             # else:
#             #     length = len(self.upcoming_releases)
#             #     self.upcoming_releases.loc[length] = row
#         self.all_releases = self.all_releases.values.tolist()


#         for i in range(len(self.all_releases)):
#             if self.all_releases[i][0] != "":
#                 self.all_releases[i][0] = f"10-{self.all_releases[i][0][:-2]}-2022"
#             else:
#                 self.all_releases[i][0] = self.all_releases[i - 1][0]

#             if self.all_releases[i][1] == "" or self.all_releases[i][1] == "?":
#                 self.all_releases[i][1] = "N/A"

#             if datetime.datetime.strptime(self.all_releases[i][0], "%m-%d-%Y") < date:
#                 self.past_releases.append(self.all_releases[i])
#             else:
#                 self.upcoming_releases.append(self.all_releases[i])

#     def get_closest_releases(self):
#         return self.upcoming_releases[0:3]


# TODAY_DATE = datetime.datetime.today()
# UPCOMING_RELEASES_URL = "https://www.reddit.com/r/kpop/wiki/upcoming-releases/2022/october/"
# headers = {'User-Agent': 'Mozilla/5.0'}

# release = Releases()

# release.get_releases(date=TODAY_DATE, request_headers=headers, url=UPCOMING_RELEASES_URL)

release = Releases()

release.get_releases()

chrome_driver_path = "/Users/tony/Documents/Development/chromedriver"

ser = Service(chrome_driver_path)
driver = webdriver.Chrome(service=ser)

for element in release.filtered_releases:
    driver.get("https://open.spotify.com/search")

    time.sleep(0.5)

    search = driver.find_element(by="tag name", value="input")

    artist_name = element[2]

    search.send_keys(artist_name, Keys.ENTER)

    time.sleep(1.5)

    artist_card = driver.find_elements(by="class name", value="Nqa6Cw3RkDMV8QnYreTr")

    if len(artist_card) == 0:
        saved_name = artist_name
        saved_url = "NOT FOUND"
        saved_img = "NOT FOUND"
        new_data = {
            saved_name: {
                "spotify url": saved_url,
                "img": saved_img,
            }
        }

    else:
        time.sleep(2)

        artist_card[0].click()

        time.sleep(1.5)

        driver.refresh()

        time.sleep(1.5)

        meta = driver.find_elements(by="tag name", value="meta")

        url = driver.current_url

        for element in meta:
            if element.get_attribute("property") == "og:image":
                img_link = element.get_attribute("content")

        saved_name = artist_name
        saved_url = url
        saved_img = img_link
        new_data = {
            saved_name: {
                "spotify url": saved_url,
                "img": saved_img,
            }
        }


    try:
        with open("static/images/card/Data.json", "r") as data_file:
            data = json.load(data_file)
            data.update(new_data)
    except FileNotFoundError:
        with open("static/images/card/Data.json", "w") as data_file:
            json.dump(data, data_file, indent=4)
    else:
        data.update(new_data)
        with open("static/images/card/Data.json", "w") as data_file:
            json.dump(data, data_file, indent=4)

driver.close()