import socket
import threading
import re
import os
import sys
import time



#Import functions and classes from your modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
#from Common.encryption_utils import encrypt_message, decrypt_message, load_key
from Common.Packet import LitProtocolPacket, TextPayload
import Common.kyber as kyber
from ui import ChatUI  

stop_event = threading.Event()

HOST = '127.0.0.1'
PORT = 12439
GLOBAL_USERNAME_TEST = "TEST"

def add_message(message):
    global chat_ui
    chat_ui.add_message(message)

def connect():
    global username
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

        init_packet = LitProtocolPacket.generateTextMessage(" ".encode())
        client.sendall(LitProtocolPacket.encodePacket(init_packet))

       
        threading.Thread(target=listen_for_messages_from_server, args=(client, str(username))).start()
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
    message = TextPayload.Generate(username, chat_ui.get_message())
    message_packet = LitProtocolPacket.generateEncryptedTextMessage(shared_secret, message.encode())
    if message_packet.payload:
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

def listen_for_messages_from_server(client_socket, username):
    global shared_secret
    EXCHANGE_COMPLETE = False
    while not stop_event.is_set():
        try:
            rx_data = client_socket.recv(2048)
            rx_packet = LitProtocolPacket.decodePacket(rx_data)  
            if rx_data:  
                if EXCHANGE_COMPLETE == False:
                    if rx_packet.init == b'\x00\x00\x00\x00\x00\x00\x00\x01':                   #LISTEN FOR PUBLIC KEY: Check if recieved packet has INIT = 1
                        public_key = rx_packet.payload
                        ciphertext, shared_secret = kyber.Kyber512.enc(public_key)
                        ciphertext_packet = LitProtocolPacket.generateTextMessage(ciphertext)    
                        
                        ciphertext_packet.init = b'\x00\x00\x00\x00\x00\x00\x00\x02'              
                        client_socket.sendall(LitProtocolPacket.encodePacket(ciphertext_packet))                                                                   #SEND PK TO CLIENT : Send packet with INIT = 1;
                        print("EXCHANGE SEQUENCE 2: SUCCESS\n")
                    elif(rx_packet.init == b'\x00\x00\x00\x00\x00\x00\x00\x03'):                #RECIEVE CIPHERTEXT: Check if recieved packet has INIT = 2
                        done_packet = LitProtocolPacket.generateEncryptedTextMessage(shared_secret, username.encode('utf-8'))     
                        client_socket.sendall(LitProtocolPacket.encodePacket(done_packet))
                        print("EXCHANGE SEQUENCE 4: SUCCESS\n")
                        EXCHANGE_COMPLETE = True
                elif EXCHANGE_COMPLETE == True: #I know it looks weird but there needs to be two checks, it stops working if theres an else here...
                    if rx_packet.init == b'\x00\x00\x00\x00\x00\x00\x00\x04':
                        #Disconnect if duplicate found...
                        if(rx_packet.options_flags == b'\x00\x03'):
                            #Close the client socket...
                            client.close()
                            rx_packet = rx_packet.decryptPayload(shared_secret)
                            add_message(TextPayload.reorient_string(rx_packet.payload))
                            chat_ui.enable_username_input()
                        else:  
                            print(shared_secret)
                            rx_packet = rx_packet.decryptPayload(shared_secret)
                            print("STUFF: " + rx_packet.payload)
                            add_message(TextPayload.reorient_string(rx_packet.payload))
                            print("end")

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
