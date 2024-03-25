import socket
import threading
import signal
import csv
from pathlib import Path
import sys

"""
This snippet below is to allow for custom modules to be shared between client and server
custom modules may be beneficial for us if we wanted to work on functionality
that both the client and server can use, saving on development time...
"""
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
from Common.Packet import TextPayload

class ChatServer:
    def __init__(self, host='127.0.0.1', port=12312, listener_limit=5):
        self.host = host
        self.port = port
        self.listener_limit = listener_limit
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active_clients_list = []   #Track active clients...
        self.sent_messages_set = set()  #Set to store previously sent messages...

        #Handle SIGINT so we can safely unbind the port with a CRTL+C signal interrupt...
        signal.signal(signal.SIGINT, self.signal_handler)

    #Listen for messages, then rebroadcast them to all other active users...
    def listen_for_messages(self, client_socket, username_str):
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
    
    #Send message to an individual client...
    def send_message_to_client(self, client_socket, message_str):
        try:
            client_socket.sendall(message_str.encode())
        except BrokenPipeError:
            print(f"Unable to send message to a disconnected client.")

    #Send messages to all users in the connected users list...
    def send_messages_to_all(self, message_str):
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

    #Save message to CSV...
    def log_message(self, message_str):
        message_obj = TextPayload.from_string(message_str)
        if message_obj:
            with open("chat_record.csv", "a", newline='') as file_obj:
                csv.writer(file_obj).writerow(message_obj.to_csv())

    #If client is disconnected, remove from connected clients list...
    def cleanup_client(self, username_str, client_socket, leave_message_str):
        self.active_clients_list.remove((username_str, client_socket))
        self.send_messages_to_all(str(TextPayload.Generate("Server", leave_message_str)))

    #When a client connects, notify other users...
    def client_handler(self, client_socket):
        username_str = client_socket.recv(2048).decode('utf-8')
        if username_str:
            self.active_clients_list.append((username_str, client_socket))
            self.send_messages_to_all(str(TextPayload.Generate("SERVER", f"{username_str} added to the chat!")))
            threading.Thread(target=self.listen_for_messages, args=(client_socket, username_str)).start()
        else:
            print("Client username is empty...")

    #Safely unbind port...
    def cleanup(self):
        print("Shutting down the server...")
        self.server_socket.close()
        print("Server shutdown successfully. Port unbound.")

    #Signal interrupt service routine...
    def signal_handler(self, sig, frame):
        self.cleanup()
        sys.exit(0)

    #Run the server, general control flow for server...
    def run(self):
        try:
            self.server_socket.bind((self.host, self.port))
            print(f"Running the server on {self.host} {self.port}")
        except Exception as e:
            print(f"Unable to bind to host {self.host} and port {self.port}. Error: {e}")
            return
        self.server_socket.listen(self.listener_limit)
        print("Press Ctrl+C to stop the server.")
        try:
            while True:
                client, address = self.server_socket.accept()
                print(f"Successfully connected to client {address[0]} {address[1]}")
                threading.Thread(target=self.client_handler, args=(client,)).start()
        except KeyboardInterrupt:
            self.cleanup()

if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.run()
