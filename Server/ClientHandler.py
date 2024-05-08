import csv
import threading
import sys
import os

common_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Common'))
sys.path.append(common_path)
from Common.Packet import TextPayload, LitProtocolPacket
from Common.encryption_utils import encrypt_message, decrypt_message, load_key
import Common.kyber as kyber
from Crypto.Cipher import AES

class ClientHandler():
    def __init__(self, active_clients_list, public_key, secret_key):
        self.active_clients_list = active_clients_list
        self.sent_messages_set = set()                        #Set to store previously sent messages...
        self.public_key = public_key
        self.secret_key = secret_key

    def handle_client(self, client_socket):
        """
        When a client connects, perform name duplication check,notify other users...
        """
        rx_data = client_socket.recv(2048)
        print(f"Before starting listening thread: {rx_data}\n")
        if(rx_data):
            threading.Thread(target=self.listen_for_messages, args=(client_socket, rx_data)).start()
        
            
               
   
        
    def listen_for_messages(self, client_socket, init_signal):
        """
        Listen for messages, then rebroadcast them to all other active users. Refer to diagram in documentation depicting
        the key-exchange process.
        """
        client_uname = "UNKNOWN" #For safety...

        init_packet = LitProtocolPacket.decodePacket(init_signal)
        if init_packet.init == b'\x00\x00\x00\x00\x00\x00\x00\x00':        #INITIAL CONNECTION: Check if recieved packet has INIT = 0
                            pk_packet = LitProtocolPacket.generateTextMessage(self.public_key)    
                            pk_packet.init = b'\x00\x00\x00\x00\x00\x00\x00\x01'             
                            client_socket.sendall(LitProtocolPacket.encodePacket(pk_packet))                                #SEND PK TO CLIENT : Send packet with INIT = 1;
                            print("EXCHANGE SEQUENCE 1: SUCCESS\n")

        EXCHANGE_COMPLETE = False
        while True:
            try:
                #Series of packet metadata checks to confirm key-exchange process occurs..
                rx_data = client_socket.recv(2048)
                rx_packet = LitProtocolPacket.decodePacket(rx_data)  
                if rx_packet:
                    if EXCHANGE_COMPLETE == False:
                        if(rx_packet.init == b'\x00\x00\x00\x00\x00\x00\x00\x02'):     #RECIEVE CIPHERTEXT: Check if recieved packet has INIT = 2
                            ciphertext = rx_packet.payload
                            shared_secret = kyber.Kyber512.dec(ciphertext,self.secret_key)  #Generate the shared secret...                       
                            print(f"SHARED SECRET ({shared_secret}) GENERATED\n")
                            done_packet = LitProtocolPacket.generateTextMessage("DONE".encode())     
                            done_packet.init = b'\x00\x00\x00\x00\x00\x00\x00\x03'       #SEND DONE SIGNAL  : Send packet with INIT = 3;
                            client_socket.sendall(LitProtocolPacket.encodePacket(done_packet))
                            print("EXCHANGE SEQUENCE 3: SUCCESS\n")
                        if(rx_packet.init == b'\x00\x00\x00\x00\x00\x00\x00\x04'):     #RECIEVE CIPHERTEXT: Check if recieved packet has INIT = 2
                            client_uname = rx_packet.payload                                #ASSIGN USERNAME   : Key-exchange complete, recieve username...
                            self.active_clients_list.append((client_uname, client_socket, shared_secret)) 
                            print(f"USERNAME ASSIGNMENT {client_uname}: SUCCESS")
                            EXCHANGE_COMPLETE = True

                        
                        
                    """
                    THIS SECTION HERE WILL CONTAIN THE MESSAGE RELAY CODE
                    """
                else: #Properly exit the loop if the client disconnects...
                    print(f"Client {client_uname} disconnected gracefully.")  
                    break  
            except ConnectionResetError:  #Exit the loop if there's a connection reset error...
                print(f"Client {client_uname} disconnected with an error.")
                break 
            self.cleanup_client(client_uname, client_socket)  #Cleanup after breaking out of the loop...

    def send_messages_to_all(self, message_packet):
        """
        Send messages to all users in the connected users list...
        """
        encoded_message = LitProtocolPacket.encodePacket(message_packet)     #Encode once, send to all...

        if message_packet.payload not in self.sent_messages_set:
            disconnected_clients_list = []
            for username_str, client_socket in self.active_clients_list[:]:
                try:
                    print(f'send_messages_to_all(): {message_packet.payload.decode()}')  #Assuming payload is bytes and needs decoding for printing...
                    client_socket.sendall(encoded_message)                               #Send the encoded message directly
                except BrokenPipeError:
                    #If a user is disconnected (broken pipe error), they will be removed from the list of active clients...
                    disconnected_clients_list.append((username_str, client_socket))

            #Remove disconnected clients and update the active list...
            for client_tuple in disconnected_clients_list:
                self.active_clients_list.remove(client_tuple)

            self.sent_messages_set.add(message_packet.payload)
           

    def cleanup_client(self, username_str, client_socket):
        """
        If client is disconnected, remove from connected clients list...
        """
        key = load_key()
        #Creating payload and encrypting it...
        payload = encrypt_message(TextPayload.Generate(f"SERVER", f"{username_str} has left the server."), key)
        #Creating packet...
        message_packet = LitProtocolPacket.generateEncryptedTextMessage(payload) 

        # If the client is in the active list, remove it and notify others
        if (username_str, client_socket) in self.active_clients_list:
            self.active_clients_list.remove((username_str, client_socket))
            self.send_messages_to_all(message_packet)
            try:
                client_socket.close()  # Ensure the client's socket is closed
            except OSError:
                pass  # Socket already closed or unusable
    
