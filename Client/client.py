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
import Common.kyber as kyber
from ui import ChatUI  

stop_event = threading.Event()

HOST = '127.0.0.1'
PORT = 12348
GLOBAL_USERNAME_TEST = "TEST"
global shared_secret
global client
client = None

def add_message(message):
    global chat_ui
    chat_ui.add_message(message)

def connect():
    
    username = chat_ui.get_username()
    username_pattern = re.compile(r'^[a-zA-Z]{3}-\d{2}$')

    if username_pattern.match(username):
        try:
            global client
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1.0)
            client.connect((HOST, PORT))
            print("Successfully connected to server")
            add_message("Successfully connected to the server")
        except Exception as e:
            chat_ui.show_error("Unable to connect to server", f"Unable to connect to server {HOST} {PORT}: {e}")
            return

        init_packet = LitProtocolPacket.generateTextMessage("ASD".encode())
        client.sendall(LitProtocolPacket.encodePacket(init_packet))

       
        threading.Thread(target=listen_for_messages_from_server, args=(client,username)).start()
        print("Listening thread started...\n")
        chat_ui.disable_username_input()
    else:
        chat_ui.show_error("Invalid username", "Username format should be 3 alphabets, one '-', and two numbers")


def exit_chat():
    #Signal the listening thread to stop...
    stop_event.set()
    time.sleep(0.1) 
    #Destroy the UI...
    chat_ui.root.destroy()
    #Close the client socket...
    client.close()
    

def send_message():
    print("send\n")
 
def listen_for_messages_from_server(client_socket, username):
    EXCHANGE_COMPLETE = False
    while not stop_event.is_set():
        try:
            rx_data = client_socket.recv(2048)
            rx_packet = LitProtocolPacket.decodePacket(rx_data)   
            if rx_packet:  
                if EXCHANGE_COMPLETE == False:
                    if rx_packet.init == b'\x00\x00\x00\x00\x00\x00\x00\x01':        #LISTEN FOR PUBLIC KEY: Check if recieved packet has INIT = 1
                        public_key = rx_packet.payload
                        ciphertext, shared_secret = kyber.Kyber512.enc(public_key)
                        ciphertext_packet = LitProtocolPacket.generateTextMessage(ciphertext)    
                        
                        ciphertext_packet.init = b'\x00\x00\x00\x00\x00\x00\x00\x02'              
                        client_socket.sendall(LitProtocolPacket.encodePacket(ciphertext_packet))                                                                   #SEND PK TO CLIENT : Send packet with INIT = 1;
                        print("EXCHANGE SEQUENCE 2: SUCCESS\n")
                    elif(rx_packet.init == b'\x00\x00\x00\x00\x00\x00\x00\x03'):     #RECIEVE CIPHERTEXT: Check if recieved packet has INIT = 2
                        done_packet = LitProtocolPacket.generateTextMessage("DONE".encode())     
                        done_packet.init = b'\x00\x00\x00\x00\x00\x00\x00\x04'       #SEND DONE SIGNAL  : Send packet with INIT = 3;
                        client_socket.sendall(LitProtocolPacket.encodePacket(done_packet))
                        print("EXCHANGE SEQUENCE 4: SUCCESS\n")
                        EXCHANGE_COMPLETE = True

                        """
                        if message:
                            if ',' in message:
                                print(message)
                                timestamp, username, content = message.split(',',2) 
                                add_message(f"[{timestamp}] [{username}] {content}")
                            else:
                                add_message(f"[SERVER] {message}")
                        """
                        #Process the message as before...
                        
            else:
                print("Server closed connection or no data received.")
                break
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
    #chat_ui = ChatUI(connect, send_message, exit_chat)
    chat_ui = ChatUI(connect, send_message, exit_chat)
    chat_ui.mainloop()
