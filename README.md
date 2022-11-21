# K-Calendar
A web application that tracks the releases of future Kpop songs. Not a finished product, will be constantly updating.

Currently hosted on Heroku until Heroku is no longer free:
https://k-calendar.herokuapp.com
***
## General Info
 * All data about artists and their releases are taken from the Spotify API
 * HTML, CSS, Bootstrap, Jinja, Flask are all used to operate the actual web application
 * spotify.py is dedicated to interacting the Spotify API 
    * Uses API's data to update Data.JSON which acts as the data base for the web application
 * Beautiful Soup is used on Reddit and dbkpop to get the upcoming releases of the month
    * Reddit gets **all** Korean music releases while dbkpop is used to filter that data to get k-pop
## Future plans
 * Incorporate Javascript and React to make the web application more responsive/dynamic
 * Add News, Rankings, and Artist Information pages to add more uses to the web application
 * **Much later down the line:** Add a user system, so users can follow artists and track their releases specifically
