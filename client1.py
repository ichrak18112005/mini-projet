import socket

global_id = 0

class ClientTaches:
    def __init__(self, name):
        self.name = name
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connecter(self, ip, port):
        self.conn.connect((ip, port))

    def envoyer(self):
        global global_id
        interface()
        choix = int(input("Choice: "))

        if choix == 5:
            self.conn.send("5,bye".encode())
            print("Goodbye")
            return False

        match choix:
            case 1:
                titre = input("Title: ")
                desc = input("Description: ")
                global_id += 1
                msg = f"1,{global_id},{self.name},{titre},{desc}"
            case 2:
                msg = f"2,{self.name}"
            case 3:
                id = input("Id: ")
                msg = f"3,{id}"
            case 4:
                id = input("Id: ")
                statut = input("Status: ")
                msg = f"4,{id},{statut}"
            case _:
                print("Invalid command")
                return True

        self.conn.send(msg.encode())
        return True

    def recevoir(self):
        print(self.conn.recv(1024).decode())

def interface():
    print("\n* Menu *")
    print("1. Add task")
    print("2. List tasks")
    print("3. Delete task")
    print("4. Change status")
    print("5. Quit")

# --- Main Program ---
name = input("Your name: ")
client = ClientTaches(name)
client.connecter("127.0.0.1", 5000)

while True:
    cont = client.envoyer()
    if not cont:
        client.conn.close()
        break
    client.recevoir()
