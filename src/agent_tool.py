import os # Pour accéder aux variables d'environnement (mots de passe)
from agents import function_tool # Outil spécial pour transformer une fonction Python en outil pour l'IA
from dotenv import load_dotenv # Pour charger le fichier .env
from upstash_vector import Index, Vector # Bibliothèque pour discuter avec la base de données vectorielle

# Charger les clés secrètes
load_dotenv()

# --- DÉFINITION DE L'OUTIL DE RECHERCHE ---
# Le décorateur @function_tool dit à l'IA : "Voici une capacité que tu peux utiliser".
@function_tool
def search_portfolio(query: str) -> str:
    """
    Cherche des informations pertinentes dans le portfolio grâce à la recherche sémantique.
    
    Args:
        query: La question ou les mots-clés de l'utilisateur.
    Returns:
        Un texte contenant les morceaux (chunks) d'information les plus pertinents trouvés.
    """
    
    # 1. On récupère les identifiants de la base de données
    url = os.getenv("UPSTASH_VECTOR_REST_URL")
    token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    
    # Si les clés sont absentes, on prévient l'IA qu'il y a un souci technique
    if not url or not token:
        return "Error: Upstash configuration missing."

    try:
        # 2. On se connecte à l'index (la base de données de vecteurs)
        index = Index(url=url, token=token)
        
        # 3. On lance la recherche
        # 'data=query' : On cherche ce qui ressemble au sens de la question
        # 'top_k=5' : On veut les 5 meilleurs résultats
        results = index.query(
            data=query, 
            top_k=5, 
            include_metadata=True, # On veut aussi le titre et la catégorie
            include_data=True      # On veut le texte complet
        )
        
        # Si on ne trouve rien, on le dit clairement
        if not results:
            return "No relevant information found in the portfolio."
            
        # 4. On met en forme les résultats pour que l'IA puisse les lire facilement
        formatted_results = []
        for res in results:
            # On récupère le texte et les infos associées
            content = getattr(res, 'data', '') or ''
            metadata = getattr(res, 'metadata', {}) or {}
            title = metadata.get('title', 'Untitled')
            source = metadata.get('source', 'Unknown')
            category = metadata.get('category', 'General')
            
            # On crée un bloc de texte structuré
            formatted_results.append(f"Catégorie: {category} | Source: {source} (Section: {title})\nContenu:\n{content}\n")
            
        # On joint tous les résultats séparés par un trait
        return "\n---\n".join(formatted_results)
        
    except Exception as e:
        # En cas d'erreur (bug), on renvoie le message d'erreur
        return f"Error occurred during search: {str(e)}"

# On donne un nom explicite à la fonction pour l'IA (en anglais car les modèles préfèrent souvent l'anglais pour les noms de fonctions)
search_portfolio.name = "search_portfolio"
