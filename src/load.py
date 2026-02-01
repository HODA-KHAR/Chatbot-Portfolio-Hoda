
"""
FONCTION : load_file
C'est la fonction la plus simple mais la plus essentielle : elle sait lire un fichier.

Args :
    file_path (str): L'adresse du fichier sur l'ordinateur.
Returns:
    str: Le contenu du fichier (ce qui est écrit dedans).
"""
def load_file(file_path: str) -> str:
    # 'open' ouvre le fichier.
    # 'r' veut dire Read (Lecture seule).
    # 'utf-8' permet de lire les accents français (é, à, è...) sans bugs.
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read() # On lit tout et on renvoie le texte

# Test rapide
if __name__ == "__main__":
    import os
    # On crée un faux fichier pour vérifier que ça marche
    if not os.path.exists("./Data"):
        try:
             os.makedirs("./Data")
             with open("./Data/test.md", "w") as f: f.write("Ceci est un test de lecture.")
             print("Lecture du fichier test :")
             print(load_file("./Data/test.md"))
        except:
             print("Impossible de créer le dossier test.")
    else:
        print("Dossier Data trouvé.")
