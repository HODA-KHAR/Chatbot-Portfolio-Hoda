
import os
import sys

# On "triche" un peu pour dire à Python de chercher les fichiers dans le dossier courant
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# On essaie d'importer la fonction load_file qui est juste à côté
try:
    from load import load_file
except ImportError:
    from src.load import load_file

"""
FONCTION : chunk_file
A quoi ça sert ?
Quand on a un très long texte (comme un CV complet), l'IA préfère recevoir des petits morceaux précis.
Cette fonction coupe le texte en morceaux logiques (Chunks).

Args:
    file_content (str): Tout le texte du fichier d' un coup.
Returns:
    list: Une liste de morceaux de texte (paragraphes).
"""
def chunk_file(file_content: str) -> list:
    # On a décidé que le symbole '#' (utilisé pour les titres en Markdown) servait de ciseaux.
    # Chaque fois qu'il y a un '#', on coupe !
    chunks = file_content.split("#")
    
    # Nettoyage :
    # 1. On parcourt chaque morceau découpé.
    # 2. .strip() enlève les espaces inutiles au début et à la fin.
    # 3. On ne garde que les morceaux qui ne sont pas vides.
    chunks = [chunk.strip() for chunk in chunks if chunk.strip() != ""]
    
    return chunks

# --- ZONE DE TEST ---
if __name__ == "__main__":
    # Ce code ne s'exécute que si on lance ce fichier directement
    # C'est pour vérifier que le découpage fonctionne bien.
    
    test_file = "./Data/experiences.md"
    # Petite vérification pour trouver le fichier si on n'est pas dans le bon dossier
    if not os.path.exists("./Data") and os.path.exists("../Data"):
        test_file = "../Data/experiences.md"
    
    if os.path.exists(test_file):
        print(f"Test avec {test_file}")
        file_content = load_file(test_file)
        chunks = chunk_file(file_content)

        print(f"J'ai trouvé {len(chunks)} morceaux !")
        for i, chunk in enumerate(chunks):
            print(f"--- Morceau n°{i+1} ---")
            print(chunk[:100].replace('\n', ' ') + "...") # On affiche juste le début
    else:
        print("Fichier de test non trouvé, impossible de tester.")
