import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

#Colors & Fonts...
DARK_GREY = "#121212"
MEDIUM_GREY = "white"
BLACK = "black"
WHITE = "white"
OCEAN_BLUE = "#464EB8"
FONT = ("Helvetica", 12, "bold")
BUTTON_FONT = ("Helvetica", 10, "bold")
SMALL_FONT = ("Helvetica", 9)

#Programmatically generate UI Elements...
class ChatUI:
    def __init__(self, connect_callback, send_message_callback, exit_callback):
        #TK Configuration...
        self.root = tk.Tk()
        self.root.geometry("600x600")
        self.root.title("Group Messenger")
        self.root.resizable(True, True)

        #TK Structure...
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=4)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        #Communications logic callbacks...
        self.connect_callback = connect_callback
        self.send_message_callback = send_message_callback
        self.exit_callback = exit_callback

        #Generate UI...
        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root, bg=DARK_GREY)
        top_frame.grid(row=0, column=0, sticky="nsew")

        middle_frame = tk.Frame(self.root, bg=MEDIUM_GREY)
        middle_frame.grid(row=1, column=0, sticky="nsew")

        bottom_frame = tk.Frame(self.root, bg=DARK_GREY)
        bottom_frame.grid(row=2, column=0, sticky="nsew")

        self.username_textbox = tk.Entry(top_frame, font=FONT, bg=MEDIUM_GREY, fg=BLACK)
        self.username_textbox.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        username_button = tk.Button(top_frame, text="Join", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=self.connect)
        username_button.pack(side=tk.LEFT, padx=15)

        self.message_textbox = tk.Entry(bottom_frame, font=FONT, bg=MEDIUM_GREY, fg=BLACK)
        self.message_textbox.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        message_button = tk.Button(bottom_frame, text="Send", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=self.send_message)
        message_button.pack(side=tk.LEFT, padx=10)

        self.exit_button = tk.Button(bottom_frame, text="Exit", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=self.exit_chat)
        self.exit_button.pack(side=tk.LEFT, padx=10)
        self.exit_button.config(state=tk.DISABLED)

        self.message_box = scrolledtext.ScrolledText(middle_frame, font=SMALL_FONT, bg=MEDIUM_GREY, fg=BLACK)
        self.message_box.config(state=tk.DISABLED)
        self.message_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def connect(self):
        if self.connect_callback:
            self.connect_callback()

    def send_message(self):
        if self.send_message_callback:
            self.send_message_callback()

    def exit_chat(self):
        if self.exit_callback:
            self.exit_callback()

    def add_message(self, message):
        self.message_box.config(state=tk.NORMAL)
        self.message_box.insert(tk.END, message + '\n')
        self.message_box.config(state=tk.DISABLED)

    def get_username(self):
        return self.username_textbox.get()

    def get_message(self):
        return self.message_textbox.get()

    def clear_message_textbox(self):
        self.message_textbox.delete(0, tk.END)

    def disable_username_input(self):
        self.username_textbox.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.NORMAL)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def mainloop(self):
        self.root.mainloop()