
import os # Pour naviguer dans les dossiers
import sys # Pour modifier les chemins système
import glob # Pour trouver tous les fichiers avec une certaine extension (ex: *.md)
from dotenv import load_dotenv # Pour charger les mots de passe

# Petit hack pour s'assurer qu'on peut importer nos propres fichiers python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# On essaie d'importer nos outils de chargement et de découpage
try:
    from load import load_file
    from chunker import chunk_file
except ImportError:
    from src.load import load_file
    from src.chunker import chunk_file

from upstash_vector import Index, Vector # Outils pour la base de données Vectorielle

# On charge les clés secrètes (.env)
load_dotenv(override=True)

"""
FONCTION PRINCIPALE : index_file
C'est le chef d'orchestre qui transforme un fichier texte en "souvenirs" pour l'IA.

Les 4 étapes clés :
1. LIRE : On ouvre le fichier et on prend tout le texte.
2. DÉCOUPER (Chunking) : On coupe le texte en petits morceaux (paragraphes) pour que l'IA ne se perde pas.
3. VECTORISER : On transforme chaque morceau en une liste de nombres (vecteur) compréhensible par l'IA.
4. SAUVEGARDER (Upsert) : On envoie ces vecteurs dans le cloud (Upstash) pour s'en souvenir plus tard.
"""
def index_file(file_path:str):
    print("Traitement du fichier : ", file_path)
    
    # Étape 1: Chargement
    file_content = load_file(file_path)
    
    # Étape 2: Découpage
    chunks = chunk_file(file_content)
    
    # Connexion à la base de données (Le Cloud)
    index = None
    try:
        index = Index.from_env() # Se connecte automatiquement grâce au fichier .env
    except Exception as e:
        print(f"⚠️ Initialisation Upstash impossible (champs manquants dans .env ou erreur réseau) : {e}")
    
    vectors = []
    
    # Étape 3: Création des "souvenirs" (Vecteurs)
    for i, chunk in enumerate(chunks):
        # On donne un nom unique à chaque morceau (ex: mon_fichier_0, mon_fichier_1...)
        safe_id = f"{os.path.basename(file_path)}_{i}"
        
        # On prépare le paquet à envoyer
        v = Vector(
            id=safe_id,
            data=chunk, # Le texte réel
            metadata={
                "source": file_path, # D'où ça vient
                "chunk_index": i     # C'est quel morceau
            }
        )
        vectors.append(v)

    # Étape 4: Envoi vers le Cloud
    if vectors:
        success_upstash = False
        if index:
            try:
                # On essaie d'envoyer à Upstash
                index.upsert(vectors=vectors) # "Upsert" = Mettre à jour ou Insérer
                print(f"✅ Indexé {len(vectors)} morceaux pour {file_path} vers UPSTASH")
                success_upstash = True
            except Exception as e:
                print(f"⚠️ Erreur lors de l'envoi vers Upstash : {e}")
        
        # SI ÇA RATE (Pas d'internet ou mauvaise configuration)
        if not success_upstash:
            print(f"⚠️ Impossible de connecter à Upstash.")
            print("🔄 Passage en mode LOCAL : Sauvegarde dans un fichier 'local_index.json' sur votre ordi.")
            
            # On utilise un fichier local comme roue de secours
            import json
            local_file = "local_index.json"
            
            # On récupère ce qu'il y avait déjà avant
            existing_data = []
            if os.path.exists(local_file):
                try:
                    with open(local_file, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                except:
                    pass
            
            # On prépare les nouvelles données
            new_data = [
                {
                    "id": v.id,
                    "data": v.data,
                    "metadata": v.metadata
                } for v in vectors
            ]
            
            # On ajoute et on sauvegarde tout
            existing_data.extend(new_data)
            with open(local_file, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Sauvegardé {len(vectors)} morceaux dans '{local_file}'")

# C'est ici que le programme commence vraiment quand on lance le fichier
if __name__ == "__main__":
    # On cherche tous les fichiers Markdown (.md) dans le dossier Data
    search_path = "../Data/*.md"
    if not os.path.exists("../Data"):
        search_path = "./Data/*.md" # Ajustement si on est dans un autre dossier
        
    files = glob.glob(search_path)
    
    if not files:
        print(f"Aucun fichier trouvé dans {search_path}")
    
    # On boucle sur chaque fichier trouvé et on lance l'indexation
    for file_path in files:
        index_file(file_path)
        print(f"Fin du traitement pour {file_path}")
