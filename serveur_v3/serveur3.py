import socket
import threading
import json

# Classe tâche
class Tache:
    def __init__(self, id, titre, description, auteur, status="TODO"):
        self.id = id
        self.titre = titre
        self.description = description
        self.auteur = auteur.strip()
        self.status = status

    def dictionnaire(self):
        return {
            "id": self.id,
            "titre": self.titre,
            "description": self.description,
            "auteur": self.auteur,
            "status": self.status
        }

# Gestionnaire avec persistance
class GestionnaireTaches:
    FICHIER = "taches.json"

    def __init__(self):
        self.TachesList = []
        self.next_id = 1
        self.charger()

    def ajouter_tache(self, tache):
        self.TachesList.append(tache)
        self.next_id += 1
        self.sauvegarder()

    def supprimer_tache(self, id):
        self.TachesList = [t for t in self.TachesList if t.id != id]
        self.sauvegarder()

    def changer_status(self, id, status):
        for t in self.TachesList:
            if t.id == id:
                t.status = status
        self.sauvegarder()

    def sauvegarder(self):
        with open(self.FICHIER, "w") as f:
            json.dump([t.dictionnaire() for t in self.TachesList], f, indent=4)

    def charger(self):
        try:
            with open(self.FICHIER, "r") as f:
                data = json.load(f)
                for item in data:
                    t = Tache(item["id"], item["titre"], item["description"], item["auteur"], item["status"])
                    self.TachesList.append(t)
                if self.TachesList:
                    self.next_id = self.TachesList[-1].id + 1
        except FileNotFoundError:
            pass

# Serveur
class ServeurTaches:
    def __init__(self, gest, host="0.0.0.0", port=5000):
        self.gest = gest
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def gerer_client(self, conn, addr):
        print(f"Connexion de {addr}")
        try:
            # Étape 1 : recevoir le nom du client
            data = conn.recv(4096).decode()
            msg = json.loads(data)
            client_nom = msg.get("auteur", "").strip()
            print(f"Nom du client : {client_nom}")
            conn.send(json.dumps({"message": f"Bienvenue {client_nom} !"}).encode())
        except:
            conn.close()
            return

        # Boucle principale pour ce client
        while True:
            try:
                data = conn.recv(4096).decode()
                if not data:
                    break

                msg = json.loads(data)
                action = msg.get("action")
                reponse = {"message": "Commande invalide"}

                # Ajouter tâche
                if action == "1":
                    titre = msg.get("titre", "")
                    desc = msg.get("description", "")
                    t = Tache(self.gest.next_id, titre, desc, client_nom)
                    self.gest.ajouter_tache(t)
                    reponse = {"message": f"Tâche ajoutée avec ID {t.id}"}

                # Lister les tâches de ce client uniquement
                elif action == "2":
                    taches_client = [t.dictionnaire() for t in self.gest.TachesList if t.auteur == client_nom]
                    reponse = {"taches": taches_client}

                # Supprimer tâche (vérifie que le client est l'auteur)
                elif action == "3":
                    task_id = int(msg.get("id", 0))
                    trouve = False
                    for t in self.gest.TachesList:
                        if t.id == task_id:
                            trouve = True
                            if t.auteur == client_nom:
                                self.gest.supprimer_tache(task_id)
                                reponse = {"message": f"Tâche {task_id} supprimée"}
                            else:
                                reponse = {"message": "Erreur : vous n'êtes pas l'auteur"}
                            break
                    if not trouve:
                        reponse = {"message": "Erreur : tâche inexistante"}

                # Changer statut (vérifie que le client est l'auteur)
                elif action == "4":
                    task_id = int(msg.get("id", 0))
                    nouveau_statut = msg.get("status", "")
                    trouve = False
                    for t in self.gest.TachesList:
                        if t.id == task_id:
                            trouve = True
                            if t.auteur == client_nom:
                                self.gest.changer_status(task_id, nouveau_statut)
                                reponse = {"message": f"Statut de la tâche {task_id} changé"}
                            else:
                                reponse = {"message": "Erreur : vous n'êtes pas l'auteur"}
                            break
                    if not trouve:
                        reponse = {"message": "Erreur : tâche inexistante"}

                # Quitter
                elif action == "5":
                    reponse = {"message": "Au revoir !"}
                    conn.send(json.dumps(reponse).encode())
                    break

                conn.send(json.dumps(reponse).encode())

            except Exception as e:
                print(f"Erreur côté serveur avec {addr}: {e}")
                break

        conn.close()
        print(f"Déconnexion de {addr}")

    def gerer(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"Serveur démarré sur {self.host}:{self.port}")

        while True:
            conn, addr = self.server.accept()
            threading.Thread(target=self.gerer_client, args=(conn, addr)).start()


if __name__ == "__main__":
    gest = GestionnaireTaches()
    serveur = ServeurTaches(gest)
    serveur.gerer()
