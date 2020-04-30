#! /bin/python3

import requests
import json
import datetime
import re
import sqlite3

def main():
    db = sqlite3.connect("episodes.db")
    cursor = db.cursor()
    cursor.execute("SELECT published FROM episodes ORDER BY published DESC")
    try:
        published = datetime.datetime.fromtimestamp(cursor.fetchone()[0])
        latest_episode = published.date()
        print(f"Senast inlagda avsnittet är {latest_episode}")
    except TypeError as identifier:
        latest_episode = "2009-01-01"
        print(f"Inget avsnitt inlagt, använder 2009-01-01 för att fylla databasen")

    print(latest_episode)

    url = "http://api.sr.se/api/v2/episodes/index?programid=2024&fromdate=" + str(latest_episode) + "&page=1&size=10&format=json"

    number_of_episodes = 0

    while url:
        response = requests.get(url)
        output = response.json()
        update_db(cursor, output["episodes"])
        number_of_episodes += int(output["pagination"]["size"])
        print(f"Uppdaterat databasen med {number_of_episodes} avsnitt totalt")
        try:
            url = output["pagination"]["nextpage"]
        except KeyError as identifier:
            print("No more pages")
            break
    
    db.commit()
    db.close()


def extract_date_from_string(utcdate):
    pattern = re.compile('\d{10}')
    match = pattern.search(utcdate)
    extracted_date = match.group()
    return extracted_date


def update_db(cursor, episodes):
    for episode in episodes:
        date = extract_date_from_string(episode['publishdateutc'])
        #print("Id: " + str(episode["id"]))
        #print("Titel: " + episode["title"])
        #print("Datum: " + date)
        #print("Beskrivning: " + episode["description"])
        #print()
        try:
            cursor.execute("INSERT INTO episodes(id, title, published, url, description) VALUES(?,?,?,?,?)",
                            (episode["id"], episode["title"], date, episode["url"], episode["description"]))
        except sqlite3.IntegrityError as identifier:
            pass


main()