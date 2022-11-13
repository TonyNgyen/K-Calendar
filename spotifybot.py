#https://selenium-python.readthedocs.io/locating-elements.html

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
import json
from releases import Releases

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