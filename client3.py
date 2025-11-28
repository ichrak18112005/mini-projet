import socket

class ClientTaches:
    def _init_(self, name):
        self.name = name
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connecter(self, ip, port):
        self.conn.connect((ip, port))

    def envoyer(self):
        interface()
        choix = int(input("Choix : "))

        if choix == 5:
            self.conn.send("5".encode())
            print(self.conn.recv(1024).decode())
            return False

        match choix:
            case 1:
                titre = input("Titre : ")
                desc = input("Description : ")
                msg = f"1,{self.name},{titre},{desc}"
            case 2:
                msg = f"2,{self.name}"
            case 3:
                id = input("Id : ")
                msg = f"3,{id}"
            case 4:
                id = input("Id : ")
                statut = input("Statut : ")
                msg = f"4,{id},{statut}"
            case _:
                print("Commande invalide")
                return True

        self.conn.send(msg.encode())
        print(self.conn.recv(1024).decode())
        return True

def interface():
    print("\n* MENU *")
    print("1. Ajouter tâche")
    print("2. Lister tâches")
    print("3. Supprimer tâche")
    print("4. Changer statut")
    print("5. Quitter")

client = ClientTaches("Ali")
client.connecter("127.0.0.1", 5000)

while True:
    if not client.envoyer():
        break
 