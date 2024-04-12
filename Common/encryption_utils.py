from cryptography.fernet import Fernet
import os


def load_key():
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # Navigate up twice
    key_path = os.path.join(dir_path, 'secret.key')
    return open(key_path, "rb").read()
    #key_path = os.path.join(dir_path, 'Common', 'secret.key')
    #return open(key_path, "rb").read()
    #return open("Common/secret.key", "rb").read()

def encrypt_message(message, key):
    f = Fernet(key)
    return f.encrypt(message.encode())

def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    return f.decrypt(encrypted_message).decode()