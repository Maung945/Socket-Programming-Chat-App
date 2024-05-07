from cryptography.fernet import Fernet
import os

def generate_key():
    key = Fernet.generate_key()
    # with open('secret.key', 'wb') as key_file:
    #     key_file.write(key)
    parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    file_path = os.path.join(parent_directory, 'secret.key')
    with open(file_path, 'wb') as key_file:
        key_file.write(key)
        
if __name__ == "__main__":
    generate_key()