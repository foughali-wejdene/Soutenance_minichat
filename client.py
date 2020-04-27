import socket
import time
import select
import queue
from gui import *
#définir deux constantes host et port
ENCODING = 'utf-8'
HOST = 'localhost'
PORT = 8887


class Client(threading.Thread):
    #executer constructeur de class client on donnons host et port(des constantes)
    def __init__(self, host, port):
        super().__init__(daemon=True, target=self.run)
        #host appartient a la classe client
        self.host = host
        self.port = port
        self.sock = None

        self.connected = self.connect_to_server()
        #taille de buffer 1024
        self.buffer_size = 1024
        #??? aprés
        self.queue = queue.Queue()
        self.lock = threading.RLock()
        #carctére vide
        self.login = ''
        # carctére vide
        self.target = ''
        #prendre pseudo de client connectée avec mise à jour de server
        self.login_list = []
        # attribue connected va prendre true si la connexion est réeussite
        #si le client est connectée
        if self.connected:
            #si le client est connectée
            #gui appartient a la classe client
            #faire instanse de classe gui
            self.gui = GUI(self)
            self.start()
            self.gui.start()
            # Only gui is non-daemon thread, therefore after closing gui app will quit

    def connect_to_server(self):
        """Connect to server via socket interface, return (is_connected)"""
        try:
            #configuration , ouverture et tester  socket
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((str(self.host), int(self.port)))
        except ConnectionRefusedError:
            print("Server is inactive, unable to connect")
            #si il ya un erreur de connexion
            return False
        #connexion au server est réussi
        return True

    def run(self):
        """Handle client-server communication using select module"""
        #mettre socket de client ouvert
        inputs = [self.sock]
        outputs = [self.sock]
        while inputs:
            try:
                read, write, exceptional = select.select(inputs, outputs, inputs)
            # if server unexpectedly quits, this will raise ValueError exception (file descriptor < 0)
            # erreur d'exeption
            except ValueError:
                print('Server error')
                #socket de client sa marche pas
                #afficher alert
                GUI.display_alert('Server error has occurred. Exit app')
                #fermeture d socket
                self.sock.close()
                break

            if self.sock in read:
                with self.lock:
                    try:
                        # recevoir data de taille (2048)
                        data = self.sock.recv(self.buffer_size)
                    # erreur d'exeption
                    except socket.error:
                        #afficher un message d'erreur
                        print("Socket error")
                        #afficher l'alert
                        GUI.display_alert('Socket error has occurred. Exit app')
                        # fermeture d socket
                        self.sock.close()
                        break
                # exécute process data
                self.process_received_data(data)

            if self.sock in write:
                # condition n'est pas vide
                if not self.queue.empty():
                    #écrire le message (get)
                    data = self.queue.get()
                    #envoyer msg
                    self.send_message(data)
                    self.queue.task_done()
                else:
                    time.sleep(0.05)

            if self.sock in exceptional:
                # erreur d'exeption
                print('Server error')
                # afficher l'alert
                GUI.display_alert('Server error has occurred. Exit app')
                #fermeture de socket
                self.sock.close()
                break

    def process_received_data(self, data):
        """Process received message from server"""
        if data:
            # tjr message codé
            message = data.decode(ENCODING)
            # séparé data par retour à la ligne
            message = message.split('\n')

            for msg in message:
                #si le msg est vide
                if msg != '':
                    # On les séparons  par ;
                    msg = msg.split(';')

                    #si le premier indice est msg
                    if msg[0] == 'msg':
                        #text va prendre le msg entré par l'utilisateur
                        text = msg[1] + ' >> ' + msg[3] + '\n'
                        #afficher le msg
                        print(msg)
                        #display msg in chatwindow
                        self.gui.display_message(text)

                        # if chosen login is already in use
                        if msg[2] != self.login and msg[2] != 'ALL':
                            self.login = msg[2]

                    elif msg[0] == 'login':
                        # envoyer msg à tout le monde avec pseudo connecter
                        self.gui.main_window.update_login_list(msg[1:])

    def notify_server(self, action, action_type):
        """Notify server if action is performed by client"""
        #on a mis l'action (==data) dans queue
        self.queue.put(action)
        if action_type == "login":
            #si action_type = login
            self.login = action.decode(ENCODING).split(';')[1] #split sépare
        elif action_type == "logout":
            #fermeture de socket
            self.sock.close()

    def send_message(self, data):
        """"Send encoded message to server"""
        with self.lock:
            try:
                #send a message
                self.sock.send(data)
                # erreur d'exeption
            except socket.error:
                #fermeture de socket
                self.sock.close()
                #afficher l'alerte
                GUI.display_alert('Server error has occurred. Exit app')


# Create new client with (IP, port)
#définir main
if __name__ == '__main__':
    # faire l'instance de class client on a donner host et port
    # executer constructeur de class client on donnons host et port(des constantes)
    Client(HOST, PORT)
