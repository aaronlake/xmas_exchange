# Copyright (c) 2022 Aaron Lake
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""Christmas Exchange Generator

Usage:
    export TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXX
    export TWILIO_AUTH_TOKEN=YYYYYYYYYYYYYYYY
    export TWILIO_NUMBER=+1ZZZZZZZZZZZZZZ

    xmas_exchange.py --action create_table
    xmas_exchange.py --action add # Add people
    xmas_exchange.py --action assign # Assign people to make gifts for each other
    xmas_exchange.py --action clear_assignments # Clear all assignments
    # Send text messages to each person with their giftee
    xmas_exchange.py --action send_sms
"""
import argparse
import sqlite3
import random
import datetime
import os
from twilio.rest import Client

# Change this to your family name
FAMILY = "McLaxter"


def main():
    """Main function"""
    action = cli()
    match action:
        case "create_table":
            create_table()
        case "add":
            person = input_person()
            create_person(person)
        case "assign":
            assign_people()
        case "clear_assignments":
            clear_assignments()
        case "send_sms":
            send_sms()
        case _:
            print("Do something")


def cli():
    """Command line interface"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", help="WTF U WANNA DO")
    args = parser.parse_args()
    return args.action


def get_year():
    """Returns the current year"""
    now = datetime.datetime.now()
    return now.year


def create_table():
    """Create the database and table"""
    con = sqlite3.connect("exchange.db")
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS people (name TEXT, phone TEXT, \
                                            house TEXT, gifter TEXT, \
                                            giftee TEXT)")


def input_person():
    """Input a person"""
    people = []
    while True:
        name = input("Name [blank to stop adding]: ")
        if name == "":
            break
        phone = input("Phone: ")
        house = input("House: ")
        people.append({"name": name, "phone": phone, "house": house})
    return people


def create_person(people):
    """Create a person in the database"""
    con = sqlite3.connect("exchange.db")
    cur = con.cursor()
    for person in people:
        cur.execute(
            f"INSERT INTO people (name, phone, house) VALUES \
                ('{person['name']}', '{person['phone']}', '{person['house']}')")
    con.commit()


def get_gifter(name):
    """Returns the gifter for a person"""
    con = sqlite3.connect("exchange.db")
    cur = con.cursor()
    cur.execute(f"SELECT gifter FROM people WHERE name = '{name}'")
    gifter = cur.fetchone()
    return gifter[0]


def get_house(name):
    """Returns the house for a person"""
    con = sqlite3.connect("exchange.db")
    cur = con.cursor()
    cur.execute(f"SELECT house FROM people WHERE name = '{name}'")
    house = cur.fetchone()
    return house[0]


def assign_people():
    """Assign people to make gifts for each other"""
    con = sqlite3.connect("exchange.db")
    cur = con.cursor()
    cur.execute("SELECT name FROM people")
    people = cur.fetchall()

    for person in people:
        name = person[0]

        # Get a random person from the database that is not the current person,
        # gifter is null, and house is not the same
        cur.execute(
            f"SELECT name FROM people WHERE name != '{name}' \
                AND gifter IS NULL AND house != '{get_house(name)}'")
        giftee = cur.fetchall()
        giftee = random.choice(giftee)[0]

        # Assign the person a giftee
        cur.execute(
            f"UPDATE people SET giftee = '{giftee}' WHERE name = '{name}'")

        # Assign the giftee the person as their gifter
        cur.execute(
            f"UPDATE people SET gifter = '{name}' WHERE name = '{giftee}'")

    con.commit()


def clear_assignments():
    """Clears all gifter and giftee assignments"""
    con = sqlite3.connect("exchange.db")
    cur = con.cursor()
    cur.execute("UPDATE people SET gifter = NULL, giftee = NULL")
    con.commit()


def send_sms():
    """Sends a text message to each person with their giftee"""
    con = sqlite3.connect("exchange.db")
    cur = con.cursor()
    cur.execute("SELECT name, phone, giftee FROM people")
    people = cur.fetchall()

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    for person in people:
        name, phone, giftee = person
        message = client.messages \
                        .create(
                            body=f"Merry {FAMILY} Xmas {get_year()} {name}. This year you have been assigned to make a gift for: {giftee}!",
                            from_=os.environ['TWILIO_NUMBER'],
                            to=f"+1{phone}")
        print(message.sid)


if __name__ == "__main__":
    main()
