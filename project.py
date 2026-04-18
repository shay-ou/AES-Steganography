from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from PIL import Image

key = b'1234567890123456'

# AES Encryption
def encrypt(message):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pad(message.encode(), 16))

# AES Decryption
def decrypt(ciphertext):
    cipher = AES.new(key, AES.MODE_ECB)
    return unpad(cipher.decrypt(ciphertext), 16).decode()

# Convert string to binary
def to_binary(data):
    return ''.join(format(ord(i), '08b') for i in data)

# ================= EMBED =================
def embed(image_path, message, output):
    img = Image.open(image_path).convert("RGB")

    # Store message length (32 bits) + message
    msg_len = format(len(message), '032b')
    binary_msg = msg_len + to_binary(message)

    data = list(img.getdata())

    # Safety check
    if len(binary_msg) > len(data) * 3:
        print("Message too large for this image!")
        return

    new_data = []
    msg_index = 0

    for pixel in data:
        r, g, b = pixel

        if msg_index < len(binary_msg):
            r = (r & ~1) | int(binary_msg[msg_index])
            msg_index += 1

        if msg_index < len(binary_msg):
            g = (g & ~1) | int(binary_msg[msg_index])
            msg_index += 1

        if msg_index < len(binary_msg):
            b = (b & ~1) | int(binary_msg[msg_index])
            msg_index += 1

        new_data.append((r, g, b))

    img.putdata(new_data)
    img.save(output)
    print("Embedded Successfully!")

# ================= EXTRACT =================
def extract(image_path):
    img = Image.open(image_path).convert("RGB")

    data = list(img.getdata())
    binary_data = ""

    for pixel in data:
        r, g, b = pixel
        binary_data += str(r & 1)
        binary_data += str(g & 1)
        binary_data += str(b & 1)

    # Get message length (first 32 bits)
    msg_len = int(binary_data[:32], 2)

    # Extract message bits
    msg_bits = binary_data[32:32 + (msg_len * 8)]

    # Convert to string
    message = ""
    for i in range(0, len(msg_bits), 8):
        byte = msg_bits[i:i+8]
        message += chr(int(byte, 2))

    return message

# ================= MAIN =================
secret = "Hello Rajnandini!"

# Encrypt
encrypted = encrypt(secret)

# Convert encrypted data to hex string
enc_str = encrypted.hex()

# Embed into image
embed("input.png", enc_str, "stego.png")

# Extract from image
extracted = extract("stego.png")

# Convert back to bytes
extracted_bytes = bytes.fromhex(extracted)

# Decrypt
original = decrypt(extracted_bytes)

print("Recovered Message:", original)