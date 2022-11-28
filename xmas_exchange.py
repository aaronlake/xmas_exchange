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
import re
import datetime
import os
from twilio.rest import Client

# Change this to your family name
FAMILY = "McLaxter"

TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']

con = sqlite3.connect("exchange.db")


def main():
    """Main function"""

    action = cli()
    match action:
        case "create_table":
            create_table()
        case "add":
            input_person()
        case "assign":
            assign_people()
        case "clear_assignments":
            clear_assignments()
        case "send_sms":
            send_sms()
        case _:
            print("Invalid action")


def db_update(sql):
    """Update the database"""
    con.cursor().execute(sql)
    con.commit()
    return True


def db_get(sql):
    """Get data from the database"""
    cur = con.cursor()
    return cur.execute(sql).fetchall()


def cli():
    """Command line interface"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action", help="Specify an action <create_table, add, assign, clear_assignments, send_sms>")
    args = parser.parse_args()
    return args.action


def get_year():
    """Returns the current year"""
    now = datetime.datetime.now()
    return now.year


def create_table():
    """Create the database and table"""
    db_update("CREATE TABLE IF NOT EXISTS people (name TEXT, phone TEXT, \
                                                  house TEXT, gifter TEXT, \
                                                  giftee TEXT)")


def input_person():
    """Input a person"""

    while True:
        name = input("Name [blank to stop adding]: ")
        if name == "":
            break

        while True:
            phone = input("Phone [ex 5553334444]: ")
            if re.match(r"^\d{10}$", phone):
                break
            print("Invalid phone number")

        house = input("House [ex Lakes]: ")

        db_update(f"INSERT INTO people (name, phone, house) VALUES \
                    ({name}, {phone}, {house})")


def assign_people():
    """Assign people to make gifts for each other"""

    people = db_get("SELECT name, house FROM people")

    for person in people:
        name, house = person

        # Get a random person from the database that is not the current person,
        # gifter is null, and house is not the same
        giftee = db_get(
            f"SELECT name FROM people WHERE name != '{name}' \
                AND gifter IS NULL AND house != '{house}'")
        giftee = random.choice(giftee)[0]

        # Assign the person a giftee
        db_update(
            f"UPDATE people SET giftee = '{giftee}' WHERE name = '{name}'")

        # Assign the giftee the person as their gifter
        db_update(
            f"UPDATE people SET gifter = '{name}' WHERE name = '{giftee}'")


def clear_assignments():
    """Clears all gifter and giftee assignments"""
    db_update("UPDATE people SET gifter = NULL, giftee = NULL")


def send_sms():
    """Sends a text message to each person with their giftee"""
    people = db_get("SELECT name, phone, giftee FROM people")
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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
