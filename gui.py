import tkinter as tk
import threading
from tkinter import scrolledtext
from tkinter import messagebox

ENCODING = 'utf-8'


class GUI(threading.Thread):
    def __init__(self, client):
        super().__init__(daemon=False, target=self.run)
        self.font = ('Helvetica', 13)
        self.client = client
        self.login_window = None
        self.main_window = None

    def run(self):
        #execution de l'attribue login window
        self.login_window = LoginWindow(self, self.font)
        #enregister le pseudo de client connecté dans login de classe chat window
        self.main_window = ChatWindow(self, self.font)
        #appelle notify server et on donne le pseudo entry login_window  enregistré qui estentré par le client
        self.notify_server(self.login_window.login, 'login')
        #instance de classe chat window
        #exécution de fonction run
        self.main_window.run()

    @staticmethod
    def display_alert(message):
        """Display alert box"""
        messagebox.showinfo('Error', message)

    def update_login_list(self, active_users):
        """Update login list in main window with list of users"""
        self.main_window.update_login_list(active_users)

    def display_message(self, message):
        """Display message in ChatWindow"""
        self.main_window.display_message(message)

    def send_message(self, message):
        """Enqueue message in client's queue"""
        #appelle à l'objet client . son attribue queue(où il ya message ). put
        self.client.queue.put(message)

    def set_target(self, target):
        """Set target for messages"""
        self.client.target = target

    def notify_server(self, message, action):
        """Notify server after action was performed"""
        #on va codé un message avec data
        data = action + ";" + message # action=logout ; pseudo de client qui est sortie
        data = data.encode(ENCODING)
        #fichier client dans classe client
        #appelle à la fonction notify server
        self.client.notify_server(data, action)

    def login(self, login):
        #notification de login de server
        self.client.notify_server(login, 'login')

    def logout(self, logout):
        # notification de logout  de server
        self.client.notify_server(logout, 'logout')


class Window(object):
    def __init__(self, title, font):
        self.root = tk.Tk()
        self.title = title
        self.root.title(title)
        self.font = font

#interface graphique de login (demende de pseudo)
class LoginWindow(Window):
    def __init__(self, gui, font):
        super().__init__("Login", font)
        self.gui = gui
        self.label = None
        self.entry = None
        self.button = None
        self.login = None

        self.build_window()
        self.run()
#interface
    def build_window(self):
        """Build login window, , set widgets positioning and event bindings"""
        self.label = tk.Label(self.root, text='Enter your login', width=20, font=self.font)
        self.label.pack(side=tk.LEFT, expand=tk.YES)

        self.entry = tk.Entry(self.root, width=20, font=self.font)
        self.entry.focus_set()
        #prendre le pseudo et la fermeture de l'interface de login
        self.entry.pack(side=tk.LEFT)
        self.entry.bind('<Return>', self.get_login_event)

        self.button = tk.Button(self.root, text='Login', font=self.font)
        self.button.pack(side=tk.LEFT)
        self.button.bind('<Button-1>', self.get_login_event)

    def run(self):
        """Handle login window actions"""
        self.root.mainloop()
        self.root.destroy()

    def get_login_event(self, event):
        """Get login from login box and close login window"""
        #entry <==> input box
        #prendre le pseudo de l'input box et ferme interface de login
        self.login = self.entry.get()
        self.root.quit()

