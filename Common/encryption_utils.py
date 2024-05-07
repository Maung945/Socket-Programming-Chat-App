from cryptography.fernet import Fernet
from .kyber import *


def load_key():
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    # dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # Navigate up twice
    # key_path = os.path.join(dir_path, 'secret.key')
    # return open(key_path, "rb").read()
    #key_path = os.path.join(dir_path, 'Common', 'secret.key')
    #return open(key_path, "rb").read()
    #return open("Common/secret.key", "rb").read()
    pk, sk = Kyber512.keygen()
    return pk, sk

def encrypt_message(message, pk):
    # f = Fernet(key)
    # return f.encrypt(message.encode())
    c, pk = Kyber512.enc(message)
    return c, pk


def decrypt_message(c, sk):
    # f = Fernet(key)
    # return f.decrypt(encrypted_message).decode()
    _key = Kyber512.dec(c, sk)
    return _key
