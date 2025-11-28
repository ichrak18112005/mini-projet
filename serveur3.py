import socket
import threading
import json

class Tache:
    def _init_(self, id, titre, description, auteur, status="TODO"):
        self.id = id
        self.titre = titre
        self.description = description
        self.status = status
        self.auteur = auteur

    def _str_(self):
        return f"{self.id}, {self.titre}, {self.description}, {self.auteur}, {self.status}"

class GestionnaireTaches:
    def _init_(self):
        self.TachesList = []
        self.next_id = 1
    def ajouter_tache(self, tache):
        self.TachesList.append(tache)

    def supprimer_tache(self, id):
        self.TachesList = [t for t in self.TachesList if t.id != id]

    def changer_status(self, newstatus, id):
        for tach in self.TachesList:
            if tach.id == id:
                tach.status = newstatus
    def sauvegarder(self):
        with open("taches.json", "w") as f:
            data = []
            for t in self.TachesList:
                data.append({
                    "id": t.id,
                    "titre": t.titre,
                    "description": t.description,
                    "auteur": t.auteur,
                    "status": t.status
                })
            json.dump(data, f, indent=4)
    def charger(self):
        try:
            with open("taches.json", "r") as f:
                data = json.load(f)
                for item in data:
                    t = Tache(item["id"], item["titre"], item["description"], item["auteur"], item["status"])
                    self.TachesList.append(t)
                if self.TachesList:
                    self.next_id = self.TachesList[-1].id + 1
        except FileNotFoundError:
            pass


class ServeurTaches:
    def _init_(self, taches):
        self.serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.taches = taches

    def gerer(self, port):
        self.serveur.bind(("0.0.0.0", port))
        self.serveur.listen()
        print("Serveur démarré, en attente de connexion...")

        while True:   # boucle infinie
            conn, address = self.serveur.accept()
            print("Client connecté :", address)
            threading.Thread(target=traiterR, args=(address,self.taches, conn)).start()

def traiterR(address,taches,connexion):
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
                    _, auteur, titre, description = data
                    t = Tache(id, titre, description, auteur)
                    taches.ajouter_tache(t)
                    taches.next_id += 1
                    connexion.send("Tâche ajoutée avec succès".encode())
                    taches.sauvegarder()
                case "2":
                    auteur = data[1] 
                    reponse=""
                    for t in taches.TachesList:
                        if t.auteur == auteur:
                            reponse += str(t) + "\n"
                    if reponse == "":
                            reponse = "Aucune tâche\n"
                    connexion.send(reponse.encode())
                    
                case "3":
                    id = data[1]
                    taches.supprimer_tache(id)
                    connexion.send("Tâche supprimée".encode())
                    taches.sauvegarder()

                case "4":
                    id, status = data[1], data[2]
                    if trouve(id, taches):
                        taches.changer_status(status, id)
                        connexion.send("Status modifié".encode())
                    else:
                        connexion.send("Cette tâche n'existe pas".encode())
                    taches.sauvegarder()

                case "5":
                    connexion.send("Vous avez déconnecté".encode())
                    print(f"🔌 Le client {address} a déconnecté")
                    break

                case _:
                    connexion.send("Commande invalide".encode())

        except ConnectionResetError:
            print("❌ Connexion interrompue brutalement par le client")
            break

    connexion.close()
def trouve(id,taches):
    t=False
    for tache in taches.TachesList:
        if tache.id==id:
            t=True
    return t
t = GestionnaireTaches()
t.charger()
s = ServeurTaches(t)
s.gerer(5000)
