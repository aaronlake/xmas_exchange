# Copyright (c) 2022 Aaron Lake
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""Christmas Exchange Generator"""

import csv
import random
import string
import json
import sys
import base64
import hashlib


def read_and_validate_csv(filename):
    """
    Reads participant data from a CSV file and validates the entries to ensure
    each participant has a name and a house. This function returns a list of
    dictionaries representing the participants, where each dictionary contains
    the participant's name and house.

    Args:
        filename (str): The path to the CSV file containing participant data.

    Returns:
        list: A list of dictionaries, each containing the "name" and "house"
        of a participant.

    Raises:
        ValueError: If any participant entry is missing a name or house.
    """

    participants = []
    try:
        with open(filename, mode="r", encoding="utf-8") as file:
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
    """
    Assigns giftees to participants while ensuring that no participant is
    assigned to someone from their own house or themselves. The function
    attempts to create valid assignments up to a specified number of attempts,
    shuffling the giftees each time to find a suitable configuration.

    Args:
        participants (list): A list of dictionaries representing participants,
        where each dictionary contains at least a "name" and "house" key.

    Returns:
        dict: A dictionary mapping each giver's name to their assigned
        giftee's name.

    Raises:
        Exception: If it fails to assign giftees without violating constraints
        after multiple attempts.
    """

    max_attempts = 1000
    for _ in range(max_attempts):
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
        "Failed to assign giftees without violating house constraints "
        + "after multiple attempts."
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
    """
    Generates a keystream based on a given key and the desired length. This
    keystream is created by hashing the combination of the key and a counter,
    ensuring a unique output for each increment of the counter.

    Args:
        key (str): The key used to generate the keystream.
        length (int): The desired length of the keystream in bytes.

    Returns:
        bytes: A bytes object containing the generated keystream of the
        specified length.
    """

    keystream = b""
    counter = 0
    while len(keystream) < length:
        data = key.encode() + counter.to_bytes(4, "big")
        data_hash = hashlib.sha256(data).digest()
        keystream += data_hash
        counter += 1
    return keystream[:length]


def encrypt(data, key):
    """
    Encrypts the provided data using a specified key through a XOR operation
    with a generated keystream. The resulting encrypted data is then encoded
    in a URL-safe base64 format for safe transmission.

    Args:
        data (str): The plaintext data to be encrypted.
        key (str): The key used to generate the keystream for encryption.

    Returns:
        str: The encrypted data encoded in a URL-safe base64 format.
    """

    data_bytes = data.encode("utf-8")
    keystream = generate_keystream(key, len(data_bytes))
    encrypted_bytes = bytes(a ^ b for (a, b) in zip(data_bytes, keystream))
    return base64.urlsafe_b64encode(encrypted_bytes).decode("utf-8")


def main():
    """
    The main function orchestrates the process of reading participant data,
    assigning giftees, and encrypting the assignments. It generates unique
    codes for each participant and saves the encrypted data along with the
    codes and encryption key to respective files.

    This function performs the following steps:
    1. Reads and validates participant data from a CSV file.
    2. Assigns giftees to participants.
    3. Generates unique codes for each participant.
    4. Creates a random encryption key and encrypts the giftee assignments.
    5. Saves the encrypted assignments and codes to JSON files and the
    encryption key to a text file.

    Returns:
        None
    """

    filename = "participants.csv"
    participants = read_and_validate_csv(filename)
    assignments = assign_giftees(participants)
    codes = generate_unique_codes(participants)

    encryption_key = "".join(
        random.choices(string.ascii_letters + string.digits, k=12)
    )

    encrypted_assignments = {}
    for name, giftee in assignments.items():
        code = codes[name]
        encrypted_data = encrypt(giftee, encryption_key)
        encrypted_assignments[code] = encrypted_data

    with open("encrypted_assignments.json", "w", encoding="utf-8") as file:
        json.dump(encrypted_assignments, file)

    with open("codes.json", "w", encoding="utf-8") as file:
        json.dump(codes, file)

    print("\nParticipant Codes:")
    for name, code in codes.items():
        print(f"Participant: {name}, Code: {code}")

    with open("encryption_key.txt", "w", encoding="utf-8") as file:
        file.write(encryption_key)
    print("\nEncryption key saved to 'encryption_key.txt'.")


if __name__ == "__main__":
    main()
