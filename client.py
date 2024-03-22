import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import re
import random
from datetime import datetime  # Added for timestamp

HOST = '127.0.0.1'
PORT = 1234

# Define colors and fonts
DARK_GREY = "#121212"
MEDIUM_GREY = "white"
BLACK = "black"
WHITE = "white"
OCEAN_BLUE = "#464EB8"
FONT = ("Helvetica", 12, "bold")
BUTTON_FONT = ("Helvetica", 10, "bold")
SMALL_FONT = ("Helvetica", 9)

# Creating a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set to store previously saved messages
saved_messages = set()

def add_message(message):
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + '\n')
    message_box.config(state=tk.DISABLED)
   
def connect():
    username = username_textbox.get()
    username_pattern = re.compile(r'^[a-zA-Z]{3}-\d{2}$')
    
    if username_pattern.match(username):
        try:
            client.connect((HOST, PORT))
            print("Successfully connected to server")
            add_message("[SERVER] Successfully connected to the server")
        except:
            messagebox.showerror("Unable to connect to server", f"Unable to connect to server {HOST} {PORT}")

        client.sendall(username.encode())
        threading.Thread(target=listen_for_messages_from_server, args=(client, )).start()
        username_textbox.config(state=tk.DISABLED)
        username_button.config(state=tk.DISABLED)
    else:
        messagebox.showerror("Invalid username", "Username format should be 3 alphabets, one '-', and two numbers")

def send_message():
    message = message_textbox.get()
    if message != '':
        client.sendall(message.encode())
        message_textbox.delete(0, len(message))
    else:
        messagebox.showerror("Empty message", "Message cannot be empty")

root = tk.Tk()
root.geometry("600x600")
root.title("Group Messenger")

# Add icon to the taskbard
root.iconbitmap('logo1.ico')

client_label = tk.Label(root, text="Messenger Client", font=FONT, bg=BLACK, fg=BLACK)
client_label.grid(row=0, column=0, sticky="w", padx=(70, 0))

root.resizable(True, True)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

top_frame = tk.Frame(root, bg=DARK_GREY)
top_frame.grid(row=0, column=0, sticky="nsew")

middle_frame = tk.Frame(root, bg=MEDIUM_GREY)
middle_frame.grid(row=1, column=0, sticky="nsew")

bottom_frame = tk.Frame(root, bg=DARK_GREY)
bottom_frame.grid(row=2, column=0, sticky="nsew")

username_label = tk.Label(top_frame, text="Enter username:", font=FONT, bg=DARK_GREY, fg=WHITE)
username_label.pack(side=tk.LEFT, padx=10)

username_textbox = tk.Entry(top_frame, font=FONT, bg=MEDIUM_GREY, fg=BLACK)
username_textbox.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

username_button = tk.Button(top_frame, text="Join", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=connect)
username_button.pack(side=tk.LEFT, padx=15)

message_textbox = tk.Entry(bottom_frame, font=FONT, bg=MEDIUM_GREY, fg=BLACK)
message_textbox.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

message_button = tk.Button(bottom_frame, text="Send", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=send_message)
message_button.pack(side=tk.LEFT, padx=10)

message_box = scrolledtext.ScrolledText(middle_frame, font=SMALL_FONT, bg=MEDIUM_GREY, fg=BLACK)
message_box.config(state=tk.DISABLED)
message_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
'''
def listen_for_messages_from_server(client):
    while True:
        message = client.recv(2048).decode('utf-8')
        if message != '':
            username = message.split("~")[0]
            content = message.split('~')[1]
            add_message(f"[{username}] {content}")
        else:
            messagebox.showerror("Error", "Message received from client is empty")
'''
def listen_for_messages_from_server(client):
    while True:
        message = client.recv(2048).decode('utf-8')
        if message != '':
            if '~' in message:
                username, content = message.split('~', 1)  # Split only once
                add_message(f"[{username}] {content}")
            else:
                add_message(f"[SERVER] Invalid message format: {message}")
        else:
            messagebox.showerror("Error", "Message received from server is empty")

def main():
    root.mainloop()
    
if __name__ == '__main__':
    main()

