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
        client_uname_decrypted = "UNKNOWN" #For safety...
        
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
                if rx_data:
                    if EXCHANGE_COMPLETE == False:
                        print("\n\n\n\nTWICE!!!!!!!\n\n\n\n")
                        if(rx_packet.init == b'\x00\x00\x00\x00\x00\x00\x00\x02'):              #RECIEVE CIPHERTEXT: Check if recieved packet has INIT = 2
                            ciphertext = rx_packet.payload
                            shared_secret = kyber.Kyber512.dec(ciphertext,self.secret_key)      #Generate the shared secret...                       
                            print(f"SHARED SECRET ({shared_secret}) GENERATED\n")
                            done_packet = LitProtocolPacket.generateTextMessage("DONE".encode('utf-8'))     
                            done_packet.init = b'\x00\x00\x00\x00\x00\x00\x00\x03'              #SEND DONE SIGNAL  : Send packet with INIT = 3;
                            client_socket.sendall(LitProtocolPacket.encodePacket(done_packet))
                            print("EXCHANGE SEQUENCE 3: SUCCESS\n")
                        elif(rx_packet.init == b'\x00\x00\x00\x00\x00\x00\x00\x04'):            #RECIEVE CIPHERTEXT: Check if recieved packet has INIT = 2                             
                            decrypted_packet = rx_packet.decryptPayload(shared_secret)                          
                            client_uname_decrypted = decrypted_packet.payload                   #ASSIGN USERNAME   : Key-exchange complete, recieve username...  
                            
                            duplicate_found = any(client_uname_decrypted == entry[0] for entry in self.active_clients_list)


                            if duplicate_found: #Send message informing user to change username...
                                #Creating payload and encrypting it...
                                dupe_message = TextPayload.Generate("SERVER",f"Someone already has username the \"{client_uname_decrypted}\"! Pick another one and reconnect.")
                                #Creating packet...
                                dupe_message_packet = LitProtocolPacket.generateEncryptedTextMessage(shared_secret, dupe_message.encode('utf-8')) 
                                dupe_message_packet.options_flags = b'\x00\x03' #Masking in a 1 into bit in position 1 (duplication error bit)...
                                #Sending message...
                                client_socket.sendall(LitProtocolPacket.encodePacket(dupe_message_packet))
                            else: #No duplicate found, add user to active client list.
                                #Send welcome message...
                                welcome_message = TextPayload.Generate("SERVER", f"Welcome {client_uname_decrypted} to the server!")
                                print("Welcome:" + welcome_message + "\n")
                                welcome_message_packet = LitProtocolPacket.generateEncryptedTextMessage(shared_secret, welcome_message.encode('utf-8'))
                                self.active_clients_list.append((client_uname_decrypted, client_socket, shared_secret)) 
                                self.send_messages_to_all(shared_secret, welcome_message_packet)
                                EXCHANGE_COMPLETE = True  
                                print(f"KEY EXCHANGE PROCESS COMPLETE FOR USER ({client_uname_decrypted})")
                    elif EXCHANGE_COMPLETE == True: #I know it looks weird but there needs to be two checks, it stops working if theres an else here...
                        
                                    
                        print("=[RECIEVED ENCRYPTED PACKET]=======================================================================================\n\n")
                        print(f"PAYLOAD: {rx_packet.payload}\n")
                        print(f"TYPE   : {type(rx_packet.payload)}\n\n")
                        print(f"\n\nRAW PACKET DATA:\n\n")
                        print(f"\n\n{rx_packet}\n\n")
                        print("=======================================================================================[RECIEVED ENCRYPTED PACKET]=\n\n")
                        self.send_messages_to_all(shared_secret, rx_packet)
                        
                else: #Properly exit the loop if the client disconnects...
                    print(f"Client {client_uname_decrypted} disconnected gracefully.")  
                    break  
            except ConnectionResetError:  #Exit the loop if there's a connection reset error...
                print(f"Client {client_uname_decrypted} disconnected with an error.")
                break 
        self.cleanup_client(client_uname_decrypted, client_socket, shared_secret)  #Cleanup after breaking out of the loop...

    def send_messages_to_all(self, shared_secret, message_packet):
        """
        Send messages to all users in the connected users list...
        """
        print(message_packet)
        #Decrypt and extract payload from packet...
        decrypted_packet = message_packet.decryptPayload(shared_secret)                          
        decrypted_message = decrypted_packet.payload
        print(f"\n\nsend_messages_to_all(...): {decrypted_message}\n\n")
        if decrypted_message not in self.sent_messages_set:
            disconnected_clients_list = []
            for username_str, recipient_socket, shared_secret in self.active_clients_list[:]:
                try:
                    #Pack payload using unique shared secret for recipient...
                    outgoing_message = LitProtocolPacket.generateEncryptedTextMessage(shared_secret, decrypted_message.encode('utf-8'))
                    recipient_socket.sendall(LitProtocolPacket.encodePacket(outgoing_message))                               #Send the encoded message directly
                except BrokenPipeError:
                    #If a user is disconnected (broken pipe error), they will be removed from the list of active clients...
                    disconnected_clients_list.append((username_str, recipient_socket, shared_secret))

            #Remove disconnected clients and update the active list...
            for client_tuple in disconnected_clients_list:
                self.active_clients_list.remove(client_tuple)

            self.sent_messages_set.add(message_packet.payload)
           
    
    def cleanup_client(self, username, client_socket, shared_secret):
        #
        #If client is disconnected, remove from connected clients list...
        #
        #Creating payload and encrypting it...
     
        payload = TextPayload.Generate("SERVER", f"{username} has left the server.")
        #Creating packet...
        message_packet = LitProtocolPacket.generateEncryptedTextMessage(shared_secret, payload.encode('utf-8'))

        # If the client is in the active list, remove it and notify others
        if (username, client_socket, shared_secret) in self.active_clients_list:
            self.active_clients_list.remove((username, client_socket, shared_secret))
            self.send_messages_to_all(shared_secret, message_packet)
            try:
                client_socket.close()  # Ensure the client's socket is closed
            except OSError:
                pass  # Socket already closed or unusable
    
