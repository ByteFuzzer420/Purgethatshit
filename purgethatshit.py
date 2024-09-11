import os
import shutil
import random
import string
from Crypto.Cipher import AES, Blowfish
from Crypto.Random import get_random_bytes
from multiprocessing import Pool, cpu_count

def generate_random_key(length):
    return get_random_bytes(length)

def generate_random_name(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def encrypt_aes(data, key):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return nonce + tag + ciphertext

def decrypt_aes(encrypted_data, key):
    nonce = encrypted_data[:16]
    tag = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
    return decrypted_data

def encrypt_blowfish(data, key):
    cipher = Blowfish.new(key, Blowfish.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return nonce + tag + ciphertext

def decrypt_blowfish(encrypted_data, key):
    nonce = encrypted_data[:8]
    tag = encrypted_data[8:16]
    ciphertext = encrypted_data[16:]
    cipher = Blowfish.new(key, Blowfish.MODE_EAX, nonce=nonce)
    decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
    return decrypted_data

def rename_files_and_folders(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for filename in files:
            file_path = os.path.join(root, filename)
            new_name = generate_random_name()
            os.rename(file_path, os.path.join(root, new_name))

        for folder in dirs:
            folder_path = os.path.join(root, folder)
            new_name = generate_random_name()
            os.rename(folder_path, os.path.join(root, new_name))

def process_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
        aes_key = generate_random_key(16)
        blowfish_key = generate_random_key(16)
        encrypted_aes = encrypt_aes(file_content, aes_key)
        encrypted_aes_key = encrypt_blowfish(aes_key, blowfish_key)

        with open(file_path, 'wb') as f:
            f.write(encrypted_aes_key + encrypted_aes)
          
        os.remove(file_path)
        print(f"File '{file_path}' shredded and deleted.")
    except Exception as e:
        print(f"An error occurred for file '{file_path}': {e}")

def shred_files(directory):
    try:
        rename_files_and_folders(directory)

        files_to_process = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                files_to_process.append(file_path)

        num_processes = min(cpu_count(), 4)
        with Pool(num_processes) as pool:
            pool.map(process_file, files_to_process)

        print("All files shredded and deleted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    user_directory = input("Enter the directory path: ")
    
    if os.path.exists(user_directory) and os.path.isdir(user_directory):
        shred_files(user_directory)
    else:
        print("Invalid directory path. Please provide a valid directory.")
