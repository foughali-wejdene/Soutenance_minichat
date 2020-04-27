import socket
import select
import queue
import signal

HOST = 'localhost'
#définir deux constantes host et port
PORT = 8887
ENCODING = 'utf-8'


class Server(object):
    def __init__(self, host, port):


        self.host = host
        self.port = port
        self.buffer_size = 2048

        #creer objet sock où on a met la configuration de socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # login:connection dictionary
        #on a mis dedans pseudo de client connecté
        self.login_list = {}

        #tableau où il ya objet sock qu'on a défini
        self.inputs = [self.sock]
        #tableau vide
        self.outputs = []
        self.message_queues = {}

        self.shutdown = False
        try:
            #lié port et host avec socket qu'on a fait a l'aide de (bind)
            self.sock.bind((str(self.host), int(self.port)))
            #attendre la connexion d'un client
            self.sock.listen(10)
            self.sock.setblocking(False)
        except socket.error:
            self.shutdown = True

        # Trap for SIGINT for exiting
        signal.signal(signal.SIGINT, self.sighandler)
        self.run()

    def run(self):
        """Main server method"""
        #si shutdown = true <==>donc ya ereur
        if self.shutdown:
            raise Exception("This server was unable to bind with socket")
        #si non
        print("Server started")
        #boucle commence lorsque il ya au moins socket défini bien configuré (sutdown false) (objet sock bien défini)
        while self.inputs:
            try:
                # Use select to get lists of sockets ready for IO operations
                # select pour avoir liste de socket disponible pret pour les opérations input
                #parcourirs la socket dans la liste existe dans write read ou eexeptional
                read, write, exceptional = select.select(self.inputs, self.outputs, [])
            except select.error:
                break

            # Sockets processing
            # 1) readable sockets
            for socket in read:
                # a) processing server socket (incoming connection)
                #si socket de class server
                if socket is self.sock:
                    try:
                        #accepter connection , adresse
                        connection, address = socket.accept()
                        connection.setblocking(False)
                    except socket.error:
                        pass
                    #input tableau de socket
                    #append ajoute a la fin de tableau valeur
                    self.inputs.append(connection)
                    self.outputs.append(connection)
                    self.message_queues[connection] = queue.Queue()

                # b) processing client socket (incoming messages)
                # si non <==> socket de client pas de server
                else:
                    # une autre socket de server
                    # recevoir data de taille (2048)
                    data = socket.recv(self.buffer_size)
                    #exécute process data
                    self.process_data(data, socket)

            # 2) writeable s
            for socket in write:

                if socket in self.inputs: #condition n'est pas vide
                    if not self.message_queues[socket].empty():
                        #stucture qui contient message récu de client ou de server
                        # serveur envoie un message au client avec get
                        data = self.message_queues[socket].get()
                        socket.send(data)

            # 3) sockets where exceptions has occured
            for socket in exceptional:
                #effacer si un client déconnecter
                self.inputs.remove(socket)
                if socket in self.outputs:
                    self.outputs.remove(socket)
                    #effacer si le server déconnecter
                del self.message_queues[socket]
                #on ferme aaprés la suppression
                socket.close()
                #si il ya login ou adresse avec socket fermé il va l'effacer
                for login, address in self.login_list.items():
                    if address == socket:
                        del self.login_list[login]
                        break
                #execution de update login_list aprés suprression login et la sortie de socket
                self.update_login_list()
                #input peut avoir plusieur socket
    def process_data(self, data, socket):
        """Process data received by socket"""
        if data:
            #tjr message codé
            message = data.decode(ENCODING)
            #séparé data par (;)
            #diviser donnée au niveau de ; pour qu'on obtient sous forme d'un tableau
            message = message.split(';', 3)
            # at most 4 splits (don't split the message if it contains ;)
            #les données séparées par ;
            # Processing data
            # 1) new user logged in
            #si le premier indice est login
            if message[0] == 'login':
                #enregister le pseudo de client (qui est dans l'indice 1 déja)
                tmp_login = message[1]
                #si le pseudo dans login liste
                while message[1] in self.login_list:
                    #concatination de carctére #
                    message[1] += '#'
                if tmp_login != message[1]:
                    #envoyer un message de login
                    #message codé msg (msg envoyée ) , server c'est qui a envoyer  , pseudo
                    prompt = 'msg;server;' + message[1] + ';Login ' + tmp_login \
                             + ' already in use. Your login changed to ' + message[1] + '\n'
                    #envoyé prompt avec put si temp_login =! msg 1
                    self.message_queues[socket].put(prompt.encode(ENCODING))
                #enregister socket de client connecter dans la structure login_liste
                self.login_list[message[1]] = socket
                print(message[1] + ' has logged in')

                #envoyer msg à tout le monde avec pseudo connecter
                # Update list of active users, send it to clients
                self.update_login_list()

            # 2) user logged out
            elif message[0] == 'logout':
                #ecrire dans cmd pseudo de client
                print(message[1] + ' has logged out')
                #supression de socket
                self.inputs.remove(socket)
                if socket in self.outputs:
                    #effacer memoir (output)
                    self.outputs.remove(socket)
                del self.message_queues[socket]
                #fermeture de socket
                socket.close()
                #mise à jour de login list
                for login, address in self.login_list.items():
                    if address == socket:
                        #supression de login
                        del self.login_list[login]
                        break

                # Update list of active users, send it to clients
                #mise à jour à tout les clients connectés
                self.update_login_list()

            # 3) Message from one user to another (msg;origin;target;message) si le message va envoyer pour tout le monde
            elif message[0] == 'msg' and message[2] != 'all': #(target prend all)
                msg = data.decode(ENCODING) + '\n'
                data = msg.encode(ENCODING)
                target = self.login_list[message[2]]
                #le message vue par tout les clients
                self.message_queues[target].put(data)

            # 4) Message from one user to all users (msg;origin;all;message)
            elif message[0] == 'msg':
                msg = data.decode(ENCODING) + '\n'
                data = msg.encode(ENCODING)
                for connection, connection_queue in self.message_queues.items():
                    if connection != socket:
                        connection_queue.put(data)

        # Empty result in socket ready to be read from == closed connection
        #où il ya pas data qu'on va lire
        else:
            self.inputs.remove(socket)
            if socket in self.outputs:
                self.outputs.remove(socket)
            del self.message_queues[socket]
            socket.close()

            for login, address in self.login_list.items():
                if address == socket:
                    del self.login_list[login]
                    break

            self.update_login_list()

    def update_login_list(self):
        """Update login list and send it to active users"""
        logins = 'login'
        for login in self.login_list:
            #écrire les destination des message dont tout les pseudo des clients connectée qui recoient les messzages
            logins += ';' + login
        #message envoyer au client connecté avec pseudo
        logins += ';all' + '\n'
        logins = logins.encode(ENCODING)
        for connection, connection_queue in self.message_queues.items():
            connection_queue.put(logins)

    def sighandler(self, signum, frame):
        """Handle trapped SIGINT"""
        # close the server
        print('Shutting down server...')
        # close existing client sockets
        for connection in self.outputs:
            connection.close()
        self.sock.close()


if __name__ == '__main__':
    #exécuter l'stance de class server
    server = Server(HOST, PORT)
