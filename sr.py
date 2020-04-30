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
        latest_episode = convert_utc_to_date(cursor.fetchone()[0])
        print(f"Senast inlagda avsnittet är {latest_episode}")
    except TypeError as identifier:
        latest_episode = "2009-01-01"
        print(f"Inget avsnitt inlagt, använder 2009-01-04 för att fylla databasen")

    url = "http://api.sr.se/api/v2/episodes/index?programid=2024&fromdate=2009-01-01&todate=2009-02-10&page=1&size=10&format=json"
    #url = "http://api.sr.se/api/v2/episodes/index?programid=2024&fromdate=" + str(latest_episode) + "&page=1&size=10&format=json"

    number_of_episodes = 0

    while url:
        break
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
    
    search_episode(cursor)
    
    db.commit()
    db.close()

def search_episode(cursor):
    search_term = input("Ange sökterm: ")
    print()
    terms = search_term.split()
    
    cursor.execute(f"SELECT * FROM episodes WHERE description LIKE '%{search_term}%'")
    for row in cursor:
        print_episode(row)
        print()


def print_episode(episode_info):
    print(f"Titel: {episode_info[1]}")
    print(f"Datum: {convert_utc_to_date(episode_info[2])}")
    print(f"Länk: {episode_info[3]}")
    print(f"Beskrivning: {episode_info[4]}")


def extract_date_from_string(date_string):
    pattern = re.compile('\d{10}')
    match = pattern.search(date_string)
    extracted_date = match.group()
    return extracted_date


def convert_utc_to_date(utcdate):
    human_date = datetime.datetime.fromtimestamp(int(utcdate))
    return human_date.date()


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