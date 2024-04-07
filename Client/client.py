import sys
import os
import socket
import threading
import re
from ui import ChatUI  

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_path = os.path.join(project_dir, 'Common')
sys.path.append(common_path)
from encryption_utils import encrypt_message, decrypt_message, load_key

HOST = '127.0.0.1'
PORT = 12312

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def add_message(message):
    global chat_ui
    chat_ui.add_message(message)

def connect():
    username = chat_ui.get_username()
    username_pattern = re.compile(r'^[a-zA-Z]{3}-\d{2}$')

    if username_pattern.match(username):
        try:
            client.connect((HOST, PORT))
            print("Successfully connected to server")
            add_message("Successfully connected to the server")
        except Exception as e:
            chat_ui.show_error("Unable to connect to server", f"Unable to connect to server {HOST} {PORT}: {e}")
            return

        client.sendall(username.encode())
        threading.Thread(target=listen_for_messages_from_server, args=(client,)).start()
        chat_ui.disable_username_input()
    else:
        chat_ui.show_error("Invalid username", "Username format should be 3 alphabets, one '-', and two numbers")

def send_message():
    message = chat_ui.get_message()
    if message != '':
        print('send_message():' + message)
        key = load_key()
        encrypted_message = encrypt_message(message, key)
        client.sendall(encrypted_message)
        #client.sendall(message.encode())
        chat_ui.clear_message_textbox()
    else:
        chat_ui.show_error("Empty message", "Message cannot be empty")

def exit_chat():
    client.close()
    chat_ui.root.destroy()

def listen_for_messages_from_server(client_socket):
    key = load_key()  # Load the key
    while True:
        try:
            encrypted_message = client_socket.recv(2048)
            if encrypted_message:
                message = decrypt_message(encrypted_message, key)
                print(message)  # It's now decrypted and readable
                #add_message(message)
                if ',' in message:
                    timestamp, username, content = message.split(',',2)  # Split only once
                    formatted_message = f"[{timestamp}] [{username}] {content}"
                    #add_message(f"[{timestamp}] [{username}] {content}")
                else:
                    formatted_message = f"[SERVER] {message}"
                    #add_message(f"[SERVER] {message}")
                add_message(formatted_message)
            else:
                chat_ui.show_error("Error", "Disconnected from server")
                break
        except Exception as e:
            print("Error receiving message: ", e)
            break

if __name__ == '__main__':
    chat_ui = ChatUI(connect, send_message, exit_chat)
    chat_ui.mainloop()