import sys
import csv
from pathlib import Path
import threading
from ..Common.Packet import TextPayload


class ClientHandler():
    def __init__(self, active_clients_list):
        self.active_clients_list = active_clients_list
        self.sent_messages_set = set()                  #Set to store previously sent messages...
        
    def handle_client(self, client_socket):
        """
        When a client connects, notify other users...
        """
        username_str = client_socket.recv(2048).decode('utf-8')
        if username_str:
            self.active_clients_list.append((username_str, client_socket))
            self.send_messages_to_all(str(TextPayload.Generate("SERVER", f"{username_str} added to the chat!")))
            threading.Thread(target=self.listen_for_messages, args=(client_socket, username_str)).start()
        else:
            print("Client username is empty...")
    
    
    def listen_for_messages(self, client_socket, username_str):
        """
        Listen for messages, then rebroadcast them to all other active users...
        """
        while True:
            try:
                content_str = client_socket.recv(2048).decode('utf-8')
                if content_str:
                    message_obj = TextPayload.Generate(username_str, content_str)
                    print(f'listen_for_messages(): {message_obj}')  #Debug line
                    self.send_messages_to_all(str(message_obj))
                else:
                    print(f"The message sent from client {username_str} is empty...")
                    break  #Client disconnected
            except ConnectionResetError:
                print(f"Client {username_str} disconnected")
                self.cleanup_client(username_str, client_socket, f"{username_str} left the chatroom...")
                break
    
    def send_message_to_client(self, client_socket, message_str):
        """
        Send message to an individual client...
        """
        try:
            client_socket.sendall(message_str.encode())
        except BrokenPipeError:
            print(f"Unable to send message to a disconnected client.")

    def send_messages_to_all(self, message_str):
        """
        Send messages to all users in the connected users list...
        """
        print(f'send_messages_to_all(): {message_str}')  #Debug line
        if message_str not in self.sent_messages_set:
            disconnected_clients_list = []
            for username_str, client_socket in self.active_clients_list[:]:
                try:
                    self.send_message_to_client(client_socket, message_str)
                except BrokenPipeError: 
                    #If a user is disconnected (broken pipe error), they will be removed from the list of active clients...
                    disconnected_clients_list.append((username_str, client_socket))

            #Remove disconnected clients and update the active list...
            for client_tuple in disconnected_clients_list:
                self.active_clients_list.remove(client_tuple)

            self.sent_messages_set.add(message_str)
            self.log_message(message_str)

    
    def cleanup_client(self, username_str, client_socket, leave_message_str):
        """
        If client is disconnected, remove from connected clients list...
        """
        self.active_clients_list.remove((username_str, client_socket))
        self.send_messages_to_all(str(TextPayload.Generate("Server", leave_message_str)))
    
    def log_message(self, message_str):
        """
        Save message to CSV...
        """
        message_obj = TextPayload.from_string(message_str)
        if message_obj:
            with open("chat_record.csv", "a", newline='') as file_obj:
                csv.writer(file_obj).writerow(message_obj.to_csv())
