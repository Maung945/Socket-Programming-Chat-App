from cryptography.fernet import Fernet
import kyber
import os


def load_key():
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    # dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # Navigate up twice
    # key_path = os.path.join(dir_path, 'secret.key')
    # return open(key_path, "rb").read()
    #key_path = os.path.join(dir_path, 'Common', 'secret.key')
    #return open(key_path, "rb").read()
    #return open("Common/secret.key", "rb").read()
    pk, sk = kyber.Kyber512.keygen()
    return pk, sk

def encrypt_message(message, pk):
    # f = Fernet(key)
    # return f.encrypt(message.encode())
    c, key = kyber.Kyber512.enc(pk)
    return c, key


def decrypt_message(c, sk):
    # f = Fernet(key)
    # return f.decrypt(encrypted_message).decode()
    _key = kyber.Kyber512.dec(c, sk)
    return _key
