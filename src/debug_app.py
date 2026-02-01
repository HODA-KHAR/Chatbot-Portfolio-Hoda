
import streamlit as st  # Bibliothèque pour créer le site web
import asyncio          # Pour simuler des temps d'attente (simulation de l'IA)
import uuid             # Pour générer des ID uniques
from dotenv import load_dotenv # Pour charger la config (même si moins utilisé ici)

# --- 1. CONFIGURATION (MODE TEST) ---
# On configure la page en mode "DEBUG"
st.set_page_config(
    page_title="Portfolio Assistant (DEBUG MODE)",
    page_icon="🛠️",
    layout="centered"
)

# --- 2. GESTION DE LA SESSION (MÉMOIRE TEMPORAIRE) ---
# On vérifie si la mémoire "messages" existe, sinon on la crée
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.question_count = 0
    # Message d'accueil par défaut
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Bonjour ! Je suis l'assistant virtuel. Posez-moi des questions sur mes projets."
    })

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

# --- 3. EN-TÊTE & BOUTON RÉINITIALISER ---
col1, col2 = st.columns([5, 2])
with col1:
    st.title("✨ Assistant Portfolio")
with col2:
    if st.button("Réinitialiser", help="Effacer l'historique"):
        # RAZ (Remise à Zéro) de la mémoire
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.question_count = 0 
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Bonjour ! Je suis Hoda (version IA). Posez-moi des questions sur mes projets."
        })
        st.rerun()

# --- 4. MESSAGE DE BIENVENUE ---
# Affiché uniquement au tout début
if len(st.session_state.messages) <= 1:
    st.header("Bonjour !")
    st.subheader("Bienvenue sur mon portfolio")
    st.markdown("Une question sur mon parcours Data ? Besoin de détails sur mes projets en Power BI ou Python ? **Écrivez-moi ci-dessous.**")

# --- 5. AFFICHAGE DE L'HISTORIQUE ---
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        # On ignore le premier message si on est sur l'accueil
        if message == st.session_state.messages[0] and len(st.session_state.messages) <= 1:
            continue
            
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 6. LOGIQUE DES SUGGESTIONS ---
def get_suggestions(last_message_content):
    content = last_message_content.lower()
    suggestions = []
    
    # Simple logique locale pour le mode Debug
    # Si on parle de projet et qu'on a déjà commencé à discuter
    if "projet" in content and st.session_state.question_count > 0:
        suggestions.append("Quelles sont les technologies utilisées ?")
        suggestions.append("Peux-tu décrire ce projet ?")
        suggestions.append("Quels sont les apports de ce projet ?")
    else:
        # Suggestions par défaut au démarrage
        if st.session_state.question_count < 2:
            suggestions.append("Peux-tu me parler de ton alternance chez Enedis ?")
            suggestions.append("Quels sont tes projets ?")
            suggestions.append("Que retiens-tu du BUT Science des Données ?")
    return suggestions

def handle_suggestion(question):
    st.session_state.messages.append({"role": "user", "content": question})
    asyncio.run(process_mock_response(question))
    st.rerun()

# --- 7. SIMULATION DE L'IA (MOCK) ---
# Ici, pas de vraie IA, on fait semblant pour tester l'interface
async def process_mock_response(user_input):
    st.session_state.question_count += 1
    
    with st.chat_message("assistant"):
        with st.spinner("Simulation..."):
            await asyncio.sleep(0.5) # On attend une demi-seconde
            response = f"**Réponse simulée** pour '{user_input}'.\n(Environnement Data validé)."
            
            # Test du pied de page LinkedIn
            if st.session_state.question_count >= 5 and st.session_state.question_count % 5 == 0:
                 footer_msg = "\n\n---\n*Si vous avez plus de questions, veuillez me contacter via [mon LinkedIn](https://www.linkedin.com/in/hoda-kharbouche-/).*"
                 response += footer_msg
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- 8. AFFICHAGE DES SUGGESTIONS (BAS DE PAGE) ---
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

# --- 9. ENTRÉE UTILISATEUR ---
if prompt := st.chat_input("Testez l'interface ici..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    asyncio.run(process_mock_response(prompt))
