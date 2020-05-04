#! /bin/python3

import requests
import datetime
import re
import sqlite3

def main():
    db = sqlite3.connect("episodes.db")
    cursor = db.cursor()

    if ask_for_upgrade(cursor) and update_db(cursor):
        print("committing changes to db")
        db.commit()

    while search_episode(cursor):
        pass
    
    db.close()

def ask_for_upgrade(cursor):
    latest_episode = check_latest_episode_in_db(cursor)
    answer = input(f"Vill du uppdatera databasen? Senaste inlagda avsnittet är {latest_episode} (j/n): ")
    if answer.lower() == "j":
        return True
    return False

def update_db(cursor):
    latest_episode = check_latest_episode_in_db(cursor)
    latest_episode += datetime.timedelta(days=1)
    url = "http://api.sr.se/api/v2/episodes/index?programid=2024&fromdate=" + str(latest_episode) + "&page=1&size=25&format=json"

    number_of_episodes = 0

    while True:
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
    except TypeError as identifier:
        latest_episode = "2009-01-01"
        print(f"Inget avsnitt inlagt, använder 2009-01-04 för att fylla databasen")
    return latest_episode


def search_episode(cursor):
    search_term = ""
    while len(search_term) < 3:
        search_term = input("Ange sökterm (min 3 bokstäver): ")
        if len(search_term) == 0:
            return False
        
    print()
    terms = search_term.split()

    sql_string = f"SELECT * FROM episodes WHERE description LIKE '%{terms[0]}%'"
    for i in range(1, len(terms)):
        sql_string += f" AND description LIKE '%{terms[i]}%'"
    
    cursor.execute(sql_string)
    number_of_results = 0

    for row in cursor:
        print_episode(row)
        number_of_results += 1
        print()
    print(f"Totalt antal träffar: {number_of_results}")
    return True
    


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
        try:
            cursor.execute("INSERT INTO episodes(id, title, published, url, description) VALUES(?,?,?,?,?)",
                            (episode["id"], episode["title"], date, episode["url"], episode["description"]))
        except sqlite3.IntegrityError as identifier:
            pass

if __name__ == "__main__":
    main()
