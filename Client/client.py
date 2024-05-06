import socket
import threading
import re
import os
import sys
import time
import emoji

#Import functions and classes from your modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from Common.encryption_utils import encrypt_message, decrypt_message, load_key
from Common.Packet import LitProtocolPacket
from ui import ChatUI  

stop_event = threading.Event()

HOST = '127.0.0.1'
PORT = 12345

def add_message(message):
    global chat_ui
    chat_ui.add_message(message)

def connect():
    global client
    username = chat_ui.get_username()
    username_pattern = re.compile(r'^[a-zA-Z]{3}-\d{2}$')

    if username_pattern.match(username):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1.0)
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
    print("Sending message...")  #Debugging statement...

    #Sample values
    message_type = b'\x00\x00'                                      #0x00 = TEXT MESSAGE, 0x01 = IMAGE, 0x02 = GENERIC FILE (subject to change)...
    message_options_flags = b'\x00\x01'                             #0x00 = NO ENCRYPTION, 0x01 = ENCRYPTION...
    message_message_id = os.urandom(8)                              #For other features maybe...
    message_iv = os.urandom(16)                                     #Dummy IV, for when we implement encryption...  
    key = load_key()                                                #Load up the s3cr3t key...
    print('send_message():' + chat_ui.get_message())                #Debug line before encryption...
    
    #Encode message with emoji support
    message_text = chat_ui.get_message()
    message_text_with_emoji = emoji.emojize(message_text)
    
    message_payload = encrypt_message(message_text_with_emoji, key)   #Fetch message and encrypt it using the s3cr3t key...
    message_hmac = os.urandom(32)                                     #Dummy HMAC, for when we implement encryption...
    
    #Creating the LitProtocolPacket object...
    message_packet = LitProtocolPacket(
        message_type=message_type,
        options_flags=message_options_flags,
        message_id=message_message_id,
        iv=message_iv,
        hmac=message_hmac,
        payload=message_payload  #Serializing the payload to a byte string for TCP transmission...
    )        
    
    print('send_message():' + str(message_packet.payload)) #Debug line after encryption...
    if message_packet.payload.decode() != '':
        try:
            client.sendall(LitProtocolPacket.encodePacket(message_packet))
            print("Message sent successfully.")  #Debugging statement...
            chat_ui.clear_message_textbox()
        except OSError as e:
            if e.errno == 9:  #Bad file descriptor...
                print("")
            else:
                print(f"Unexpected error: {e}")
        except Exception as e:
            print(f"Error sending message: {e}")  #Debugging statement...
            chat_ui.show_error("Send Error", f"Error sending message: {e}")
        
    else:
        chat_ui.show_error("Empty message", "Message cannot be empty")


def exit_chat():
    #Signal the listening thread to stop...
    stop_event.set()
    time.sleep(0.1) 
    #Close the client socket...
    client.close()
    #Destroy the UI...
    chat_ui.root.destroy()


def listen_for_messages_from_server(client_socket):
    key = load_key()  #Load the key...
    while not stop_event.is_set():
        try:
            data = client_socket.recv(2048)
            if not data:
                print("Server closed connection or no data received.")
                break
            message_packet = LitProtocolPacket.decodePacket(data)
            if(message_packet.options_flags == b'\x00\x03'):
                #Close the client socket...
                client.close()
        
            print(message_packet.payload)
            message = decrypt_message(message_packet.payload, key) #Decoding and decrypting message...
            print("from server decrypted:" + message)
            #Process the message as before...
            if message:
                if ',' in message:
                    print(message)
                    timestamp, username, content = message.split(',',2) 
                    add_message(f"[{timestamp}] [{username}] {content}")
                else:
                    add_message(f"[SERVER] {message}")
        except socket.timeout:
            continue
        except (OSError, ConnectionResetError) as e:
            if e.errno == 9:  # Bad file descriptor...
                print("Socket has been closed, exiting listener.")
                break
            else:
                print(f"Unexpected error: {e}")
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

if __name__ == '__main__':
    chat_ui = ChatUI(connect, send_message, exit_chat)
    chat_ui.mainloop()
