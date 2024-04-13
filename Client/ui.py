import tkinter as tk
import webbrowser
from tkinter import scrolledtext, filedialog
from tkinter import messagebox
import emoji  # Import the emoji library

# Colors & Fonts...
DARK_GREY = "#121212"
MEDIUM_GREY = "white"
BLACK = "black"
WHITE = "white"
OCEAN_BLUE = "#464EB8"
FONT = ("Helvetica", 12, "bold")
BUTTON_FONT = ("Helvetica", 10, "bold")
SMALL_FONT = ("Helvetica", 9)

class ChatUI:
    def __init__(self, connect_callback, send_message_callback, exit_callback):
        # TK Configuration...
        self.root = tk.Tk()
        self.root.geometry("600x600")
        self.root.title("PSCCA Chat App")
        self.root.resizable(True, True)

        # Set application icon
        self.root.iconbitmap("Client/logo1.ico")

        # TK Structure...
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=4)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Communications logic callbacks...
        self.connect_callback = connect_callback
        self.send_message_callback = send_message_callback
        self.exit_callback = exit_callback

        # Emoji list
        if hasattr(emoji, 'UNICODE_EMOJI'):
            self.emoji_list = [emoji.emojize(f":{emoj}:") for emoj in emoji.UNICODE_EMOJI["en"]]
        else:
            self.emoji_list = [
            "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇",
            "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚", "😋", "😛",
            "😜", "🤪", "😝", "🤑", "🤗", "🤓", "😎", "🤩", "🥳", "😏",
            "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫",
            "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳",
            "😻", "🙀", "😿", "😹", "😾", "😸", "😺", "😽", "😼", "👍",
            "👎", "👌", "🤏", "✌️", "🤞", "🤟", "🤘", "🤙", "👋", "🤚",
            "🖐️", "✋", "🖖", "👏", "🙌", "👐", "🤲", "🤝", "🙏", "✍️",
            "💅", "🤳", "💪", "🦾", "🦵", "🦿", "🦶", "👂", "🦻", "👃",
            "🧠", "🦷", "🦴", "👀", "👁️", "👅", "👄", "👶", "🧒", "👦",
            "👧", "🧑", "👱‍♂️", "👱‍♀️", "🧔", "👨", "👩", "🧑‍🦱", "🧑‍🦰", "🧑‍🤝‍🧑",
            "🧑‍🦳", "🧑‍🦲", "👴", "👵", "🙍‍♂️", "🙍‍♀️", "🙎‍♂️", "🙎‍♀️", "🙅‍♂️", "👬",
            "🙅‍♀️", "🙆‍♂️", "🙆‍♀️", "💁‍♂️", "💁‍♀️", "🙋‍♂️", "🙋‍♀️", "🙇‍♂️", "🙇‍♀️", "👭",
            "🤦‍♂️", "🤦‍♀️", "🤷‍♂️", "🤷‍♀️", "👨‍⚕️", "👩‍⚕️", "👨‍🎓", "👩‍🎓", "👨‍🏫", "👫",
            "👩‍🏫", "👨‍⚖️", "👩‍⚖️", "👨‍🌾", "👩‍🌾", "👨‍🍳", "👩‍🍳", "👨‍🔧", "👩‍🔧", "👩‍❤️‍👨",
            "👨‍🏭", "👩‍🏭", "👨‍💼", "👩‍💼", "👨‍🔬", "👩‍🔬", "👨‍💻", "👩‍💻", "👨‍🎤",
            "👩‍🎤", "👨‍🎨", "👩‍🎨", "👨‍✈️", "👩‍✈️", "👨‍🚀", "👩‍🚀", "👨‍🚒", "👩‍🚒",      
            ]
        self.emoji_popup = None  # Placeholder for the pop-up window

        # Generate UI...
        self.setup_ui()

    def setup_ui(self):
        # Create a menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Create a file menu
        filemenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.read_more)
        filemenu.add_command(label="Open", command=self.read_more)  # TODO
        filemenu.add_command(label="Save", command=self.export_chat)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_closing)

        # Create a help menu
        helpmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="Read Me", command=self.read_more)
        helpmenu.add_command(label="About", command=self.about_message)

        top_frame = tk.Frame(self.root, bg=DARK_GREY)
        top_frame.grid(row=0, column=0, sticky="nsew")

        middle_frame = tk.Frame(self.root, bg=MEDIUM_GREY)
        middle_frame.grid(row=1, column=0, sticky="nsew")

        bottom_frame = tk.Frame(self.root, bg=DARK_GREY)
        bottom_frame.grid(row=2, column=0, sticky="nsew")

        self.username_textbox = tk.Entry(top_frame, font=FONT, bg=MEDIUM_GREY, fg=BLACK)
        # Set the focus on the username textbox...
        self.username_textbox.focus_set()
        # Bind the enter key to the connect method
        self.username_textbox.bind("<KeyPress>", self.join_shortcut)
        self.username_textbox.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        username_button = tk.Button(top_frame, text="Join", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE,
                                    command=self.connect)
        username_button.pack(side=tk.LEFT, padx=15)

        # clear button
        clear_button = tk.Button(bottom_frame, text="Clear", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE,
                                command=self.clear_message_textbox)
        clear_button.pack(side=tk.LEFT, padx=10)

        # Create a StringVar to track changes in the message textbox
        self.message_text_var = tk.StringVar()
        self.message_text_var.trace("w", self.validate_message_text)

        self.message_textbox = tk.Entry(bottom_frame, font=FONT, bg=MEDIUM_GREY, fg=BLACK, textvariable=self.message_text_var)
        self.message_textbox.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Send Button
        self.send_button = tk.Button(bottom_frame, text="Send", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE,
                                command=self.send_message, state=tk.DISABLED)
        self.send_button.pack(side=tk.LEFT, padx=10)

        self.exit_button = tk.Button(bottom_frame, text="Exit", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE,
                                    command=self.on_closing)

        # Emoji button
        self.emoji_button = tk.Button(bottom_frame, text="Emoji", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE,
                            command=self.show_emoji_popup)
        self.emoji_button.pack(side=tk.LEFT, padx=10)
        self.emoji_button.config(state=tk.DISABLED)

        self.exit_button.pack(side=tk.LEFT, padx=10)
        self.exit_button.config(state=tk.DISABLED)

        self.message_box = scrolledtext.ScrolledText(middle_frame, font=SMALL_FONT, bg=MEDIUM_GREY, fg=BLACK)
        self.message_box.config(state=tk.DISABLED)
        self.message_box.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def connect(self):
        if self.connect_callback:
            self.connect_callback()

    def send_message(self):
        if self.send_message_callback:
            self.send_message_callback()
        
        # After sending the message, clear the message textbox and disable the send button
        self.clear_message_textbox()
        self.send_button.config(state=tk.DISABLED)

    def exit_chat(self):
        if self.exit_callback:
            self.exit_callback()

    def add_message(self, message):
        # Convert emoji codes to actual emojis
        message_with_emojis = emoji.emojize(message)
        self.message_box.config(state=tk.NORMAL)
        self.message_box.insert(tk.END, message_with_emojis + '\n')
        self.message_box.config(state=tk.DISABLED)
        self.message_box.config(font=("Helvetica", 12))

    def get_username(self):
        return self.username_textbox.get()

    def get_message(self):
        return self.message_textbox.get()

    def clear_message_textbox(self):
        self.message_textbox.delete(0, tk.END)

    def disable_username_input(self):
        self.username_textbox.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.NORMAL)
        self.emoji_button.config(state=tk.NORMAL)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def send_shortcut(self, event):
        # Check if the "Ctrl" key and the "Enter" key are pressed simultaneously
        if event.state & 0x4 and event.keysym.lower() == "return":
            self.send_message()

    # function that will mimic the join button through a shortcut key which is "Enter"
    def join_shortcut(self, event):
        # check if the key pressed is "Enter"
        if event.keysym.lower() == "return":
            self.connect()

    # the about message function
    def about_message(self):
        messagebox.showinfo("About",
                            "PSCCA is a simple chat program. It is intended for educational purposes only."
                            "\n\nCreated by : Daniel Appel, Noah King, Myo Aung, Sungeun Kim, and Tony Alhusari.",
                            icon=tk.messagebox.INFO)

    # the read more function
    def read_more(self):
        webbrowser.open("https://github.com/Maung945/socket-programming-chat-app")

    def on_closing(self):
        # show a info box when closing the window
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.exit_chat()
    
    def show_emoji_popup(self):
        if not self.emoji_popup:
            self.emoji_popup = tk.Toplevel(self.root)
            self.emoji_popup.title("Emoji List")
            self.emoji_popup.iconbitmap("Client/logo1.ico")

            # Create a canvas for the emoji list
            emoji_canvas = tk.Canvas(self.emoji_popup)
            emoji_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Add a scrollbar to the canvas
            emoji_scrollbar = tk.Scrollbar(self.emoji_popup, orient="vertical", command=emoji_canvas.yview)
            emoji_scrollbar.pack(side=tk.RIGHT, fill="y")

            # Configure the canvas to work with the scrollbar
            emoji_canvas.configure(yscrollcommand=emoji_scrollbar.set)

            # Create a frame inside the canvas to contain the emoji buttons
            emoji_frame = tk.Frame(emoji_canvas)
            emoji_canvas.create_window((0, 0), window=emoji_frame, anchor='nw')

            for i, emoj in enumerate(self.emoji_list):
                emoji_button = tk.Button(emoji_frame, text=emoj, font=("Arial", 15),
                                        command=lambda e=emoj: self.insert_emoji(e))
                emoji_button.grid(row=i // 5, column=i % 5, padx=5, pady=5)

            # Bind the canvas scrolling to the mousewheel
            emoji_frame.bind("<Configure>", lambda e: emoji_canvas.configure(scrollregion=emoji_canvas.bbox("all")))

            # Bind the canvas scrolling to the arrow keys
            emoji_canvas.bind("<Configure>", lambda e: emoji_canvas.configure(scrollregion=emoji_canvas.bbox("all")))

            # Close the popup when the window is closed
            self.emoji_popup.protocol("WM_DELETE_WINDOW", self.close_emoji_popup)

    def insert_emoji(self, emoji):
        self.message_textbox.insert(tk.END, emoji)
        self.close_emoji_popup()

    def close_emoji_popup(self):
        if self.emoji_popup:
            self.emoji_popup.destroy()
            self.emoji_popup = None
    '''
    def export_chat(self):
        # first check if the file exists
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt")
            if file_path:
                with open(file_path, 'a') as file:
                    content = self.message_box.get("1.0", tk.END)
                    file.write(content)
        except OSError as oe:
            messagebox.showerror("Error", f"OS error: {str(oe)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export chat: {str(e)}")
    '''    
    def export_chat(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt")  # Change the default extension to .txt
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    messages = self.message_box.get("1.0", tk.END)
                    file.write(messages)
        except OSError as oe:
            messagebox.showerror("Error", f"OS error: {str(oe)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export chat: {str(e)}")

    def validate_message_text(self, *args):
        # Check if the message textbox is empty
        if self.get_message():
            # If there is something in the textbox, enable the send button
            self.send_button.config(state=tk.NORMAL)
        else:
            # If the textbox is empty, disable the send button
            self.send_button.config(state=tk.DISABLED)

    def mainloop(self):
        self.root.mainloop()