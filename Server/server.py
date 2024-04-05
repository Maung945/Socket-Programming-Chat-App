import socket
import threading
import signal
import sys
from ClientHandler import ClientHandler

class ChatServer:
    def __init__(self, host='127.0.0.1', port=12312, listener_limit=5):
        self.host = host                                                        #Host IP address...
        self.port = port                                                        #Host port number...
        self.listener_limit = listener_limit                                    #Max number of clients...
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #Server socket...
        self.active_clients_list = []                                           #Track active clients...
        self.client_handler = ClientHandler(self.active_clients_list)           #Instantiate a ClientHandler object...
        signal.signal(signal.SIGINT, self.signal_handler)                       #Handle SIGINT so we can safely unbind the port with a CRTL+C signal interrupt...

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
                print(f"Successfully connected to client {address[0]} on port {address[1]}!")
                threading.Thread(target=self.client_handler.handle_client, args=(client,)).start()
        except KeyboardInterrupt:
            self.cleanup()

if __name__ == '__main__':
    chat_server = ChatServer()
    chat_server.run()



    