#room des messages public
class ChatWindow(Window):
    def __init__(self, gui, font):
        super().__init__("Python Chat", font)
        self.gui = gui
        self.messages_list = None
        self.logins_list = None
        self.entry = None
        self.send_button = None
        self.exit_button = None
        self.lock = threading.RLock()
        self.target = ''
        #atrribue login va prendre l'attribu de class login window où enregistrer pseudo de client connecté
        self.login = self.gui.login_window.login
                    #fermeture de fenetre
        self.build_window()
    #ouverture un nouvelle fenetre
    def build_window(self):
        """Build chat window, set widgets positioning and event bindings"""
        # Size config
        self.root.geometry('750x500')
        self.root.minsize(600, 400)

        # Frames config
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E)

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # List of messages
        frame00 = tk.Frame(main_frame)
        frame00.grid(column=0, row=0, rowspan=2, sticky=tk.N + tk.S + tk.W + tk.E)

        # List of logins
        frame01 = tk.Frame(main_frame)
        frame01.grid(column=1, row=0, rowspan=3, sticky=tk.N + tk.S + tk.W + tk.E)

        # Message entry
        frame02 = tk.Frame(main_frame)
        frame02.grid(column=0, row=2, columnspan=1, sticky=tk.N + tk.S + tk.W + tk.E)

        # Buttons
        frame03 = tk.Frame(main_frame)
        frame03.grid(column=0, row=3, columnspan=2, sticky=tk.N + tk.S + tk.W + tk.E)

        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=8)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # ScrolledText widget for displaying messages
        self.messages_list = scrolledtext.ScrolledText(frame00, wrap='word', font=self.font)
        self.messages_list.insert(tk.END, 'Welcome to Python Chat\n')
        self.messages_list.configure(state='disabled')

        # Listbox widget for displaying active users and selecting them
        #liste des pseudos connecté
        self.logins_list = tk.Listbox(frame01, selectmode=tk.SINGLE, font=self.font,
                                      exportselection=False)
        self.logins_list.bind('<<ListboxSelect>>', self.selected_login_event)

        # Entry widget for typing messages in
        self.entry = tk.Text(frame02, font=self.font)
        self.entry.focus_set()
        self.entry.bind('<Return>', self.send_entry_event)

        # Button widget for sending messages
        self.send_button = tk.Button(frame03, text='Send', font=self.font)
        self.send_button.bind('<Button-1>', self.send_entry_event)

        # Button for exiting
        self.exit_button = tk.Button(frame03, text='Exit', font=self.font)
        self.exit_button.bind('<Button-1>', self.exit_event)

        # Positioning widgets in frame
        self.messages_list.pack(fill=tk.BOTH, expand=tk.YES)
        self.logins_list.pack(fill=tk.BOTH, expand=tk.YES)
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.send_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.exit_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

        # Protocol for closing window using 'x' button
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing_event)

    def run(self):
        """Handle chat window actions"""
        self.root.mainloop()
        self.root.destroy()

    def selected_login_event(self, event):
        """Set as target currently selected login on login list"""
        target = self.logins_list.get(self.logins_list.curselection())
        self.target = target
        self.gui.set_target(target)

    def send_entry_event(self, event):
        """Send message from entry field to target"""
        #décodage
        text = self.entry.get(1.0, tk.END)
        if text != '\n':
            message = 'msg;' + self.login + ';' + self.target + ';' + text[:-1]
            #self.target car lorsque on va selectionné pseudo dans l'attribue  target  de la classe chat window
            print(message)
            #exécution la fct send messg dans classe gui
            self.gui.send_message(message.encode(ENCODING))
            #créé une mark à une position donnée dans un texte (avec mark_set)
            self.entry.mark_set(tk.INSERT, 1.0)
            self.entry.delete(1.0, tk.END)
            #curseur sur entry<==> input box
            self.entry.focus_set()
        else:
            messagebox.showinfo('Warning', 'You must enter non-empty message')

        with self.lock:
            self.messages_list.configure(state='normal')
            if text != '\n':
                self.messages_list.insert(tk.END, text)
            self.messages_list.configure(state='disabled')
            self.messages_list.see(tk.END)
        return 'break'

    def exit_event(self, event):
        """Send logout message and quit app when "Exit" pressed"""
        #lors de la fermeture de fenetre on va éxecuter notify server
        self.gui.notify_server(self.login, 'logout')
        self.root.quit()

    def on_closing_event(self):
        """Exit window when 'x' button is pressed"""
        self.exit_event(None)

    def display_message(self, message):
        """Display message in ScrolledText widget"""
        with self.lock:
            self.messages_list.configure(state='normal')
            self.messages_list.insert(tk.END, message)
            #message readable <==> juste lire
            self.messages_list.configure(state='disabled')
            #hilight pour dernier message
            self.messages_list.see(tk.END)

    def update_login_list(self, active_users):
        """Update listbox with list of active users"""
        self.logins_list.delete(0, tk.END)
        for user in active_users:
            self.logins_list.insert(tk.END, user)
        self.logins_list.select_set(0)
        self.target = self.logins_list.get(self.logins_list.curselection())
