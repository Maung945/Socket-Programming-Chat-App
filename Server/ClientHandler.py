import csv
import threading
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from Common.Packet import TextPayload, LitProtocolPacket
from Common.encryption_utils import encrypt_message, decrypt_message, load_key


class ClientHandler():
    def __init__(self, active_clients_list):
        self.active_clients_list = active_clients_list
        self.sent_messages_set = set()                        #Set to store previously sent messages...
        
    def handle_client(self, client_socket):
        """
        When a client connects, perform name duplication check,notify other users...
        """
        key = load_key()
        username_str = client_socket.recv(2048).decode('utf-8')
        
        #Set the username duplication flag if a duplicate username is detected...
        duplicate_bool = False
        for entries in self.active_clients_list:
            if username_str == entries[0]:
                duplicate_bool=True
                print("DUPLICATE FOUND")

        
        if duplicate_bool: #Send message informing user to change username...
            #Creating payload and encrypting it...
            payload = encrypt_message(TextPayload.Generate("SERVER",f"Someone already has username the \"{username_str}\"! Pick another one and reconnect."), key)
            #Creating packet...
            message_packet = LitProtocolPacket.generateEncryptedTextMessage(payload) 
            message_packet.options_flags = b'\x00\x03' #Masking in a 1 into bit in position 1 (duplication error bit)...
            #Sending message...
            client_socket.sendall(LitProtocolPacket.encodePacket(message_packet))

        else: #No duplicate found, add user to active client list.
            if username_str:
                #Creating payload and encrypting it...
                payload = encrypt_message(TextPayload.Generate("SERVER",f"{username_str} has joined the server!"), key)
                #Creating packet...
                message_packet = LitProtocolPacket.generateEncryptedTextMessage(payload) 
                #Sending message...
                self.active_clients_list.append((username_str, client_socket))
                self.send_messages_to_all(message_packet)
                threading.Thread(target=self.listen_for_messages, args=(client_socket, username_str)).start()
            else:
                print("Client username is empty...")
        
    def listen_for_messages(self, client_socket, username_str):
        """
        Listen for messages, then rebroadcast them to all other active users...
        """
        key = load_key()
        while True:
            try:
                data = client_socket.recv(2048)
                if data: #We should probably not do this here, but I'll fix it later...
                    message_packet = LitProtocolPacket.decodePacket(data)    #Recieve the message packet...
                    decrypted_payload = decrypt_message(message_packet.payload, key) #Decrypt the message packet...
                    formatted_payload = TextPayload.Generate(username_str, decrypted_payload) #Format the new payload (this line is really bad, fix later)...
                    message_packet.payload = encrypt_message(formatted_payload, key) #Fix this line later...
                    
                    print("[BEGIN RECEIVED PACKET]\n" + str(message_packet) + "\n[END PACKET]")  #Debug line...
                    if message_packet.payload:
                        print(f'listen_for_messages(): {message_packet}')  #Debug line
                        self.send_messages_to_all(message_packet)
                    else:
                        print(f"The message sent from client {username_str} is empty...")
                        break
                else:
                    print(f"Client {username_str} disconnected gracefully.")
                    break  #Properly exit the loop if the client disconnects...
            except ConnectionResetError:
                print(f"Client {username_str} disconnected with an error.")
                break  #Exit the loop if there's a connection reset error...
        
        self.cleanup_client(username_str, client_socket)  # Cleanup after breaking out of the loop...

    def send_messages_to_all(self, message_packet):
        """
        Send messages to all users in the connected users list...
        """
        encoded_message = LitProtocolPacket.encodePacket(message_packet)     #Encode once, send to all...
        print(f'send_messages_to_all(): {encoded_message}')  #Debug line
        if message_packet.payload not in self.sent_messages_set:
            disconnected_clients_list = []
            for username_str, client_socket in self.active_clients_list[:]:
                try:
                    print(f'send_messages_to_all(): {message_packet.payload.decode()}')  #Assuming payload is bytes and needs decoding for printing...
                    client_socket.sendall(encoded_message)  #Send the encoded message directly
                except BrokenPipeError:
                    #If a user is disconnected (broken pipe error), they will be removed from the list of active clients...
                    disconnected_clients_list.append((username_str, client_socket))

            #Remove disconnected clients and update the active list...
            for client_tuple in disconnected_clients_list:
                self.active_clients_list.remove(client_tuple)

            self.sent_messages_set.add(message_packet.payload)
            self.log_message(message_packet.payload.decode())

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
    
    def log_message(self, formatted_payload_str):
        """
        Save message to CSV file...
        """
        #Splitting...
        message_parts = formatted_payload_str.split(',', maxsplit=2)

        #Split the string at the first two commas only...
        if len(message_parts) == 3:
            with open("chat_record.csv", "a", newline='') as file_obj:
                csv_writer = csv.writer(file_obj)
                csv_writer.writerow(message_parts) 
 