import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import webbrowser

# Colors & Fonts...
GUNMETAL = "#29353D"
ELECTRIC_BLUE = "#007FFF"
TIMBERWOLF = "#DDD6D0"
PLATINUM = "#1a2227"
FONT = ("Segoe UI", 12, "bold")
BUTTON_FONT = ("Segoe UI", 10, "bold")
SMALL_FONT = ("Segoe UI", 9)

class ChatUI:
    def __init__(self, connect_callback, send_message_callback, exit_callback):
        #CTk Configuration...
        self.root = ctk.CTk()
        self.root.config(bg=TIMBERWOLF)
        self.root.geometry("600x600")
        self.root.title("PSCCA Chat App")
        self.root.resizable(True, True)
        self.menu_visible = False

        #Menu toggle...
        self.root.bind("<Alt_L>", self.toggle_menu)  #Bind Alt key for left Alt...
        self.root.bind("<Alt_R>", self.toggle_menu)  #Bind Alt key for right Alt...

        #Set application icon...
        self.root.iconbitmap("Client/logo1.ico")
        
        # Communications logic callbacks...
        self.connect_callback = connect_callback
        self.send_message_callback = send_message_callback
        self.exit_callback = exit_callback

        # CTk Structure using grid manager...
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=4)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Generate UI...
        self.setup_ui()

    def setup_ui(self):
        #Menubar...
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=tk.NONE)  # Initially visible...

        filemenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.read_more)
        filemenu.add_command(label="Open", command=self.read_more)
        filemenu.add_command(label="Save", command=self.export_chat)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_closing)

        helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="Read Me", command=self.read_more)
        helpmenu.add_command(label="About", command=self.about_message)

        #Top Frame...
        top_frame = ctk.CTkFrame(self.root, fg_color=PLATINUM, corner_radius = 0)
        top_frame.grid(row=0, column=0, sticky="nsew")

        self.username_textbox = ctk.CTkEntry(top_frame, font=FONT, fg_color=GUNMETAL, text_color=TIMBERWOLF, border_width=0)
        self.username_textbox.focus_set()
        self.username_textbox.bind("<KeyPress>", self.join_shortcut)
        self.username_textbox.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        username_button = ctk.CTkButton(top_frame, text="Join", font=BUTTON_FONT, fg_color=ELECTRIC_BLUE, text_color=PLATINUM, command=self.connect)
        username_button.pack(side=tk.LEFT, padx=15)

        #Middle Frame...
        middle_frame = ctk.CTkFrame(self.root, fg_color=PLATINUM, corner_radius = 0)
        middle_frame.grid(row=1, column=0, sticky="nsew")
        #Setting up the scrolled text and custom scrollbar...
        self.message_box = tk.Text(middle_frame, borderwidth=0, font=SMALL_FONT, bg=PLATINUM, fg=TIMBERWOLF, padx=10)
        self.message_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.message_box.config(state=tk.DISABLED)
        scrollbar = ctk.CTkScrollbar(middle_frame, command=self.message_box.yview, button_color=TIMBERWOLF, width= 10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_box.config(yscrollcommand=scrollbar.set)

        #Bottom frame...
        bottom_frame = ctk.CTkFrame(self.root, fg_color=PLATINUM, corner_radius = 0)
        bottom_frame.grid(row=2, column=0, sticky="nsew")
        self.message_textbox = ctk.CTkEntry(bottom_frame, font=FONT, fg_color=GUNMETAL, text_color=TIMBERWOLF, border_width=0)
        self.message_textbox.bind("<KeyPress>", self.send_shortcut)
        self.message_textbox.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        message_button = ctk.CTkButton(bottom_frame, text="Send", font=BUTTON_FONT, fg_color=ELECTRIC_BLUE, text_color=PLATINUM, command=self.send_message)
        message_button.pack(side=tk.LEFT, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    
    def toggle_menu(self, event=None):
        if self.menu_visible:
            self.root.config(menu=tk.NONE)  # Hide the menu
            self.menu_visible = False
        else:
            self.root.config(menu=self.menubar)  # Show the menu
            self.menu_visible = True

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
        """
        Check if the "Ctrl" key and the "Enter" key are pressed simultaneously
        """
        if event.state & 0x4 and event.keysym.lower() == "return":
            self.send_message()

    def join_shortcut(self, event):
        """
        function that will mimic the join button through a shortcut key which is "Enter"
        check if the key pressed is "Enter"
        """
        if event.keysym.lower() == "return":
            self.connect()

   
    def about_message(self):
        """
        the about message function
        """
        messagebox.showinfo("About",
                            "PSCCA is a simple chat program. It is intended for educational purposes only."
                            "\n\nAuthors: Tony Alhusari, Daniel Appel, Myo Aung, Sungeun Kim, Noah King",
                            icon=tk.messagebox.INFO)
 
    def read_more(self):
        """
        the read more function
        """
        webbrowser.open("https://github.com/Maung945/socket-programming-chat-app")

    def on_closing(self):
        """
        show a info box when closing the window
        """
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.exit_chat()

    def export_chat(self):
        """
        first check if the file exists
        if it does not, then create it
        if it does, then ask if you want to overwrite it
        if not, then ask if you want to save it as a new file
        """
       

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
