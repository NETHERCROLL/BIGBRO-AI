<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Ton Grand Frère IA</title>
    <style>
        :root {
            --primary: #1e3a8a; /* Bleu Roi */
            --secondary: #f59e0b; /* Jaune Or */
            --bg: #f3f4f6;
            --chat-bg: #ffffff;
            --text: #1f2937;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: var(--bg);
            color: var(--text);
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }

        header {
            background-color: var(--primary);
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 1.2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
        }

        header .status {
            font-size: 0.75rem;
            display: block;
            font-weight: normal;
            margin-top: 2px;
        }

        .status-online { color: #10b981; }
        .status-offline { color: var(--secondary); }

        #chat-container {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 16px;
            line-height: 1.4;
            font-size: 0.95rem;
            word-wrap: break-word;
        }

        .user {
            background-color: var(--primary);
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }

        .ai {
            background-color: var(--chat-bg);
            color: var(--text);
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }

        .message img {
            max-width: 100%;
            border-radius: 8px;
            margin-bottom: 8px;
            display: block;
        }

        #preview-container {
            display: none;
            padding: 8px 15px;
            background: #e5e7eb;
            align-items: center;
            gap: 10px;
        }

        #image-preview {
            height: 50px;
            border-radius: 4px;
            object-fit: cover;
        }

        #cancel-image {
            background: #ef4444;
            color: white;
            border: none;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 12px;
            cursor: pointer;
        }

        #input-container {
            background-color: var(--chat-bg);
            padding: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
            border-top: 1px solid #e5e7eb;
        }

        .btn-icon {
            background: #f3f4f6;
            border: none;
            width: 42px;
            height: 42px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.2rem;
            transition: background 0.2s;
        }

        .btn-icon:hover { background: #e5e7eb; }

        #text-input {
            flex: 1;
            padding: 12px;
            border: 1px solid #d1d5db;
            border-radius: 24px;
            outline: none;
            font-size: 0.95rem;
        }

        #send-btn {
            background-color: var(--secondary);
            color: white;
        }

        #send-btn:hover { background-color: #d97706; }

        /* Mode d'emploi Offline */
        .offline-notice {
            background-color: #fef3c7;
            border: 1px solid #f59e0b;
            color: #b45309;
            padding: 10px;
            border-radius: 8px;
            font-size: 0.85rem;
            margin-bottom: 10px;
            text-align: center;
        }
    </style>
