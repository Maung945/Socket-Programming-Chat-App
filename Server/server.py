#Python standard library imports...
import socket
import threading
import signal
import sys
import os

#Import functions and classes from your modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import Common.kyber as kyber
from ClientHandler import ClientHandler

class ChatServer:
    """
    A simple chat server implementation.

    This class represents a chat server that listens for incoming connections
    from clients, handles client connections, and facilitates communication
    between clients.

    Attributes:
        host (str): The IP address of the host where the server is running.
        port (int): The port number on which the server is listening for connections.
        listener_limit (int): The maximum number of clients the server can accept.
        server_socket (socket.socket): The server's main socket for accepting client connections.
        active_clients_list (list): A list to track active client connections.
        client_handler (ClientHandler): An instance of the ClientHandler class responsible for handling client connections.
    """

    def __init__(self, host='127.0.0.1', port=12439, listener_limit=5):
        self.host = host                                                        #Host IP address...
        self.port = port                                                        #Host port number...
        self.listener_limit = listener_limit                                    #Max number of clients...
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #Server socket...
        self.active_clients_list = []                                           #Track active clients...
        self.public_key, self.secret_key = kyber.Kyber512.keygen()      
        self.client_handler = ClientHandler(self.active_clients_list, self.public_key, self.secret_key)           #Instantiate a ClientHandler object...
                #Generating Kyber Public and Secret Key...
        signal.signal(signal.SIGINT, self.signal_handler)                       #Handle SIGINT so we can safely unbind the port with a CRTL+C signal interrupt...

   
    def cleanup(self):
        """
        Safely unbind port...
        """
        print("Shutting down the server...")
        self.server_socket.close()
        print("Server shutdown successfully. Port unbound.")

    
    def signal_handler(self, sig, frame):
        """
        Signal interrupt service routine...
        """
        self.cleanup()
        sys.exit(0)

    def run(self):
        """
        Run the server, general control flow for server...
        """
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
                print(f"Successfully connected to client {address[0]} on port {address[1]}!")
                threading.Thread(target=self.client_handler.handle_client, args=(client,)).start()
        except KeyboardInterrupt:
            self.cleanup()

if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.run()



    
