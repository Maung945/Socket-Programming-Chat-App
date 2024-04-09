import tkinter as tk
import webbrowser
from tkinter import scrolledtext, filedialog
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
        self.root.title("PSCCA Chat App")
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
        # Create a menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Create a file menu
        filemenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.read_more)
        filemenu.add_command(label="Open", command=self.read_more) #TODO
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

        username_button = tk.Button(top_frame, text="Join", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=self.connect)
        username_button.pack(side=tk.LEFT, padx=15)

        # clear button
        clear_button = tk.Button(bottom_frame, text="Clear", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE,
                                 command=self.clear_message_textbox)
        clear_button.pack(side=tk.LEFT, padx=10)

        self.message_textbox = tk.Entry(bottom_frame, font=FONT, bg=MEDIUM_GREY, fg=BLACK)
        self.message_textbox.bind("<KeyPress>", self.send_shortcut)
        self.message_textbox.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        message_button = tk.Button(bottom_frame, text="Send", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=self.send_message)
        message_button.pack(side=tk.LEFT, padx=10)



        self.exit_button = tk.Button(bottom_frame, text="Exit", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=self.on_closing)
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

    def send_shortcut(self, event):
        if event.state == 12 and event.keysym.lower() == "return":
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
        #show a info box when closing the window
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.exit_chat()

    def export_chat(self):
        # first check if the file exists
        # if it does not, then create it
        # if it does, then ask if you want to overwrite it
        # if not, then ask if you want to save it as a new file

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

    def mainloop(self):
        self.root.mainloop()
