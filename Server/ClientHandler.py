import csv
import threading
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from Common.Packet import TextPayload, LitProtocolPacket


class ClientHandler():
    def __init__(self, active_clients_list):
        self.active_clients_list = active_clients_list
        self.sent_messages_set = set()                        #Set to store previously sent messages...
        
    def handle_client(self, client_socket):
        """
        When a client connects, notify other users...
        """
        username_str = client_socket.recv(2048).decode('utf-8')
        if username_str:
            welcome_message = TextPayload.Generate("SERVER", f"{username_str} was added to the chat!")
            
            #Sample values
            message_type = b'\x00\x00'                         #0x00 = TEXT MESSAGE, 0x01 = IMAGE, 0x02 = GENERIC FILE (subject to change)...
            message_options_flags = b'\x00\x00'                #0x00 = NO ENCRYPTION, 0x01 = ENCRYPTION...
            message_message_id = os.urandom(8)                 #For other features maybe...
            message_iv = os.urandom(16)                        #Dummy IV, for when we implement encryption...
            message_payload = welcome_message                  #Payload (currently as TextPayload)
            message_hmac = os.urandom(32)                      #Dummy HMAC, for when we implement encryption...
            
            #Creating the LitProtocolPacket object...
            message_packet = LitProtocolPacket(
                message_type=message_type,
                options_flags=message_options_flags,
                message_id=message_message_id,
                iv=message_iv,
                hmac=message_hmac,
                payload=message_payload.encode()               #Serializing the payload to a byte string for TCP transmission...
            )        

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
        while True:
            try:
                data = client_socket.recv(2048)
                if data:
                    message_packet = LitProtocolPacket.decodePacket(data)
                    message_packet.payload = TextPayload.Generate(username_str, message_packet.payload.decode('utf-8')).encode('utf-8')
                
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
        exit_message = TextPayload.Generate("Server", f"{username_str} has left the server.")
            
        #Sample values
        message_type = b'\x00\x00'                         #0x00 = TEXT MESSAGE, 0x01 = IMAGE, 0x02 = GENERIC FILE (subject to change)...
        message_options_flags = b'\x00\x00'                #0x00 = NO ENCRYPTION, 0x01 = ENCRYPTION...
        message_message_id = os.urandom(8)                 #For other features maybe...
        message_iv = os.urandom(16)                        #Dummy IV, for when we implement encryption...
        message_payload = exit_message                     #Payload (currently as TextPayload)
        message_hmac = os.urandom(32)                      #Dummy HMAC, for when we implement encryption...
        
        #Creating the LitProtocolPacket object...
        message_packet = LitProtocolPacket(
            message_type=message_type,
            options_flags=message_options_flags,
            message_id=message_message_id,
            iv=message_iv,
            hmac=message_hmac,
            payload=message_payload.encode()               #Serializing the payload to a byte string for TCP transmission...
        )        
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
