import socket
import json

def interface():
    print("\n📝 GESTION DES TÂCHES")
    print("1. Ajouter une tâche")
    print("2. Lister toutes les tâches")
    print("3. Supprimer une tâche")
    print("4. Changer le statut d'une tâche")
    print("5. Quitter ❌")

class ClientTaches:
    statuss = ["TODO", "DOING", "DONE"]

    def __init__(self, nom):
        self.nom = nom.strip()
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connecter(self, ip, port=5000):
        self.conn.connect((ip, port))
        # Envoyer le nom au serveur à la connexion
        self.conn.send(json.dumps({"auteur": self.nom}).encode())
        resp = self.conn.recv(4096).decode()
        print(json.loads(resp)["message"])

    def envoyer(self, data):
        self.conn.send(json.dumps(data).encode())
        resp = self.conn.recv(4096).decode()
        return json.loads(resp)

    def run(self):
        while True:
            interface()
            choix = input("Choix (entre 1 et 5) : ").strip()
            if not choix.isdigit():
                print("⚠️ Entrée invalide")
                continue

            choix = int(choix)
            msg = {}

            if choix == 1:
                titre = input("Titre : ").strip()
                desc = input("Description : ").strip()
                if not titre or not desc:
                    print("⚠️ Titre et description obligatoires")
                    continue
                msg = {"action": "1", "titre": titre, "description": desc}

            elif choix == 2:
                msg = {"action": "2"}

            elif choix == 3:
                id_input = input("ID à supprimer : ").strip()
                if not id_input.isdigit():
                    print("⚠️ ID invalide")
                    continue
                msg = {"action": "3", "id": int(id_input)}

            elif choix == 4:
                id_input = input("ID : ").strip()
                if not id_input.isdigit():
                    print("⚠️ ID invalide")
                    continue
                print("Statuts possibles : TODO, DOING, DONE")
                status = input("Nouveau statut : ").upper().strip()
                if status not in self.statuss:
                    print("⚠️ Statut invalide")
                    continue
                msg = {"action": "4", "id": int(id_input), "status": status}

            elif choix == 5:
                msg = {"action": "5"}
                resp = self.envoyer(msg)
                print(resp["message"])
                self.conn.close()
                break

            else:
                print("⚠️ Choix invalide")
                continue

            resp = self.envoyer(msg)
            if choix == 2:
                tasks = resp.get("taches", [])
                print("\nVos tâches :")
                for t in tasks:
                    print(f"ID: {t['id']} | Titre: {t['titre']} | Description: {t['description']} | Statut: {t['status']}")
            else:
                print(resp["message"])


if __name__ == "__main__":
    nom = input("Donnez votre nom : ").strip()
    if not nom:
        print("⚠️ Nom obligatoire")
        exit()
    client = ClientTaches(nom)
    try:
        client.connecter("127.0.0.1")
    except ConnectionRefusedError:
        print("❌ Impossible de se connecter au serveur")
        exit()
    client.run()
