#! /bin/python3

import requests
import datetime
import re
import sqlite3

def main():
    db = sqlite3.connect("episodes.db")
    cursor = db.cursor()

    if update_db(cursor):
        db.commit()
    
    search_episode(cursor)
    
    db.close()


def update_db(cursor):
    latest_episode = check_latest_episode_in_db(cursor)
    url = "http://api.sr.se/api/v2/episodes/index?programid=2024&fromdate=2009-01-01&todate=2009-02-10&page=1&size=25&format=json"
    #url = "http://api.sr.se/api/v2/episodes/index?programid=2024&fromdate=" + str(latest_episode) + "&page=1&size=25&format=json"

    number_of_episodes = 0

    while True:
        break
        response = requests.get(url)
        json_response = response.json()
        insert_episodes_into_db(cursor, json_response["episodes"])
        number_of_episodes += int(json_response["pagination"]["size"])
        print(f"Uppdaterat databasen med {number_of_episodes} avsnitt totalt")
        try:
            url = json_response["pagination"]["nextpage"]
        except KeyError as identifier:
            print("No more pages")
            break
    if number_of_episodes:
        return True
    return False



def check_latest_episode_in_db(cursor):
    cursor.execute("SELECT published FROM episodes ORDER BY published DESC")
    try:
        latest_episode = convert_utc_to_date(cursor.fetchone()[0])
        print(f"Senast inlagda avsnittet är {latest_episode}")
    except TypeError as identifier:
        latest_episode = "2009-01-01"
        print(f"Inget avsnitt inlagt, använder 2009-01-04 för att fylla databasen")
    return latest_episode


def search_episode(cursor):
    search_term = input("Ange sökterm: ")
    print()
    terms = search_term.split()
    sql_string = f"SELECT * FROM episodes WHERE description LIKE '%{terms[0]}%'"
    for i in range(1, len(terms)):
        sql_string += f" AND description LIKE '%{terms[i]}%'"
    cursor.execute(sql_string)
    for row in cursor:
        print_episode(row)
        print()
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


def insert_episodes_into_db(cursor, episodes):
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

if __name__ == "__main__":
    main()