</head>
<body>

    <header>
        🎓 Kolo-Exam
        <span id="network-status" class="status status-online">● Connecté au Grand Frère</span>
    </header>

    <div id="chat-container">
        <div class="message ai">
            Mbala ! C'est ton grand frère Kolo-Exam. Tu es bloqué sur quel exercice de mathématiques, physique ou chimie ? Envoie-moi l'énoncé ou prends simplement une photo propre. On va gérer ça ensemble pas à pas, mon petit !
        </div>
    </div>

    <div id="preview-container">
        <img id="image-preview" src="" alt="Aperçu">
        <button id="cancel-image">×</button>
        <span style="font-size: 0.85rem; color: #4b5563;">Photo ajoutée au message</span>
    </div>

    <div id="input-container">
        <label class="btn-icon" for="file-input">
            📷
            <input type="file" id="file-input" accept="image/*" style="display: none;">
        </label>
        <input type="text" id="text-input" placeholder="Pose ta question ici...">
        <button id="send-btn" class="btn-icon">➔</button>
    </div>

    <script>
        // CONFIGURATION : Mets ta clé API Gemini entre les guillemets ci-dessous !
        const GEMINI_API_KEY = "VOTRE_CLE_API_GEMINI_ICI";

        const chatContainer = document.getElementById('chat-container');
        const textInput = document.getElementById('text-input');
        const sendBtn = document.getElementById('send-btn');
        const fileInput = document.getElementById('file-input');
        const previewContainer = document.getElementById('preview-container');
        const imagePreview = document.getElementById('image-preview');
        const cancelImage = document.getElementById('cancel-image');
        const networkStatus = document.getElementById('network-status');

        let selectedImageBase64 = null;
        let selectedImageType = null;
        let isOnline = navigator.onLine;

        // Gestion de la détection du réseau (Internet / Hors-ligne)
        function updateNetworkStatus() {
            isOnline = navigator.onLine;
            if (isOnline) {
                networkStatus.textContent = "● Connecté au Grand Frère (En ligne)";
                networkStatus.className = "status status-online";
            } else {
                networkStatus.textContent = "● Mode Local (Hors-ligne activé)";
                networkStatus.className = "status status-offline";
                
                // Notification éducative sur l'écran
                const notice = document.createElement('div');
                notice.className = 'offline-notice';
                notice.textContent = "⚠️ Tu es hors-ligne. Le mode local nécessite une intégration d'IA embarquée (via Android). Les requêtes directes à l'API en ligne échoueront tant que le réseau ne revient pas.";
                chatContainer.appendChild(notice);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }
        window.addEventListener('online', updateNetworkStatus);
        window.addEventListener('offline', updateNetworkStatus);
        updateNetworkStatus(); // Exécution initiale

        // Gestion de l'image
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                selectedImageType = file.type;
                const reader = new FileReader();
                reader.onload = function(evt) {
                    selectedImageBase64 = evt.target.result.split(',')[1];
                    imagePreview.src = evt.target.result;
                    previewContainer.style.display = 'flex';
                };
                reader.readAsDataURL(file);
            }
        });

        cancelImage.addEventListener('click', function() {
            selectedImageBase64 = null;
            selectedImageType = null;
            fileInput.value = '';
            previewContainer.style.display = 'none';
        });

        // Envoi de message
        async function sendMessage() {
            const text = textInput.value.trim();
            if (!text && !selectedImageBase64) return;

            // 1. Rendu du message utilisateur sur l'écran
            const userDiv = document.createElement('div');
            userDiv.className = 'message user';
            
            if (selectedImageBase64) {
                const img = document.createElement('img');
                img.src = `data:${selectedImageType};base64,${selectedImageBase64}`;
                userDiv.appendChild(img);
            }
            if (text) {
                const p = document.createElement('p');
                p.textContent = text;
                userDiv.appendChild(p);
            }
            chatContainer.appendChild(userDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            // Sauvegarde des données actuelles pour l'envoi et reset des champs d'entrée
            const msgText = text;
            const imgBase64 = selectedImageBase64;
            const imgType = selectedImageType;

            textInput.value = '';
            cancelImage.click();

            // 2. Rendu de l'état de chargement IA
            const aiDiv = document.createElement('div');
            aiDiv.className = 'message ai';
            aiDiv.textContent = "Attends un peu, ton grand frère réfléchit...";
            chatContainer.appendChild(aiDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            // 3. Gestion de l'alternative hors-ligne
            if (!isOnline) {
                aiDiv.innerHTML = "<strong>[Mode Kolo-Local]</strong> : Majo, je suis déconnecté du réseau ! Pour que je te réponde sans internet au village, ce prototype web doit être converti en application Android native avec l'IA directement téléchargée dans ton téléphone. Reconnecte-toi pour interroger mon serveur en ligne.";
                return;
            }

            if (GEMINI_API_KEY === "VOTRE_CLE_API_GEMINI_ICI" || GEMINI_API_KEY === "") {
                aiDiv.innerHTML = "⚠️ <strong>Erreur :</strong> Tu as oublié d'entrer ta clé API Gemini à la ligne 146 du code ! Récupère une clé gratuite sur Google AI Studio et colle-la dans le fichier.";
                return;
            }

            // 4. Appel à l'API Google Gemini (Vision & Texte)
            try {
                // Définition du prompt système adapté à la culture camerounaise
                const systemInstruction = "Tu es Kolo-Exam, un grand frère et tuteur IA expert du programme scolaire camerounais (MINESEC : BEPC, Probatoire, Baccalauréat). Ton but est d'aider l'élève à résoudre ses exercices de mathématiques, physique ou chimie. RÈGLE ABSOLUE : Ne donne jamais la solution directement. Guide l'élève pas à pas. Pose-lui des questions sur son cours pour le pousser à trouver la formule. Utilise des expressions camerounaises bienveillantes (ex: 'Mon petit', 'Tu t'en sors ?', 'Regarde bien l'énoncé, ne te presse pas'). Reste concis dans tes réponses pour préserver la lisibilité sur mobile.";

                let contentsPayload = [];
                let parts = [];

                if (imgBase64) {
                    parts.push({
                        inlineData: {
                            mimeType: imgType,
                            data: imgBase64
                        }
                    });
                }
                
                parts.push({ text: msgText || "Analyse cette image et guide-moi selon tes consignes de tuteur." });
                contentsPayload.push({ parts: parts });

                const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        contents: contentsPayload,
                        systemInstruction: { parts: [{ text: systemInstruction }] }
                    })
                });

                const data = await response.json();
                if (data.candidates && data.candidates[0].content.parts[0].text) {
                    aiDiv.textContent = data.candidates[0].content.parts[0].text;
                } else {
                    aiDiv.textContent = "Akié, j'ai eu un petit problème pour lire ce message. Réessaie encore ?";
                }
            } catch (error) {
                console.error(error);
                aiDiv.textContent = "Erreur de connexion avec l'API. Vérifie ta clé ou ton réseau, mon petit.";
            }
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        sendBtn.addEventListener('click', sendMessage);
        textInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>