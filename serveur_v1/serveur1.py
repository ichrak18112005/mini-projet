import socket
import threading

class Tache:
    def __init__(self, id, titre, description, auteur, status="TODO"):
        self.id = id
        self.titre = titre
        self.description = description
        self.status = status
        self.auteur = auteur

    def __str__(self):
        return f"{self.id}, {self.titre}, {self.description}, {self.auteur}, {self.status}"

class GestionnaireTaches:
    def __init__(self):
        self.TachesList = []

    def ajouter_tache(self, tache):
        self.TachesList.append(tache)

    def supprimer_tache(self, id):
        self.TachesList = [t for t in self.TachesList if t.id != id]

    def changer_status(self, newstatus, id):
        for tach in self.TachesList:
            if tach.id == id:
                tach.status = newstatus

class ServeurTaches:
    def __init__(self, taches):
        self.serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.taches = taches

    def gerer(self, port):
        self.serveur.bind(("0.0.0.0", port))
        self.serveur.listen()
        print("Serveur démarré, en attente de connexion...")

        while True:   # boucle infinie
            conn, address = self.serveur.accept()
            print("Client connecté :", address)
            threading.Thread(target=traiterR, args=(self.taches, conn)).start()

def traiterR(taches, connexion):
    while True:
        try:
            msg = connexion.recv(1024).decode()
            if not msg:   # client fermé
                print("🔌 Client déconnecté")
                break

            data = msg.split(",")
            commande = data[0]

            match commande:
                case "1":
                    _, id, auteur, titre, description = data
                    t = Tache(id, titre, description, auteur)
                    taches.ajouter_tache(t)
                    connexion.send("Tâche ajoutée avec succès".encode())

                case "2":
                    auteur = data[1]   # correction d'erreur !
                    for t in taches.TachesList:
                        if t.auteur == auteur:
                            connexion.send((str(t) + "\n").encode())
                    connexion.send("FIN".encode())

                case "3":
                    id = data[1]
                    taches.supprimer_tache(id)
                    connexion.send("Tâche supprimée".encode())

                case "4":
                    id, status = data[1], data[2]
                    taches.changer_status(status, id)
                    connexion.send("Status modifié".encode())

                case "5":
                    connexion.send("Vous avez déconnecté".encode())
                    print("🔌 Client a envoyé la commande 5 → déconnexion")
                    break

                case _:
                    connexion.send("Commande invalide".encode())

        except ConnectionResetError:
            print("❌ Connexion interrompue brutalement par le client")
            break

    connexion.close()

t = GestionnaireTaches()
s = ServeurTaches(t)
s.gerer(5000)