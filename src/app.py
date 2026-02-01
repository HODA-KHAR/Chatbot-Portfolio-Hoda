import streamlit as st  # Bibliothèque pour créer le site web facilement
import asyncio          # Pour gérer les tâches asynchrones (attendre des réponses sans bloquer)
import os               # Pour interagir avec le système d'exploitation (fichiers, variables d'environnement)
import uuid             # Pour générer des identifiants Uniques (UUID) pour chaque session
import json             # Pour gérer le format de données JSON (texte structuré)
from dotenv import load_dotenv  # Pour charger les mots de passe depuis le fichier .env caché
from agents import Runner       # Le "moteur" qui fait tourner notre agent IA
from agent import portfolio_agent # Notre agent IA spécifique (Hoda) importé depuis agent.py
from upstash_redis import Redis   # Connecteur pour la base de données Redis (mémoire externe)

# --- 1. CHARGEMENT DE LA CONFIGURATION ---
# On charge les clés secrètes (API keys) depuis le fichier .env
load_dotenv()

# --- 2. CONFIGURATION DE LA PAGE ---
# On définit le titre de l'onglet, l'icône, et la mise en page
st.set_page_config(
    page_title="Portfolio Assistant - Hoda Kharbouche",
    page_icon="🤖",
    layout="centered"
)

# --- 3. EN-TÊTE & BOUTON RÉINITIALISER ---
# On divise l'écran en 2 colonnes : une grande (5) pour le titre, une petite (2) pour le bouton
col1, col2 = st.columns([5, 2])
with col1:
    st.title("✨ Assistant Portfolio")

with col2:
    # Si on clique sur le bouton "Réinitialiser"
    if st.button("Réinitialiser", help="Effacer l'historique"):
        st.session_state.messages = []          # On vide la liste des messages
        st.session_state.session_id = str(uuid.uuid4()) # On crée une nouvelle session
        st.session_state.question_count = 0     # On remet le compteur de questions à 0
        
        # On ajoute le message de bienvenue par défaut
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Bonjour ! Je suis Hoda (version IA). Posez-moi des questions sur mes projets."
        })
        st.rerun() # On recharge la page pour appliquer les changements

# --- 4. CONNEXION À LA BASE DE DONNÉES (REDIS) ---
# Cette fonction se connecte à la mémoire externe pour sauvegarder les conversations
@st.cache_resource
def get_redis_client():
    url = os.getenv("UPSTASH_REDIS_REST_URL")
    token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    # Si on a bien l'URL et le mot de passe, on se connecte
    if url and token:
        try:
            return Redis(url=url, token=token)
        except Exception as e:
            st.error(f"Failed to connect to Redis: {e}")
            return None
    return None

redis_client = get_redis_client()

# --- 5. GESTION DE LA SESSION (MÉMOIRE LOCALE) ---
# Si c'est la première visite, on initialise l'historique
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.question_count = 0

# Clé unique pour retrouver l'historique de cet utilisateur dans Redis
SESSION_KEY = f"chat_history:{st.session_state.session_id}"

# Fonction pour récupérer l'historique sauvegardé
def load_history():
    if redis_client:
        try:
            stored_data = redis_client.get(SESSION_KEY)
            if stored_data:
                return json.loads(stored_data) # On convertit le texte JSON en liste Python
        except Exception:
            pass
    return []

# Fonction pour sauvegarder l'historique
def save_history(messages):
    if redis_client:
        try:
            # On sauvegarde pour 24 heures (86400 secondes)
            redis_client.setex(SESSION_KEY, 86400, json.dumps(messages))
        except Exception as e:
            print(f"Error saving to Redis: {e}")

# Au démarrage, on charge les messages précédents s'ils existent
if "messages" not in st.session_state or not st.session_state.messages:
    loaded_msgs = load_history()
    if loaded_msgs:
        st.session_state.messages = loaded_msgs
        st.session_state.question_count = sum(1 for m in loaded_msgs if m["role"] == "user")
    else:
        # Sinon, on commence vide avec juste le message d'accueil
        st.session_state.messages = []
        st.session_state.question_count = 0
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Bonjour ! Je suis Hoda (version IA). Posez-moi des questions sur mes projets."
        })

# --- 6. AFFICHAGE DE L'ACCUEIL ---
# Affiche le grand titre "Bonjour" seulement si la conversation vient de commencer
if len(st.session_state.messages) <= 1:
    st.header("Bonjour !")
    st.subheader("Bienvenue sur mon portfolio")
    st.markdown("Une question sur mon parcours Data ? Besoin de détails sur mes projets en Power BI ou Python ? **Écrivez-moi ci-dessous.**")

