# Copyright (c) 2022 Aaron Lake
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""Christmas Exchange Generator"""

import os
import csv
import random
import string
import json
import sys
import base64
import hashlib


def read_and_validate_csv(filename):
    participants = []
    try:
        with open(filename, mode="r") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                name = row.get("name", "").strip()
                house = row.get("house", "").strip()
                if not name or not house:
                    raise ValueError(
                        "All participants must have a name and a house."
                    )
                participants.append({"name": name, "house": house})
    except FileNotFoundError:
        print(f"File {filename} not found.")
        sys.exit(1)
    return participants


def assign_giftees(participants):
    max_attempts = 1000
    for attempt in range(max_attempts):
        givers = participants.copy()
        giftees = participants.copy()
        random.shuffle(giftees)
        assignments = {}
        success = True

        for giver in givers:
            valid_giftees = [
                giftee
                for giftee in giftees
                if giftee["house"] != giver["house"]
                and giftee["name"] != giver["name"]
            ]
            if not valid_giftees:
                success = False
                break
            chosen_giftee = random.choice(valid_giftees)
            assignments[giver["name"]] = chosen_giftee["name"]
            giftees.remove(chosen_giftee)

        if success:
            return assignments
    raise Exception(
        "Failed to assign giftees without violating house constraints after multiple attempts."
    )


def generate_unique_codes(participants):
    codes = {}
    used_codes = set()
    characters = string.ascii_uppercase + string.digits
    for participant in participants:
        while True:
            code = "".join(random.choices(characters, k=4))
            if code not in used_codes:
                used_codes.add(code)
                codes[participant["name"]] = code
                break
    return codes


def generate_keystream(key, length):
    # Generate a keystream of the required length using SHA256
    keystream = b""
    counter = 0
    while len(keystream) < length:
        data = key.encode() + counter.to_bytes(4, "big")
        hash = hashlib.sha256(data).digest()
        keystream += hash
        counter += 1
    return keystream[:length]


def encrypt(data, key):
    data_bytes = data.encode("utf-8")
    keystream = generate_keystream(key, len(data_bytes))
    encrypted_bytes = bytes(a ^ b for (a, b) in zip(data_bytes, keystream))
    return base64.urlsafe_b64encode(encrypted_bytes).decode("utf-8")


def main():
    # Step 1: Read and validate CSV input
    filename = "participants.csv"
    participants = read_and_validate_csv(filename)

    # Step 2: Randomly assign giftees with house constraints
    assignments = assign_giftees(participants)

    # Step 3: Generate unique participant codes
    codes = generate_unique_codes(participants)

    # Step 4: Encrypt the matches and save to encrypted JSON
    encryption_key = "".join(
        random.choices(string.ascii_letters + string.digits, k=12)
    )

    encrypted_assignments = {}
    for name, giftee in assignments.items():
        code = codes[name]
        encrypted_data = encrypt(giftee, encryption_key)
        encrypted_assignments[code] = encrypted_data

    # Save encrypted data to JSON
    with open("encrypted_assignments.json", "w") as file:
        json.dump(encrypted_assignments, file)

    # Save codes to a JSON file for validation or future reference (optional)
    with open("codes.json", "w") as file:
        json.dump(codes, file)

    # Step 5: Output participant names and codes to the CLI
    print("\nParticipant Codes:")
    for name, code in codes.items():
        print(f"Participant: {name}, Code: {code}")

    # Save the encryption key securely (do NOT store in code or commit to version control)
    with open("encryption_key.txt", "w") as file:
        file.write(encryption_key)
    print(
        "\nEncryption key saved to 'encryption_key.txt'. Keep this file secure."
    )


if __name__ == "__main__":
    main()
