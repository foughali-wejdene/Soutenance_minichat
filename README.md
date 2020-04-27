# Soutenance_minichat
### Simple chat in Python with Tkinter GUI on client side. 

## Getting started

### Requirements  
Python 3.4 or higher  

Modules:  
``` 
socket
tkinter
threading
select 
time
queue
```   
## Usage

### Lancement
Pour l'utiliser localement, vous devez d'abord exécuter le fichier serveur, 'server_select`, puis vous pouvez exécuter` client.py` dans un terminal séparé.     
### Sortie
Pour quitter le client, cliquez simplement sur le bouton «Quitter» ou «x» dans le coin supérieur droit.

### Protocole de messagerie

Ce serveur utilise un protocole de communication simple, qui est le suivant:

* modèle: `type_action; origine; cible; contenu_message`
* user1 envoie un message à user2: `msg; user1; user2; message_contents`
* l'utilisateur envoie un message à tous les utilisateurs: `msg; user; ALL; message_contents`
* l'utilisateur se connecte ou se déconnecte: `login; user` /` logout; user`
* le serveur informe les utilisateurs des changements dans la liste de connexion `login; user1; user2; user3; [...]; ALL