# --- 7. AFFICHAGE DES MESSAGES ---
# On parcourt tout l'historique et on affiche chaque message
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        # On saute le tout premier message si on est encore sur l'écran d'accueil
        if message == st.session_state.messages[0] and len(st.session_state.messages) <= 1:
            continue

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 8. LOGIQUE DES SUGGESTIONS ---
def get_suggestions(last_message_content):
    """
    Détermine les boutons de suggestions à afficher en bas de l'écran.
    """
    content = last_message_content.lower() # On met tout en minuscule pour faciliter la comparaison
    suggestions = []
    
    # Dictionnaire de mots-clés pour reconnaître les projets
    project_map = {
        "rome": "le projet Rome",
        "territoire": "le projet Rome",
        "météo": "le concours Météo France",
        "meteo": "le concours Météo France",
        "climat": "le concours Météo France",
        "immo": "la régression immobilière",
        "régression": "la régression immobilière",
        "regression": "la régression immobilière",
        "reporting": "le reporting Excel/VBA",
        "excel": "le reporting Excel/VBA",
        "vba": "le reporting Excel/VBA",
        "scraping": "le projet de Scraping",
        "enquête": "le projet d'enquête",
        "enquete": "le projet d'enquête",
        "martinique": "le projet Martinique",
        "chômage": "le projet Martinique",
        "chomage": "le projet Martinique",
        "mysql": "la base de données",
        "base de données": "la base de données",
        "sql": "la base de données",
        "échantillonnage": "le projet d'estimation",
        "echantillonnage": "le projet d'estimation",
        "accidents": "l'analyse des accidents",
        "power bi": "Power BI"
    }

    # On cherche si un mot-clé de projet est présent dans le dernier message
    detected_project = None
    for keyword, name in project_map.items():
        if keyword in content:
            detected_project = name
            break
    
    # CAS 1 : On parle d'un projet spécifique -> On propose d'approfondir (Tech, Desc, Apports)
    if detected_project:
        suggestions.append(f"Quelles sont les technologies pour {detected_project} ?")
        suggestions.append(f"Peux-tu décrire {detected_project} ?")
        suggestions.append(f"Quels sont les apports de {detected_project} ?")
        return suggestions
        
    # CAS 2 : On parle de "projet" en général -> On propose de creuser
    # On vérifie question_count > 0 pour ne pas déclencher ça sur le message "Bonjour"
    elif ("projet" in content or "réalisé" in content) and st.session_state.question_count > 0:
        suggestions.append("Quelles sont les technologies utilisées ?")
        suggestions.append("Peux-tu décrire ce projet ?")
        suggestions.append("Quels sont les apports de ce projet ?")
        return suggestions
    
    # CAS 3 : DÉFAUT (Début de conversation ou sujet inconnu) -> Suggestions principales
    else:
         if st.session_state.question_count < 2: 
            suggestions.append("Peux-tu me parler de ton alternance chez Enedis ?")
            suggestions.append("Quels sont tes projets ?")
            suggestions.append("Que retiens-tu du BUT Science des Données ?")
    
    return suggestions

# Fonction pour gérer le clic sur un bouton de suggestion
def handle_suggestion(question):
    st.session_state.messages.append({"role": "user", "content": question})
    process_response(question) # On lance la réponse de l'IA directement
    st.rerun()

# --- 9. TRAITEMENT DE LA RÉPONSE (IA) ---
def process_response(user_input):
    st.session_state.question_count += 1 # On incrémente le compteur
    
    with st.chat_message("assistant"):
        with st.spinner("Je réfléchis..."): # Affiche le petit sablier
            try:
                # C'est ICI qu'on appelle l'Intelligence Artificielle
                result = Runner.run_sync(portfolio_agent, user_input)
                response = result.final_output
                
                # Ajout du lien LinkedIn tous les 5 messages
                if st.session_state.question_count >= 5 and st.session_state.question_count % 5 == 0:
                     footer_msg = "\n\n---\n*Si vous avez plus de questions, veuillez me contacter via [mon LinkedIn](https://www.linkedin.com/in/hoda-kharbouche-/).*"
                     response += footer_msg
                
                # Affichage de la réponse
                st.markdown(response)
                
                # Sauvegarde dans la mémoire
                st.session_state.messages.append({"role": "assistant", "content": response})
                save_history(st.session_state.messages)

            except Exception as e:
                error_msg = f"Une erreur est survenue: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# --- 10. AFFICHAGE DES SUGGESTIONS ---
# Si le dernier message vient de l'assistant, on affiche des suggestions pertinentes
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    last_msg = st.session_state.messages[-1]["content"]
    suggestions = get_suggestions(last_msg)
    
    if suggestions:
        st.markdown("### Suggestions :")
        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            if i < len(cols):
                with cols[i]:
                    if st.button(suggestion):
                        handle_suggestion(suggestion)

# --- 11. ZONE DE SAISIE UTILISATEUR ---
# La barre en bas pour taper sa question
if prompt := st.chat_input("Votre question..."):
    # On affiche le message de l'utilisateur
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history(st.session_state.messages)
    
    # On lance la réflexion de l'IA
    process_response(prompt)
