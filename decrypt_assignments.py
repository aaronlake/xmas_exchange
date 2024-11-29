import json
import base64
import hashlib
import csv


def generate_keystream(key, length):
    # Generate a keystream of the required length using SHA256
    keystream = b""
    counter = 0
    while len(keystream) < length:
        data = key.encode("utf-8") + counter.to_bytes(4, "big")
        hash_digest = hashlib.sha256(data).digest()
        keystream += hash_digest
        counter += 1
    return keystream[:length]


def decrypt(encrypted_data, key):
    encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode("utf-8"))
    keystream = generate_keystream(key, len(encrypted_bytes))
    decrypted_bytes = bytes(
        a ^ b for (a, b) in zip(encrypted_bytes, keystream)
    )
    return decrypted_bytes.decode("utf-8")


def main():
    # Load the encryption key
    with open("encryption_key.txt", "r") as file:
        encryption_key = file.read()

    # Load the encrypted assignments
    with open("encrypted_assignments.json", "r") as file:
        encrypted_assignments = json.load(file)

    # Load the codes mapping
    with open("codes.json", "r") as file:
        codes = json.load(file)

    # Reverse the codes mapping to get code to participant name
    code_to_name = {code: name for name, code in codes.items()}

    # Load participants data
    participants = {}
    with open("participants.csv", mode="r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            name = row["name"].strip()
            house = row["house"].strip()
            participants[name] = house

    # Decrypt the assignments
    decrypted_assignments = {}
    for code, encrypted_giftee in encrypted_assignments.items():
        try:
            giver_name = code_to_name.get(code, "Unknown")
            giftee_name = decrypt(encrypted_giftee, encryption_key)
            decrypted_assignments[giver_name] = giftee_name
        except Exception as e:
            print(f"Error decrypting code {code}: {e}")

    # Validate the assignments
    print("\nValidating Assignments...\n")
    valid = True
    for giver, giftee in decrypted_assignments.items():
        giver_house = participants.get(giver, "Unknown")
        giftee_house = participants.get(giftee, "Unknown")
        if giver == giftee:
            print(f"Validation Error: {giver} is assigned to themselves.")
            valid = False
        if giver_house == giftee_house:
            print(
                f"Validation Error: {giver} and {giftee} are from the same house ({giver_house})."
            )
            valid = False

    if valid:
        print("All assignments are valid.\n")
    else:
        print("There were validation errors.\n")

    # Print the decrypted assignments
    print("Decrypted Assignments:")
    for giver, giftee in decrypted_assignments.items():
        print(f"Giver: {giver}, Giftee: {giftee}")


if __name__ == "__main__":
    main()
