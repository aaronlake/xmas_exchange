import json
import os
import base64
import hashlib


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


def lambda_handler(event, context):
    # Get the code from query parameters
    code = (
        event.get("queryStringParameters", {}).get("code", "").upper().strip()
    )
    if not code or len(code) != 4:
        return response(400, {"message": "Invalid code format."})

    # Load the encrypted assignments
    encrypted_assignments = load_encrypted_assignments()

    if code not in encrypted_assignments:
        return response(400, {"message": "Invalid code."})

    # Retrieve the encryption key from environment variables
    encryption_key = os.environ["ENCRYPTION_KEY"]

    try:
        encrypted_data = encrypted_assignments[code]
        giftee = decrypt(encrypted_data, encryption_key)
    except Exception as e:
        print(f"Decryption error: {e}")
        return response(500, {"message": "Internal server error."})

    return response(200, {"giftee": giftee})


def load_encrypted_assignments():
    # Load from the local file packaged with the Lambda function
    with open("encrypted_assignments.json", "r") as file:
        return json.load(file)


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # Enable CORS
        },
        "body": json.dumps(body),
    }
