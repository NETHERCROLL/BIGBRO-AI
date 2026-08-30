import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CONFIGURATION DE L'IA (Mettez votre clé Google AI Studio ici)
GEMINI_API_KEY = "VOTRE_CLE_API_GEMINI_ICI"

# Configuration de la page Streamlit pour mobile
st.set_page_config(page_title="Kolo-Exam", page_icon="🎓", layout="centered")

# Injection CSS propre pour le design Cameroun (Bleu, Blanc, Or)
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-title {
        color: #0b3c5d;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        color: #d9b310;
        text-align: center;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .status-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .online { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .offline { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    </style>
""", unsafe_allow_html=True)

# En-tête de l'application
st.markdown("<h1 class='main-title'>🎓 Kolo-Exam</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Ton Grand Frère IA pour le BEPC, Probatoire et Bac</p>", unsafe_allow_html=True)

# 2. GESTION DU MODE EN LIGNE / HORS-LIGNE
# Option pour simuler la connexion sur Streamlit
mode = st.radio("Connexion réseau :", ["En ligne (Connecté au Grand Frère)", "Hors-ligne (Mode Local Kolo)"], horizontal=True)

if mode == "En ligne (Connecté au Grand Frère)":
    st.markdown("<div class='status-badge online'>🟢 Connecté au Grand Frère - Prêt à t'aider</div>", unsafe_allow_html=True)
    is_online = True
else:
    st.markdown("<div class='status-badge offline'>🟠 Mode Kolo-Local activé (Simulation)</div>", unsafe_allow_html=True)
    is_online = False

# 3. INITIALISATION DE L'IA
if is_online:
    if GEMINI_API_KEY == "VOTRE_CLE_API_GEMINI_ICI" or not GEMINI_API_KEY:
        st.warning("⚠️ N'oublie pas de remplacer 'VOTRE_CLE_API_GEMINI_ICI' par ta vraie clé dans le code app.py.")
    else:
        genai.configure(api_key=GEMINI_API_KEY)

# Conserver l'historique de la discussion
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les anciens messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 4. ZONE DE SCAN PHOTO (MULTIMODALITÉ)
st.write("---")
uploaded_file = st.file_input("📷 Scanne ou prends en photo ton exercice :", type=["png", "jpg", "jpeg"])

image_to_send = None
if uploaded_file is not None:
    image_to_send = Image.open(uploaded_file)
    st.image(image_to_send, caption="Exercice chargé avec succès !", use_container_width=True)

# 5. ENVOI DU MESSAGE ET LOGIQUE DE L'IA
if prompt := st.chat_input("Pose ta question ici (ex: Je bloque sur l'exercice de physique...)"):
    # Afficher le message de l'élève
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Générer la réponse
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        if not is_online:
            # Réponse simulée si le téléphone n'a pas internet
            reponse_locale = "💡 *[Mode Kolo-Local]* : Salut mon petit ! Je vois que le réseau dérange. En mode hors-ligne complet, je ne peux pas encore analyser de nouvelles images sans encombrer la mémoire de ton téléphone. Relis bien les formules de ton cahier en attendant que le réseau revienne, ou active le mode 'En ligne' pour que je t'aide !"
            response_placeholder.write(reponse_locale)
            st.session_state.messages.append({"role": "assistant", "content": reponse_locale})
        else:
            try:
                # Configuration du comportement de l'IA (System Prompt)
                system_instruction = (
                    "Tu es Kolo-Exam, un grand frère et tuteur IA expert du programme scolaire camerounais (MINESEC : BEPC, Probatoire, Baccalauréat). "
                    "Ton but est d'aider l'élève à résoudre ses exercices de mathématiques, physique ou chimie. "
                    "RÈGLE ABSOLUE : Ne donne jamais la solution directement. Guide l'élève pas à pas. Pose-lui des questions sur son cours pour le pousser à trouver la formule. "
                    "Utilise des expressions camerounaises bienveillantes mais sérieuses (ex: 'Mon petit', 'Tu t'en sors ?', 'Regarde bien l'énoncé, ne te presse pas', 'On est ensemble')."
                )
                
                # Choix du modèle Gemini léger et rapide
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_instruction
                )
                
                # Préparation du contenu (Texte seul OU Texte + Image)
                content_payload = [prompt]
                if image_to_send:
                    content_payload.append(image_to_send)
                
                # Appel à l'IA
                with st.spinner("Le Grand Frère réfléchit..."):
                    response = model.generate_content(content_payload)
                    
                response_placeholder.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                response_placeholder.write(f"❌ Erreur lors de la connexion à l'IA : {e}")
