# Xmas Gift Exchange

## Description

This is a simple app that allows you to create a gift exchange for a group of
people. It is designed to be used for a secret Santa type of gift exchange. It
is not a full-featured app, but it does the job.

## Requirements

This app requires the following:

- Python 3.8+
- An active Twilio account
- A Twilio phone number

## Usage

```
export TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXX
export TWILIO_AUTH_TOKEN=YYYYYYYYYYYYYYYY
export TWILIO_NUMBER=+1ZZZZZZZZZZZZZZ

xmas_exchange.py --action create_table
xmas_exchange.py --action add # Add people
xmas_exchange.py --action assign # Assign people to make gifts for each other
xmas_exchange.py --action clear_assignments # Clear all assignments
xmas_exchange.py --action send_sms # Send text messages to each person with their giftee
```
